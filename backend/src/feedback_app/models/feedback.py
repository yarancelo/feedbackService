"""Feedback ORM model (the Model layer, feedback entity)."""
import datetime
import uuid

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from feedback_app.core.database import Base
from feedback_app.models.columns import created_at_column, id_column


class Feedback(Base):
    """A single anonymous feedback item."""

    __tablename__ = "feedbacks"

    # id + created_at are generated on the database side on PostgreSQL.
    id: Mapped[uuid.UUID] = id_column()
    topic: Mapped[str] = mapped_column(String(500), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime.datetime] = created_at_column()
