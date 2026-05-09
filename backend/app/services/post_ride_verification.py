"""Post-Ride Verification Service

Mentor feedback: Verify that the ride went well after completion.
If anomaly detected, alert the fleet or trusted person.
Post-ride behavior affects the driver's SafeRide score (not fixed).

Checks performed:
- Did the driver reach the destination? (Geofencing)
- Was the route followed? (Deviation check)
- Was the duration normal? (Time ratio)
- Were there suspicious stops?
- Was connectivity maintained? (QoD)
- Is the passenger at the destination? (Location Verification)
"""

import random
from datetime import datetime
from uuid import uuid4

from ..schemas import (
    AlertTarget,
    Coordinates,
    DriverProfile,
    DriverScoreAdjustment,
    DriverScoreHistory,
    PostRideAlert,
    PostRideAnomaly,
    PostRideAnomalyType,
    RideSession,
    RideVerificationResult,
)
from .camara import _haversine_km

# In-memory score history store (PostgreSQL in production)
SCORE_HISTORY: dict[str, DriverScoreHistory] = {}


def verify_ride(ride: RideSession, driver: DriverProfile) -> RideVerificationResult:
    """Verify a completed ride using AI anomaly detection.

    Checks route, duration, destination, and connectivity.
    Returns verification result with anomalies and alerts.
    """
    anomalies: list[PostRideAnomaly] = []
    pickup = ride.pickup
    destination = ride.destination
    driver_loc = driver.current_location

    # --- Check 1: Destination reached (Geofencing) ---
    dest_distance_km = _haversine_km(driver_loc, destination)
    destination_reached = dest_distance_km <= 0.2  # 200m radius
    if not destination_reached:
        severity = "critical" if dest_distance_km > 1.0 else "warning"
        anomalies.append(PostRideAnomaly(
            anomaly_type=PostRideAnomalyType.destination_not_reached,
            severity=severity,
            description_en=f"Driver is {dest_distance_km:.1f}km from destination",
            description_fr=f"Le chauffeur est à {dest_distance_km:.1f}km de la destination",
            detail=f"distance={dest_distance_km:.2f}km, threshold=0.2km",
        ))

    # --- Check 2: Route deviation (simulated for hackathon) ---
    route_deviation = random.uniform(0, 15) if not driver.inside_geofence else random.uniform(0, 5)
    if route_deviation > 30:
        anomalies.append(PostRideAnomaly(
            anomaly_type=PostRideAnomalyType.route_deviation,
            severity="critical",
            description_en=f"Route deviation: {route_deviation:.0f}% from expected path",
            description_fr=f"Déviation d'itinéraire : {route_deviation:.0f}% du trajet prévu",
            detail=f"deviation={route_deviation:.1f}%, threshold=30%",
        ))
    elif route_deviation > 15:
        anomalies.append(PostRideAnomaly(
            anomaly_type=PostRideAnomalyType.route_deviation,
            severity="warning",
            description_en=f"Minor route deviation: {route_deviation:.0f}%",
            description_fr=f"Déviation mineure : {route_deviation:.0f}%",
            detail=f"deviation={route_deviation:.1f}%, threshold=15%",
        ))

    # --- Check 3: Duration anomaly ---
    distance_km = _haversine_km(pickup, destination)
    estimated_minutes = max(3, int(distance_km * 3))
    # Simulate actual duration (0.5x to 2.5x estimated)
    duration_ratio = random.uniform(0.7, 1.5) if destination_reached else random.uniform(1.2, 2.5)
    actual_minutes = round(estimated_minutes * duration_ratio, 1)

    if duration_ratio > 2.0:
        anomalies.append(PostRideAnomaly(
            anomaly_type=PostRideAnomalyType.duration_anomalous,
            severity="critical",
            description_en=f"Ride took {duration_ratio:.1f}x longer than estimated ({actual_minutes:.0f} vs {estimated_minutes} min)",
            description_fr=f"Course {duration_ratio:.1f}x plus longue que prévu ({actual_minutes:.0f} vs {estimated_minutes} min)",
            detail=f"ratio={duration_ratio:.2f}, actual={actual_minutes}min, estimated={estimated_minutes}min",
        ))
    elif duration_ratio < 0.3:
        anomalies.append(PostRideAnomaly(
            anomaly_type=PostRideAnomalyType.duration_anomalous,
            severity="warning",
            description_en=f"Ride completed suspiciously fast ({actual_minutes:.0f} vs {estimated_minutes} min)",
            description_fr=f"Course terminée suspectement vite ({actual_minutes:.0f} vs {estimated_minutes} min)",
            detail=f"ratio={duration_ratio:.2f}, actual={actual_minutes}min, estimated={estimated_minutes}min",
        ))

    # --- Check 4: Suspicious stops (simulated) ---
    if not destination_reached and duration_ratio > 1.5:
        anomalies.append(PostRideAnomaly(
            anomaly_type=PostRideAnomalyType.suspicious_stop,
            severity="critical",
            description_en="Suspicious stop detected during ride",
            description_fr="Arrêt suspect détecté pendant la course",
            detail="Stop duration > 4 min with no route progress",
        ))

    # --- Check 5: Connectivity (QoD) ---
    if not driver.quality_on_demand_ready:
        anomalies.append(PostRideAnomaly(
            anomaly_type=PostRideAnomalyType.connectivity_drop,
            severity="warning",
            description_en="Network connectivity was degraded during ride",
            description_fr="Connectivité réseau dégradée pendant la course",
            detail="QoD session unavailable, real-time tracking was degraded",
        ))

    # --- Check 6: Passenger location mismatch (simulated) ---
    if not destination_reached and dest_distance_km > 2.0:
        anomalies.append(PostRideAnomaly(
            anomaly_type=PostRideAnomalyType.passenger_location_mismatch,
            severity="critical",
            description_en="Passenger far from expected destination",
            description_fr="Le passager est loin de la destination attendue",
            detail=f"Passenger {dest_distance_km:.1f}km from destination",
        ))

    # --- Determine verification result ---
    verified = len(anomalies) == 0
    critical_count = sum(1 for a in anomalies if a.severity == "critical")
    warning_count = sum(1 for a in anomalies if a.severity == "warning")

    # --- Calculate score impact ---
    score_impact = 0.0
    if verified:
        score_impact = 2.0  # Bonus for clean ride
    else:
        score_impact = -(critical_count * 5.0 + warning_count * 2.0)  # Penalty

    # --- Generate alerts if anomalies detected ---
    alerts: list[PostRideAlert] = []
    if anomalies:
        alert_targets = _determine_alert_targets(driver, critical_count)
        alerts.append(PostRideAlert(
            ride_id=ride.id,
            driver_id=driver.id,
            passenger_name=ride.passenger_name,
            anomalies=anomalies,
            alert_targets=alert_targets,
            driver_gps_lat=driver.current_location.lat,
            driver_gps_lng=driver.current_location.lng,
            timestamp_iso=datetime.utcnow().isoformat(timespec="seconds") + "Z",
        ))

    # --- AI explanation ---
    ai_explanation_en = _generate_explanation_en(verified, anomalies, score_impact)
    ai_explanation_fr = _generate_explanation_fr(verified, anomalies, score_impact)

    return RideVerificationResult(
        ride_id=ride.id,
        driver_id=driver.id,
        verified=verified,
        anomalies=anomalies,
        alerts_sent=alerts,
        duration_actual_minutes=actual_minutes,
        duration_estimated_minutes=estimated_minutes,
        route_deviation_percent=round(route_deviation, 1),
        destination_reached=destination_reached,
        score_impact=score_impact,
        ai_explanation_en=ai_explanation_en,
        ai_explanation_fr=ai_explanation_fr,
    )


def _determine_alert_targets(driver: DriverProfile, critical_count: int) -> list[AlertTarget]:
    """Determine who should be alerted based on driver type and anomaly severity."""
    targets: list[AlertTarget] = []

    # If driver is in a fleet (heuristic: rides_completed > 50 suggests fleet)
    if driver.rides_completed > 50:
        targets.append(AlertTarget.fleet_manager)
    else:
        targets.append(AlertTarget.trusted_contact)

    # Critical anomalies also alert SafeRide ops
    if critical_count > 0:
        targets.append(AlertTarget.saferide_ops)

    return targets


def _generate_explanation_en(verified: bool, anomalies: list[PostRideAnomaly], score_impact: float) -> str:
    if verified:
        return f"Ride verified: no anomalies detected. Driver score +{score_impact:.0f} (clean ride bonus)."
    critical = [a for a in anomalies if a.severity == "critical"]
    warning = [a for a in anomalies if a.severity == "warning"]
    parts = [f"{len(critical)} critical, {len(warning)} warning anomalies detected."]
    if score_impact < 0:
        parts.append(f"Driver score impact: {score_impact:.0f} (penalty).")
    if critical:
        parts.append("Alerts sent to fleet manager / trusted contact + SafeRide ops.")
    return " ".join(parts)


def _generate_explanation_fr(verified: bool, anomalies: list[PostRideAnomaly], score_impact: float) -> str:
    if verified:
        return f"Course vérifiée : aucune anomalie détectée. Score chauffeur +{score_impact:.0f} (bonus course propre)."
    critical = [a for a in anomalies if a.severity == "critical"]
    warning = [a for a in anomalies if a.severity == "warning"]
    parts = [f"{len(critical)} anomalies critiques, {len(warning)} avertissements détectés."]
    if score_impact < 0:
        parts.append(f"Impact score chauffeur : {score_impact:.0f} (pénalité).")
    if critical:
        parts.append("Alertes envoyées au gérant de flotte / personne de confiance + SafeRide Ops.")
    return " ".join(parts)


# ---------------------------------------------------------------------------
# Dynamic Score Adjustment (Score is NOT fixed)
# ---------------------------------------------------------------------------


def apply_score_adjustment(driver_id: str, verification: RideVerificationResult) -> DriverScoreAdjustment:
    """Apply a score adjustment based on post-ride verification.

    The driver's SafeRide score evolves over time based on behavior.
    Clean rides give bonuses, anomalous rides give penalties.
    """
    history = SCORE_HISTORY.get(driver_id)
    if not history:
        history = DriverScoreHistory(
            driver_id=driver_id,
            current_base_score=75.0,  # Starting score
        )
        SCORE_HISTORY[driver_id] = history

    previous_score = history.current_base_score
    new_score = max(0.0, min(100.0, previous_score + verification.score_impact))
    history.current_base_score = new_score

    adjustment = DriverScoreAdjustment(
        id=f"adj-{uuid4().hex[:8]}",
        driver_id=driver_id,
        ride_id=verification.ride_id,
        adjustment=verification.score_impact,
        reason_en=verification.ai_explanation_en,
        reason_fr=verification.ai_explanation_fr,
        timestamp_iso=datetime.utcnow().isoformat(timespec="seconds") + "Z",
        previous_score=previous_score,
        new_score=new_score,
    )
    history.adjustments.append(adjustment)

    # Update ride counts
    history.total_rides_verified += 1
    if verification.verified:
        history.rides_clean += 1
    else:
        history.rides_with_anomaly += 1

    # Update trend
    if len(history.adjustments) >= 3:
        recent = [a.adjustment for a in history.adjustments[-3:]]
        if sum(recent) > 0:
            history.trust_trend = "improving"
        elif sum(recent) < -5:
            history.trust_trend = "declining"
        else:
            history.trust_trend = "stable"

    return adjustment


def get_driver_score_history(driver_id: str) -> DriverScoreHistory | None:
    """Get the complete score history for a driver."""
    return SCORE_HISTORY.get(driver_id)


def get_driver_adjusted_base_score(driver_id: str) -> float:
    """Get the driver's current adjusted base score (evolves over time)."""
    history = SCORE_HISTORY.get(driver_id)
    if not history:
        return 75.0  # Default starting score
    return history.current_base_score
