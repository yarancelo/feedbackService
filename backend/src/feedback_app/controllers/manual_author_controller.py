import uuid
from fastapi import APIRouter, Depends
from feedback_app.core.dependencies import get_current_admin, get_manual_author_service
from feedback_app.models.user import User
from feedback_app.schemas.manual_author import ManualAuthorOut, ManualAuthorUpdate
from feedback_app.services.manual_author_service import ManualAuthorService

router = APIRouter(prefix="/manual-authors", tags=["manual authors"])

@router.get("", response_model=list[ManualAuthorOut])
def list_manual_authors(_admin: User = Depends(get_current_admin), service: ManualAuthorService = Depends(get_manual_author_service)):
    return service.list()

@router.post("/from-idea/{idea_id}", response_model=ManualAuthorOut)
def confirm_manual_author(idea_id: uuid.UUID, _admin: User = Depends(get_current_admin), service: ManualAuthorService = Depends(get_manual_author_service)):
    return service.confirm_from_idea(idea_id)

@router.patch("/{author_id}", response_model=ManualAuthorOut)
def update_manual_author(author_id: uuid.UUID, payload: ManualAuthorUpdate, _admin: User = Depends(get_current_admin), service: ManualAuthorService = Depends(get_manual_author_service)):
    return service.update(author_id, payload)
