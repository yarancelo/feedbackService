"""Dependency providers: DB session lifecycle + admin resolution."""
from unittest.mock import MagicMock, patch

import pytest
from fastapi.security import HTTPAuthorizationCredentials

from feedback_app.core import dependencies
from feedback_app.core.exceptions import AdminNotFoundError, TokenError
from feedback_app.core.security import create_access_token
from feedback_app.services.auth_service import AuthService
from feedback_app.services.feedback_service import FeedbackService

from tests.conftest import FakeUserRepository, make_user


# ---------------- get_db ----------------
def test_get_db_commits_on_success():
    session = MagicMock()
    with patch.object(dependencies, "SessionLocal", return_value=session):
        gen = dependencies.get_db()
        assert next(gen) is session
        with pytest.raises(StopIteration):
            next(gen)  # drive generator to completion -> commit path
    session.commit.assert_called_once()
    session.rollback.assert_not_called()
    session.close.assert_called_once()


def test_get_db_rolls_back_on_exception():
    session = MagicMock()
    with patch.object(dependencies, "SessionLocal", return_value=session):
        gen = dependencies.get_db()
        next(gen)
        with pytest.raises(ValueError):
            gen.throw(ValueError("boom"))  # inject error at the yield point
    session.rollback.assert_called_once()
    session.commit.assert_not_called()
    session.close.assert_called_once()


# ---------------- service factories ----------------
def test_get_auth_service_builds_service():
    assert isinstance(dependencies.get_auth_service(db=MagicMock()), AuthService)


def test_get_feedback_service_builds_service():
    assert isinstance(dependencies.get_feedback_service(db=MagicMock()), FeedbackService)


# ---------------- get_current_admin ----------------
def _creds(token):
    return HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)


def test_get_current_admin_returns_admin():
    admin = make_user()
    service = AuthService(FakeUserRepository([admin]))
    token = create_access_token(str(admin.id))
    result = dependencies.get_current_admin(credentials=_creds(token), auth_service=service)
    assert result.id == admin.id


def test_get_current_admin_bad_token():
    service = AuthService(FakeUserRepository([]))
    with pytest.raises(TokenError):
        dependencies.get_current_admin(credentials=_creds("garbage"), auth_service=service)


def test_get_current_admin_unknown_admin():
    service = AuthService(FakeUserRepository([]))
    token = create_access_token("00000000-0000-0000-0000-000000000000")
    with pytest.raises(AdminNotFoundError):
        dependencies.get_current_admin(credentials=_creds(token), auth_service=service)
