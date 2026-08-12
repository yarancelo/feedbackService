"""Idea submission and moderation HTTP API."""
import datetime
import uuid
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from feedback_app.core.dependencies import get_current_admin, get_db, get_idea_service
from feedback_app.models.idea import Idea, IdeaStatus, SubmissionType
from feedback_app.models.manual_author import ManualAuthor
from feedback_app.models.user import User
from feedback_app.schemas.idea import GoldStatusUpdate, IdeaCreate, IdeaOut, IdeaPage, IdeaStatusUpdate, ReactionUpdate
from feedback_app.services.idea_service import IdeaService

router = APIRouter(prefix="/ideas", tags=["ideas"])

@router.post("", response_model=IdeaOut, status_code=status.HTTP_201_CREATED)
def create_idea(payload: IdeaCreate, service: IdeaService = Depends(get_idea_service)) -> IdeaOut:
    return service.create(payload)

@router.get("", response_model=IdeaPage)
def list_ideas(_admin: User = Depends(get_current_admin), service: IdeaService = Depends(get_idea_service), page: int = Query(1, ge=1), status: IdeaStatus | None = None, category: str | None = None, date_from: datetime.datetime | None = None, date_to: datetime.datetime | None = None, submission_type: SubmissionType = SubmissionType.idea) -> IdeaPage:
    return service.list_page(page, status=status, category=category, date_from=date_from, date_to=date_to, submission_type=submission_type)

@router.patch("/{idea_id}/status", response_model=IdeaOut)
def update_status(idea_id: uuid.UUID, payload: IdeaStatusUpdate, _admin: User = Depends(get_current_admin), service: IdeaService = Depends(get_idea_service)) -> IdeaOut:
    return service.update_status(idea_id, payload)


@router.patch("/{idea_id}/gold", response_model=IdeaOut)
def update_gold_status(idea_id: uuid.UUID, payload: GoldStatusUpdate, _admin: User = Depends(get_current_admin), service: IdeaService = Depends(get_idea_service)) -> IdeaOut:
    return service.update_gold_status(idea_id, payload)


@router.post("/{idea_id}/confirm-author", response_model=IdeaOut)
def confirm_manual_author(idea_id: uuid.UUID, _admin: User = Depends(get_current_admin), db: Session = Depends(get_db)) -> IdeaOut:
    """Add a typed author to the local directory after an admin review."""
    idea = db.get(Idea, idea_id)
    if not idea:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    if not idea.author_name or idea.author_bitrix_id:
        raise HTTPException(status_code=409, detail="Автор уже подтвержден или не указан")
    full_name = idea.author_name.strip()
    author = db.query(ManualAuthor).filter_by(full_name=full_name).first()
    if not author:
        author = ManualAuthor(full_name=full_name, department=idea.author_department, company=idea.author_company)
        db.add(author)
        db.flush()
    idea.author_bitrix_id = f"manual:{author.id}"
    db.flush()
    return IdeaOut.model_validate(idea)

@router.delete("/{idea_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_idea(idea_id: uuid.UUID, _admin: User = Depends(get_current_admin), service: IdeaService = Depends(get_idea_service)) -> None:
    service.delete(idea_id)


@router.post("/{idea_id}/reaction", response_model=IdeaOut)
def react_to_idea(idea_id: uuid.UUID, payload: ReactionUpdate, service: IdeaService = Depends(get_idea_service)) -> IdeaOut:
    """Public, browser-scoped reaction. A new choice replaces the prior one."""
    return service.react(idea_id, payload.client_key, payload.value)
