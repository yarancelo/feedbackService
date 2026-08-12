"""Data-access for administrators.

This is the data level: methods return values (or None) and do not raise
domain exceptions. Business meaning is assigned one layer up, in services.
"""
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from feedback_app.core.logging import get_logger
from feedback_app.models.user import User

logger = get_logger(__name__)


class UserRepository:
    """Read access to the users table."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_login(self, login: str) -> User | None:
        """Return the admin with this login, or None."""
        logger.debug("Looking up user by login")
        return self._session.execute(
            select(User).where(User.login == login)
        ).scalar_one_or_none()

    def get_by_id(self, user_id: uuid.UUID) -> User | None:
        """Return the admin with this id, or None."""
        logger.debug("Looking up user by id")
        return self._session.get(User, user_id)
