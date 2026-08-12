import uuid
from pydantic import BaseModel, ConfigDict, field_validator


class ManualAuthorUpdate(BaseModel):
    full_name: str | None = None
    position: str | None = None
    company: str | None = None
    department: str | None = None

    @field_validator("full_name")
    @classmethod
    def name_is_not_blank(cls, value: str | None) -> str | None:
        if value is None:
            return value
        value = value.strip()
        if not value:
            raise ValueError("Укажите ФИО.")
        return value


class ManualAuthorOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    full_name: str
    position: str | None
    company: str | None
    department: str | None
