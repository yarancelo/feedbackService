"""UserRepository data-access (mocked SQLAlchemy Session)."""
import uuid
from unittest.mock import MagicMock

from feedback_app.repositories.user_repository import UserRepository


def test_get_by_login_returns_scalar():
    session = MagicMock()
    sentinel = object()
    session.execute.return_value.scalar_one_or_none.return_value = sentinel

    repo = UserRepository(session)
    assert repo.get_by_login("admin") is sentinel
    session.execute.assert_called_once()


def test_get_by_login_returns_none_when_absent():
    session = MagicMock()
    session.execute.return_value.scalar_one_or_none.return_value = None
    assert UserRepository(session).get_by_login("nobody") is None


def test_get_by_id_delegates_to_session_get():
    session = MagicMock()
    sentinel = object()
    session.get.return_value = sentinel
    user_id = uuid.uuid4()

    assert UserRepository(session).get_by_id(user_id) is sentinel
    session.get.assert_called_once()
