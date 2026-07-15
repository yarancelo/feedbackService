"""JWT creation/verification."""
import datetime

import jwt
import pytest

from feedback_app.core.config import settings
from feedback_app.core.exceptions import TokenError
from feedback_app.core.security import create_access_token, decode_access_token


def test_roundtrip():
    token = create_access_token("subject-1")
    assert decode_access_token(token) == "subject-1"


def test_rejects_garbage():
    with pytest.raises(TokenError):
        decode_access_token("not.a.jwt")


def test_rejects_wrong_secret():
    token = jwt.encode({"sub": "x"}, "another-secret", algorithm=settings.jwt_algorithm)
    with pytest.raises(TokenError):
        decode_access_token(token)


def test_rejects_missing_subject():
    token = jwt.encode({"foo": "bar"}, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    with pytest.raises(TokenError):
        decode_access_token(token)


def test_rejects_expired():
    past = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=1)
    token = jwt.encode({"sub": "x", "exp": past}, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    with pytest.raises(TokenError):
        decode_access_token(token)
