"""Optimized Decision Matrix for API Call Sequencing

Implements mentor feedback on cost optimization:
- Number Verification FIRST (mentor: if number verify fails, why call SIM Swap?)
- Sequential API calls with early stopping
- Cost combinations with margin calculation
- 25-75% average cost reduction depending on fraud patterns

Reference: docs/MENTOR_RESPONSES.md Section 2
"""

from dataclasses import dataclass
from typing import Callable

from ..schemas import (
    DecisionMatrixCase, 
    OptimizedTrustEvaluation, 
    TrustStatus,
    TrustScoreWeights
)


@dataclass
class APICallResult:
    api_name: str
    score: float
    raw_value: str
    flags: list[str]
    duration_ms: int


# Estimated cost per API call in EUR (Nokia NaC pricing estimates)
API_COST_EUR: dict[str, float] = {
    "number_verify": 0.03,   # Cheapest — Authorization flow
    "sim_swap": 0.05,        # CIBA flow
    "device_status": 0.04,   # CIBA flow
    "location": 0.06,        # Most expensive — requires network positioning
}

# SafeRide charges B2B clients per evaluation
SAFERIDE_CHARGE_PER_EVALUATION_EUR = 0.50


# Pre-defined decision matrix (Mentor's insight: Number Verify first)
DECISION_MATRIX: list[DecisionMatrixCase] = [
    DecisionMatrixCase(
        case_id="case_1_all_ok",
        name="Tous les checks OK",
        conditions={"number": "verified", "sim_swap": "clean", "device": "healthy", "location": "match"},
        apis_to_call=["number_verify", "sim_swap", "device_status", "location"],
        apis_skipped=[],
        score_formula="weighted_average",
        action="allow",
        estimated_cost=1.0
    ),
    DecisionMatrixCase(
        case_id="case_2_number_failed",
        name="Number verification échouée",
        conditions={"number": "failed"},
        apis_to_call=["number_verify"],  # Early stop - only 1 API called
        apis_skipped=["sim_swap", "device_status", "location"],
        score_formula="zero_score_block",
        action="block",
        estimated_cost=0.14  # 0.03 / 0.18 = ~14% of full cost
    ),
    DecisionMatrixCase(
        case_id="case_3_sim_swap_fraud",
        name="SIM Swap récent détecté (après Number Verify OK)",
        conditions={"number": "verified", "sim_swap": "recent_swap"},
        apis_to_call=["number_verify", "sim_swap"],  # 2 APIs called
        apis_skipped=["device_status", "location"],
        score_formula="zero_score_block",
        action="block",
        estimated_cost=0.44  # (0.03+0.05) / 0.18 = ~44%
    ),
    DecisionMatrixCase(
        case_id="case_4_device_suspicious",
        name="Device suspect",
        conditions={"number": "verified", "sim_swap": "clean", "device": "suspicious"},
        apis_to_call=["number_verify", "sim_swap", "device_status", "location"],  # Full check
        apis_skipped=[],
        score_formula="weighted_with_penalty",
        action="review",
        estimated_cost=1.0
    ),
    DecisionMatrixCase(
        case_id="case_5_location_mismatch",
        name="Location mismatch",
        conditions={"number": "verified", "sim_swap": "clean", "device": "healthy", "location": "mismatch"},
        apis_to_call=["number_verify", "sim_swap", "device_status", "location"],
        apis_skipped=[],
        score_formula="reduced_weight_location",
        action="review",
        estimated_cost=1.0
    ),
    DecisionMatrixCase(
        case_id="case_6_fast_track",
        name="Conducteur premium connu",
        conditions={"driver_type": "premium", "rides_completed": ">100", "history": "clean"},
        apis_to_call=["number_verify"],  # Quick check only
        apis_skipped=["sim_swap", "device_status", "location"],
        score_formula="high_trust_override",
        action="allow",
        estimated_cost=0.14  # 75% savings for trusted drivers
    ),
]


class OptimizedTrustScorer:
    """Trust scorer with sequential API calls and early stopping.
    
    Mentor feedback: "optimiser leur exécution aurait du sens sur les revenus de Saferide"
    Mentor insight: Start with Number Verification — if it fails, no need for SIM Swap.
    """
    
    def __init__(self, weights: TrustScoreWeights | None = None):
        self.weights = weights or TrustScoreWeights()
        self.decision_path: list[str] = []
        
    def evaluate_optimized(
        self,
        driver_id: str,
        sim_swap_call: Callable[[], APICallResult],
        device_status_call: Callable[[], APICallResult],
        location_call: Callable[[], APICallResult],
        number_verify_call: Callable[[], APICallResult],
        driver_premium: bool = False,
        driver_rides_completed: int = 0
    ) -> OptimizedTrustEvaluation:
        """Evaluate driver with optimized API sequencing.
        
        Order: Number Verify → SIM Swap → Device → Location
        Early stop if fraud detected (saves API costs).
        """
        apis_called = []
        apis_skipped = []
        decision_path = []
        start_time = __import__('time').time()
        
        # Step 1: Number Verification (ALWAYS FIRST — mentor insight)
        num_result = number_verify_call()
        apis_called.append("number_verify")
        decision_path.append(f"Step 1: Number Verify score={num_result.score}")
        
        # Early stop: Number verification failed → identity compromised
        if num_result.score < 30 or "number_mismatch" in num_result.flags:
            return OptimizedTrustEvaluation(
                driver_id=driver_id,
                final_score=0.0,
                status=TrustStatus.blocked,
                apis_called=apis_called,
                apis_skipped=["sim_swap", "device_status", "location"],
                skipped_reason="Early stop: Number verification failed — identity compromised, no need for SIM Swap/Device/Location",
                cost_vs_full_check=0.17,  # 0.03/0.18 ≈ 17% — 83% savings
                execution_time_ms=int((__import__('time').time() - start_time) * 1000),
                decision_path=decision_path + ["BLOCKED: Number verification failed — 83% API cost saved"]
            )
        
        # Step 2: SIM Swap (35% weight)
        sim_result = sim_swap_call()
        apis_called.append("sim_swap")
        decision_path.append(f"Step 2: SimSwap score={sim_result.score}")
        
        # Early stop: SIM swap fraud
        if sim_result.score < 30 or "recent_swap" in sim_result.flags:
            return OptimizedTrustEvaluation(
                driver_id=driver_id,
                final_score=0.0,
                status=TrustStatus.blocked,
                apis_called=apis_called,
                apis_skipped=["device_status", "location"],
                skipped_reason="Early stop: SIM swap detected — no need for Device/Location checks",
                cost_vs_full_check=0.44,  # (0.03+0.05)/0.18 ≈ 44% — 56% savings
                execution_time_ms=int((__import__('time').time() - start_time) * 1000),
                decision_path=decision_path + ["BLOCKED: SIM swap fraud — 56% API cost saved"]
            )
        
        # Step 3: Device Status (20% weight)
        device_result = device_status_call()
        apis_called.append("device_status")
        decision_path.append(f"Step 3: Device score={device_result.score}")
        
        # Step 4: Location (25% weight)
        location_result = location_call()
        apis_called.append("location")
        decision_path.append(f"Step 4: Location score={location_result.score}")
        
        # Check for location mismatch
        if location_result.score < 50:
            decision_path.append("WARNING: Location mismatch detected")
        
        # Calculate weighted score
        final_score = (
            sim_result.score * self.weights.sim_swap_weight +
            device_result.score * self.weights.device_weight +
            location_result.score * self.weights.location_weight +
            num_result.score * self.weights.number_weight
        )
        
        # Determine status
        if final_score >= 70:
            status = TrustStatus.reliable
        elif final_score >= 40:
            status = TrustStatus.attention
        else:
            status = TrustStatus.blocked
        
        cost_ratio = len(apis_called) / 4.0  # vs full 4-API check
        
        return OptimizedTrustEvaluation(
            driver_id=driver_id,
            final_score=round(final_score, 1),
            status=status,
            apis_called=apis_called,
            apis_skipped=apis_skipped,
            skipped_reason="Full check required — all APIs called" if not apis_skipped else "Early stopping optimization",
            cost_vs_full_check=round(cost_ratio, 2),
            execution_time_ms=int((__import__('time').time() - start_time) * 1000),
            decision_path=decision_path
        )


def get_decision_matrix() -> list[DecisionMatrixCase]:
    """Return the decision matrix for documentation/metrics."""
    return DECISION_MATRIX


def calculate_potential_savings(
    total_evaluations: int,
    fraud_rate: float = 0.15,  # 15% fraud
    premium_rate: float = 0.20  # 20% premium drivers
) -> dict:
    """Calculate API cost savings based on mentor's optimization.
    
    Example:
    - 1000 evaluations
    - 15% fraud = 150 cases stopped after 1 API (save 3 calls each)
    - 20% premium = 200 cases using 1 API instead of 4
    
    Savings: (150*3 + 200*3) / 4000 = 26.25% savings
    """
    fraud_cases = int(total_evaluations * fraud_rate)
    premium_cases = int(total_evaluations * premium_rate)
    normal_cases = total_evaluations - fraud_cases - premium_cases
    
    full_cost = total_evaluations * 4  # 4 APIs each
    
    # Fraud cases: 1 API called (Number Verify fails)
    # Premium cases: 1 API called (fast track)
    # Normal cases: 4 APIs called
    actual_cost = (fraud_cases * 1) + (premium_cases * 1) + (normal_cases * 4)
    
    savings = full_cost - actual_cost
    savings_percent = (savings / full_cost) * 100
    
    return {
        "total_evaluations": total_evaluations,
        "fraud_cases": fraud_cases,
        "premium_fast_track": premium_cases,
        "normal_cases": normal_cases,
        "apis_without_optimization": full_cost,
        "apis_with_optimization": actual_cost,
        "savings_absolute": savings,
        "savings_percent": round(savings_percent, 1),
        "estimated_cost_eur": round(actual_cost * 0.05, 2)  # 0.05€ per API call
    }


def get_cost_combinations_with_margin() -> list[dict]:
    """Calculate cost per combination with SafeRide margin.

    Shows how much each API combination costs, what SafeRide charges,
    and the resulting margin. This is key for the business model.
    """
    full_cost_eur = sum(API_COST_EUR.values())  # 0.18 EUR

    combinations = [
        {
            "case": "Number Verify only (fraud detected early)",
            "apis_called": ["number_verify"],
            "api_cost_eur": API_COST_EUR["number_verify"],
            "saferide_charge_eur": SAFERIDE_CHARGE_PER_EVALUATION_EUR,
            "margin_eur": round(SAFERIDE_CHARGE_PER_EVALUATION_EUR - API_COST_EUR["number_verify"], 3),
            "margin_percent": round(
                (SAFERIDE_CHARGE_PER_EVALUATION_EUR - API_COST_EUR["number_verify"])
                / SAFERIDE_CHARGE_PER_EVALUATION_EUR * 100, 1
            ),
            "savings_vs_full_check": round((1 - API_COST_EUR["number_verify"] / full_cost_eur) * 100, 1),
        },
        {
            "case": "Number Verify + SIM Swap (SIM fraud after number OK)",
            "apis_called": ["number_verify", "sim_swap"],
            "api_cost_eur": API_COST_EUR["number_verify"] + API_COST_EUR["sim_swap"],
            "saferide_charge_eur": SAFERIDE_CHARGE_PER_EVALUATION_EUR,
            "margin_eur": round(
                SAFERIDE_CHARGE_PER_EVALUATION_EUR
                - API_COST_EUR["number_verify"] - API_COST_EUR["sim_swap"], 3
            ),
            "margin_percent": round(
                (SAFERIDE_CHARGE_PER_EVALUATION_EUR
                 - API_COST_EUR["number_verify"] - API_COST_EUR["sim_swap"])
                / SAFERIDE_CHARGE_PER_EVALUATION_EUR * 100, 1
            ),
            "savings_vs_full_check": round(
                (1 - (API_COST_EUR["number_verify"] + API_COST_EUR["sim_swap"]) / full_cost_eur) * 100, 1
            ),
        },
        {
            "case": "Number Verify + SIM Swap + Device (3 APIs, device suspicious)",
            "apis_called": ["number_verify", "sim_swap", "device_status"],
            "api_cost_eur": API_COST_EUR["number_verify"] + API_COST_EUR["sim_swap"] + API_COST_EUR["device_status"],
            "saferide_charge_eur": SAFERIDE_CHARGE_PER_EVALUATION_EUR,
            "margin_eur": round(
                SAFERIDE_CHARGE_PER_EVALUATION_EUR
                - API_COST_EUR["number_verify"] - API_COST_EUR["sim_swap"] - API_COST_EUR["device_status"], 3
            ),
            "margin_percent": round(
                (SAFERIDE_CHARGE_PER_EVALUATION_EUR
                 - API_COST_EUR["number_verify"] - API_COST_EUR["sim_swap"] - API_COST_EUR["device_status"])
                / SAFERIDE_CHARGE_PER_EVALUATION_EUR * 100, 1
            ),
            "savings_vs_full_check": round(
                (1 - (API_COST_EUR["number_verify"] + API_COST_EUR["sim_swap"] + API_COST_EUR["device_status"]) / full_cost_eur) * 100, 1
            ),
        },
        {
            "case": "Full check (all 4 APIs — normal case)",
            "apis_called": ["number_verify", "sim_swap", "device_status", "location"],
            "api_cost_eur": full_cost_eur,
            "saferide_charge_eur": SAFERIDE_CHARGE_PER_EVALUATION_EUR,
            "margin_eur": round(SAFERIDE_CHARGE_PER_EVALUATION_EUR - full_cost_eur, 3),
            "margin_percent": round(
                (SAFERIDE_CHARGE_PER_EVALUATION_EUR - full_cost_eur)
                / SAFERIDE_CHARGE_PER_EVALUATION_EUR * 100, 1
            ),
            "savings_vs_full_check": 0.0,
        },
        {
            "case": "Premium fast track (Number Verify only)",
            "apis_called": ["number_verify"],
            "api_cost_eur": API_COST_EUR["number_verify"],
            "saferide_charge_eur": SAFERIDE_CHARGE_PER_EVALUATION_EUR * 0.6,  # 40% discount for premium
            "margin_eur": round(SAFERIDE_CHARGE_PER_EVALUATION_EUR * 0.6 - API_COST_EUR["number_verify"], 3),
            "margin_percent": round(
                (SAFERIDE_CHARGE_PER_EVALUATION_EUR * 0.6 - API_COST_EUR["number_verify"])
                / (SAFERIDE_CHARGE_PER_EVALUATION_EUR * 0.6) * 100, 1
            ),
            "savings_vs_full_check": round((1 - API_COST_EUR["number_verify"] / full_cost_eur) * 100, 1),
        },
    ]

    return combinations
