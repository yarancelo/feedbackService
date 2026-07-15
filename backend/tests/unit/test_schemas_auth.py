"""Auth schema validation."""
import pytest
from pydantic import ValidationError

from feedback_app.schemas.auth import LoginRequest, TokenResponse


def test_valid_login():
    req = LoginRequest(login="admin", password="password")
    assert req.login == "admin"


def test_login_requires_non_empty():
    with pytest.raises(ValidationError):
        LoginRequest(login="", password="x")
    with pytest.raises(ValidationError):
        LoginRequest(login="x", password="")


def test_token_response_defaults():
    assert TokenResponse(access_token="t").token_type == "bearer"
