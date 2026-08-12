from fastapi import APIRouter, Depends, Query

from feedback_app.core.dependencies import get_idea_service
from feedback_app.schemas.idea import IdeaBankOut
from feedback_app.services.idea_service import IdeaService

router = APIRouter(prefix="/idea-bank", tags=["idea bank"])


@router.get("", response_model=IdeaBankOut)
def get_idea_bank(client_key: str | None = Query(None, max_length=64), service: IdeaService = Depends(get_idea_service)) -> IdeaBankOut:
    return service.idea_bank(client_key)
