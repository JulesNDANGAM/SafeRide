"""Admin router: driver CRUD, ride listing, subscription management, stats."""

from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException

from .auth import require_admin
from .schemas import (
    AdminDriverUpsert,
    AdminStats,
    Coordinates,
    DriverProfile,
    DriverTrustSnapshot,
    RideSession,
    Subscription,
    TrustStatus,
)
from .store import DRIVERS, RIDES, SUBSCRIPTIONS
from . import subscriptions as subs


router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(require_admin)])


def _scoring():  # late import to avoid circular dep at module load
    from .main import scoring  # type: ignore
    return scoring


def _payload_to_driver(idx: str, p: AdminDriverUpsert) -> DriverProfile:
    return DriverProfile(
        id=idx,
        name=p.name,
        phone_number=p.phone_number,
        carrier=p.carrier,
        city=p.city,
        vehicle=p.vehicle,
        plate=p.plate,
        rating=p.rating,
        rides_completed=p.rides_completed,
        avatar_color=p.avatar_color,
        current_location=Coordinates(lat=p.current_lat, lng=p.current_lng),
        network_location=Coordinates(lat=p.network_lat, lng=p.network_lng),
        device_status=p.device_status,
        number_verified=p.number_verified,
        sim_swap_recent=p.sim_swap_recent,
        quality_on_demand_ready=p.quality_on_demand_ready,
        congestion_level=p.congestion_level,
        inside_geofence=p.inside_geofence,
    )


@router.get("/login")
def login() -> dict[str, str]:
    """Lightweight verification endpoint for the admin UI to validate the token."""
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# Drivers CRUD
# ---------------------------------------------------------------------------


@router.get("/drivers", response_model=list[DriverTrustSnapshot])
def list_drivers() -> list[DriverTrustSnapshot]:
    scoring = _scoring()
    return [
        scoring.evaluate(d, d.current_location, d.current_location) for d in DRIVERS.values()
    ]


@router.post("/drivers", response_model=DriverProfile, status_code=201)
def create_driver(payload: AdminDriverUpsert) -> DriverProfile:
    new_id = f"drv-{uuid4().hex[:6]}"
    driver = _payload_to_driver(new_id, payload)
    DRIVERS[new_id] = driver
    return driver


@router.put("/drivers/{driver_id}", response_model=DriverProfile)
def update_driver(driver_id: str, payload: AdminDriverUpsert) -> DriverProfile:
    if driver_id not in DRIVERS:
        raise HTTPException(404, "Driver not found")
    driver = _payload_to_driver(driver_id, payload)
    DRIVERS[driver_id] = driver
    return driver


@router.delete("/drivers/{driver_id}", status_code=204)
def delete_driver(driver_id: str) -> None:
    if driver_id not in DRIVERS:
        raise HTTPException(404, "Driver not found")
    DRIVERS.pop(driver_id, None)


# ---------------------------------------------------------------------------
# Rides
# ---------------------------------------------------------------------------


@router.get("/rides", response_model=list[RideSession])
def list_rides() -> list[RideSession]:
    return list(RIDES.values())  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Subscriptions
# ---------------------------------------------------------------------------


@router.get("/subscriptions", response_model=list[Subscription])
def list_subscriptions() -> list[Subscription]:
    return subs.list_subscriptions()


@router.post("/subscriptions/{sub_id}/cancel", response_model=Subscription)
def cancel_subscription(sub_id: str) -> Subscription:
    sub = subs.cancel_subscription(sub_id)
    if not sub:
        raise HTTPException(404, "Subscription not found")
    return sub


# ---------------------------------------------------------------------------
# Stats
# ---------------------------------------------------------------------------


@router.get("/stats", response_model=AdminStats)
def stats() -> AdminStats:
    scoring = _scoring()
    snaps = [scoring.evaluate(d, d.current_location, d.current_location) for d in DRIVERS.values()]
    total = len(snaps)
    reliable = sum(1 for s in snaps if s.status == TrustStatus.reliable)
    attention = sum(1 for s in snaps if s.status == TrustStatus.attention)
    blocked = sum(1 for s in snaps if s.status == TrustStatus.blocked)
    avg = round(sum(s.trust_score for s in snaps) / total, 2) if total else 0.0

    rides_list: list[RideSession] = list(RIDES.values())  # type: ignore[arg-type]
    in_progress = sum(1 for r in rides_list if r.status == "in_progress")
    completed = sum(1 for r in rides_list if r.status == "completed")

    sub_list = subs.list_subscriptions()
    active_subs = [s for s in sub_list if s.status.value == "active"]
    mrr = sum(s.price_xaf for s in active_subs)

    return AdminStats(
        total_drivers=total,
        reliable=reliable,
        attention=attention,
        blocked=blocked,
        total_rides=len(rides_list),
        rides_in_progress=in_progress,
        rides_completed=completed,
        total_subscriptions=len(sub_list),
        active_subscriptions=len(active_subs),
        monthly_recurring_revenue_xaf=mrr,
        average_trust_score=avg,
    )
