"""AuthService business logic (fake repository)."""
import uuid

import pytest

from feedback_app.core.exceptions import AdminNotFoundError, InvalidCredentialsError, TokenError
from feedback_app.core.security import create_access_token
from feedback_app.services.auth_service import AuthService

from tests.conftest import FakeUserRepository, make_user


def _service_with(*users):
    return AuthService(FakeUserRepository(list(users)))


def test_authenticate_success():
    admin = make_user(login="admin", password="password")
    assert _service_with(admin).authenticate("admin", "password") is admin


def test_authenticate_wrong_password():
    admin = make_user(login="admin", password="password")
    with pytest.raises(InvalidCredentialsError):
        _service_with(admin).authenticate("admin", "nope")


def test_authenticate_unknown_user():
    with pytest.raises(InvalidCredentialsError):
        _service_with().authenticate("ghost", "x")


def test_login_returns_token():
    admin = make_user(login="admin", password="password")
    token = _service_with(admin).login("admin", "password")
    assert isinstance(token, str) and token


def test_identify_valid_token():
    admin = make_user()
    token = create_access_token(str(admin.id))
    assert _service_with(admin).identify(token).id == admin.id


def test_identify_unknown_subject():
    token = create_access_token(str(uuid.uuid4()))
    with pytest.raises(AdminNotFoundError):
        _service_with().identify(token)


def test_identify_bad_token():
    with pytest.raises(TokenError):
        _service_with().identify("garbage")
