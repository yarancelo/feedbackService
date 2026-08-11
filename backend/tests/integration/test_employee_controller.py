"""Employee endpoints: public list (stub) + admin-only sync."""
import pytest

from feedback_app.core.dependencies import get_bitrix_client, get_current_admin
from feedback_app.integrations.bitrix_client import BitrixClient
from feedback_app.services import employee_service

from tests.conftest import make_user


@pytest.fixture(autouse=True)
def _stub_client(app):
    employee_service.clear_cache()
    app.dependency_overrides[get_bitrix_client] = lambda: BitrixClient(None)
    yield
    employee_service.clear_cache()


def test_list_employees_public(client):
    resp = client.get("/api/employees")
    assert resp.status_code == 200
    body = resp.json()
    assert len(body) == 4
    assert body[0]["full_name"]


def test_sync_requires_admin(client):
    assert client.post("/api/employees/sync").status_code in (401, 403)


def test_sync_as_admin(app, client):
    app.dependency_overrides[get_current_admin] = lambda: make_user()
    resp = client.post("/api/employees/sync")
    assert resp.status_code == 200
    assert len(resp.json()) == 4
