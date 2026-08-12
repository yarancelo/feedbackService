"""Feedback view schemas (request validation + response shape)."""
import datetime
import uuid

from pydantic import BaseModel, ConfigDict, field_validator


class FeedbackCreate(BaseModel):
    """Incoming feedback payload. Topic and body are both required."""

    topic: str
    body: str

    @field_validator("topic", "body")
    @classmethod
    def _reject_blank(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Поле не может быть пустым")
        return cleaned


class FeedbackOut(BaseModel):
    """Feedback as returned to clients."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    topic: str
    body: str
    created_at: datetime.datetime


class FeedbackPage(BaseModel):
    """A single page of feedback plus pagination metadata."""

    items: list[FeedbackOut]
    page: int
    page_size: int
    total: int
    total_pages: int
