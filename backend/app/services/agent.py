"""SafeRide Agentic AI orchestrator (lightweight LLM stub).

Decides the order of CAMARA API calls based on context, applies
regional fraud heuristics, and produces an explainability log.

Mentor insight: Start with Number Verification — if it fails,
the phone doesn't belong to the declared carrier, so SIM Swap
and other checks are pointless. Early stopping saves API costs.
"""

from datetime import datetime
from typing import Callable

from ..schemas import AIAgentStep, CamaraSignal, City, DriverProfile, TrustScoreWeights
from .camara import CamaraMockService

DEFAULT_WEIGHTS = TrustScoreWeights()

REGIONAL_HEURISTICS: dict[City, str] = {
    City.douala: "Number Verify first, then SIM Swap (high SIM-swap pressure)",
    City.lagos: "Number Verify first, then Device Status (device fraud spikes)",
    City.nairobi: "Number Verify first (standard order)",
    City.dakar: "Number Verify first (fragile in suburbs)",
    City.yaounde: "Number Verify first (standard)",
}


class TrustAgent:
    def __init__(self, camara: CamaraMockService) -> None:
        self.camara = camara

    def orchestrate(
        self,
        driver: DriverProfile,
        weights: TrustScoreWeights | None = None,
    ) -> tuple[list[CamaraSignal], list[AIAgentStep]]:
        """Orchestrate CAMARA API calls with early stopping.

        Mentor insight: Number Verification is the cheapest and most
        decisive check. If the phone number doesn't belong to the
        declared carrier, there is no point calling SIM Swap, Device
        Status, or Location Verification — the identity is already
        compromised. This saves 75% of API costs on fraud cases.
        """
        log: list[AIAgentStep] = []
        step = 1
        w = weights or DEFAULT_WEIGHTS

        heuristic = REGIONAL_HEURISTICS.get(driver.city, "Number Verify first (standard)")
        log.append(AIAgentStep(step=step, action="context", detail=f"{driver.city.value} | {heuristic}", duration_ms=4))
        step += 1

        # --- Step 1: Number Verification (ALWAYS FIRST — mentor insight) ---
        num_sig = self.camara.number_verification(driver)
        log.append(AIAgentStep(
            step=step, action=f"call:{num_sig.api}",
            detail=f"score={num_sig.score} ({num_sig.duration_ms}ms) [FIRST - mentor insight]",
            duration_ms=num_sig.duration_ms,
        ))
        step += 1

        # Early stop: Number verification failed → identity compromised, no need for further checks
        if num_sig.score < 30:
            log.append(AIAgentStep(
                step=step, action="early_stop",
                detail=f"Number Verification FAILED (score={num_sig.score}) — identity compromised, skipping SIM Swap/Device/Location",
                duration_ms=2,
            ))
            supp_signals, supp_log = self._supplementary_signals(driver, step + 1)
            signals = [num_sig] + supp_signals
            log.extend(supp_log)
            log.append(AIAgentStep(step=len(log) + 1, action="decision",
                                   detail="BLOCKED: Number verification failed — early stop saved 75% API costs", duration_ms=2))
            return signals, log

        # --- Build remaining order based on city heuristics ---
        remaining: list[Callable[[DriverProfile], CamaraSignal]]
        if driver.city == City.lagos:
            remaining = [self.camara.device_status, self.camara.sim_swap, self.camara.location_verification]
        elif driver.city == City.douala:
            remaining = [self.camara.sim_swap, self.camara.location_verification, self.camara.device_status]
        else:
            remaining = [self.camara.sim_swap, self.camara.location_verification, self.camara.device_status]

        signals: list[CamaraSignal] = [num_sig]
        for fn in remaining:
            sig = fn(driver)
            signals.append(sig)
            log.append(AIAgentStep(step=step, action=f"call:{sig.api}", detail=f"score={sig.score} ({sig.duration_ms}ms)", duration_ms=sig.duration_ms))
            step += 1

            # Early stop: SIM swap fraud detected
            if sig.api == "SIM Swap" and (sig.score < 30 or any("SIM swap" in f for f in sig.flags)):
                log.append(AIAgentStep(
                    step=step, action="early_stop",
                    detail=f"SIM Swap fraud detected (score={sig.score}) — stopping, remaining checks skipped",
                    duration_ms=2,
                ))
                supp_signals, supp_log = self._supplementary_signals(driver, step + 1)
                signals.extend(supp_signals)
                log.extend(supp_log)
                log.append(AIAgentStep(step=len(log) + 1, action="decision",
                                       detail="BLOCKED: SIM swap fraud — early stop saved 50% API costs", duration_ms=2))
                return signals, log

        # supplementary signals (non-weighted)
        supp_signals, supp_log = self._supplementary_signals(driver, step)
        signals.extend(supp_signals)
        log.extend(supp_log)

        log.append(AIAgentStep(step=len(log) + 1, action="decision",
                               detail=f"Weighted scoring complete (weights: SIM={w.sim_swap_weight}, Loc={w.location_weight}, Dev={w.device_weight}, Num={w.number_weight})", duration_ms=2))
        return signals, log

    def _supplementary_signals(self, driver: DriverProfile, start_step: int) -> tuple[list[CamaraSignal], list[AIAgentStep]]:
        """Collect non-weighted monitoring signals (QoD, Congestion, Geofencing)."""
        signals: list[CamaraSignal] = []
        log: list[AIAgentStep] = []
        step = start_step
        for fn in (self.camara.quality_on_demand, self.camara.congestion_insights, self.camara.geofencing):
            sig = fn(driver)
            signals.append(sig)
            log.append(AIAgentStep(step=step, action=f"call:{sig.api}", detail=f"raw={sig.raw_value}", duration_ms=sig.duration_ms))
            step += 1
        return signals, log

    @staticmethod
    def now_iso() -> str:
        return datetime.utcnow().isoformat(timespec="seconds") + "Z"
