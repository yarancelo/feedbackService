"""Authentication controller (routes only; no business logic)."""
import time
from collections import defaultdict, deque
from fastapi import APIRouter, Depends, HTTPException, Request, status

from feedback_app.core.dependencies import get_auth_service
from feedback_app.core.logging import get_logger
from feedback_app.schemas.auth import LoginRequest, TokenResponse
from feedback_app.services.auth_service import AuthService

logger = get_logger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])
_failed_logins: dict[str, deque[float]] = defaultdict(deque)
_LOGIN_WINDOW_SECONDS = 15 * 60
_LOGIN_MAX_FAILURES = 6


@router.post("/login", response_model=TokenResponse)
def login(
    payload: LoginRequest,
    request: Request,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    """Exchange credentials for an access token (401 on failure)."""
    ip = request.client.host if request.client else "unknown"
    now = time.monotonic(); attempts = _failed_logins[ip]
    while attempts and now - attempts[0] > _LOGIN_WINDOW_SECONDS: attempts.popleft()
    if len(attempts) >= _LOGIN_MAX_FAILURES:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Слишком много попыток. Попробуйте позже.")
    try:
        token = auth_service.login(payload.login, payload.password)
    except Exception:
        attempts.append(now)
        raise
    _failed_logins.pop(ip, None)
    return TokenResponse(access_token=token)
