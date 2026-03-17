"""Tests for user endpoints."""


class TestCreateUser:
    def test_create_user_success(self, client):
        resp = client.post("/api/v1/users/", json={
            "email": "bob@example.com",
            "name": "Bob Smith",
            "role": "admin",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["email"] == "bob@example.com"
        assert data["role"] == "admin"

    def test_create_duplicate_email(self, client, sample_user):
        resp = client.post("/api/v1/users/", json={
            "email": "alice@example.com",
            "name": "Alice Clone",
        })
        assert resp.status_code == 409


class TestListUsers:
    def test_list_users(self, client, sample_user):
        resp = client.get("/api/v1/users/")
        assert resp.status_code == 200
        assert len(resp.json()) == 1


class TestGetUser:
    def test_get_user(self, client, sample_user):
        resp = client.get(f"/api/v1/users/{sample_user['id']}")
        assert resp.status_code == 200
        assert resp.json()["name"] == "Alice Johnson"

    def test_get_nonexistent_user(self, client):
        resp = client.get("/api/v1/users/9999")
        assert resp.status_code == 404
