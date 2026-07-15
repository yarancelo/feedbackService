"""Application configuration.

A single responsibility: expose typed settings read from the environment.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Typed application settings, populated from environment variables."""

    # Database (SQLAlchemy URL using the psycopg v3 driver).
    database_url: str = "postgresql+psycopg://admin:password@postgres:5432/feedback"

    # Authentication: 30-minute JWT access tokens.
    jwt_secret: str = "internal-only-change-me-please-set-a-real-secret"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 30

    # Optional: directory of a built SPA to serve (single-process/local mode).
    serve_static_dir: str | None = None

    # Observability.
    log_level: str = "DEBUG"

    model_config = SettingsConfigDict(env_file=".env", env_prefix="", extra="ignore")


settings = Settings()
