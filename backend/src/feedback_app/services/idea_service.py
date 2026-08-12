"""Idea rules: author snapshots, moderation, wall and weekly ranking."""
import datetime
import math
import uuid
from zoneinfo import ZoneInfo

from feedback_app.core.exceptions import IdeaNotFoundError, UnknownAuthorError
from feedback_app.integrations.bitrix_client import Employee
from feedback_app.models.idea import Idea, IdeaStatus, Visibility
from feedback_app.repositories.idea_repository import IdeaRepository
from feedback_app.schemas.idea import IdeaCreate, IdeaPage, IdeaStatusUpdate, LeaderboardEntry, LeaderboardOut

PAGE_SIZE = 50


class IdeaService:
    def __init__(self, repository: IdeaRepository, employee_lookup) -> None:
        self._repository = repository
        self._employee_lookup = employee_lookup

    def create(self, payload: IdeaCreate) -> Idea:
        author: Employee | None = None
        if payload.visibility != Visibility.anonymous and payload.author_bitrix_id:
            author = self._employee_lookup(payload.author_bitrix_id)
            if author is None:
                raise UnknownAuthorError()
        return self._repository.add(Idea(
            topic=payload.topic or None, body=payload.body, category=payload.category or None,
            visibility=payload.visibility, status=IdeaStatus.new,
            author_bitrix_id=author.bitrix_id if author else None,
            author_name=author.full_name if author else payload.author_name,
            author_company=author.company if author else None,
            author_department=author.department if author else None,
        ))

    def list_page(self, page: int, client_key: str | None = None, **filters) -> IdeaPage:
        total = self._repository.count(**filters)
        items = self._repository.list(limit=PAGE_SIZE, offset=(page - 1) * PAGE_SIZE, **filters)
        return IdeaPage(items=[self._present(item, client_key) for item in items], page=page, page_size=PAGE_SIZE, total=total,
                        total_pages=math.ceil(total / PAGE_SIZE) if total else 0)

    def update_status(self, idea_id: uuid.UUID, payload: IdeaStatusUpdate) -> Idea:
        idea = self._require(idea_id)
        idea.status = payload.status
        idea.review_note = payload.review_note
        idea.reviewed_at = datetime.datetime.now(datetime.timezone.utc)
        return idea

    def delete(self, idea_id: uuid.UUID) -> None:
        self._repository.delete(self._require(idea_id))

    def wall(self, page: int, client_key: str | None = None) -> IdeaPage:
        result = self.list_page(page, client_key=client_key, public_only=True)
        for idea in result.items:
            idea.author_bitrix_id = None
            if idea.visibility != Visibility.public:
                idea.author_name = idea.author_company = idea.author_department = None
        return result

    def react(self, idea_id: uuid.UUID, client_key: str, value: int):
        idea = self._require(idea_id)
        if idea.status == IdeaStatus.rejected:
            raise IdeaNotFoundError()
        self._repository.set_reaction(idea_id, client_key, value)
        return self._present(idea, client_key)

    def _present(self, idea: Idea, client_key: str | None = None):
        likes, dislikes, reaction = self._repository.reaction_counts(idea.id, client_key)
        idea.likes, idea.dislikes, idea.viewer_reaction = likes, dislikes, reaction
        return idea

    def leaderboard(self, week: str | None) -> LeaderboardOut:
        tz = ZoneInfo("Europe/Moscow")
        if week:
            year, number = week.split("-W")
            start = datetime.datetime.fromisocalendar(int(year), int(number), 1).replace(tzinfo=tz)
        else:
            now = datetime.datetime.now(tz)
            start = (now - datetime.timedelta(days=now.isoweekday() - 1)).replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + datetime.timedelta(days=7)
        ideas = self._repository.list(limit=10000, offset=0, status=IdeaStatus.accepted,
                                      date_from=start.astimezone(datetime.timezone.utc), date_to=end.astimezone(datetime.timezone.utc))
        groups: dict[str, list[Idea]] = {}
        for idea in ideas:
            if idea.author_bitrix_id:
                groups.setdefault(idea.author_bitrix_id, []).append(idea)
        ranked = sorted(groups.values(), key=lambda xs: (-len(xs), max(x.created_at for x in xs), xs[0].author_name or ""))
        if not ranked:
            return LeaderboardOut(week=start.strftime("%G-W%V"), winners=[])
        max_count = len(ranked[0])
        return LeaderboardOut(week=start.strftime("%G-W%V"), winners=[LeaderboardEntry(
            author_bitrix_id=xs[0].author_bitrix_id, author_name=xs[0].author_name or "",
            author_company=xs[0].author_company, author_department=xs[0].author_department,
            accepted_count=len(xs), deciding_idea_created_at=max(x.created_at for x in xs),
        ) for xs in ranked if len(xs) == max_count])

    def _require(self, idea_id: uuid.UUID) -> Idea:
        idea = self._repository.get(idea_id)
        if idea is None:
            raise IdeaNotFoundError()
        return idea
