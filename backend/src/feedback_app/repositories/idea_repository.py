"""Data access for ideas."""
import datetime
import uuid

from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from feedback_app.models.idea import Idea, IdeaStatus
from feedback_app.models.reaction import IdeaReaction


class IdeaRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, idea: Idea) -> Idea:
        self._session.add(idea)
        self._session.flush()
        self._session.refresh(idea)
        return idea

    def get(self, idea_id: uuid.UUID) -> Idea | None:
        return self._session.get(Idea, idea_id)

    def delete(self, idea: Idea) -> None:
        self._session.delete(idea)

    def set_reaction(self, idea_id: uuid.UUID, client_key: str, value: int) -> None:
        existing = self._session.execute(select(IdeaReaction).where(IdeaReaction.idea_id == idea_id, IdeaReaction.client_key == client_key)).scalar_one_or_none()
        if value == 0:
            if existing:
                self._session.delete(existing)
            return
        if existing:
            existing.value = value
        else:
            self._session.add(IdeaReaction(idea_id=idea_id, client_key=client_key, value=value))
        self._session.flush()

    def reaction_counts(self, idea_id: uuid.UUID, client_key: str | None = None) -> tuple[int, int, int]:
        likes, dislikes = self._session.execute(select(
            func.coalesce(func.sum(case((IdeaReaction.value == 1, 1), else_=0)), 0),
            func.coalesce(func.sum(case((IdeaReaction.value == -1, 1), else_=0)), 0),
        ).where(IdeaReaction.idea_id == idea_id)).one()
        reaction = 0
        if client_key:
            reaction = self._session.execute(select(IdeaReaction.value).where(IdeaReaction.idea_id == idea_id, IdeaReaction.client_key == client_key)).scalar_one_or_none() or 0
        return int(likes), int(dislikes), reaction

    def list(self, *, limit: int, offset: int, status: IdeaStatus | None = None,
             category: str | None = None, date_from: datetime.datetime | None = None,
             date_to: datetime.datetime | None = None, accepted_only: bool = False, public_only: bool = False) -> list[Idea]:
        stmt = select(Idea)
        stmt = self._filtered(stmt, status, category, date_from, date_to, accepted_only, public_only)
        return list(self._session.execute(stmt.order_by(Idea.created_at.desc()).limit(limit).offset(offset)).scalars())

    def count(self, *, status: IdeaStatus | None = None, category: str | None = None,
              date_from: datetime.datetime | None = None, date_to: datetime.datetime | None = None,
              accepted_only: bool = False, public_only: bool = False) -> int:
        stmt = self._filtered(select(func.count()).select_from(Idea), status, category, date_from, date_to, accepted_only, public_only)
        return self._session.execute(stmt).scalar_one()

    @staticmethod
    def _filtered(stmt, status, category, date_from, date_to, accepted_only, public_only):
        if accepted_only:
            stmt = stmt.where(Idea.status == IdeaStatus.accepted)
        elif status:
            stmt = stmt.where(Idea.status == status)
        if public_only:
            stmt = stmt.where(Idea.status != IdeaStatus.rejected)
        if category:
            stmt = stmt.where(Idea.category == category)
        if date_from:
            stmt = stmt.where(Idea.created_at >= date_from)
        if date_to:
            stmt = stmt.where(Idea.created_at <= date_to)
        return stmt
