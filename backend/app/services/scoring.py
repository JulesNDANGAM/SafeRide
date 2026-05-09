from ..config import settings
from ..schemas import (
    Coordinates,
    DriverProfile,
    DriverTrustSnapshot,
    LLMInsight,
    TrustBreakdown,
    TrustStatus,
    TrustScoreWeights,
)
from .agent import TrustAgent
from .camara import CamaraMockService, _haversine_km
from .llm import agent as llm_agent


class TrustScoringService:
    def __init__(self, agent: TrustAgent) -> None:
        self.agent = agent

    def evaluate(
        self,
        driver: DriverProfile,
        pickup: Coordinates,
        destination: Coordinates,
        with_llm: bool = False,
    ) -> DriverTrustSnapshot:
        # Get dynamic weights from driver's score history (score is NOT fixed)
        weights = self._get_dynamic_weights(driver)

        signals, log = self.agent.orchestrate(driver, weights=weights)

        weighted = {s.api: s for s in signals}

        # Check for early stop (Number Verify or SIM Swap failed)
        early_stop = any(step.action == "early_stop" for step in log)

        if early_stop:
            # Early stop: identity compromised or SIM fraud — block immediately
            num = weighted.get("Number Verification")
            sim = weighted.get("SIM Swap")
            loc = None
            dev = None

            final = 0.0
            blended = 0.0
            status = TrustStatus.blocked

            anomalies: list[str] = []
            if num and num.flags:
                anomalies.extend(num.flags)
            if sim and sim.flags:
                anomalies.extend(sim.flags)
        else:
            sim = weighted["SIM Swap"]
            loc = weighted["Location Verification"]
            dev = weighted["Device Status"]
            num = weighted["Number Verification"]

            final = round(
                sim.score * weights.sim_swap_weight +
                loc.score * weights.location_weight +
                dev.score * weights.device_weight +
                num.score * weights.number_weight, 2,
            )

            # Apply dynamic base score adjustment from post-ride history
            from .post_ride_verification import get_driver_adjusted_base_score
            base_adjustment = get_driver_adjusted_base_score(driver.id)
            # Blend: 70% from API signals, 30% from historical behavior
            blended = round(final * 0.70 + base_adjustment * 0.30, 2)

            if blended >= 70:
                status = TrustStatus.reliable
            elif blended >= 40:
                status = TrustStatus.attention
            else:
                status = TrustStatus.blocked

            anomalies = []
            for api in ("SIM Swap", "Location Verification", "Device Status", "Number Verification"):
                anomalies.extend(weighted[api].flags)

        qod = weighted.get("Quality on Demand")
        cong = weighted.get("Congestion Insights")
        geo = weighted.get("Geofencing")

        monitoring_alerts: list[str] = []
        if qod:
            monitoring_alerts.extend(qod.flags)
        if cong:
            monitoring_alerts.extend(cong.flags)
        if geo:
            monitoring_alerts.extend(geo.flags)

        distance_km = _haversine_km(driver.current_location, pickup) + _haversine_km(pickup, destination)
        eta = max(3, int(distance_km * 3))
        fare = round(settings.base_fare_xaf + distance_km * settings.fare_per_km_xaf, 0)

        # Build breakdown — use 0 for missing signals in early stop case
        snapshot = DriverTrustSnapshot(
            driver=driver,
            status=status,
            trust_score=blended,
            breakdown=TrustBreakdown(
                sim_swap=sim.score if hasattr(sim, 'score') else 0.0,
                location_verification=loc.score if hasattr(loc, 'score') else 0.0,
                device_status=dev.score if hasattr(dev, 'score') else 0.0,
                number_verification=num.score if hasattr(num, 'score') else 0.0,
                final_score=blended,
            ),
            distance_km=round(distance_km, 2),
            eta_minutes=eta,
            fare_xaf=fare,
            signals=signals,
            anomalies=anomalies,
            monitoring_alerts=monitoring_alerts,
            qod_active=driver.quality_on_demand_ready,
            ai_log=log,
        )

        if with_llm:
            insight = llm_agent.explain({
                "driver_name": driver.name,
                "city": driver.city.value,
                "carrier": driver.carrier,
                "trust_score": blended,
                "status": status.value,
                "anomalies": anomalies,
                "monitoring_alerts": monitoring_alerts,
                "breakdown": {
                    "sim_swap": sim,
                    "location": loc,
                    "device": dev,
                    "number": num,
                },
            })
            snapshot.llm_insight = LLMInsight(
                message_fr=insight.message_fr,
                message_en=insight.message_en,
                recommendation=insight.recommendation,
                model=insight.model,
                used_llm=insight.used_llm,
            )
            snapshot.ai_log.append(
                snapshot.ai_log[-1].__class__(
                    step=len(snapshot.ai_log) + 1,
                    action="llm:explain",
                    detail=f"model={insight.model} used={insight.used_llm}",
                    duration_ms=0,
                )
            )

        return snapshot

    def _get_dynamic_weights(self, driver: DriverProfile) -> TrustScoreWeights:
        """Get dynamic weights based on driver's city and history.

        The weights are NOT fixed — they adapt based on:
        - City-specific fraud patterns (regional heuristics)
        - Driver's historical behavior (post-ride verification)
        """
        from .post_ride_verification import get_driver_score_history

        # Base weights
        w = TrustScoreWeights()

        # City-specific adjustments
        from ..schemas import City
        if driver.city == City.lagos:
            # Lagos: GPS fraud more common → increase location weight
            w.location_weight = 0.30
            w.sim_swap_weight = 0.30
            w.device_weight = 0.25
            w.number_weight = 0.15
        elif driver.city == City.douala:
            # Douala: SIM swap dominant → increase SIM weight
            w.sim_swap_weight = 0.40
            w.location_weight = 0.25
            w.device_weight = 0.15
            w.number_weight = 0.20
        elif driver.city == City.dakar:
            # Dakar: Number verification fragile → increase number weight
            w.number_weight = 0.25
            w.sim_swap_weight = 0.35
            w.location_weight = 0.20
            w.device_weight = 0.20

        # History-based adjustments
        history = get_driver_score_history(driver.id)
        if history and history.total_rides_verified >= 3:
            # If driver has declining trend, increase scrutiny
            if history.trust_trend == "declining":
                w.sim_swap_weight += 0.05
                w.location_weight += 0.05
                w.device_weight -= 0.05
                w.number_weight -= 0.05
            # If driver has improving trend, can relax slightly
            elif history.trust_trend == "improving":
                w.sim_swap_weight -= 0.05
                w.number_weight += 0.05

            # Normalize weights to sum to 1.0
            total = w.sim_swap_weight + w.location_weight + w.device_weight + w.number_weight
            if total != 1.0:
                w.sim_swap_weight /= total
                w.location_weight /= total
                w.device_weight /= total
                w.number_weight /= total

            w.model_version = "v2.0-dynamic"
            w.last_trained_at = history.adjustments[-1].timestamp_iso if history.adjustments else None

        return w
