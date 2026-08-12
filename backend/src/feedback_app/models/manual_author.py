import uuid
from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column
from feedback_app.core.database import Base
from feedback_app.models.columns import created_at_column, id_column

class ManualAuthor(Base):
    __tablename__ = 'manual_authors'
    id: Mapped[uuid.UUID] = id_column()
    full_name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    department: Mapped[str | None] = mapped_column(String(255))
    company: Mapped[str | None] = mapped_column(String(255))
    position: Mapped[str | None] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[object] = created_at_column()
