"""Idea submission and moderation HTTP API."""
import datetime
import uuid
from fastapi import APIRouter, Depends, Query, status

from feedback_app.core.dependencies import get_current_admin, get_idea_service
from feedback_app.models.idea import IdeaStatus
from feedback_app.models.user import User
from feedback_app.schemas.idea import IdeaCreate, IdeaOut, IdeaPage, IdeaStatusUpdate, ReactionUpdate
from feedback_app.services.idea_service import IdeaService

router = APIRouter(prefix="/ideas", tags=["ideas"])

@router.post("", response_model=IdeaOut, status_code=status.HTTP_201_CREATED)
def create_idea(payload: IdeaCreate, service: IdeaService = Depends(get_idea_service)) -> IdeaOut:
    return service.create(payload)

@router.get("", response_model=IdeaPage)
def list_ideas(_admin: User = Depends(get_current_admin), service: IdeaService = Depends(get_idea_service), page: int = Query(1, ge=1), status: IdeaStatus | None = None, category: str | None = None, date_from: datetime.datetime | None = None, date_to: datetime.datetime | None = None) -> IdeaPage:
    return service.list_page(page, status=status, category=category, date_from=date_from, date_to=date_to)

@router.patch("/{idea_id}/status", response_model=IdeaOut)
def update_status(idea_id: uuid.UUID, payload: IdeaStatusUpdate, _admin: User = Depends(get_current_admin), service: IdeaService = Depends(get_idea_service)) -> IdeaOut:
    return service.update_status(idea_id, payload)

@router.delete("/{idea_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_idea(idea_id: uuid.UUID, _admin: User = Depends(get_current_admin), service: IdeaService = Depends(get_idea_service)) -> None:
    service.delete(idea_id)


@router.post("/{idea_id}/reaction", response_model=IdeaOut)
def react_to_idea(idea_id: uuid.UUID, payload: ReactionUpdate, service: IdeaService = Depends(get_idea_service)) -> IdeaOut:
    """Public, browser-scoped reaction. A new choice replaces the prior one."""
    return service.react(idea_id, payload.client_key, payload.value)
