import datetime
import uuid

from pydantic import BaseModel, ConfigDict, field_validator


class CommentCreate(BaseModel):
    client_key: str
    body: str

    @field_validator("client_key")
    @classmethod
    def valid_client_key(cls, value: str) -> str:
        value = value.strip()
        if not value or len(value) > 64:
            raise ValueError("Invalid browser identifier")
        return value

    @field_validator("body")
    @classmethod
    def valid_body(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Комментарий не может быть пустым")
        if len(value) > 2_000:
            raise ValueError("Комментарий слишком длинный")
        return value


class CommentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    body: str
    created_at: datetime.datetime
