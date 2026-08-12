"""Domain exception hierarchy.

Error handling above the data layer is done with these exceptions. Each maps
to exactly one failure meaning; controllers translate them into HTTP responses
(see controllers/error_handlers.py). The data layer (repositories) never raises
these — it returns values instead.
"""


class AppError(Exception):
    """Base class for all application-level errors."""

    message: str = "Что-то пошло не так. Попробуйте ещё раз."

    def __init__(self, message: str | None = None) -> None:
        super().__init__(message or self.message)
        self.message = message or self.message


class AuthError(AppError):
    """Base class for authentication/authorization failures."""

    message = "Не удалось войти. Проверьте данные и попробуйте ещё раз."


class InvalidCredentialsError(AuthError):
    """Login or password did not match."""

    message = "Неверный логин или пароль"


class TokenError(AuthError):
    """Access token is missing, malformed or expired."""

    message = "Сессия истекла. Войдите снова."


class AdminNotFoundError(AuthError):
    """Token was valid but the referenced admin no longer exists."""

    message = "Учётная запись не найдена."


class NotFoundError(AppError):
    """Base class for missing-resource errors."""

    message = "Запрашиваемые данные не найдены."


class FeedbackNotFoundError(NotFoundError):
    """A feedback item with the requested id does not exist."""

    message = "Сообщение не найдено."


class IdeaNotFoundError(NotFoundError):
    message = "Idea not found"


class UnknownAuthorError(NotFoundError):
    message = "Author not found in employee directory"


class IntegrationError(AppError):
    """Base class for failures talking to an external system."""

    message = "Сервис временно недоступен. Попробуйте позже."


class BitrixError(IntegrationError):
    """A call to the Bitrix24 REST API failed."""

    message = "Не удалось загрузить данные из Bitrix24. Попробуйте ещё раз."
