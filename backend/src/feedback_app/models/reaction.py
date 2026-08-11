"""One browser reaction per idea."""
import uuid

from sqlalchemy import CheckConstraint, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from feedback_app.core.database import Base
from feedback_app.models.columns import id_column
from feedback_app.models.types import GUID


class IdeaReaction(Base):
    __tablename__ = "idea_reactions"
    __table_args__ = (
        UniqueConstraint("idea_id", "client_key", name="uq_idea_reactions_idea_client"),
        CheckConstraint("value IN (-1, 1)", name="ck_idea_reactions_value"),
    )

    id: Mapped[uuid.UUID] = id_column()
    idea_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("ideas.id", ondelete="CASCADE"), nullable=False)
    client_key: Mapped[str] = mapped_column(String(64), nullable=False)
    value: Mapped[int] = mapped_column(Integer, nullable=False)
