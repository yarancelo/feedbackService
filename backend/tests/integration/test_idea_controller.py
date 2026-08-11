"""Public ideas, admin moderation, wall and leaderboard contracts."""
import datetime

from feedback_app.core.dependencies import get_current_admin, get_idea_service
from feedback_app.integrations.bitrix_client import Employee
from feedback_app.models.idea import IdeaStatus
from feedback_app.services.idea_service import IdeaService
from tests.conftest import FakeIdeaRepository, make_idea, make_user


def _service(repo):
    employees = {"1": Employee("1", "Иван Петров", company="Отель", department="Ресепшен")}
    return IdeaService(repo, employees.get)


def _as_admin(app):
    app.dependency_overrides[get_current_admin] = lambda: make_user()


def test_public_submission_is_anonymous_by_default(app, client):
    app.dependency_overrides[get_idea_service] = lambda: _service(FakeIdeaRepository())
    response = client.post("/api/ideas", json={"body": "Новая идея"})
    assert response.status_code == 201
    assert response.json()["visibility"] == "anonymous"
    assert response.json()["author_name"] is None


def test_named_submission_uses_directory_snapshot(app, client):
    app.dependency_overrides[get_idea_service] = lambda: _service(FakeIdeaRepository())
    response = client.post("/api/ideas", json={"body": "Идея", "visibility": "private", "author_bitrix_id": "1"})
    assert response.status_code == 201
    assert response.json()["author_company"] == "Отель"


def test_admin_moderates_and_wall_masks_private_author(app, client):
    idea = make_idea(visibility="private", author_id="1")
    idea.author_name = "Иван Петров"
    app.dependency_overrides[get_idea_service] = lambda: _service(FakeIdeaRepository([idea]))
    _as_admin(app)
    assert client.patch(f"/api/ideas/{idea.id}/status", json={"status": "accepted"}).status_code == 200
    wall = client.get("/api/wall").json()
    assert wall["total"] == 1
    assert wall["items"][0]["author_name"] is None


def test_admin_endpoints_require_auth(client):
    assert client.get("/api/ideas").status_code in (401, 403)
    assert client.get("/api/leaderboard").status_code in (401, 403)


def test_reaction_is_one_per_browser_and_can_switch(app, client):
    idea = make_idea()
    app.dependency_overrides[get_idea_service] = lambda: _service(FakeIdeaRepository([idea]))
    first = client.post(f"/api/ideas/{idea.id}/reaction", json={"client_key": "browser-1", "value": 1})
    assert first.status_code == 200
    assert first.json()["likes"] == 1
    changed = client.post(f"/api/ideas/{idea.id}/reaction", json={"client_key": "browser-1", "value": -1})
    assert changed.json()["likes"] == 0
    assert changed.json()["dislikes"] == 1


def test_leaderboard_counts_accepted_named_ideas(app, client):
    first = make_idea(status=IdeaStatus.accepted, author_id="1", created_at=datetime.datetime.now(datetime.timezone.utc))
    second = make_idea(status=IdeaStatus.accepted, author_id="1", created_at=datetime.datetime.now(datetime.timezone.utc))
    for item in (first, second):
        item.author_name = "Иван Петров"
    app.dependency_overrides[get_idea_service] = lambda: _service(FakeIdeaRepository([first, second]))
    _as_admin(app)
    result = client.get("/api/leaderboard").json()
    assert result["winners"][0]["accepted_count"] == 2
