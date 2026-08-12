import uuid

from fastapi import HTTPException, status

from feedback_app.models.category import IdeaCategory
from feedback_app.repositories.category_repository import CategoryRepository
from feedback_app.schemas.category import CategoryCreate, CategoryUpdate


class CategoryService:
    def __init__(self, repository: CategoryRepository) -> None:
        self._repository = repository

    def list(self, active_only: bool = False) -> list[IdeaCategory]:
        return self._repository.list(active_only)

    def create(self, payload: CategoryCreate) -> IdeaCategory:
        return self._repository.add(IdeaCategory(name=payload.name))

    def update(self, category_id: uuid.UUID, payload: CategoryUpdate) -> IdeaCategory:
        category = self._require(category_id)
        if payload.name is not None:
            category.name = payload.name
        if payload.is_active is not None:
            category.is_active = payload.is_active
        return category

    def delete(self, category_id: uuid.UUID) -> None:
        self._repository.delete(self._require(category_id))

    def _require(self, category_id: uuid.UUID) -> IdeaCategory:
        category = self._repository.get(category_id)
        if category is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Тема не найдена")
        return category
