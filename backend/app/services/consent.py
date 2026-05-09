"""Consent Management Service - Nokia NaC CAMARA Compliance

Implements mentor feedback on GDPR/privacy:
- Consent collected at onboarding (Consent Info API)
- Reusable OAuth tokens for CIBA flows
- No interactive consent during rides
"""

from datetime import datetime, timedelta
from uuid import uuid4

from ..schemas import ConsentRecordPayload, ConsentScope, ConsentStatus, DriverConsent
from ..store import DRIVERS

# In-memory store for hackathon (replace with PostgreSQL in production)
CONSENTS: dict[str, DriverConsent] = {}


def create_consent(driver_id: str, phone_number: str, payload: ConsentRecordPayload, 
                   ip_address: str | None = None, user_agent: str | None = None) -> DriverConsent:
    """Record driver consent for CAMARA API access.
    
    This is called during driver onboarding (first app launch).
    The consent covers all four APIs for 12 months by default.
    """
    now = datetime.utcnow()
    expires = now + timedelta(days=30 * payload.duration_months)
    
    consent = DriverConsent(
        id=f"consent-{uuid4().hex[:12]}",
        driver_id=driver_id,
        phone_number=phone_number,
        status=ConsentStatus.granted,
        scopes=payload.scopes,
        granted_at=now.isoformat(),
        expires_at=expires.isoformat(),
        purpose="Driver identity verification for SafeRide platform",
        ip_address=ip_address,
        user_agent=user_agent
    )
    
    CONSENTS[consent.id] = consent
    return consent


def get_driver_consent(driver_id: str) -> DriverConsent | None:
    """Get the active consent record for a driver."""
    for consent in CONSENTS.values():
        if consent.driver_id == driver_id and consent.status == ConsentStatus.granted:
            # Check expiration
            expires = datetime.fromisoformat(consent.expires_at)
            if datetime.utcnow() < expires:
                return consent
    return None


def check_consent_scope(driver_id: str, scope: ConsentScope) -> bool:
    """Check if driver has granted consent for a specific API scope."""
    consent = get_driver_consent(driver_id)
    if not consent:
        return False
    return scope in consent.scopes


def revoke_consent(consent_id: str, reason: str = "user_request") -> DriverConsent | None:
    """Revoke consent (GDPR right to withdraw)."""
    consent = CONSENTS.get(consent_id)
    if consent:
        consent.status = ConsentStatus.denied
        # In production: also notify Nokia NaC to invalidate OAuth tokens
    return consent


def refresh_consent(consent_id: str, extension_months: int = 12) -> DriverConsent | None:
    """Extend consent validity (driver re-confirms)."""
    consent = CONSENTS.get(consent_id)
    if not consent:
        return None
        
    now = datetime.utcnow()
    new_expires = now + timedelta(days=30 * extension_months)
    consent.expires_at = new_expires.isoformat()
    consent.status = ConsentStatus.granted
    return consent


def list_expired_consents() -> list[DriverConsent]:
    """List consents needing renewal (for cron job)."""
    now = datetime.utcnow()
    expired = []
    for consent in CONSENTS.values():
        if consent.status == ConsentStatus.granted:
            expires = datetime.fromisoformat(consent.expires_at)
            if now >= expires:
                consent.status = ConsentStatus.expired
                expired.append(consent)
    return expired


def get_consent_summary(driver_id: str) -> dict:
    """Quick summary for debugging and admin dashboard."""
    consent = get_driver_consent(driver_id)
    if not consent:
        return {
            "has_consent": False,
            "can_call_ciba_apis": False,
            "can_call_number_verify": False,
            "expires_in_days": None
        }
    
    expires = datetime.fromisoformat(consent.expires_at)
    days_left = (expires - datetime.utcnow()).days
    
    return {
        "has_consent": True,
        "consent_id": consent.id,
        "scopes": [s.value for s in consent.scopes],
        "can_call_ciba_apis": ConsentScope.sim_swap in consent.scopes,
        "can_call_number_verify": ConsentScope.number_verify in consent.scopes,
        "expires_in_days": days_left,
        "expires_at": consent.expires_at
    }
