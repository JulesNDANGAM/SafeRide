"""Real Nokia Network-as-Code client (RapidAPI gateway).

Architecture discovered from Nokia's official sample app
(https://github.com/nokia/Network-as-Code-Number-Verification-App):

- Each Nokia NaC API has its OWN RapidAPI subdomain
  (e.g. ``number-verification.p-eu.rapidapi.com`` with host header
   ``number-verification.nokia.rapidapi.com``).
- Each API requires a separate **subscription** on RapidAPI (Basic = free
  tier exists; "free" plans must be activated explicitly per API).
- ``Number Verification`` additionally requires an OAuth2 / CIBA flow:
  the consumer first calls ``well-known-metadata`` and
  ``nac-authorization-server/clientcredentials``, then redirects the
  end-user to authorize, then exchanges the auth code for a Bearer token.
- ``Device Status``, ``KYC Match`` etc. only need the RapidAPI key once
  the subscription is active (no end-user consent flow on the simulator).

This client implements the **simple cases** (RapidAPI key only). The CIBA
flow is documented as a TODO (would need a public callback URL and a real
SIM during the demo). All calls fail-open: if a real call returns an
error, the caller receives ``None`` and can fall back to the mock.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

import httpx

from ..config import settings


logger = logging.getLogger("saferide.nac")


# Per-API host configuration ------------------------------------------------
# slug -> (gateway_host, host_id_header)
NAC_APIS: dict[str, tuple[str, str]] = {
    "well-known-metadata":     ("well-known-metadata.p-eu.rapidapi.com",     "well-known-metadata.nokia.rapidapi.com"),
    "nac-authorization-server": ("nac-authorization-server.p-eu.rapidapi.com", "nac-authorization-server.nokia.rapidapi.com"),
    "number-verification":      ("number-verification.p-eu.rapidapi.com",      "number-verification.nokia.rapidapi.com"),
    "device-status":            ("device-status.p-eu.rapidapi.com",            "device-status.nokia.rapidapi.com"),
    "device-roaming-status":    ("device-roaming-status.p-eu.rapidapi.com",    "device-roaming-status.nokia.rapidapi.com"),
    "kyc-match":                ("kyc-match.p-eu.rapidapi.com",                "kyc-match.nokia.rapidapi.com"),
    "kyc-age-verification":     ("kyc-age-verification.p-eu.rapidapi.com",     "kyc-age-verification.nokia.rapidapi.com"),
    # The following are typically gated behind paid plans:
    "sim-swap":                 ("sim-swap.p-eu.rapidapi.com",                 "sim-swap.nokia.rapidapi.com"),
    "location-verification":    ("location-verification.p-eu.rapidapi.com",    "location-verification.nokia.rapidapi.com"),
    "quality-on-demand":        ("quality-on-demand.p-eu.rapidapi.com",        "quality-on-demand.nokia.rapidapi.com"),
    "congestion-insights":      ("congestion-insights.p-eu.rapidapi.com",      "congestion-insights.nokia.rapidapi.com"),
    "geofencing-subscriptions": ("geofencing-subscriptions.p-eu.rapidapi.com", "geofencing-subscriptions.nokia.rapidapi.com"),
}


@dataclass
class NACResult:
    api: str
    ok: bool
    status_code: int
    data: Optional[dict]
    error: Optional[str]
    source: str  # "real-nac" or "mock"


def _headers(api_slug: str) -> dict[str, str]:
    _, host_id = NAC_APIS[api_slug]
    return {
        "x-rapidapi-key": settings.nokia_nac_api_key,
        "x-rapidapi-host": host_id,
        "content-type": "application/json",
    }


def _post(api_slug: str, path: str, body: dict) -> NACResult:
    if not settings.nokia_nac_api_key:
        return NACResult(api_slug, False, 0, None, "no-api-key", "mock")
    if api_slug not in NAC_APIS:
        return NACResult(api_slug, False, 0, None, "unknown-api", "mock")
    gw, _ = NAC_APIS[api_slug]
    url = f"https://{gw}{path}"
    try:
        with httpx.Client(timeout=settings.nokia_nac_timeout_s) as client:
            response = client.post(url, headers=_headers(api_slug), json=body)
        ok = 200 <= response.status_code < 300
        try:
            payload = response.json()
        except ValueError:
            payload = {"raw": response.text[:300]}
        return NACResult(
            api=api_slug,
            ok=ok,
            status_code=response.status_code,
            data=payload if ok else None,
            error=None if ok else (payload.get("message") if isinstance(payload, dict) else "http-error"),
            source="real-nac",
        )
    except httpx.HTTPError as exc:
        logger.warning("Nokia NaC %s call failed: %s", api_slug, exc)
        return NACResult(api_slug, False, 0, None, str(exc), "real-nac")


def _get(api_slug: str, path: str) -> NACResult:
    if not settings.nokia_nac_api_key:
        return NACResult(api_slug, False, 0, None, "no-api-key", "mock")
    if api_slug not in NAC_APIS:
        return NACResult(api_slug, False, 0, None, "unknown-api", "mock")
    gw, _ = NAC_APIS[api_slug]
    url = f"https://{gw}{path}"
    try:
        with httpx.Client(timeout=settings.nokia_nac_timeout_s) as client:
            response = client.get(url, headers=_headers(api_slug))
        ok = 200 <= response.status_code < 300
        try:
            payload = response.json()
        except ValueError:
            payload = {"raw": response.text[:300]}
        return NACResult(
            api=api_slug, ok=ok, status_code=response.status_code,
            data=payload if ok else None,
            error=None if ok else (payload.get("message") if isinstance(payload, dict) else "http-error"),
            source="real-nac",
        )
    except httpx.HTTPError as exc:
        return NACResult(api_slug, False, 0, None, str(exc), "real-nac")


# Public helpers ------------------------------------------------------------

def is_enabled() -> bool:
    """``True`` when SAFERIDE_USE_REAL_NAC is partial/full and a key is set."""
    mode = settings.use_real_nokia_nac
    return mode in {"partial", "full"} and bool(settings.nokia_nac_api_key)


def call_device_status_roaming(phone_number: str) -> NACResult:
    """CAMARA Device Status — Roaming retrieve (RapidAPI key only)."""
    return _post("device-status", "/roaming", {"device": {"phoneNumber": phone_number}})


def call_kyc_match(phone_number: str, name: str) -> NACResult:
    return _post("kyc-match", "/match", {"phoneNumber": phone_number, "name": name})


def call_number_verification_simple(phone_number: str) -> NACResult:
    """Best-effort Number Verification (will fail until OAuth/CIBA flow done)."""
    return _post("number-verification", "/verify", {"phoneNumber": phone_number})


def probe_subscriptions() -> dict[str, dict]:
    """Quick health check on each API root (returns subscription/health status)."""
    out: dict[str, dict] = {}
    for slug in NAC_APIS:
        res = _get(slug, "/")
        out[slug] = {
            "status_code": res.status_code,
            "ok": res.ok,
            "error": res.error,
            "subscribed_hint": res.error != "You are not subscribed to this API." and res.status_code != 403,
        }
    return out
