"""Shared test fixtures and in-memory fakes.

The fakes let us test services and controllers without a real PostgreSQL
instance (the DB-side uuidv7()/now() defaults require PG18 at runtime).
"""
import datetime
import uuid

import pytest
from fastapi.testclient import TestClient

from feedback_app.models.feedback import Feedback
from feedback_app.models.user import User


# --------------------------- in-memory fakes ---------------------------
class FakeUserRepository:
    """Stand-in for UserRepository backed by a dict."""

    def __init__(self, users=None):
        self._by_login = {}
        self._by_id = {}
        for user in users or []:
            self._by_login[user.login] = user
            self._by_id[user.id] = user

    def get_by_login(self, login):
        return self._by_login.get(login)

    def get_by_id(self, user_id):
        return self._by_id.get(user_id)


class FakeFeedbackRepository:
    """Stand-in for FeedbackRepository backed by a list."""

    def __init__(self, items=None):
        self._items = list(items or [])

    def add(self, feedback):
        if feedback.id is None:
            feedback.id = uuid.uuid4()
        if getattr(feedback, "created_at", None) is None:
            feedback.created_at = datetime.datetime.now(datetime.timezone.utc)
        self._items.append(feedback)
        return feedback

    def get_by_id(self, feedback_id):
        return next((f for f in self._items if f.id == feedback_id), None)

    def delete(self, feedback):
        self._items = [f for f in self._items if f.id != feedback.id]

    def _filtered(self, date_from, date_to):
        result = self._items
        if date_from is not None:
            result = [f for f in result if f.created_at >= date_from]
        if date_to is not None:
            result = [f for f in result if f.created_at <= date_to]
        return result

    def count(self, date_from, date_to):
        return len(self._filtered(date_from, date_to))

    def list(self, *, limit, offset, date_from, date_to, newest_first):
        ordered = sorted(
            self._filtered(date_from, date_to),
            key=lambda f: f.created_at,
            reverse=newest_first,
        )
        return ordered[offset : offset + limit]


# --------------------------- factories ---------------------------
def make_user(login="admin", password="password", user_id=None):
    return User(id=user_id or uuid.uuid4(), login=login, password=password)


def make_feedback(topic="Тема", body="Текст", created_at=None, feedback_id=None):
    fb = Feedback(topic=topic, body=body)
    fb.id = feedback_id or uuid.uuid4()
    fb.created_at = created_at or datetime.datetime.now(datetime.timezone.utc)
    return fb


# --------------------------- fixtures ---------------------------
@pytest.fixture
def admin_user():
    return make_user()


@pytest.fixture
def app():
    from feedback_app.main import create_app

    return create_app()


@pytest.fixture
def client(app):
    """A TestClient with server exceptions surfaced as responses."""
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client
    app.dependency_overrides.clear()
