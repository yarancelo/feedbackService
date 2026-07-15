"""Domain exception hierarchy.

Error handling above the data layer is done with these exceptions. Each maps
to exactly one failure meaning; controllers translate them into HTTP responses
(see controllers/error_handlers.py). The data layer (repositories) never raises
these — it returns values instead.
"""


class AppError(Exception):
    """Base class for all application-level errors."""

    message: str = "Внутренняя ошибка приложения"

    def __init__(self, message: str | None = None) -> None:
        super().__init__(message or self.message)
        self.message = message or self.message


class AuthError(AppError):
    """Base class for authentication/authorization failures."""

    message = "Ошибка авторизации"


class InvalidCredentialsError(AuthError):
    """Login or password did not match."""

    message = "Неверный логин или пароль"


class TokenError(AuthError):
    """Access token is missing, malformed or expired."""

    message = "Недействительный или просроченный токен"


class AdminNotFoundError(AuthError):
    """Token was valid but the referenced admin no longer exists."""

    message = "Администратор не найден"


class NotFoundError(AppError):
    """Base class for missing-resource errors."""

    message = "Ресурс не найден"


class FeedbackNotFoundError(NotFoundError):
    """A feedback item with the requested id does not exist."""

    message = "Отзыв не найден"
