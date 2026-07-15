"""FastAPI dependency providers.

Wires the layers together: a request-scoped DB session (commit on success,
rollback on any exception) and factories that assemble repositories + services.
"""
from collections.abc import Iterator

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from feedback_app.core.database import SessionLocal
from feedback_app.core.logging import get_logger
from feedback_app.models.user import User
from feedback_app.repositories.feedback_repository import FeedbackRepository
from feedback_app.repositories.user_repository import UserRepository
from feedback_app.services.auth_service import AuthService
from feedback_app.services.feedback_service import FeedbackService

logger = get_logger(__name__)

_bearer = HTTPBearer(auto_error=True)


def get_db() -> Iterator[Session]:
    """Yield a session; commit on success, roll back on ANY exception."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
        logger.debug("DB session committed")
    except Exception:
        session.rollback()
        logger.exception("DB session rolled back due to an exception")
        raise
    finally:
        session.close()


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    """Assemble the authentication service for a request."""
    return AuthService(UserRepository(db))


def get_feedback_service(db: Session = Depends(get_db)) -> FeedbackService:
    """Assemble the feedback service for a request."""
    return FeedbackService(FeedbackRepository(db))


def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
    auth_service: AuthService = Depends(get_auth_service),
) -> User:
    """Resolve the bearer token to the authenticated admin (or raise AuthError)."""
    return auth_service.identify(credentials.credentials)
