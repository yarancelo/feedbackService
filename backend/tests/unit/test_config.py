"""Settings smoke tests."""
from feedback_app.core.config import Settings, settings


def test_defaults_are_sane():
    assert settings.jwt_expire_minutes == 30
    assert settings.jwt_algorithm == "HS256"
    assert "postgresql" in settings.database_url


def test_env_override(monkeypatch):
    monkeypatch.setenv("JWT_EXPIRE_MINUTES", "5")
    assert Settings().jwt_expire_minutes == 5
