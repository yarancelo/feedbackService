"""Bitrix client: stub, pagination, mapping, error handling."""
import json
from unittest.mock import MagicMock, patch

import pytest

from feedback_app.core.exceptions import BitrixError
from feedback_app.integrations import bitrix_client as bc
from feedback_app.integrations.bitrix_client import BitrixClient, _full_name


def _fake_response(payload):
    resp = MagicMock()
    resp.read.return_value = json.dumps(payload).encode("utf-8")
    resp.__enter__.return_value = resp
    resp.__exit__.return_value = False
    return resp


def test_stub_when_unconfigured():
    client = BitrixClient(None)
    assert client.configured is False
    employees = client.fetch_employees()
    assert len(employees) == 4
    assert employees[0].bitrix_id.startswith("stub")


def test_full_name_orders_last_first_second():
    assert _full_name({"NAME": "Иван", "LAST_NAME": "Петров", "SECOND_NAME": "С"}) == "Петров Иван С"
    assert _full_name({"NAME": "Иван"}) == "Иван"


def test_error_envelope_raises():
    client = BitrixClient("https://x.bitrix24.ru/rest/1/abc/")
    with patch.object(bc.urllib.request, "urlopen",
                      return_value=_fake_response({"error": "QUERY_LIMIT_EXCEEDED"})):
        with pytest.raises(BitrixError):
            client._call("user.get", {})


def test_network_error_raises():
    client = BitrixClient("https://x.bitrix24.ru/rest/1/abc/")
    with patch.object(bc.urllib.request, "urlopen", side_effect=bc.urllib.error.URLError("down")):
        with pytest.raises(BitrixError):
            client._call("user.get", {})


def test_pagination_follows_next():
    client = BitrixClient("https://x.bitrix24.ru/rest/1/abc/")
    pages = [
        {"result": [{"ID": i} for i in range(50)], "next": 50, "total": 75},
        {"result": [{"ID": i} for i in range(50, 75)], "total": 75},
    ]
    with patch.object(client, "_call", side_effect=pages) as call:
        rows = client._list_all("user.get", {})
    assert len(rows) == 75
    assert call.call_count == 2


def test_fetch_maps_users_and_departments():
    client = BitrixClient("https://x.bitrix24.ru/rest/1/abc/")

    def fake_call(method, params):
        if method == "department.get":
            return {"result": [{"ID": 1, "NAME": "Кухня"}], "total": 1}
        return {
            "result": [
                {"ID": 10, "NAME": "Иван", "LAST_NAME": "Петров",
                 "WORK_POSITION": "Су-шеф", "UF_DEPARTMENT": [1]}
            ],
            "total": 1,
        }

    with patch.object(client, "_call", side_effect=fake_call):
        employees = client.fetch_employees()

    assert len(employees) == 1
    emp = employees[0]
    assert emp.bitrix_id == "10"
    assert emp.full_name == "Петров Иван"
    assert emp.position == "Су-шеф"
    assert emp.unit == "Кухня"


def test_pagination_continues_without_total():
    """Regression: pages must keep loading on `next` even when `total` is absent."""
    client = BitrixClient("https://x.bitrix24.ru/rest/1/abc/")
    pages = [
        {"result": [{"ID": i} for i in range(50)], "next": 50},  # no total field
        {"result": [{"ID": i} for i in range(50, 70)]},          # no next -> stop
    ]
    with patch.object(client, "_call", side_effect=pages) as call:
        rows = client._list_all("user.get", {})
    assert len(rows) == 70
    assert call.call_count == 2


def test_pagination_respects_page_cap():
    """A cursor that never ends must not loop forever."""
    client = BitrixClient("https://x.bitrix24.ru/rest/1/abc/")
    with patch.object(client, "_call", return_value={"result": [{"ID": 1}], "next": 1}):
        rows = client._list_all("user.get", {})
    assert len(rows) == bc._MAX_PAGES


def test_user_get_uses_top_level_active_filter():
    """Regression: user.get filter fields go top-level, not under `filter`."""
    client = BitrixClient("https://x.bitrix24.ru/rest/1/abc/")
    seen = {}

    def fake_call(method, params):
        seen[method] = params
        return {"result": [], "total": 0}

    with patch.object(client, "_call", side_effect=fake_call):
        client.fetch_employees()

    user_params = seen["user.get"]
    assert user_params.get("ACTIVE") is True
    assert "filter" not in user_params


def test_scalar_department_is_tolerated():
    """UF_DEPARTMENT delivered as a scalar should not crash mapping."""
    client = BitrixClient("https://x.bitrix24.ru/rest/1/abc/")

    def fake_call(method, params):
        if method == "department.get":
            return {"result": [{"ID": 7, "NAME": "Ресепшн"}], "total": 1}
        return {"result": [{"ID": 3, "NAME": "Анна", "LAST_NAME": "И",
                            "UF_DEPARTMENT": 7}], "total": 1}  # scalar, not list

    with patch.object(client, "_call", side_effect=fake_call):
        employees = client.fetch_employees()
    assert employees[0].unit == "Ресепшн"
