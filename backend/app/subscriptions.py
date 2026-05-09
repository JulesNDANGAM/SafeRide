"""Subscription management with Chariow checkout integration.

Chariow (https://chariow.com) is an African digital-product platform
supporting Mobile Money (Orange Money, MTN MoMo, Wave, Moov), bank cards
and crypto. SafeRide uses it to monetize the Premium driver subscription
(5,000 FCFA / month, see SafeRide_Ideation PDF section 8 - Business Model).

Integration pattern:
1. The merchant creates a product on Chariow and copies its checkout URL.
2. We expose `/subscriptions/checkout` which returns the URL embedded
   client-side in an iframe.
3. Chariow notifies us via webhook (`/subscriptions/webhook/chariow`)
   once the payment succeeds; the subscription becomes `active`.
"""

from datetime import datetime
from uuid import uuid4

from .config import settings
from .schemas import (
    ChariowWebhookPayload,
    CreateSubscriptionPayload,
    Subscription,
    SubscriptionPlan,
    SubscriptionStatus,
)
from .store import DRIVERS, SUBSCRIPTIONS


PLANS: dict[str, SubscriptionPlan] = {
    "premium-driver": SubscriptionPlan(
        code="premium-driver",
        label_en="Premium Driver",
        label_fr="Chauffeur Premium",
        price_xaf=settings.premium_subscription_xaf,
        interval="month",
        features_en=[
            "Priority access to high-score rides",
            "Boosted visibility on the passenger map",
            "Detailed monthly trust report",
            "Priority support",
        ],
        features_fr=[
            "Accès prioritaire aux courses à haut score",
            "Visibilité boostée sur la carte passager",
            "Rapport de confiance mensuel détaillé",
            "Support prioritaire",
        ],
        chariow_url=settings.chariow_checkout_url,
    ),
}


def _now() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


def list_plans() -> list[SubscriptionPlan]:
    return list(PLANS.values())


def get_plan(code: str) -> SubscriptionPlan | None:
    return PLANS.get(code)


def create_subscription(payload: CreateSubscriptionPayload) -> Subscription:
    if payload.driver_id not in DRIVERS:
        raise ValueError("Driver not found")
    plan = PLANS.get(payload.plan_code)
    if not plan:
        raise ValueError("Plan not found")

    sub = Subscription(
        id=f"sub-{uuid4().hex[:8]}",
        driver_id=payload.driver_id,
        plan_code=plan.code,
        status=SubscriptionStatus.pending,
        price_xaf=plan.price_xaf,
        chariow_checkout_url=f"{plan.chariow_url}?ref={uuid4().hex[:10]}",
        created_at=_now(),
        updated_at=_now(),
        customer_email=payload.customer_email,
        customer_phone=payload.customer_phone,
    )
    SUBSCRIPTIONS[sub.id] = sub
    return sub


def list_subscriptions() -> list[Subscription]:
    return list(SUBSCRIPTIONS.values())  # type: ignore[arg-type]


def get_subscription(sub_id: str) -> Subscription | None:
    return SUBSCRIPTIONS.get(sub_id)  # type: ignore[return-value]


def simulate_payment(sub_id: str) -> Subscription | None:
    """Prototype-only: mark a subscription as `active` without going through Chariow.

    This shortcut exists because the hackathon prototype must demonstrate the
    full lifecycle (subscribe → pay → unlock Premium) without depending on a
    real Chariow merchant account. Disable in production by setting
    SAFERIDE_DISABLE_PAYMENT_SIMULATION=true (or simply removing the route).
    """
    sub: Subscription | None = SUBSCRIPTIONS.get(sub_id)  # type: ignore[assignment]
    if not sub:
        return None
    sub.status = SubscriptionStatus.active
    sub.updated_at = _now()
    sub.last_chariow_event = "simulated:payment.succeeded"
    SUBSCRIPTIONS[sub_id] = sub
    return sub


def cancel_subscription(sub_id: str) -> Subscription | None:
    sub: Subscription | None = SUBSCRIPTIONS.get(sub_id)  # type: ignore[assignment]
    if not sub:
        return None
    sub.status = SubscriptionStatus.cancelled
    sub.updated_at = _now()
    SUBSCRIPTIONS[sub_id] = sub
    return sub


_STATUS_MAP = {
    "succeeded": SubscriptionStatus.active,
    "success": SubscriptionStatus.active,
    "completed": SubscriptionStatus.active,
    "paid": SubscriptionStatus.active,
    "active": SubscriptionStatus.active,
    "pending": SubscriptionStatus.pending,
    "failed": SubscriptionStatus.expired,
    "cancelled": SubscriptionStatus.cancelled,
    "refunded": SubscriptionStatus.cancelled,
}


def handle_chariow_webhook(payload: ChariowWebhookPayload) -> Subscription | None:
    """Update a subscription state from a Chariow event."""
    target_sub: Subscription | None = None
    # Match by subscription id passed in metadata.subscription_id, or by reference suffix.
    if payload.metadata and "subscription_id" in payload.metadata:
        target_sub = SUBSCRIPTIONS.get(payload.metadata["subscription_id"])  # type: ignore[assignment]
    if target_sub is None:
        for sub in SUBSCRIPTIONS.values():
            if payload.reference and payload.reference in sub.chariow_checkout_url:  # type: ignore[union-attr]
                target_sub = sub  # type: ignore[assignment]
                break
    if target_sub is None:
        return None

    new_status = _STATUS_MAP.get(payload.status.lower(), target_sub.status)
    target_sub.status = new_status
    target_sub.updated_at = _now()
    target_sub.last_chariow_event = f"{payload.event}:{payload.status}"
    if payload.customer_email and not target_sub.customer_email:
        target_sub.customer_email = payload.customer_email
    if payload.customer_phone and not target_sub.customer_phone:
        target_sub.customer_phone = payload.customer_phone
    SUBSCRIPTIONS[target_sub.id] = target_sub
    return target_sub
