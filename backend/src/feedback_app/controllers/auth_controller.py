"""Authentication controller (routes only; no business logic)."""
from fastapi import APIRouter, Depends

from feedback_app.core.dependencies import get_auth_service
from feedback_app.core.logging import get_logger
from feedback_app.schemas.auth import LoginRequest, TokenResponse
from feedback_app.services.auth_service import AuthService

logger = get_logger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(
    payload: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    """Exchange credentials for an access token (401 on failure)."""
    logger.info("Login requested for login=%s", payload.login)
    token = auth_service.login(payload.login, payload.password)
    return TokenResponse(access_token=token)
