"""Request and response schemas for ideas."""
import datetime
import uuid

from pydantic import BaseModel, ConfigDict, field_validator, model_validator

from feedback_app.models.idea import IdeaStatus, Visibility


class IdeaCreate(BaseModel):
    topic: str | None = None
    body: str
    category: str | None = None
    visibility: Visibility = Visibility.anonymous
    author_bitrix_id: str | None = None
    author_name: str | None = None

    @field_validator("topic", "body", "category", "author_name", mode="before")
    @classmethod
    def clean_text(cls, value):
        return value.strip() if isinstance(value, str) else value

    @field_validator("body")
    @classmethod
    def body_required(cls, value: str) -> str:
        if not value:
            raise ValueError("Расскажите, в чём заключается идея.")
        return value

    @model_validator(mode="after")
    def author_matches_visibility(self):
        if self.visibility == Visibility.anonymous and (self.author_bitrix_id or self.author_name):
            raise ValueError("Для анонимной идеи автор не указывается.")
        if self.visibility != Visibility.anonymous and not (self.author_bitrix_id or self.author_name):
            raise ValueError("Выберите автора.")
        return self


class IdeaStatusUpdate(BaseModel):
    status: IdeaStatus
    review_note: str | None = None


class IdeaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    topic: str | None
    body: str
    category: str | None
    visibility: Visibility
    status: IdeaStatus
    author_bitrix_id: str | None
    author_name: str | None
    author_company: str | None
    author_department: str | None
    reviewed_at: datetime.datetime | None
    review_note: str | None
    created_at: datetime.datetime
    likes: int = 0
    dislikes: int = 0
    viewer_reaction: int = 0


class ReactionUpdate(BaseModel):
    client_key: str
    value: int

    @field_validator("client_key")
    @classmethod
    def client_key_is_present(cls, value: str) -> str:
        if not value.strip() or len(value) > 64:
            raise ValueError("Invalid browser identifier")
        return value.strip()

    @field_validator("value")
    @classmethod
    def reaction_is_supported(cls, value: int) -> int:
        if value not in (-1, 0, 1):
            raise ValueError("Reaction must be -1, 0, or 1")
        return value


class IdeaPage(BaseModel):
    items: list[IdeaOut]
    page: int
    page_size: int
    total: int
    total_pages: int


class LeaderboardEntry(BaseModel):
    author_bitrix_id: str
    author_name: str
    author_company: str | None
    author_department: str | None
    accepted_count: int
    deciding_idea_created_at: datetime.datetime


class LeaderboardOut(BaseModel):
    week: str
    winners: list[LeaderboardEntry]
