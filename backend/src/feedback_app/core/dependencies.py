"""FastAPI dependency providers.

Wires the layers together: a request-scoped DB session (commit on success,
rollback on any exception) and factories that assemble repositories + services.
"""
from collections.abc import Iterator
import uuid

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from feedback_app.core.config import settings
from feedback_app.core.database import SessionLocal
from feedback_app.core.logging import get_logger
from feedback_app.models.user import User
from feedback_app.repositories.user_repository import UserRepository
from feedback_app.repositories.feedback_repository import FeedbackRepository
from feedback_app.services.auth_service import AuthService
from feedback_app.services.feedback_service import FeedbackService
from feedback_app.integrations.bitrix_client import BitrixClient
from feedback_app.repositories.idea_repository import IdeaRepository
from feedback_app.services.idea_service import IdeaService
from feedback_app.services import employee_service
from feedback_app.repositories.category_repository import CategoryRepository
from feedback_app.services.category_service import CategoryService
from feedback_app.repositories.comment_repository import CommentRepository
from feedback_app.services.comment_service import CommentService
from feedback_app.models.manual_author import ManualAuthor
from feedback_app.integrations.bitrix_client import Employee

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
    """Legacy provider retained only for compatibility with external extensions."""
    return FeedbackService(FeedbackRepository(db))


def get_bitrix_client() -> BitrixClient:
    """Provide a Bitrix client built from settings (stub when webhook is unset)."""
    return BitrixClient(settings.bitrix_webhook_url, settings.bitrix_timeout_seconds)


def get_idea_service(
    db: Session = Depends(get_db), client: BitrixClient = Depends(get_bitrix_client)
) -> IdeaService:
    """Assemble the ideas service with the current employee directory."""
    def lookup(bitrix_id):
        if bitrix_id and bitrix_id.startswith('manual:'):
            try:
                item = db.get(ManualAuthor, uuid.UUID(bitrix_id.split(':', 1)[1]))
            except ValueError:
                return None
            return Employee(bitrix_id, item.full_name, item.position, item.company, item.department) if item and item.is_active else None
        return employee_service.find_employee(client, bitrix_id)
    return IdeaService(IdeaRepository(db), lookup)


def get_category_service(db: Session = Depends(get_db)) -> CategoryService:
    return CategoryService(CategoryRepository(db))


def get_comment_service(db: Session = Depends(get_db)) -> CommentService:
    return CommentService(CommentRepository(db), IdeaRepository(db))



def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
    auth_service: AuthService = Depends(get_auth_service),
) -> User:
    """Resolve the bearer token to the authenticated admin (or raise AuthError)."""
    return auth_service.identify(credentials.credentials)
