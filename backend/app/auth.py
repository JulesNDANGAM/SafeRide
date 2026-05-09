from fastapi import Header, HTTPException, status

from .config import settings


def require_admin(authorization: str | None = Header(default=None)) -> None:
    """FastAPI dependency: requires `Authorization: Bearer <admin token>`.

    The expected token is configured via SAFERIDE_ADMIN_TOKEN.
    For production, replace this with proper auth (JWT + RBAC + KMS).
    """
    expected = settings.admin_token
    if not expected:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail="Admin token not configured")
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Missing bearer token")
    token = authorization.split(" ", 1)[1].strip()
    if token != expected:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid admin token")
