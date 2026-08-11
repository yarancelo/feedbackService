"""Employee directory business logic.

Caches the Bitrix directory in memory with a TTL so we hit Bitrix roughly once a
day (not on every page load). On a Bitrix failure we serve the last good cache if
we have one; only a cold cache surfaces the error.
"""
import datetime
import threading

from feedback_app.core.config import settings
from feedback_app.core.exceptions import BitrixError
from feedback_app.core.logging import get_logger
from feedback_app.integrations.bitrix_client import BitrixClient, Employee

logger = get_logger(__name__)

_lock = threading.Lock()
_cache: dict[str, object] = {"items": None, "fetched_at": None}


def _is_fresh(now: datetime.datetime) -> bool:
    fetched_at = _cache["fetched_at"]
    if fetched_at is None:
        return False
    ttl = datetime.timedelta(minutes=settings.bitrix_cache_ttl_minutes)
    return (now - fetched_at) < ttl


def list_employees(client: BitrixClient, force: bool = False) -> list[Employee]:
    """Return the (cached) employee directory, refreshing from Bitrix when stale."""
    now = datetime.datetime.now(datetime.timezone.utc)
    with _lock:
        if _cache["items"] is not None and _is_fresh(now) and not force:
            logger.debug("Employee directory served from cache")
            return _cache["items"]  # type: ignore[return-value]

        try:
            items = client.fetch_employees()
        except BitrixError:
            if _cache["items"] is not None:
                logger.warning("Bitrix fetch failed; serving stale employee cache")
                return _cache["items"]  # type: ignore[return-value]
            raise

        _cache["items"] = items
        _cache["fetched_at"] = now
        logger.info("Employee directory refreshed (%d entries)", len(items))
        return items


def find_employee(client: BitrixClient, bitrix_id: str | None) -> Employee | None:
    if not bitrix_id:
        return None
    return next((item for item in list_employees(client) if item.bitrix_id == bitrix_id), None)


def clear_cache() -> None:
    """Reset the cache (used by tests)."""
    with _lock:
        _cache["items"] = None
        _cache["fetched_at"] = None
