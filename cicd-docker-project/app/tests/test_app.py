import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app as flask_app


@pytest.fixture
def client():
    flask_app.config.update(TESTING=True)
    with flask_app.test_client() as client:
        yield client


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "ok"


def test_get_tasks_returns_seed_data(client):
    resp = client.get("/tasks")
    assert resp.status_code == 200
    tasks = resp.get_json()
    assert isinstance(tasks, list)
    assert len(tasks) >= 3


def test_create_task(client):
    resp = client.post("/tasks", json={"title": "Write report"})
    assert resp.status_code == 201
    body = resp.get_json()
    assert body["title"] == "Write report"
    assert body["done"] is False


def test_create_task_without_title_fails(client):
    resp = client.post("/tasks", json={})
    assert resp.status_code == 400


def test_get_single_task(client):
    create_resp = client.post("/tasks", json={"title": "Temp task"})
    task_id = create_resp.get_json()["id"]

    get_resp = client.get(f"/tasks/{task_id}")
    assert get_resp.status_code == 200
    assert get_resp.get_json()["title"] == "Temp task"


def test_get_missing_task_returns_404(client):
    resp = client.get("/tasks/99999")
    assert resp.status_code == 404


def test_update_task(client):
    create_resp = client.post("/tasks", json={"title": "Old title"})
    task_id = create_resp.get_json()["id"]

    update_resp = client.put(f"/tasks/{task_id}", json={"title": "New title", "done": True})
    assert update_resp.status_code == 200
    body = update_resp.get_json()
    assert body["title"] == "New title"
    assert body["done"] is True


def test_delete_task(client):
    create_resp = client.post("/tasks", json={"title": "Delete me"})
    task_id = create_resp.get_json()["id"]

    delete_resp = client.delete(f"/tasks/{task_id}")
    assert delete_resp.status_code == 200

    get_resp = client.get(f"/tasks/{task_id}")
    assert get_resp.status_code == 404
