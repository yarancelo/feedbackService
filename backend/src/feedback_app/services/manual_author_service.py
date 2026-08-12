import uuid
from fastapi import HTTPException, status
from feedback_app.models.idea import Idea
from feedback_app.models.manual_author import ManualAuthor
from feedback_app.repositories.idea_repository import IdeaRepository
from feedback_app.repositories.manual_author_repository import ManualAuthorRepository
from feedback_app.schemas.manual_author import ManualAuthorUpdate


class ManualAuthorService:
    def __init__(self, authors: ManualAuthorRepository, ideas: IdeaRepository) -> None:
        self._authors = authors; self._ideas = ideas

    def list(self) -> list[ManualAuthor]:
        return self._authors.list()

    def confirm_from_idea(self, idea_id: uuid.UUID) -> ManualAuthor:
        idea = self._ideas.get(idea_id)
        if idea is None or not idea.author_name or idea.author_bitrix_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Для этой идеи нельзя добавить автора вручную.")
        author = self._authors.find_by_name(idea.author_name) or self._authors.add(ManualAuthor(full_name=idea.author_name, company=idea.author_company, department=idea.author_department))
        idea.author_bitrix_id = f"manual:{author.id}"
        return author

    def update(self, author_id: uuid.UUID, payload: ManualAuthorUpdate) -> ManualAuthor:
        author = self._require(author_id)
        for field in ("full_name", "position", "company", "department"):
            value = getattr(payload, field)
            if value is not None:
                setattr(author, field, value.strip() if isinstance(value, str) else value)
        return author

    def as_employee(self, bitrix_id: str):
        if not bitrix_id.startswith("manual:"):
            return None
        try:
            author = self._authors.get(uuid.UUID(bitrix_id.removeprefix("manual:")))
        except ValueError:
            return None
        if author is None:
            return None
        from feedback_app.integrations.bitrix_client import Employee
        return Employee(bitrix_id=bitrix_id, full_name=author.full_name, position=author.position, company=author.company, department=author.department)

    def _require(self, author_id: uuid.UUID) -> ManualAuthor:
        author = self._authors.get(author_id)
        if author is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Автор не найден.")
        return author
