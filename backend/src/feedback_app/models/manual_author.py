"""Locally confirmed authors not present in the Bitrix directory."""
import uuid

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from feedback_app.core.database import Base
from feedback_app.models.columns import id_column


class ManualAuthor(Base):
    __tablename__ = "manual_authors"

    id: Mapped[uuid.UUID] = id_column()
    full_name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    position: Mapped[str | None] = mapped_column(String(255), nullable=True)
    company: Mapped[str | None] = mapped_column(String(255), nullable=True)
    department: Mapped[str | None] = mapped_column(String(255), nullable=True)
