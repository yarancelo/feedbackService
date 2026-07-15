"""Feedback controller (routes only; delegates to the service)."""
import datetime
import uuid

from fastapi import APIRouter, Depends, Query, status

from feedback_app.core.dependencies import get_current_admin, get_feedback_service
from feedback_app.core.logging import get_logger
from feedback_app.models.user import User
from feedback_app.schemas.feedback import FeedbackCreate, FeedbackOut, FeedbackPage
from feedback_app.services.feedback_service import FeedbackService

logger = get_logger(__name__)
router = APIRouter(prefix="/feedbacks", tags=["feedbacks"])


@router.post("", response_model=FeedbackOut, status_code=status.HTTP_201_CREATED)
def create_feedback(
    payload: FeedbackCreate,
    service: FeedbackService = Depends(get_feedback_service),
) -> FeedbackOut:
    """Public: submit anonymous feedback."""
    logger.info("Public feedback submission received")
    return service.create(payload.topic, payload.body)


@router.get("", response_model=FeedbackPage)
def list_feedbacks(
    _admin: User = Depends(get_current_admin),
    service: FeedbackService = Depends(get_feedback_service),
    page: int = Query(1, ge=1),
    date_from: datetime.datetime | None = Query(None),
    date_to: datetime.datetime | None = Query(None),
    order: str = Query("desc", pattern="^(asc|desc)$"),
) -> FeedbackPage:
    """Admin only: paginated (50/page), date-filterable, date-sortable list."""
    logger.debug("Admin listing feedback page=%d order=%s", page, order)
    return service.list_page(page, date_from, date_to, newest_first=(order == "desc"))


@router.delete("/{feedback_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_feedback(
    feedback_id: uuid.UUID,
    _admin: User = Depends(get_current_admin),
    service: FeedbackService = Depends(get_feedback_service),
) -> None:
    """Admin only: delete a feedback item (404 if it does not exist)."""
    logger.info("Admin deleting feedback id=%s", feedback_id)
    service.delete(feedback_id)
