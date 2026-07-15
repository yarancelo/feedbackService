"""Domain exception hierarchy + HTTP mapping."""
from fastapi import status

from feedback_app.controllers.error_handlers import _status_for
from feedback_app.core.exceptions import (
    AdminNotFoundError,
    AppError,
    AuthError,
    FeedbackNotFoundError,
    InvalidCredentialsError,
    NotFoundError,
    TokenError,
)


def test_default_messages():
    assert InvalidCredentialsError().message == "Неверный логин или пароль"
    assert FeedbackNotFoundError().message == "Отзыв не найден"


def test_custom_message():
    assert AppError("boom").message == "boom"


def test_hierarchy():
    assert issubclass(InvalidCredentialsError, AuthError)
    assert issubclass(TokenError, AuthError)
    assert issubclass(AdminNotFoundError, AuthError)
    assert issubclass(FeedbackNotFoundError, NotFoundError)
    assert issubclass(AuthError, AppError)


def test_status_mapping():
    assert _status_for(InvalidCredentialsError()) == status.HTTP_401_UNAUTHORIZED
    assert _status_for(TokenError()) == status.HTTP_401_UNAUTHORIZED
    assert _status_for(FeedbackNotFoundError()) == status.HTTP_404_NOT_FOUND
    assert _status_for(AppError()) == status.HTTP_500_INTERNAL_SERVER_ERROR
