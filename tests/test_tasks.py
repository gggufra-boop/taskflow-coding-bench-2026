"""Tests for task endpoints and business logic."""

import pytest
from app.models.task import TaskStatus


class TestCreateTask:
    def test_create_task_success(self, client, sample_user, sample_project):
        resp = client.post("/api/v1/tasks/", json={
            "title": "Write README",
            "priority": "low",
            "project_id": sample_project["id"],
            "creator_id": sample_user["id"],
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["title"] == "Write README"
        assert data["status"] == "todo"
        assert data["priority"] == "low"

    def test_create_task_invalid_project(self, client, sample_user):
        resp = client.post("/api/v1/tasks/", json={
            "title": "Orphan task",
            "project_id": 9999,
            "creator_id": sample_user["id"],
        })
        assert resp.status_code == 404

    def test_create_task_invalid_creator(self, client, sample_project):
        resp = client.post("/api/v1/tasks/", json={
            "title": "Ghost task",
            "project_id": sample_project["id"],
            "creator_id": 9999,
        })
        assert resp.status_code == 404


class TestListTasks:
    def test_list_empty(self, client):
        resp = client.get("/api/v1/tasks/")
        assert resp.status_code == 200
        assert resp.json()["total"] == 0

    def test_list_with_filters(self, client, sample_task, sample_user, sample_project):
        resp = client.get("/api/v1/tasks/", params={"project_id": sample_project["id"]})
        assert resp.status_code == 200
        assert resp.json()["total"] == 1

        resp = client.get("/api/v1/tasks/", params={"status": "in_progress"})
        assert resp.json()["total"] == 0


class TestUpdateTask:
    def test_update_title(self, client, sample_task):
        resp = client.patch(f"/api/v1/tasks/{sample_task['id']}", json={
            "title": "Updated title",
        })
        assert resp.status_code == 200
        assert resp.json()["title"] == "Updated title"

    def test_valid_status_transition(self, client, sample_task):
        # todo → in_progress is valid
        resp = client.patch(f"/api/v1/tasks/{sample_task['id']}", json={
            "status": "in_progress",
        })
        assert resp.status_code == 200
        assert resp.json()["status"] == "in_progress"

    def test_invalid_status_transition(self, client, sample_task):
        # todo → done is NOT valid (must go through in_progress first)
        resp = client.patch(f"/api/v1/tasks/{sample_task['id']}", json={
            "status": "done",
        })
        assert resp.status_code == 422

    def test_full_lifecycle(self, client, sample_task):
        """Test a task going through its full lifecycle."""
        tid = sample_task["id"]

        # todo → in_progress
        resp = client.patch(f"/api/v1/tasks/{tid}", json={"status": "in_progress"})
        assert resp.status_code == 200

        # in_progress → in_review
        resp = client.patch(f"/api/v1/tasks/{tid}", json={"status": "in_review"})
        assert resp.status_code == 200

        # in_review → done
        resp = client.patch(f"/api/v1/tasks/{tid}", json={"status": "done"})
        assert resp.status_code == 200
        assert resp.json()["status"] == "done"


class TestDeleteTask:
    def test_delete_task(self, client, sample_task):
        resp = client.delete(f"/api/v1/tasks/{sample_task['id']}")
        assert resp.status_code == 204

        resp = client.get(f"/api/v1/tasks/{sample_task['id']}")
        assert resp.status_code == 404

    def test_delete_nonexistent(self, client):
        resp = client.delete("/api/v1/tasks/9999")
        assert resp.status_code == 404


class TestProjectStats:
    def test_stats_empty_project(self, client, sample_project):
        resp = client.get(f"/api/v1/tasks/projects/{sample_project['id']}/stats")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 0

    def test_stats_with_tasks(self, client, sample_task, sample_project):
        resp = client.get(f"/api/v1/tasks/projects/{sample_project['id']}/stats")
        data = resp.json()
        assert data["total"] == 1
        assert data["todo"] == 1
