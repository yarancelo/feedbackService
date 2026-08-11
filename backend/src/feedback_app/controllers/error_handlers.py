"""Translation of domain exceptions into HTTP responses.

Keeps controllers free of try/except: they call services and let exceptions
propagate here, where each domain error becomes exactly one HTTP status.
"""
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from feedback_app.core.exceptions import AppError, AuthError, IntegrationError, NotFoundError
from feedback_app.core.logging import get_logger

logger = get_logger(__name__)

_STATUS_BY_TYPE = [
    (AuthError, status.HTTP_401_UNAUTHORIZED),
    (NotFoundError, status.HTTP_404_NOT_FOUND),
    (IntegrationError, status.HTTP_502_BAD_GATEWAY),
    (AppError, status.HTTP_500_INTERNAL_SERVER_ERROR),
]


def _status_for(exc: AppError) -> int:
    """Map a domain exception to an HTTP status code."""
    for exc_type, http_status in _STATUS_BY_TYPE:
        if isinstance(exc, exc_type):
            return http_status
    return status.HTTP_500_INTERNAL_SERVER_ERROR


def register_error_handlers(app: FastAPI) -> None:
    """Attach the domain-exception handler to the app."""

    @app.exception_handler(AppError)
    async def _handle_app_error(_request: Request, exc: AppError) -> JSONResponse:
        http_status = _status_for(exc)
        if http_status >= 500:
            logger.error("Unhandled application error: %s", exc.message)
        else:
            logger.debug("Domain error -> %d: %s", http_status, exc.message)
        return JSONResponse(status_code=http_status, content={"detail": exc.message})
