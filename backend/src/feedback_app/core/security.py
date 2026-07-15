"""JWT token creation and verification.

Each function does one thing. Verification failures are surfaced as a domain
exception (TokenError), never as a raw library error.
"""
import datetime

import jwt

from feedback_app.core.config import settings
from feedback_app.core.exceptions import TokenError
from feedback_app.core.logging import get_logger

logger = get_logger(__name__)


def create_access_token(subject: str) -> str:
    """Create a signed JWT whose subject is the admin id."""
    now = datetime.datetime.now(datetime.timezone.utc)
    expires_at = now + datetime.timedelta(minutes=settings.jwt_expire_minutes)
    payload = {"sub": subject, "iat": now, "exp": expires_at}

    token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    logger.debug("Issued access token for subject=%s (exp=%s)", subject, expires_at.isoformat())
    return token


def decode_access_token(token: str) -> str:
    """Verify a JWT and return its subject, or raise TokenError."""
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except jwt.PyJWTError as exc:
        logger.warning("Rejected access token: %s", exc)
        raise TokenError() from exc

    subject = payload.get("sub")
    if not subject:
        logger.warning("Access token has no subject claim")
        raise TokenError()

    logger.debug("Accepted access token for subject=%s", subject)
    return subject
