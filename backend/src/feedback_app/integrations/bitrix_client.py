"""Bitrix24 employee-directory client with a local fallback."""
import dataclasses
import json
import urllib.error
import urllib.request

from feedback_app.core.exceptions import BitrixError
from feedback_app.core.logging import get_logger

logger = get_logger(__name__)
PAGE_SIZE = 50
_MAX_PAGES = 1000


@dataclasses.dataclass(frozen=True)
class Employee:
    bitrix_id: str
    full_name: str
    position: str | None = None
    company: str | None = None
    department: str | None = None

    @property
    def unit(self) -> str | None:
        """Legacy alias retained for integrations using the former directory view."""
        return self.department


STUB_EMPLOYEES = [
    Employee("stub-1", "Смирнова Анна", "Администратор", "Отель «Центр»", "Ресепшен"),
    Employee("stub-2", "Петров Иван", "Хостес", "Отель «Центр»", "Ресторан"),
    Employee("stub-3", "Ким Мария", "Су-шеф", "Отель «Север»", "Кухня"),
    Employee("stub-4", "Соколов Дмитрий", "Менеджер", "Отель «Север»", "Бронирование"),
]


def _full_name(user: dict) -> str:
    return " ".join(part.strip() for part in (user.get("LAST_NAME"), user.get("NAME"), user.get("SECOND_NAME")) if part and part.strip())


class BitrixClient:
    def __init__(self, webhook_url: str | None, timeout: float = 10.0) -> None:
        self._base = webhook_url.rstrip("/") + "/" if webhook_url else None
        self._timeout = timeout

    @property
    def configured(self) -> bool:
        return self._base is not None

    def _call(self, method: str, params: dict) -> dict:
        request = urllib.request.Request(
            f"{self._base}{method}.json", data=json.dumps(params).encode("utf-8"),
            headers={"Content-Type": "application/json", "Accept": "application/json"}, method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self._timeout) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError, ValueError) as exc:
            raise BitrixError() from exc
        if not isinstance(payload, dict) or payload.get("error"):
            raise BitrixError()
        return payload

    def _list_all(self, method: str, params: dict) -> list[dict]:
        rows, start = [], 0
        for _ in range(_MAX_PAGES):
            payload = self._call(method, {**params, "start": start})
            rows.extend(payload.get("result") or [])
            if payload.get("next") is None:
                return rows
            start = payload["next"]
        logger.warning("Bitrix pagination for %s hit page cap", method)
        return rows

    def fetch_employees(self) -> list[Employee]:
        if not self.configured:
            return list(STUB_EMPLOYEES)
        try:
            departments = {str(row["ID"]): row for row in self._list_all("department.get", {}) if row.get("ID") is not None}
            users = self._list_all("user.get", {"ACTIVE": True, "SORT": "LAST_NAME", "ORDER": "asc"})
        except BitrixError:
            raise
        return [self._employee_from_user(user, departments) for user in users]

    @staticmethod
    def _employee_from_user(user: dict, departments: dict[str, dict]) -> Employee:
        ids = user.get("UF_DEPARTMENT") or []
        if not isinstance(ids, list):
            ids = [ids]
        department = departments.get(str(ids[0])) if ids else None
        root = department
        seen = set()
        while root and root.get("PARENT") and str(root.get("PARENT")) not in seen:
            seen.add(str(root.get("ID")))
            root = departments.get(str(root["PARENT"]))
        return Employee(
            bitrix_id=str(user["ID"]), full_name=_full_name(user) or f"ID {user['ID']}",
            position=user.get("WORK_POSITION") or None,
            company=root.get("NAME") if root else None,
            department=department.get("NAME") if department else None,
        )
