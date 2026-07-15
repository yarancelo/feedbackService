"""Auth controller: login success + failure translation."""
from feedback_app.core.dependencies import get_auth_service
from feedback_app.services.auth_service import AuthService

from tests.conftest import FakeUserRepository, make_user


def _use_admin(app, admin):
    app.dependency_overrides[get_auth_service] = lambda: AuthService(
        FakeUserRepository([admin])
    )


def test_login_success(app, client):
    _use_admin(app, make_user(login="admin", password="password"))
    resp = client.post("/api/auth/login", json={"login": "admin", "password": "password"})
    assert resp.status_code == 200
    assert resp.json()["access_token"]
    assert resp.json()["token_type"] == "bearer"


def test_login_wrong_password(app, client):
    _use_admin(app, make_user(login="admin", password="password"))
    resp = client.post("/api/auth/login", json={"login": "admin", "password": "nope"})
    assert resp.status_code == 401
    assert resp.json()["detail"] == "Неверный логин или пароль"


def test_login_validation_error(client):
    resp = client.post("/api/auth/login", json={"login": "", "password": ""})
    assert resp.status_code == 422
