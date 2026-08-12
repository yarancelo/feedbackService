"""Authentication business logic.

Depends on the data layer (UserRepository) and on token functions. Failures are
raised as domain exceptions; this layer never returns None to signal an error.
"""
import uuid
import bcrypt

from feedback_app.core.exceptions import AdminNotFoundError, InvalidCredentialsError
from feedback_app.core.logging import get_logger
from feedback_app.core.security import create_access_token, decode_access_token
from feedback_app.models.user import User
from feedback_app.repositories.user_repository import UserRepository

logger = get_logger(__name__)


class AuthService:
    """Authenticates admins and issues/validates access tokens."""

    def __init__(self, users: UserRepository) -> None:
        self._users = users

    def authenticate(self, login: str, password: str) -> User:
        """Return the admin for valid credentials, else raise InvalidCredentialsError."""
        user = self._users.get_by_login(login)
        if user is None or not user.password_hash or not bcrypt.checkpw(password.encode(), user.password_hash.encode()):
            logger.warning("Failed login attempt")
            raise InvalidCredentialsError()
        logger.info("Successful login")
        return user

    def login(self, login: str, password: str) -> str:
        """Authenticate and return a signed access token."""
        user = self.authenticate(login, password)
        return create_access_token(str(user.id))

    def identify(self, token: str) -> User:
        """Resolve an access token to the admin it belongs to."""
        subject = decode_access_token(token)  # raises TokenError if invalid
        user = self._users.get_by_id(uuid.UUID(subject))
        if user is None:
            logger.warning("Token subject=%s has no matching admin", subject)
            raise AdminNotFoundError()
        logger.debug("Token resolved to admin id=%s", user.id)
        return user
