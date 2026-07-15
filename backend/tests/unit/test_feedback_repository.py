"""FeedbackRepository data-access (mocked SQLAlchemy Session)."""
import datetime
import uuid
from unittest.mock import MagicMock

from feedback_app.repositories.feedback_repository import FeedbackRepository


def test_add_flushes_and_refreshes():
    session = MagicMock()
    repo = FeedbackRepository(session)
    feedback = MagicMock(topic="t")

    result = repo.add(feedback)

    session.add.assert_called_once_with(feedback)
    session.flush.assert_called_once()
    session.refresh.assert_called_once_with(feedback)
    assert result is feedback


def test_get_by_id_delegates():
    session = MagicMock()
    sentinel = object()
    session.get.return_value = sentinel
    assert FeedbackRepository(session).get_by_id(uuid.uuid4()) is sentinel


def test_delete_delegates():
    session = MagicMock()
    feedback = MagicMock()
    FeedbackRepository(session).delete(feedback)
    session.delete.assert_called_once_with(feedback)


def test_count_returns_scalar():
    session = MagicMock()
    session.execute.return_value.scalar_one.return_value = 7
    assert FeedbackRepository(session).count(None, None) == 7


def test_list_returns_scalars():
    session = MagicMock()
    rows = [object(), object()]
    session.execute.return_value.scalars.return_value.all.return_value = rows

    result = FeedbackRepository(session).list(
        limit=50, offset=0, date_from=None, date_to=None, newest_first=True
    )
    assert result == rows


def test_list_with_dates_executes():
    session = MagicMock()
    session.execute.return_value.scalars.return_value.all.return_value = []
    now = datetime.datetime.now(datetime.timezone.utc)

    FeedbackRepository(session).list(
        limit=10, offset=0, date_from=now, date_to=now, newest_first=False
    )
    session.execute.assert_called_once()
