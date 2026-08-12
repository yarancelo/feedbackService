import uuid
from sqlalchemy import select
from sqlalchemy.orm import Session
from feedback_app.models.manual_author import ManualAuthor


class ManualAuthorRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def list(self) -> list[ManualAuthor]:
        return list(self._session.execute(select(ManualAuthor).order_by(ManualAuthor.full_name)).scalars())

    def get(self, author_id: uuid.UUID) -> ManualAuthor | None:
        return self._session.get(ManualAuthor, author_id)

    def find_by_name(self, full_name: str) -> ManualAuthor | None:
        return self._session.execute(select(ManualAuthor).where(ManualAuthor.full_name == full_name)).scalar_one_or_none()

    def add(self, author: ManualAuthor) -> ManualAuthor:
        self._session.add(author); self._session.flush(); self._session.refresh(author); return author
