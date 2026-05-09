"""B2B Trust Score API - SaaS Model

Implements mentor feedback on B2B business model:
- SDK léger pour apps mobiles partenaires
- Backend SaaS avec facturation par appel
- Rate limiting, API keys, webhooks
"""

from datetime import datetime
from uuid import uuid4

from ..schemas import (
    B2BClient,
    B2BTrustScoreRequest,
    B2BTrustScoreResponse,
    B2BUsageMetrics,
    TrustStatus
)

# In-memory stores (PostgreSQL in production)
B2B_CLIENTS: dict[str, B2BClient] = {}
USAGE_LOG: list[dict] = []  # B2BUsageMetrics


def register_b2b_client(name: str, webhook_url: str | None = None) -> B2BClient:
    """Register a new B2B partner."""
    client = B2BClient(
        id=f"b2b-{uuid4().hex[:12]}",
        name=name,
        api_key=f"sk_b2b_{uuid4().hex[:24]}",
        webhook_url=webhook_url,
        rate_limit_per_minute=100,
        pricing_tier="standard",
        active=True
    )
    B2B_CLIENTS[client.api_key] = client
    return client


def verify_api_key(api_key: str) -> B2BClient | None:
    """Verify B2B API key and check rate limits."""
    client = B2B_CLIENTS.get(api_key)
    if not client or not client.active:
        return None
    return client


def calculate_trust_score_b2b(
    request: B2BTrustScoreRequest,
    client: B2BClient
) -> B2BTrustScoreResponse:
    """Calculate trust score for B2B client request.
    
    This is a simplified version for the hackathon MVP.
    In production, this would call the full evaluation engine.
    """
    # Mock evaluation logic (replace with real Nokia NaC calls)
    import random
    
    # Simulate API calls with early stopping (optimization)
    checks_performed = []
    checks_skipped = []
    
    # Step 1: SIM Swap (always called)
    checks_performed.append("sim_swap")
    sim_score = random.uniform(60, 95)
    
    # Early stop for fraud cases
    if sim_score < 40:
        return B2BTrustScoreResponse(
            trust_score=15.0,
            risk_level="critical",
            verification_status="failed",
            checks_performed=["sim_swap"],
            checks_skipped=["device_status", "location", "number_verify"],
            cost_optimization_saved=75.0,
            recommendation="reject",
            timestamp=datetime.utcnow().isoformat(),
            request_id=f"b2b-req-{uuid4().hex[:12]}"
        )
    
    # Continue with other checks for normal cases
    checks_performed.extend(["device_status", "location"])
    
    # Premium optimization: skip number verify if good scores
    if sim_score > 80:
        checks_skipped.append("number_verify")
        number_score = 85.0  # assumed good
    else:
        checks_performed.append("number_verify")
        number_score = random.uniform(60, 90)
    
    # Calculate final score
    trust_score = (
        sim_score * 0.35 +
        random.uniform(70, 95) * 0.20 +  # device
        random.uniform(65, 90) * 0.25 +   # location
        number_score * 0.20
    )
    
    # Determine recommendation
    if trust_score >= 75:
        risk_level = "low"
        recommendation = "approve"
        verification_status = "full"
    elif trust_score >= 50:
        risk_level = "medium"
        recommendation = "review"
        verification_status = "partial"
    else:
        risk_level = "high"
        recommendation = "reject"
        verification_status = "partial"
    
    # Calculate optimization savings
    if "number_verify" in checks_skipped:
        cost_optimization_saved = 25.0  # 1 of 4 APIs skipped
    else:
        cost_optimization_saved = 0.0
    
    return B2BTrustScoreResponse(
        trust_score=round(trust_score, 1),
        risk_level=risk_level,
        verification_status=verification_status,
        checks_performed=checks_performed,
        checks_skipped=checks_skipped,
        cost_optimization_saved=cost_optimization_saved,
        recommendation=recommendation,
        timestamp=datetime.utcnow().isoformat(),
        request_id=f"b2b-req-{uuid4().hex[:12]}"
    )


def log_usage(client_id: str, request: B2BTrustScoreRequest, 
              response: B2BTrustScoreResponse) -> None:
    """Log API usage for billing."""
    USAGE_LOG.append({
        "client_id": client_id,
        "request_context": request.request_context,
        "timestamp": datetime.utcnow().isoformat(),
        "trust_score": response.trust_score,
        "apis_called": len(response.checks_performed),
        "cost_saved_percent": response.cost_optimization_saved,
        "recommendation": response.recommendation
    })


def get_usage_metrics(client_id: str, month: str) -> B2BUsageMetrics:
    """Calculate usage metrics for billing."""
    month_logs = [log for log in USAGE_LOG 
                  if log["client_id"] == client_id and log["timestamp"].startswith(month)]
    
    total_calls = len(month_logs)
    successful_calls = len([l for l in month_logs if l["trust_score"] > 50])
    blocked = len([l for l in month_logs if l["recommendation"] == "reject"])
    
    # Pricing: 0.10€ per API call
    avg_cost = 0.10 * (sum(l["apis_called"] for l in month_logs) / max(total_calls, 1))
    total_billable = 0.10 * sum(l["apis_called"] for l in month_logs)
    
    return B2BUsageMetrics(
        client_id=client_id,
        month=month,
        total_calls=total_calls,
        successful_calls=successful_calls,
        blocked_fraud_attempts=blocked,
        avg_cost_per_call=round(avg_cost, 2),
        total_billable_amount=round(total_billable, 2)
    )


def get_b2b_pricing_tiers() -> list[dict]:
    """Return pricing tiers for B2B clients."""
    return [
        {
            "tier": "starter",
            "monthly_fee": 0,
            "per_call_rate": 0.12,
            "included_calls": 0,
            "description": "For startups testing the API"
        },
        {
            "tier": "standard",
            "monthly_fee": 99,
            "per_call_rate": 0.08,
            "included_calls": 1000,
            "description": "For delivery apps with medium volume"
        },
        {
            "tier": "enterprise",
            "monthly_fee": 499,
            "per_call_rate": 0.05,
            "included_calls": 10000,
            "description": "For large logistics platforms"
        }
    ]
