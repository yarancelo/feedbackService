"""Feedback business logic.

Owns the rules: what "a page" means, and that deleting a missing item is an
error. Delegates all persistence to the data layer.
"""
import datetime
import math
import uuid

from feedback_app.core.exceptions import FeedbackNotFoundError
from feedback_app.core.logging import get_logger
from feedback_app.models.feedback import Feedback
from feedback_app.repositories.feedback_repository import FeedbackRepository
from feedback_app.schemas.feedback import FeedbackPage

logger = get_logger(__name__)

PAGE_SIZE = 50


class FeedbackService:
    """Create, list (paginated) and delete feedback."""

    def __init__(self, repository: FeedbackRepository) -> None:
        self._repository = repository

    def create(self, topic: str, body: str) -> Feedback:
        """Create a feedback item (id + timestamp assigned by the database)."""
        logger.info("Creating feedback topic=%r", topic)
        feedback = Feedback(topic=topic, body=body)
        return self._repository.add(feedback)

    def list_page(
        self,
        page: int,
        date_from: datetime.datetime | None,
        date_to: datetime.datetime | None,
        newest_first: bool,
    ) -> FeedbackPage:
        """Return one page (50 items) of feedback with pagination metadata."""
        logger.debug("Listing feedback page=%d newest_first=%s", page, newest_first)
        total = self._repository.count(date_from, date_to)
        items = self._repository.list(
            limit=PAGE_SIZE,
            offset=(page - 1) * PAGE_SIZE,
            date_from=date_from,
            date_to=date_to,
            newest_first=newest_first,
        )
        total_pages = math.ceil(total / PAGE_SIZE) if total else 0
        return FeedbackPage(
            items=items,
            page=page,
            page_size=PAGE_SIZE,
            total=total,
            total_pages=total_pages,
        )

    def delete(self, feedback_id: uuid.UUID) -> None:
        """Delete a feedback item, or raise FeedbackNotFoundError."""
        logger.info("Deleting feedback id=%s", feedback_id)
        feedback = self._repository.get_by_id(feedback_id)
        if feedback is None:
            logger.warning("Delete requested for missing feedback id=%s", feedback_id)
            raise FeedbackNotFoundError()
        self._repository.delete(feedback)
