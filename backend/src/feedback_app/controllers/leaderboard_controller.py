from fastapi import APIRouter, Depends, Query
from feedback_app.core.dependencies import get_current_admin, get_idea_service
from feedback_app.models.user import User
from feedback_app.schemas.idea import LeaderboardOut
from feedback_app.services.idea_service import IdeaService

router = APIRouter(prefix="/leaderboard", tags=["leaderboard"])

@router.get("", response_model=LeaderboardOut)
def get_leaderboard(week: str | None = Query(None, pattern=r"^\d{4}-W\d{2}$"), _admin: User = Depends(get_current_admin), service: IdeaService = Depends(get_idea_service)) -> LeaderboardOut:
    return service.leaderboard(week)


@router.get("/history", response_model=list[LeaderboardOut])
def get_leaderboard_history(_admin: User = Depends(get_current_admin), service: IdeaService = Depends(get_idea_service)) -> list[LeaderboardOut]:
    return service.leaderboard_history()
