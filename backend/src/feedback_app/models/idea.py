"""Idea domain model."""
import datetime
import enum
import uuid

from sqlalchemy import Boolean, DateTime, Enum, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from feedback_app.core.database import Base
from feedback_app.models.columns import created_at_column, id_column


class Visibility(str, enum.Enum):
    anonymous = "anonymous"
    private = "private"
    public = "public"


class IdeaStatus(str, enum.Enum):
    new = "new"
    accepted = "accepted"
    rejected = "rejected"


class SubmissionType(str, enum.Enum):
    idea = "idea"
    feedback = "feedback"


class Idea(Base):
    """A submitted idea, including an immutable author snapshot."""

    __tablename__ = "ideas"

    id: Mapped[uuid.UUID] = id_column()
    topic: Mapped[str | None] = mapped_column(String(500), nullable=True)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    submission_type: Mapped[SubmissionType] = mapped_column(
        Enum(SubmissionType, native_enum=False), nullable=False, default=SubmissionType.idea
    )
    is_gold: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    visibility: Mapped[Visibility] = mapped_column(Enum(Visibility, native_enum=False), nullable=False)
    status: Mapped[IdeaStatus] = mapped_column(
        Enum(IdeaStatus, native_enum=False), nullable=False, default=IdeaStatus.new
    )
    author_bitrix_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    author_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    author_company: Mapped[str | None] = mapped_column(String(255), nullable=True)
    author_department: Mapped[str | None] = mapped_column(String(255), nullable=True)
    reviewed_at: Mapped[datetime.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    review_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime.datetime] = created_at_column()
