from fastapi import APIRouter, Depends, Query
from feedback_app.core.dependencies import get_idea_service
from feedback_app.schemas.idea import IdeaPage
from feedback_app.services.idea_service import IdeaService

router = APIRouter(prefix="/wall", tags=["wall"])

@router.get("", response_model=IdeaPage)
def get_wall(page: int = Query(1, ge=1), client_key: str | None = Query(None, max_length=64), service: IdeaService = Depends(get_idea_service)) -> IdeaPage:
    return service.wall(page, client_key)
