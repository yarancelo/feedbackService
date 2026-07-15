"""Data-access for feedback items.

Data level: returns values, performs no pagination arithmetic and raises no
domain exceptions. Query construction lives here; page math lives in the service.
"""
import datetime
import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from feedback_app.core.logging import get_logger
from feedback_app.models.feedback import Feedback

logger = get_logger(__name__)


class FeedbackRepository:
    """CRUD + filtered listing for the feedbacks table."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, feedback: Feedback) -> Feedback:
        """Persist a new feedback and return it with DB-generated fields loaded."""
        logger.debug("Inserting feedback topic=%r", feedback.topic)
        self._session.add(feedback)
        self._session.flush()        # emit INSERT so the DB fills id + created_at
        self._session.refresh(feedback)  # read those server-generated values back
        return feedback

    def get_by_id(self, feedback_id: uuid.UUID) -> Feedback | None:
        """Return the feedback with this id, or None."""
        logger.debug("Fetching feedback id=%s", feedback_id)
        return self._session.get(Feedback, feedback_id)

    def delete(self, feedback: Feedback) -> None:
        """Remove a feedback row."""
        logger.debug("Deleting feedback id=%s", feedback.id)
        self._session.delete(feedback)

    def count(
        self,
        date_from: datetime.datetime | None,
        date_to: datetime.datetime | None,
    ) -> int:
        """Count feedback rows matching the optional date range."""
        stmt = select(func.count()).select_from(Feedback)
        stmt = self._apply_date_filters(stmt, date_from, date_to)
        return self._session.execute(stmt).scalar_one()

    def list(
        self,
        *,
        limit: int,
        offset: int,
        date_from: datetime.datetime | None,
        date_to: datetime.datetime | None,
        newest_first: bool,
    ) -> list[Feedback]:
        """Return one window of feedback rows, ordered by creation date."""
        ordering = Feedback.created_at.desc() if newest_first else Feedback.created_at.asc()
        stmt = select(Feedback)
        stmt = self._apply_date_filters(stmt, date_from, date_to)
        stmt = stmt.order_by(ordering).limit(limit).offset(offset)
        logger.debug("Listing feedback limit=%d offset=%d newest_first=%s", limit, offset, newest_first)
        return list(self._session.execute(stmt).scalars().all())

    @staticmethod
    def _apply_date_filters(stmt, date_from, date_to):
        """Attach optional created_at bounds to a statement."""
        if date_from is not None:
            stmt = stmt.where(Feedback.created_at >= date_from)
        if date_to is not None:
            stmt = stmt.where(Feedback.created_at <= date_to)
        return stmt
