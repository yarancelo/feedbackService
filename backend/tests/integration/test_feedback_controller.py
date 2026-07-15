"""Feedback controller: public create, admin list/delete, guards."""
import uuid

from feedback_app.core.dependencies import get_current_admin, get_feedback_service
from feedback_app.services.feedback_service import FeedbackService

from tests.conftest import FakeFeedbackRepository, make_feedback, make_user


def _use_feedback_repo(app, repo):
    app.dependency_overrides[get_feedback_service] = lambda: FeedbackService(repo)


def _as_admin(app):
    app.dependency_overrides[get_current_admin] = lambda: make_user()


# ---- public create ----
def test_create_feedback(app, client):
    _use_feedback_repo(app, FakeFeedbackRepository())
    resp = client.post("/api/feedbacks", json={"topic": "Кофе", "body": "Нужна вторая машина"})
    assert resp.status_code == 201
    body = resp.json()
    assert body["topic"] == "Кофе"
    assert body["id"] and body["created_at"]


def test_create_feedback_blank_rejected(app, client):
    _use_feedback_repo(app, FakeFeedbackRepository())
    resp = client.post("/api/feedbacks", json={"topic": "", "body": "x"})
    assert resp.status_code == 422


# ---- admin list ----
def test_list_requires_auth(client):
    assert client.get("/api/feedbacks").status_code in (401, 403)


def test_list_as_admin(app, client):
    _as_admin(app)
    _use_feedback_repo(app, FakeFeedbackRepository([make_feedback() for _ in range(3)]))
    resp = client.get("/api/feedbacks")
    assert resp.status_code == 200
    assert resp.json()["total"] == 3


# ---- admin delete ----
def test_delete_as_admin(app, client):
    fb = make_feedback()
    _as_admin(app)
    _use_feedback_repo(app, FakeFeedbackRepository([fb]))
    assert client.delete(f"/api/feedbacks/{fb.id}").status_code == 204


def test_delete_missing_returns_404(app, client):
    _as_admin(app)
    _use_feedback_repo(app, FakeFeedbackRepository())
    resp = client.delete(f"/api/feedbacks/{uuid.uuid4()}")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Отзыв не найден"
