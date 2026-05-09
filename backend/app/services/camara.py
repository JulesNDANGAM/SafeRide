"""Simulation locale du SDK Nokia Network-as-Code et des APIs CAMARA.

Chaque méthode mime un appel CAMARA distant (latence + signal) et renvoie
un score normalisé [0, 100], le détail brut, et la liste des drapeaux.

Sources officielles des APIs orchestrées (toutes standardisées CAMARA,
hébergées par la Linux Foundation et exposées par les opérateurs via
Nokia Network-as-Code) :

- CAMARA Project (Linux Foundation)
  https://camaraproject.org/
  https://github.com/camaraproject

- Nokia Network-as-Code (SDK + portail développeur)
  https://networkascode.nokia.io/
  https://www.nokia.com/programmable-networks/network-as-code/

- APIs CAMARA utilisées par SafeRide :
  * SIM Swap                    https://camaraproject.org/sim-swap/
  * Number Verification         https://github.com/camaraproject/NumberVerification
  * Device Status / Reachability https://github.com/camaraproject/DeviceStatus
  * Location Verification        https://github.com/camaraproject/DeviceLocation
  * Quality On Demand (QoD)      https://github.com/camaraproject/QualityOnDemand
  * Congestion Insights          https://github.com/camaraproject/CongestionInsights
  * Geofencing Subscriptions     https://github.com/camaraproject/Geofencing

Pour passer en production : positionner SAFERIDE_USE_REAL_NAC=true et
fournir SAFERIDE_NOKIA_NAC_API_KEY (clé Nokia NaC). Cette classe peut
alors être étendue pour appeler le SDK officiel `network-as-code` (PyPI:
`pip install network-as-code`) au lieu du mock.
"""

from math import asin, cos, radians, sin, sqrt
import random

from ..schemas import CamaraSignal, Coordinates, DriverProfile


def _haversine_km(a: Coordinates, b: Coordinates) -> float:
    r = 6371.0
    lat1, lat2 = radians(a.lat), radians(b.lat)
    dlat = lat2 - lat1
    dlng = radians(b.lng - a.lng)
    h = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlng / 2) ** 2
    return 2 * r * asin(sqrt(h))


class CamaraMockService:
    """Mock Nokia NaC orchestrator. Deterministic where it matters, with
    realistic-looking latency jitter to mimic real network calls."""

    @staticmethod
    def _latency(base: int) -> int:
        return base + random.randint(20, 80)

    def sim_swap(self, driver: DriverProfile) -> CamaraSignal:
        score = 0.0 if driver.sim_swap_recent else 100.0
        flags = ["SIM swap detected within last 72h"] if driver.sim_swap_recent else []
        return CamaraSignal(
            api="SIM Swap",
            category="Identity & Fraud",
            mandatory=True,
            score=score,
            weight=0.35,
            duration_ms=self._latency(120),
            raw_value="swap_detected" if driver.sim_swap_recent else "no_recent_swap",
            flags=flags,
        )

    def location_verification(self, driver: DriverProfile) -> CamaraSignal:
        delta_km = _haversine_km(driver.current_location, driver.network_location)
        if delta_km <= 0.2:
            score, flags = 100.0, []
        elif delta_km <= 1.0:
            score, flags = 75.0, ["Light deviation between GPS and network location"]
        elif delta_km <= 5.0:
            score, flags = 35.0, ["Significant GPS / network mismatch"]
        else:
            score, flags = 5.0, ["Critical GPS spoofing suspicion"]
        return CamaraSignal(
            api="Location Verification",
            category="Identity & Fraud",
            mandatory=True,
            score=score,
            weight=0.25,
            duration_ms=self._latency(140),
            raw_value=f"delta_km={delta_km:.2f}",
            flags=flags,
        )

    def device_status(self, driver: DriverProfile) -> CamaraSignal:
        mapping = {
            "healthy": (100.0, []),
            "unknown": (55.0, ["Device status unverified"]),
            "suspicious": (10.0, ["Device flagged as suspicious"]),
        }
        score, flags = mapping.get(driver.device_status, (40.0, ["Unknown device state"]))
        return CamaraSignal(
            api="Device Status",
            category="Network Intelligence",
            mandatory=True,
            score=score,
            weight=0.20,
            duration_ms=self._latency(90),
            raw_value=driver.device_status,
            flags=flags,
        )

    def number_verification(self, driver: DriverProfile) -> CamaraSignal:
        ok = driver.number_verified
        return CamaraSignal(
            api="Number Verification",
            category="Identity & Fraud",
            mandatory=True,
            score=100.0 if ok else 25.0,
            weight=0.20,
            duration_ms=self._latency(80),
            raw_value=f"carrier={driver.carrier}, verified={ok}",
            flags=[] if ok else ["Phone number not bound to declared carrier"],
        )

    def quality_on_demand(self, driver: DriverProfile) -> CamaraSignal:
        ok = driver.quality_on_demand_ready
        return CamaraSignal(
            api="Quality on Demand",
            category="Connectivity",
            mandatory=False,
            score=100.0 if ok else 30.0,
            weight=0.0,
            duration_ms=self._latency(60),
            raw_value="qos_session_ready" if ok else "qos_unavailable",
            flags=[] if ok else ["QoD session unavailable, real-time tracking degraded"],
        )

    def congestion_insights(self, driver: DriverProfile) -> CamaraSignal:
        mapping = {
            "low": (100.0, []),
            "moderate": (70.0, ["Moderate network congestion"]),
            "high": (30.0, ["High network congestion - tracking risk"]),
        }
        score, flags = mapping.get(driver.congestion_level, (60.0, []))
        return CamaraSignal(
            api="Congestion Insights",
            category="Network Intelligence",
            mandatory=False,
            score=score,
            weight=0.0,
            duration_ms=self._latency(70),
            raw_value=driver.congestion_level,
            flags=flags,
        )

    def geofencing(self, driver: DriverProfile) -> CamaraSignal:
        inside = driver.inside_geofence
        return CamaraSignal(
            api="Geofencing",
            category="Network Intelligence",
            mandatory=False,
            score=100.0 if inside else 0.0,
            weight=0.0,
            duration_ms=self._latency(50),
            raw_value="inside_perimeter" if inside else "outside_perimeter",
            flags=[] if inside else ["Driver outside expected route perimeter"],
        )
