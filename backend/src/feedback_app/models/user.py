"""Administrator ORM model (the Model layer, admin entity)."""
import uuid

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from feedback_app.core.database import Base
from feedback_app.models.columns import id_column


class User(Base):
    """An administrator who can review and moderate feedback."""

    __tablename__ = "users"

    # Generated on the database side on PostgreSQL (uuidv7()).
    id: Mapped[uuid.UUID] = id_column()
    login: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    # Plaintext by requirement: internal-only tool, admins provisioned via the DB.
    password: Mapped[str] = mapped_column(String(255), nullable=False)
