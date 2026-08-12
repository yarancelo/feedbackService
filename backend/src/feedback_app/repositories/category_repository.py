import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from feedback_app.models.category import IdeaCategory


class CategoryRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def list(self, active_only: bool = False) -> list[IdeaCategory]:
        stmt = select(IdeaCategory)
        if active_only:
            stmt = stmt.where(IdeaCategory.is_active.is_(True))
        return list(self._session.execute(stmt.order_by(IdeaCategory.sort_order, IdeaCategory.name)).scalars())

    def get(self, category_id: uuid.UUID) -> IdeaCategory | None:
        return self._session.get(IdeaCategory, category_id)

    def add(self, category: IdeaCategory) -> IdeaCategory:
        self._session.add(category)
        self._session.flush()
        self._session.refresh(category)
        return category

    def delete(self, category: IdeaCategory) -> None:
        self._session.delete(category)
