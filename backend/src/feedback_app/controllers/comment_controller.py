import uuid

from fastapi import APIRouter, Depends, status

from feedback_app.core.dependencies import get_comment_service
from feedback_app.schemas.comment import CommentCreate, CommentOut
from feedback_app.services.comment_service import CommentService

router = APIRouter(prefix="/ideas/{idea_id}/comments", tags=["comments"])


@router.get("", response_model=list[CommentOut])
def list_comments(idea_id: uuid.UUID, service: CommentService = Depends(get_comment_service)) -> list[CommentOut]:
    return service.list(idea_id)


@router.post("", response_model=CommentOut, status_code=status.HTTP_201_CREATED)
def create_comment(idea_id: uuid.UUID, payload: CommentCreate, service: CommentService = Depends(get_comment_service)) -> CommentOut:
    return service.create(idea_id, payload)
