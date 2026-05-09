from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class TrustStatus(str, Enum):
    reliable = "reliable"
    attention = "attention"
    blocked = "blocked"


class City(str, Enum):
    douala = "Douala"
    yaounde = "Yaounde"
    lagos = "Lagos"
    nairobi = "Nairobi"
    dakar = "Dakar"


class Coordinates(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)


class CamaraSignal(BaseModel):
    api: str
    category: str
    mandatory: bool
    score: float
    weight: float
    duration_ms: int
    raw_value: str
    flags: list[str] = Field(default_factory=list)


class DriverProfile(BaseModel):
    id: str
    name: str
    phone_number: str
    carrier: str
    city: City
    vehicle: str
    plate: str
    rating: float
    rides_completed: int
    avatar_color: str
    current_location: Coordinates
    network_location: Coordinates
    device_status: str  # healthy | unknown | suspicious
    number_verified: bool
    sim_swap_recent: bool
    quality_on_demand_ready: bool
    congestion_level: str  # low | moderate | high
    inside_geofence: bool = True


class TrustBreakdown(BaseModel):
    sim_swap: float
    location_verification: float
    device_status: float
    number_verification: float
    final_score: float


class AIAgentStep(BaseModel):
    step: int
    action: str
    detail: str
    duration_ms: int


class LLMInsight(BaseModel):
    message_fr: str
    message_en: str
    recommendation: str  # accept | review | reject
    model: str
    used_llm: bool


class DriverTrustSnapshot(BaseModel):
    driver: DriverProfile
    status: TrustStatus
    trust_score: float
    breakdown: TrustBreakdown
    distance_km: float
    eta_minutes: int
    fare_xaf: float
    signals: list[CamaraSignal]
    anomalies: list[str] = Field(default_factory=list)
    monitoring_alerts: list[str] = Field(default_factory=list)
    qod_active: bool = True
    ai_log: list[AIAgentStep] = Field(default_factory=list)
    llm_insight: Optional[LLMInsight] = None


class DriverBucketsResponse(BaseModel):
    pickup: Coordinates
    destination: Coordinates
    city: City
    reliable: list[DriverTrustSnapshot] = Field(default_factory=list)
    attention: list[DriverTrustSnapshot] = Field(default_factory=list)
    blocked: list[DriverTrustSnapshot] = Field(default_factory=list)


class RideRequestPayload(BaseModel):
    passenger_name: str = Field(..., min_length=2, max_length=80)
    city: City = City.douala
    pickup: Coordinates
    destination: Coordinates
    radius_km: float = Field(default=3.0, gt=0, le=20)


class StartRidePayload(RideRequestPayload):
    selected_driver_id: str


class MonitorRidePayload(BaseModel):
    simulate_route_deviation: bool = False
    simulate_network_drop: bool = False
    simulate_location_mismatch: bool = False
    simulate_congestion_spike: bool = False


class RideEvent(BaseModel):
    cycle: int
    timestamp_iso: str
    severity: str  # info | warning | critical
    code: str
    message_en: str
    message_fr: str


class RideSession(BaseModel):
    id: str
    passenger_name: str
    city: City
    pickup: Coordinates
    destination: Coordinates
    selected_driver_id: str
    trust_snapshot: DriverTrustSnapshot
    fare_xaf: float
    commission_xaf: float
    status: str = "in_progress"  # in_progress | completed | cancelled
    monitoring_cycle: int = 0
    events: list[RideEvent] = Field(default_factory=list)


class Neighborhood(BaseModel):
    code: str
    label: str
    coordinates: Coordinates


class CityInfo(BaseModel):
    code: City
    label: str
    country: str
    center: Coordinates
    operator_partner: Optional[str] = None
    neighborhoods: list[Neighborhood] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Subscriptions (Premium driver - Chariow integration)
# ---------------------------------------------------------------------------


class SubscriptionStatus(str, Enum):
    pending = "pending"
    active = "active"
    cancelled = "cancelled"
    expired = "expired"


class SubscriptionPlan(BaseModel):
    code: str
    label_en: str
    label_fr: str
    price_xaf: float
    interval: str = "month"
    features_en: list[str] = Field(default_factory=list)
    features_fr: list[str] = Field(default_factory=list)
    chariow_url: str


class CreateSubscriptionPayload(BaseModel):
    driver_id: str
    plan_code: str = "premium-driver"
    customer_email: Optional[str] = None
    customer_phone: Optional[str] = None


class Subscription(BaseModel):
    id: str
    driver_id: str
    plan_code: str
    status: SubscriptionStatus
    price_xaf: float
    chariow_checkout_url: str
    created_at: str
    updated_at: str
    customer_email: Optional[str] = None
    customer_phone: Optional[str] = None
    last_chariow_event: Optional[str] = None


class ChariowWebhookPayload(BaseModel):
    """Webhook payload pushed by Chariow when a payment occurs.

    Reference: https://help.chariow.com (Webhooks section). The fields
    accepted are intentionally permissive so that any Chariow event with
    a transaction reference and status can be handled.
    """

    event: str
    reference: str
    status: str
    amount: Optional[float] = None
    customer_email: Optional[str] = None
    customer_phone: Optional[str] = None
    metadata: Optional[dict] = None


# ---------------------------------------------------------------------------
# Admin
# ---------------------------------------------------------------------------


class AdminDriverUpsert(BaseModel):
    name: str
    phone_number: str
    carrier: str
    city: City
    vehicle: str
    plate: str
    rating: float = 4.5
    rides_completed: int = 0
    avatar_color: str = "#22d3ee"
    current_lat: float
    current_lng: float
    network_lat: float
    network_lng: float
    device_status: str = "healthy"
    number_verified: bool = True
    sim_swap_recent: bool = False
    quality_on_demand_ready: bool = True
    congestion_level: str = "low"
    inside_geofence: bool = True


class AdminStats(BaseModel):
    total_drivers: int
    reliable: int
    attention: int
    blocked: int
    total_rides: int
    rides_in_progress: int
    rides_completed: int
    total_subscriptions: int
    active_subscriptions: int
    monthly_recurring_revenue_xaf: float
    average_trust_score: float


# ---------------------------------------------------------------------------
# Consent API (Mentor feedback - GDPR/CAMARA compliance)
# ---------------------------------------------------------------------------


class ConsentStatus(str, Enum):
    granted = "granted"
    denied = "denied"
    expired = "expired"
    pending = "pending"


class ConsentScope(str, Enum):
    sim_swap = "SIM_SWAP"
    location = "LOCATION"
    device_status = "DEVICE_STATUS"
    number_verify = "NUMBER_VERIFY"


class DriverConsent(BaseModel):
    """GDPR-compliant consent record for Nokia NaC CAMARA APIs.

    Mentor feedback: Consent collected at onboarding prevents
    interactive consent requests during rides.
    """
    id: str
    driver_id: str
    phone_number: str
    status: ConsentStatus
    scopes: list[ConsentScope]  # Which APIs driver consented to
    granted_at: str  # ISO timestamp
    expires_at: str  # ISO timestamp (typically +12 months)
    purpose: str = "Driver identity verification for SafeRide platform"
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class ConsentRecordPayload(BaseModel):
    scopes: list[ConsentScope]
    duration_months: int = Field(default=12, ge=1, le=24)


# ---------------------------------------------------------------------------
# B2B Trust Score API (SaaS model - Mentor feedback)
# ---------------------------------------------------------------------------


class B2BClient(BaseModel):
    """B2B partner using SafeRide Trust Score as a Service."""
    id: str
    name: str
    api_key: str
    webhook_url: Optional[str] = None
    rate_limit_per_minute: int = 100
    pricing_tier: str = "standard"  # standard, enterprise
    active: bool = True


class B2BTrustScoreRequest(BaseModel):
    """Request from B2B client (e.g., HelloFood, pharmacy delivery)."""
    phone_number: str = Field(..., description="Driver/delivery person phone number")
    request_context: str = "ride"  # ride, delivery, field_service
    location: Optional[Coordinates] = None
    client_reference: Optional[str] = None  # B2B client's internal ID


class B2BTrustScoreResponse(BaseModel):
    """Response with trust score and risk assessment."""
    trust_score: float = Field(..., ge=0, le=100)
    risk_level: str  # low, medium, high, critical
    verification_status: str  # full, partial, failed
    checks_performed: list[str]  # Which APIs were called
    checks_skipped: list[str]  # Which APIs were skipped (optimization)
    cost_optimization_saved: float  # % of API calls saved vs full check
    recommendation: str  # approve, review, reject
    timestamp: str
    request_id: str


class B2BUsageMetrics(BaseModel):
    """Metering for B2B billing."""
    client_id: str
    month: str
    total_calls: int
    successful_calls: int
    blocked_fraud_attempts: int
    avg_cost_per_call: float
    total_billable_amount: float  # in EUR/USD


# ---------------------------------------------------------------------------
# Optimized Decision Matrix (Mentor feedback - API cost optimization)
# ---------------------------------------------------------------------------


class DecisionMatrixCase(BaseModel):
    """One case in the decision matrix for API call optimization.

    Mentor insight: If Number Verify fails, why call SimSwap?
    Sequential checks with early stopping save API costs.
    """
    case_id: str
    name: str
    conditions: dict[str, str]  # e.g., {"sim_swap": "recent", "number_verify": "failed"}
    apis_to_call: list[str]  # Which APIs should be called
    apis_skipped: list[str]  # Which APIs are skipped (with reason)
    score_formula: str  # How to compute partial score
    action: str  # allow, block, review
    estimated_cost: float  # Relative cost vs full check (1.0 = 100%)


class OptimizedTrustEvaluation(BaseModel):
    """Result of optimized evaluation with cost tracking.

    Shows mentor's concern for API cost optimization:
    - Full check costs 4 API calls
    - Optimized can cost 1-2 calls for obvious fraud cases
    """
    driver_id: str
    final_score: float
    status: TrustStatus
    apis_called: list[str]
    apis_skipped: list[str]
    skipped_reason: str  # e.g., "Early stop: SIM swap detected"
    cost_vs_full_check: float  # 0.25 = 75% savings
    execution_time_ms: int
    decision_path: list[str]  # Step-by-step decision log


class TrustScoreWeights(BaseModel):
    """Dynamic weights for ML-based scoring (Mentor: TensorFlow/Scikit-learn).

    Static formula: SCR = SIM(35%) + Loc(25%) + Dev(20%) + Num(20%)
    Dynamic: These weights adjust based on historical fraud patterns.
    """
    sim_swap_weight: float = 0.35
    location_weight: float = 0.25
    device_weight: float = 0.20
    number_weight: float = 0.20
    model_version: str = "v1.0-static"
    last_trained_at: Optional[str] = None


# ---------------------------------------------------------------------------
# Post-Ride Verification (Mentor feedback — before/after ride)
# ---------------------------------------------------------------------------


class PostRideAnomalyType(str, Enum):
    route_deviation = "route_deviation"
    destination_not_reached = "destination_not_reached"
    duration_anomalous = "duration_anomalous"
    suspicious_stop = "suspicious_stop"
    connectivity_drop = "connectivity_drop"
    passenger_location_mismatch = "passenger_location_mismatch"


class PostRideAnomaly(BaseModel):
    """A single anomaly detected during post-ride verification."""
    anomaly_type: PostRideAnomalyType
    severity: str  # info | warning | critical
    description_en: str
    description_fr: str
    detail: str  # e.g., "Deviation 45% from expected route"


class AlertTarget(str, Enum):
    fleet_manager = "fleet_manager"
    trusted_contact = "trusted_contact"
    saferide_ops = "saferide_ops"


class PostRideAlert(BaseModel):
    """Alert sent when post-ride verification detects anomalies."""
    ride_id: str
    driver_id: str
    passenger_name: str
    anomalies: list[PostRideAnomaly]
    alert_targets: list[AlertTarget]
    driver_gps_lat: Optional[float] = None
    driver_gps_lng: Optional[float] = None
    timestamp_iso: str


class RideVerificationResult(BaseModel):
    """Result of post-ride AI verification."""
    ride_id: str
    driver_id: str
    verified: bool  # True if no anomalies
    anomalies: list[PostRideAnomaly] = Field(default_factory=list)
    alerts_sent: list[PostRideAlert] = Field(default_factory=list)
    duration_actual_minutes: Optional[float] = None
    duration_estimated_minutes: Optional[float] = None
    route_deviation_percent: Optional[float] = None
    destination_reached: Optional[bool] = None
    score_impact: float = 0.0  # Negative = penalty, positive = bonus
    ai_explanation_en: str = ""
    ai_explanation_fr: str = ""


# ---------------------------------------------------------------------------
# Dynamic Driver Score History (Score is NOT fixed)
# ---------------------------------------------------------------------------


class DriverScoreAdjustment(BaseModel):
    """A score adjustment event for a driver (post-ride behavior affects future score)."""
    id: str
    driver_id: str
    ride_id: Optional[str] = None
    adjustment: float  # Positive = bonus, Negative = penalty
    reason_en: str
    reason_fr: str
    timestamp_iso: str
    previous_score: float
    new_score: float


class DriverScoreHistory(BaseModel):
    """Complete score history for a driver — the score evolves over time."""
    driver_id: str
    current_base_score: float  # Current base score (0-100) adjusted by history
    adjustments: list[DriverScoreAdjustment] = Field(default_factory=list)
    total_rides_verified: int = 0
    rides_with_anomaly: int = 0
    rides_clean: int = 0
    trust_trend: str = "stable"  # improving | stable | declining

