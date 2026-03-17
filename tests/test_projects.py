"""Tests for project endpoints."""


class TestCreateProject:
    def test_create_project_success(self, client):
        resp = client.post("/api/v1/projects/", json={
            "name": "Mobile App",
            "description": "iOS and Android app",
            "slug": "mobile-app",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "Mobile App"
        assert data["slug"] == "mobile-app"

    def test_create_duplicate_slug(self, client, sample_project):
        resp = client.post("/api/v1/projects/", json={
            "name": "Another Project",
            "slug": "backend-revamp",
        })
        assert resp.status_code == 409


class TestListProjects:
    def test_list_projects(self, client, sample_project):
        resp = client.get("/api/v1/projects/")
        assert resp.status_code == 200
        assert len(resp.json()) == 1


class TestGetProject:
    def test_get_project(self, client, sample_project):
        resp = client.get(f"/api/v1/projects/{sample_project['id']}")
        assert resp.status_code == 200
        assert resp.json()["slug"] == "backend-revamp"

    def test_get_nonexistent(self, client):
        resp = client.get("/api/v1/projects/9999")
        assert resp.status_code == 404
