"""Idea rules: author snapshots, moderation, wall and weekly ranking."""
import datetime
import math
import uuid
from zoneinfo import ZoneInfo

from fastapi import HTTPException, status

from feedback_app.core.exceptions import IdeaNotFoundError, UnknownAuthorError
from feedback_app.integrations.bitrix_client import Employee
from feedback_app.models.idea import Idea, IdeaStatus, SubmissionType, Visibility
from feedback_app.repositories.idea_repository import IdeaRepository
from feedback_app.schemas.idea import GoldStatusUpdate, IdeaBankOut, IdeaBankWeek, IdeaCreate, IdeaPage, IdeaStatusUpdate, LeaderboardEntry, LeaderboardOut

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
            visibility=payload.visibility, submission_type=payload.submission_type, status=IdeaStatus.new,
            author_bitrix_id=author.bitrix_id if author else None,
            author_name=author.full_name if author else (payload.author_name or None),
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
        if payload.status != IdeaStatus.accepted:
            idea.is_gold = False
        idea.review_note = payload.review_note
        idea.reviewed_at = datetime.datetime.now(datetime.timezone.utc)
        return idea

    def delete(self, idea_id: uuid.UUID) -> None:
        self._repository.delete(self._require(idea_id))

    def update_gold_status(self, idea_id: uuid.UUID, payload: GoldStatusUpdate) -> Idea:
        idea = self._require(idea_id)
        if not payload.is_gold:
            idea.is_gold = False
            return idea
        if idea.status != IdeaStatus.accepted or idea.submission_type != SubmissionType.idea:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Золотой статус можно присвоить только принятому предложению")
        tz = ZoneInfo("Europe/Moscow")
        local_time = idea.created_at.astimezone(tz)
        week_start = (local_time - datetime.timedelta(days=local_time.isoweekday() - 1)).replace(hour=0, minute=0, second=0, microsecond=0)
        week_end = week_start + datetime.timedelta(days=7)
        same_week = self._repository.list(
            limit=10_000, offset=0, status=IdeaStatus.accepted, submission_type=SubmissionType.idea,
            date_from=week_start.astimezone(datetime.timezone.utc), date_to=week_end.astimezone(datetime.timezone.utc),
        )
        has_other_gold = any(item.is_gold and item.id != idea.id for item in same_week)
        if has_other_gold and not payload.override_week_limit:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="За эту неделю уже есть золотое предложение. Подтвердите добавление второго.")
        idea.is_gold = True
        return idea

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
        idea.comments_count = self._repository.comment_count(idea.id)
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
                                      date_from=start.astimezone(datetime.timezone.utc), date_to=end.astimezone(datetime.timezone.utc), submission_type=SubmissionType.idea)
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

    def leaderboard_history(self) -> list[LeaderboardOut]:
        """Calculate weekly leaders for every week that contains eligible proposals."""
        tz = ZoneInfo("Europe/Moscow")
        accepted = self._repository.list(limit=10_000, offset=0, status=IdeaStatus.accepted, submission_type=SubmissionType.idea)
        grouped: dict[str, list[Idea]] = {}
        for idea in accepted:
            if idea.author_bitrix_id:
                grouped.setdefault(idea.created_at.astimezone(tz).strftime("%G-W%V"), []).append(idea)
        result: list[LeaderboardOut] = []
        for week in sorted(grouped, reverse=True):
            by_author: dict[str, list[Idea]] = {}
            for idea in grouped[week]:
                by_author.setdefault(idea.author_bitrix_id or "", []).append(idea)
            ranked = sorted(by_author.values(), key=lambda xs: (-len(xs), max(x.created_at for x in xs), xs[0].author_name or ""))
            best_count = len(ranked[0])
            result.append(LeaderboardOut(week=week, winners=[LeaderboardEntry(
                author_bitrix_id=xs[0].author_bitrix_id, author_name=xs[0].author_name or "",
                author_company=xs[0].author_company, author_department=xs[0].author_department,
                accepted_count=len(xs), deciding_idea_created_at=max(x.created_at for x in xs),
            ) for xs in ranked if len(xs) == best_count]))
        return result

    def idea_bank(self, client_key: str | None = None) -> IdeaBankOut:
        """Return ideas written by the weekly winners, grouped by Moscow ISO week."""
        tz = ZoneInfo("Europe/Moscow")
        accepted = self._repository.list(limit=10_000, offset=0, status=IdeaStatus.accepted, submission_type=SubmissionType.idea)
        weeks: dict[str, list[Idea]] = {}
        for idea in accepted:
            if not idea.is_gold:
                continue
            local_time = idea.created_at.astimezone(tz)
            key = local_time.strftime("%G-W%V")
            weeks.setdefault(key, []).append(idea)
        result: list[IdeaBankWeek] = []
        for key in sorted(weeks, reverse=True):
            ideas = weeks[key]
            monday = datetime.datetime.fromisocalendar(int(key[:4]), int(key[-2:]), 1).date()
            sunday = monday + datetime.timedelta(days=6)
            result.append(IdeaBankWeek(
                week=key,
                title=f"{monday.strftime('%d.%m.%Y')} по {sunday.strftime('%d.%m.%Y')}",
                winner_names=sorted({idea.author_name or "Анонимно" for idea in ideas}),
                ideas=[self._present(idea, client_key) for idea in ideas],
            ))
        return IdeaBankOut(weeks=result)

    def _require(self, idea_id: uuid.UUID) -> Idea:
        idea = self._repository.get(idea_id)
        if idea is None:
            raise IdeaNotFoundError()
        return idea
