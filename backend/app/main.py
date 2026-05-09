from uuid import uuid4

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .schemas import (
    B2BTrustScoreRequest,
    B2BTrustScoreResponse,
    B2BUsageMetrics,
    ChariowWebhookPayload,
    City,
    CityInfo,
    ConsentRecordPayload,
    CreateSubscriptionPayload,
    DecisionMatrixCase,
    DriverBucketsResponse,
    DriverConsent,
    DriverScoreAdjustment,
    DriverScoreHistory,
    DriverTrustSnapshot,
    MonitorRidePayload,
    OptimizedTrustEvaluation,
    RideEvent,
    RideRequestPayload,
    RideSession,
    RideVerificationResult,
    StartRidePayload,
    Subscription,
    SubscriptionPlan,
    TrustStatus,
)
from .services.agent import TrustAgent
from .services.camara import CamaraMockService
from .services.scoring import TrustScoringService
from .store import CITIES, DRIVERS, RIDES
from . import subscriptions as subs
from .admin import router as admin_router

app = FastAPI(title=settings.app_name, version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.allowed_origins),
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

camara = CamaraMockService()
agent = TrustAgent(camara)
scoring = TrustScoringService(agent)


def _evaluate_for(payload: RideRequestPayload) -> DriverBucketsResponse:
    snapshots = [
        scoring.evaluate(driver, payload.pickup, payload.destination)
        for driver in DRIVERS.values()
        if driver.city == payload.city
    ]
    return DriverBucketsResponse(
        pickup=payload.pickup,
        destination=payload.destination,
        city=payload.city,
        reliable=[s for s in snapshots if s.status == TrustStatus.reliable],
        attention=[s for s in snapshots if s.status == TrustStatus.attention],
        blocked=[s for s in snapshots if s.status == TrustStatus.blocked],
    )


@app.get("/")
def root() -> dict[str, object]:
    """Friendly landing payload so the user does not see a bare `Not Found`.

    Lists the main groups of endpoints. Interactive docs live at `/docs`.
    """
    return {
        "service": settings.app_name,
        "version": "1.0.0",
        "status": "ok",
        "docs": "/docs",
        "endpoints": {
            "health": "/health",
            "cities": "/cities",
            "drivers": "/drivers?city=Douala",
            "request_ride": "POST /rides/request",
            "ai_status": "/ai/status",
            "nokia_nac_status": "/nac/status",
            "subscription_plans": "/subscriptions/plans",
        },
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": settings.app_name, "version": "1.0.0"}


@app.get("/cities", response_model=list[CityInfo])
def list_cities() -> list[CityInfo]:
    return list(CITIES.values())


@app.get("/drivers", response_model=list[DriverTrustSnapshot])
def list_drivers(city: City = City.douala) -> list[DriverTrustSnapshot]:
    info = CITIES[city]
    payload = RideRequestPayload(passenger_name="anonymous", city=city, pickup=info.center, destination=info.center)
    snaps = [scoring.evaluate(d, payload.pickup, payload.destination) for d in DRIVERS.values() if d.city == city]
    return snaps


@app.post("/drivers/{driver_id}/explain", response_model=DriverTrustSnapshot)
def explain_driver(driver_id: str, city: City = City.douala) -> DriverTrustSnapshot:
    """Run a full evaluation **with the OpenRouter LLM** for one driver.

    Returns the snapshot enriched with ``llm_insight`` (bilingual passenger
    message + recommendation). Falls back to a deterministic template if
    ``SAFERIDE_OPENROUTER_API_KEY`` is not set.
    """
    driver = DRIVERS.get(driver_id)
    if not driver or driver.city != city:
        raise HTTPException(status_code=404, detail="Driver not found in this city")
    info = CITIES[city]
    return scoring.evaluate(driver, info.center, info.center, with_llm=True)


@app.get("/nac/status")
def nac_status() -> dict[str, object]:
    """Nokia Network-as-Code integration status: mode + per-API subscription health."""
    from .services.nokia_nac import is_enabled, probe_subscriptions
    enabled = is_enabled()
    out: dict[str, object] = {
        "mode": settings.use_real_nokia_nac,
        "enabled": enabled,
        "host": settings.nokia_nac_host,
        "key_configured": bool(settings.nokia_nac_api_key),
    }
    if enabled:
        out["subscriptions"] = probe_subscriptions()
    return out


@app.get("/ai/status")
def ai_status() -> dict[str, object]:
    """Tells whether the OpenRouter LLM agent is configured and which model is selected."""
    from .services.llm import agent as _llm
    return {
        "configured": _llm.configured,
        "model": _llm.model,
        "base_url": _llm.base_url,
    }


@app.post("/rides/request", response_model=DriverBucketsResponse)
def request_ride(payload: RideRequestPayload) -> DriverBucketsResponse:
    return _evaluate_for(payload)


@app.post("/rides/start", response_model=RideSession)
def start_ride(payload: StartRidePayload) -> RideSession:
    driver = DRIVERS.get(payload.selected_driver_id)
    if not driver or driver.city != payload.city:
        raise HTTPException(status_code=404, detail="Driver not found in this city")

    snapshot = scoring.evaluate(driver, payload.pickup, payload.destination)
    if snapshot.status == TrustStatus.blocked:
        raise HTTPException(status_code=400, detail="Driver blocked by Trust Engine")

    commission = round(snapshot.fare_xaf * settings.commission_rate, 0)
    ride = RideSession(
        id=f"ride-{uuid4().hex[:8]}",
        passenger_name=payload.passenger_name,
        city=payload.city,
        pickup=payload.pickup,
        destination=payload.destination,
        selected_driver_id=driver.id,
        trust_snapshot=snapshot,
        fare_xaf=snapshot.fare_xaf,
        commission_xaf=commission,
        events=[
            RideEvent(
                cycle=0,
                timestamp_iso=agent.now_iso(),
                severity="info",
                code="ride_started",
                message_en=f"Ride started with {driver.name} (trust score {snapshot.trust_score}).",
                message_fr=f"Course démarrée avec {driver.name} (score de confiance {snapshot.trust_score}).",
            )
        ],
    )
    RIDES[ride.id] = ride
    return ride


@app.get("/rides/{ride_id}", response_model=RideSession)
def get_ride(ride_id: str) -> RideSession:
    ride = RIDES.get(ride_id)
    if not ride:
        raise HTTPException(status_code=404, detail="Ride not found")
    return ride


@app.post("/rides/{ride_id}/monitor", response_model=RideSession)
def monitor_ride(ride_id: str, payload: MonitorRidePayload) -> RideSession:
    ride: RideSession = RIDES.get(ride_id)  # type: ignore
    if not ride:
        raise HTTPException(status_code=404, detail="Ride not found")

    ride.monitoring_cycle += 1
    cycle = ride.monitoring_cycle
    new_events: list[RideEvent] = []

    if payload.simulate_route_deviation:
        new_events.append(RideEvent(cycle=cycle, timestamp_iso=agent.now_iso(), severity="critical", code="geofence_breach",
                                     message_en="Geofencing alert: driver left expected route perimeter.",
                                     message_fr="Alerte geofencing : le chauffeur quitte le périmètre prévu."))
    if payload.simulate_network_drop:
        new_events.append(RideEvent(cycle=cycle, timestamp_iso=agent.now_iso(), severity="warning", code="qod_drop",
                                     message_en="QoD alert: critical connectivity drop detected.",
                                     message_fr="Alerte QoD : chute critique de connectivité détectée."))
    if payload.simulate_location_mismatch:
        new_events.append(RideEvent(cycle=cycle, timestamp_iso=agent.now_iso(), severity="critical", code="location_mismatch",
                                     message_en="Location mismatch between GPS and mobile network.",
                                     message_fr="Incohérence entre position GPS et réseau mobile."))
    if payload.simulate_congestion_spike:
        new_events.append(RideEvent(cycle=cycle, timestamp_iso=agent.now_iso(), severity="warning", code="congestion_spike",
                                     message_en="Congestion Insights: rerouting recommended.",
                                     message_fr="Congestion Insights : ré-itinéraire recommandé."))

    if not new_events:
        new_events.append(RideEvent(cycle=cycle, timestamp_iso=agent.now_iso(), severity="info", code="heartbeat",
                                     message_en=f"Cycle {cycle}: all CAMARA signals nominal.",
                                     message_fr=f"Cycle {cycle} : tous les signaux CAMARA sont nominaux."))

    ride.events.extend(new_events)
    RIDES[ride_id] = ride
    return ride


@app.post("/rides/{ride_id}/complete", response_model=RideSession)
def complete_ride(ride_id: str) -> RideSession:
    """Complete a ride and automatically run post-ride verification.

    The AI verifies that the ride went well:
    - Did the driver reach the destination?
    - Was the route followed?
    - Was the duration normal?
    If anomalies detected, alerts are sent to fleet or trusted contact.
    """
    ride: RideSession = RIDES.get(ride_id)  # type: ignore
    if not ride:
        raise HTTPException(status_code=404, detail="Ride not found")

    # Run post-ride verification
    from .services.post_ride_verification import verify_ride, apply_score_adjustment
    driver = DRIVERS.get(ride.selected_driver_id)
    if driver:
        verification = verify_ride(ride, driver)

        # Add verification events to ride log
        if verification.verified:
            ride.events.append(RideEvent(
                cycle=ride.monitoring_cycle, timestamp_iso=agent.now_iso(),
                severity="info", code="ride_verified",
                message_en=f"Ride verified by AI. No anomalies. Driver score +{verification.score_impact:.0f}.",
                message_fr=f"Course vérifiée par l'IA. Aucune anomalie. Score chauffeur +{verification.score_impact:.0f}.",
            ))
        else:
            for anomaly in verification.anomalies:
                ride.events.append(RideEvent(
                    cycle=ride.monitoring_cycle, timestamp_iso=agent.now_iso(),
                    severity=anomaly.severity, code=f"anomaly:{anomaly.anomaly_type.value}",
                    message_en=anomaly.description_en,
                    message_fr=anomaly.description_fr,
                ))
            if verification.alerts_sent:
                targets = ", ".join(a.value for a in verification.alerts_sent[0].alert_targets)
                ride.events.append(RideEvent(
                    cycle=ride.monitoring_cycle, timestamp_iso=agent.now_iso(),
                    severity="critical", code="alert_sent",
                    message_en=f"Alert sent to: {targets}. Driver score impact: {verification.score_impact:.0f}.",
                    message_fr=f"Alerte envoyée à : {targets}. Impact score chauffeur : {verification.score_impact:.0f}.",
                ))

        # Apply dynamic score adjustment (score is NOT fixed)
        apply_score_adjustment(driver.id, verification)

    ride.status = "completed"
    ride.events.append(RideEvent(cycle=ride.monitoring_cycle, timestamp_iso=agent.now_iso(), severity="info", code="ride_completed",
                                  message_en="Ride completed successfully.",
                                  message_fr="Course terminée avec succès."))
    RIDES[ride_id] = ride
    return ride


# ---------------------------------------------------------------------------
# Subscriptions (Chariow)
# ---------------------------------------------------------------------------


@app.get("/subscriptions/plans", response_model=list[SubscriptionPlan])
def list_plans() -> list[SubscriptionPlan]:
    return subs.list_plans()


@app.post("/subscriptions", response_model=Subscription, status_code=201)
def create_subscription(payload: CreateSubscriptionPayload) -> Subscription:
    try:
        return subs.create_subscription(payload)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@app.get("/subscriptions/{sub_id}", response_model=Subscription)
def get_subscription(sub_id: str) -> Subscription:
    sub = subs.get_subscription(sub_id)
    if not sub:
        raise HTTPException(404, "Subscription not found")
    return sub


@app.post("/subscriptions/{sub_id}/simulate-payment", response_model=Subscription)
def simulate_payment(sub_id: str) -> Subscription:
    """Prototype-only: bypass Chariow and mark a subscription as `active`.

    Use this during the hackathon demo to showcase the unlock flow without
    a real Chariow merchant account. Remove or guard in production.
    """
    sub = subs.simulate_payment(sub_id)
    if not sub:
        raise HTTPException(404, "Subscription not found")
    return sub


@app.post("/subscriptions/webhook/chariow", response_model=Subscription | None)
def chariow_webhook(payload: ChariowWebhookPayload) -> Subscription | None:
    """Public webhook receiver for Chariow. Configure this URL in your
    Chariow product webhook settings.
    """
    return subs.handle_chariow_webhook(payload)


@app.post("/rides/{ride_id}/verify", response_model=RideVerificationResult)
def verify_ride_endpoint(ride_id: str) -> RideVerificationResult:
    """Run post-ride AI verification independently.

    Checks: destination reached, route deviation, duration,
    suspicious stops, connectivity, passenger location.
    Returns anomalies, alerts, and score impact.
    """
    from .services.post_ride_verification import verify_ride, apply_score_adjustment

    ride = RIDES.get(ride_id)
    if not ride:
        raise HTTPException(404, "Ride not found")

    driver = DRIVERS.get(ride.selected_driver_id)
    if not driver:
        raise HTTPException(404, "Driver not found")

    verification = verify_ride(ride, driver)
    apply_score_adjustment(driver.id, verification)
    return verification


@app.get("/drivers/{driver_id}/score-history", response_model=DriverScoreHistory)
def get_driver_score_history(driver_id: str) -> DriverScoreHistory:
    """Get the dynamic score history for a driver.

    The SafeRide score is NOT fixed — it evolves based on post-ride
    verification results. Clean rides give bonuses, anomalous rides
    give penalties.
    """
    from .services.post_ride_verification import get_driver_score_history as _get_history

    history = _get_history(driver_id)
    if not history:
        return DriverScoreHistory(driver_id=driver_id, current_base_score=75.0)
    return history


# Mount admin router (protected by Bearer token)
app.include_router(admin_router)


# ---------------------------------------------------------------------------
# Consent API - GDPR/CAMARA Compliance (Mentor feedback)
# ---------------------------------------------------------------------------


@app.post("/drivers/{driver_id}/consent", response_model=DriverConsent, status_code=201)
def record_driver_consent(
    driver_id: str,
    payload: ConsentRecordPayload,
    ip_address: str | None = None,
    user_agent: str | None = None
) -> DriverConsent:
    """Record GDPR-compliant consent for CAMARA API access.

    This is called during driver onboarding (first app launch).
    The consent covers all four APIs for 12 months by default.
    Once granted, subsequent rides use CIBA flow (no interaction needed).
    """
    from .services.consent import create_consent
    from .store import DRIVERS

    driver = DRIVERS.get(driver_id)
    if not driver:
        raise HTTPException(404, "Driver not found")

    return create_consent(
        driver_id=driver_id,
        phone_number=driver.phone_number,
        payload=payload,
        ip_address=ip_address,
        user_agent=user_agent
    )


@app.get("/drivers/{driver_id}/consent/status")
def get_driver_consent_status(driver_id: str) -> dict:
    """Check if driver has valid consent for API calls."""
    from .services.consent import get_consent_summary
    return get_consent_summary(driver_id)


@app.post("/drivers/{driver_id}/consent/refresh", response_model=DriverConsent)
def refresh_driver_consent(
    driver_id: str,
    extension_months: int = 12
) -> DriverConsent:
    """Extend consent validity (driver re-confirms)."""
    from .services.consent import get_driver_consent, refresh_consent

    consent = get_driver_consent(driver_id)
    if not consent:
        raise HTTPException(404, "No active consent found - create new consent first")

    refreshed = refresh_consent(consent.id, extension_months)
    if not refreshed:
        raise HTTPException(400, "Failed to refresh consent")
    return refreshed


# ---------------------------------------------------------------------------
# B2B Trust Score API - SaaS Model (Mentor feedback)
# ---------------------------------------------------------------------------


@app.post("/b2b/v1/trust-score", response_model=B2BTrustScoreResponse)
def b2b_trust_score(
    payload: B2BTrustScoreRequest,
    api_key: str = Header(..., description="B2B partner API key")
) -> B2BTrustScoreResponse:
    """B2B endpoint for partners (delivery, logistics, health apps).

    Example clients: HelloFood, Jumia, mobile pharmacies.
    Pricing: 0.10€ per API call (optimized with early stopping).
    """
    from .services.b2b import (
        calculate_trust_score_b2b,
        log_usage,
        verify_api_key
    )

    client = verify_api_key(api_key)
    if not client:
        raise HTTPException(401, "Invalid or expired API key")

    response = calculate_trust_score_b2b(payload, client)
    log_usage(client.id, payload, response)
    return response


@app.post("/b2b/admin/register")
def register_b2b_client(
    name: str,
    webhook_url: str | None = None,
    admin_token: str = Header(...)
) -> dict:
    """Register a new B2B partner (admin only).
    Returns API key that the partner will use for all calls."""
    if admin_token != settings.admin_token:
        raise HTTPException(401, "Invalid admin token")

    from .services.b2b import register_b2b_client as register
    client = register(name, webhook_url)
    return {
        "client_id": client.id,
        "name": client.name,
        "api_key": client.api_key,
        "pricing_tier": client.pricing_tier,
        "rate_limit": client.rate_limit_per_minute
    }


@app.get("/b2b/admin/usage/{client_id}", response_model=B2BUsageMetrics)
def get_b2b_usage(
    client_id: str,
    month: str,  # Format: YYYY-MM
    admin_token: str = Header(...)
) -> B2BUsageMetrics:
    """Get usage metrics for billing a B2B client."""
    if admin_token != settings.admin_token:
        raise HTTPException(401, "Invalid admin token")

    from .services.b2b import get_usage_metrics
    return get_usage_metrics(client_id, month)


@app.get("/b2b/pricing")
def get_b2b_pricing() -> list[dict]:
    """Public pricing tiers for B2B partners."""
    from .services.b2b import get_b2b_pricing_tiers
    return get_b2b_pricing_tiers()


# ---------------------------------------------------------------------------
# Decision Matrix - API Cost Optimization (Mentor feedback)
# ---------------------------------------------------------------------------


@app.get("/trust-matrix/cases", response_model=list[DecisionMatrixCase])
def get_decision_matrix() -> list[DecisionMatrixCase]:
    """Return the decision matrix for API call optimization.

    Shows how SafeRide optimizes API costs:
    - Early stopping on SIM swap fraud (75% cost reduction)
    - Fast track for premium drivers (75% cost reduction)
    - Location mismatch handling (25% cost reduction)
    """
    from .services.decision_matrix import get_decision_matrix
    return get_decision_matrix()


@app.get("/trust-matrix/savings-calculation")
def calculate_savings(
    total_evaluations: int = 1000,
    fraud_rate: float = 0.15,
    premium_rate: float = 0.20
) -> dict:
    """Calculate potential API cost savings with optimization.

    Example: 1000 evaluations with 15% fraud rate
    - Without optimization: 4000 API calls (4 per evaluation)
    - With optimization: ~2800 API calls (30% savings)
    """
    from .services.decision_matrix import calculate_potential_savings
    return calculate_potential_savings(total_evaluations, fraud_rate, premium_rate)


@app.get("/trust-matrix/cost-combinations")
def get_cost_combinations() -> list[dict]:
    """API cost combinations with SafeRide margin.

    Shows how much each API combination costs, what SafeRide charges,
    and the resulting margin. Key for the business model.

    Mentor insight: Number Verify first saves 83% on fraud cases.
    """
    from .services.decision_matrix import get_cost_combinations_with_margin
    return get_cost_combinations_with_margin()


@app.post("/drivers/{driver_id}/evaluate-optimized", response_model=OptimizedTrustEvaluation)
def evaluate_driver_optimized(
    driver_id: str,
    city: City = City.douala,
    force_full_check: bool = False
) -> OptimizedTrustEvaluation:
    """Evaluate driver with optimized API sequencing.

    Demonstrates the mentor's insight on cost optimization:
    - Sequential API calls with early stopping
    - If SIM swap detected: stop immediately (only 1 API call)
    - If all clean: full 4 API check

    Cost reduction: 25-75% depending on fraud patterns.
    """
    from .services.decision_matrix import APICallResult, OptimizedTrustScorer
    from .store import CITIES, DRIVERS

    driver = DRIVERS.get(driver_id)
    if not driver or driver.city != city:
        raise HTTPException(404, "Driver not found in this city")

    city_center = CITIES[city].center

    # Mock API call functions (replace with real Nokia NaC calls in production)
    def mock_sim_swap():
        return APICallResult(
            api_name="sim_swap",
            score=20.0 if driver.sim_swap_recent else 85.0,
            raw_value="recent_swap" if driver.sim_swap_recent else "clean",
            flags=["recent_swap"] if driver.sim_swap_recent else [],
            duration_ms=120
        )

    def mock_device():
        score = {"healthy": 90, "unknown": 60, "suspicious": 30}.get(driver.device_status, 50)
        return APICallResult(
            api_name="device_status",
            score=score,
            raw_value=driver.device_status,
            flags=["suspicious"] if driver.device_status == "suspicious" else [],
            duration_ms=80
        )

    def mock_location():
        # Check if driver location matches expected city center
        import math
        dist = math.sqrt(
            (driver.current_location.lat - city_center.lat) ** 2 +
            (driver.current_location.lng - city_center.lng) ** 2
        ) * 111  # rough km conversion
        match = dist < 5  # within 5km
        return APICallResult(
            api_name="location",
            score=85.0 if match else 40.0,
            raw_value=f"distance_{dist:.1f}km",
            flags=[] if match else ["location_mismatch"],
            duration_ms=150
        )

    def mock_number_verify():
        return APICallResult(
            api_name="number_verify",
            score=90.0 if driver.number_verified else 25.0,
            raw_value="verified" if driver.number_verified else "unverified",
            flags=[] if driver.number_verified else ["number_mismatch"],
            duration_ms=200
        )

    scorer = OptimizedTrustScorer()
    return scorer.evaluate_optimized(
        driver_id=driver_id,
        sim_swap_call=mock_sim_swap,
        device_status_call=mock_device,
        location_call=mock_location,
        number_verify_call=mock_number_verify,
        driver_premium=False,  # Could check subscription status
        driver_rides_completed=driver.rides_completed
    )
