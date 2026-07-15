"""FeedbackService business logic (fake repository)."""
import datetime
import uuid

import pytest

from feedback_app.core.exceptions import FeedbackNotFoundError
from feedback_app.services.feedback_service import FeedbackService

from tests.conftest import FakeFeedbackRepository, make_feedback


def test_create_assigns_db_fields():
    service = FeedbackService(FakeFeedbackRepository())
    fb = service.create("Тема", "Текст")
    assert fb.id is not None
    assert fb.created_at is not None


def test_list_page_counts_pages():
    items = [make_feedback() for _ in range(120)]
    service = FeedbackService(FakeFeedbackRepository(items))

    page = service.list_page(1, None, None, newest_first=True)
    assert page.total == 120
    assert page.total_pages == 3      # ceil(120/50)
    assert page.page_size == 50
    assert len(page.items) == 50


def test_list_page_empty():
    page = FeedbackService(FakeFeedbackRepository()).list_page(1, None, None, newest_first=True)
    assert page.total == 0
    assert page.total_pages == 0
    assert page.items == []


def test_list_page_orders_newest_first():
    old = make_feedback(created_at=datetime.datetime(2020, 1, 1, tzinfo=datetime.timezone.utc))
    new = make_feedback(created_at=datetime.datetime(2030, 1, 1, tzinfo=datetime.timezone.utc))
    service = FeedbackService(FakeFeedbackRepository([old, new]))

    newest = service.list_page(1, None, None, newest_first=True)
    assert newest.items[0].id == new.id


def test_delete_existing():
    fb = make_feedback()
    repo = FakeFeedbackRepository([fb])
    FeedbackService(repo).delete(fb.id)
    assert repo.get_by_id(fb.id) is None


def test_delete_missing_raises():
    with pytest.raises(FeedbackNotFoundError):
        FeedbackService(FakeFeedbackRepository()).delete(uuid.uuid4())
