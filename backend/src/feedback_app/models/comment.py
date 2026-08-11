"""Anonymous discussion messages attached to accepted ideas."""
import datetime
import uuid

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from feedback_app.core.database import Base
from feedback_app.models.columns import id_column


class IdeaComment(Base):
    __tablename__ = "idea_comments"

    id: Mapped[uuid.UUID] = id_column()
    idea_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ideas.id", ondelete="CASCADE"), nullable=False, index=True)
    client_key: Mapped[str] = mapped_column(String(64), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default="now()")
