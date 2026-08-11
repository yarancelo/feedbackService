"""Employee service: TTL cache + stale-on-failure behaviour."""
import pytest

from feedback_app.core.exceptions import BitrixError
from feedback_app.integrations.bitrix_client import Employee
from feedback_app.services import employee_service


@pytest.fixture(autouse=True)
def _clear_cache():
    employee_service.clear_cache()
    yield
    employee_service.clear_cache()


class FakeClient:
    def __init__(self, items, fail=False):
        self.items = items
        self.fail = fail
        self.calls = 0

    def fetch_employees(self):
        self.calls += 1
        if self.fail:
            raise BitrixError()
        return self.items


SAMPLE = [Employee("1", "Петров Иван")]


def test_first_call_fetches_then_caches():
    client = FakeClient(SAMPLE)
    assert employee_service.list_employees(client) == SAMPLE
    employee_service.list_employees(client)  # served from cache
    assert client.calls == 1


def test_force_refetches():
    client = FakeClient(SAMPLE)
    employee_service.list_employees(client)
    employee_service.list_employees(client, force=True)
    assert client.calls == 2


def test_stale_cache_served_on_failure():
    good = FakeClient(SAMPLE)
    employee_service.list_employees(good)  # populate cache
    failing = FakeClient(SAMPLE, fail=True)
    assert employee_service.list_employees(failing, force=True) == SAMPLE


def test_cold_failure_raises():
    with pytest.raises(BitrixError):
        employee_service.list_employees(FakeClient(SAMPLE, fail=True))
