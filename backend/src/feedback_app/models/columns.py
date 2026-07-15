"""Column factories that adapt to the configured database dialect.

PostgreSQL: id + created_at are generated on the DB side (uuidv7(), now()).
Other engines (SQLite for local runs): generated app-side as a fallback.
"""
import datetime

from sqlalchemy import DateTime, text
from sqlalchemy.orm import mapped_column

from feedback_app.core.config import settings
from feedback_app.core.ids import uuid7
from feedback_app.models.types import GUID

_IS_POSTGRES = settings.database_url.startswith("postgresql")


def id_column():
    """Primary key UUID column."""
    if _IS_POSTGRES:
        return mapped_column(GUID(), primary_key=True, server_default=text("uuidv7()"))
    return mapped_column(GUID(), primary_key=True, default=uuid7)


def created_at_column():
    """Timezone-aware creation timestamp column."""
    if _IS_POSTGRES:
        return mapped_column(DateTime(timezone=True), nullable=False, server_default=text("now()"))
    return mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.datetime.now(datetime.timezone.utc),
    )
