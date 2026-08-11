import uuid

from fastapi import HTTPException, status

from feedback_app.models.comment import IdeaComment
from feedback_app.models.idea import IdeaStatus
from feedback_app.repositories.comment_repository import CommentRepository
from feedback_app.repositories.idea_repository import IdeaRepository
from feedback_app.schemas.comment import CommentCreate


class CommentService:
    def __init__(self, comments: CommentRepository, ideas: IdeaRepository) -> None:
        self._comments = comments
        self._ideas = ideas

    def list(self, idea_id: uuid.UUID) -> list[IdeaComment]:
        self._accepted_idea(idea_id)
        return self._comments.list_for_idea(idea_id)

    def create(self, idea_id: uuid.UUID, payload: CommentCreate) -> IdeaComment:
        self._accepted_idea(idea_id)
        return self._comments.add(IdeaComment(idea_id=idea_id, client_key=payload.client_key, body=payload.body))

    def _accepted_idea(self, idea_id: uuid.UUID) -> None:
        idea = self._ideas.get(idea_id)
        if idea is None or idea.status != IdeaStatus.accepted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Идея не найдена")
