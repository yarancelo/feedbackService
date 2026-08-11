import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from feedback_app.models.comment import IdeaComment


class CommentRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def list_for_idea(self, idea_id: uuid.UUID) -> list[IdeaComment]:
        stmt = select(IdeaComment).where(IdeaComment.idea_id == idea_id).order_by(IdeaComment.created_at.asc())
        return list(self._session.execute(stmt).scalars())

    def add(self, comment: IdeaComment) -> IdeaComment:
        self._session.add(comment)
        self._session.flush()
        self._session.refresh(comment)
        return comment
