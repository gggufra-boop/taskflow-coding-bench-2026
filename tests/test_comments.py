from app.models.comment import Comment


class TestCreateComment:
    def test_create_comment_success(self, client, sample_user, sample_task):
        resp = client.post(f"/api/v1/tasks/{sample_task['id']}/comments/", json={
            "body": "This is a test comment",
            "task_id": sample_task["id"],
            "author_id": sample_user["id"],
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["body"] == "This is a test comment"
        assert data["task_id"] == sample_task["id"]
        assert data["author_id"] == sample_user["id"]
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_comment_invalid_task_id(self, client, sample_user):
        resp = client.post("/api/v1/tasks/9999/comments/", json={
            "body": "Comment on non-existent task",
            "task_id": 9999,
            "author_id": sample_user["id"],
        })
        assert resp.status_code == 404

    def test_create_comment_invalid_author_id(self, client, sample_task):
        resp = client.post(f"/api/v1/tasks/{sample_task['id']}/comments/", json={
            "body": "Comment by non-existent user",
            "task_id": sample_task["id"],
            "author_id": 9999,
        })
        assert resp.status_code == 404

    def test_create_comment_mismatched_task_id(self, client, sample_user, sample_task):
        resp = client.post("/api/v1/tasks/9999/comments/", json={
            "body": "Mismatched task IDs",
            "task_id": sample_task["id"],  # Different from path
            "author_id": sample_user["id"],
        })
        assert resp.status_code == 400

    def test_create_comment_empty_body(self, client, sample_user, sample_task):
        resp = client.post(f"/api/v1/tasks/{sample_task['id']}/comments/", json={
            "body": "",
            "task_id": sample_task["id"],
            "author_id": sample_user["id"],
        })
        assert resp.status_code == 422

    def test_create_comment_whitespace_only_body(self, client, sample_user, sample_task):
        resp = client.post(f"/api/v1/tasks/{sample_task['id']}/comments/", json={
            "body": "   ",
            "task_id": sample_task["id"],
            "author_id": sample_user["id"],
        })
        assert resp.status_code == 422


class TestListComments:
    def test_list_comments_empty(self, client, sample_task):
        resp = client.get(f"/api/v1/tasks/{sample_task['id']}/comments/")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 0
        assert data["comments"] == []

    def test_list_comments_with_data(self, client, sample_user, sample_task):
        # Create a few comments
        comment1 = client.post(f"/api/v1/tasks/{sample_task['id']}/comments/", json={
            "body": "First comment",
            "task_id": sample_task["id"],
            "author_id": sample_user["id"],
        })
        assert comment1.status_code == 201
        
        comment2 = client.post(f"/api/v1/tasks/{sample_task['id']}/comments/", json={
            "body": "Second comment",
            "task_id": sample_task["id"],
            "author_id": sample_user["id"],
        })
        assert comment2.status_code == 201

        # List comments
        resp = client.get(f"/api/v1/tasks/{sample_task['id']}/comments/")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 2
        assert len(data["comments"]) == 2
        
        # Check ordering (oldest first)
        assert data["comments"][0]["body"] == "First comment"
        assert data["comments"][1]["body"] == "Second comment"

    def test_list_comments_pagination(self, client, sample_user, sample_task):
        # Create multiple comments
        for i in range(5):
            resp = client.post(f"/api/v1/tasks/{sample_task['id']}/comments/", json={
                "body": f"Comment {i}",
                "task_id": sample_task["id"],
                "author_id": sample_user["id"],
            })
            assert resp.status_code == 201

        # Test pagination
        resp = client.get(f"/api/v1/tasks/{sample_task['id']}/comments/", params={"skip": 1, "limit": 2})
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 5
        assert len(data["comments"]) == 2
        assert data["comments"][0]["body"] == "Comment 1"
        assert data["comments"][1]["body"] == "Comment 2"


class TestUpdateComment:
    def test_update_comment_success(self, client, sample_user, sample_task):
        # Create a comment
        resp = client.post(f"/api/v1/tasks/{sample_task['id']}/comments/", json={
            "body": "Original comment",
            "task_id": sample_task["id"],
            "author_id": sample_user["id"],
        })
        assert resp.status_code == 201
        comment_id = resp.json()["id"]

        # Update the comment
        resp = client.patch(f"/api/v1/comments/{comment_id}", params={"author_id": sample_user["id"]}, json={
            "body": "Updated comment"
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["body"] == "Updated comment"
        assert data["id"] == comment_id

    def test_update_comment_by_different_user(self, client, sample_user, sample_task):
        # Create another user
        other_user = client.post("/api/v1/users/", json={
            "email": "bob@example.com",
            "name": "Bob Smith",
            "role": "member",
        })
        assert other_user.status_code == 201
        other_user_id = other_user.json()["id"]

        # Create a comment
        resp = client.post(f"/api/v1/tasks/{sample_task['id']}/comments/", json={
            "body": "Original comment",
            "task_id": sample_task["id"],
            "author_id": sample_user["id"],
        })
        assert resp.status_code == 201
        comment_id = resp.json()["id"]

        # Try to update the comment as different user
        resp = client.patch(f"/api/v1/comments/{comment_id}", params={"author_id": other_user_id}, json={
            "body": "Hijacked comment"
        })
        assert resp.status_code == 403

    def test_update_comment_nonexistent(self, client, sample_user):
        resp = client.patch("/api/v1/comments/9999", params={"author_id": sample_user["id"]}, json={
            "body": "Update non-existent comment"
        })
        assert resp.status_code == 404

    def test_update_comment_empty_body(self, client, sample_user, sample_task):
        # Create a comment
        resp = client.post(f"/api/v1/tasks/{sample_task['id']}/comments/", json={
            "body": "Original comment",
            "task_id": sample_task["id"],
            "author_id": sample_user["id"],
        })
        assert resp.status_code == 201
        comment_id = resp.json()["id"]

        # Try to update with empty body
        resp = client.patch(f"/api/v1/comments/{comment_id}", params={"author_id": sample_user["id"]}, json={
            "body": ""
        })
        assert resp.status_code == 422


class TestDeleteComment:
    def test_delete_comment_success(self, client, sample_user, sample_task):
        # Create a comment
        resp = client.post(f"/api/v1/tasks/{sample_task['id']}/comments/", json={
            "body": "Comment to delete",
            "task_id": sample_task["id"],
            "author_id": sample_user["id"],
        })
        assert resp.status_code == 201
        comment_id = resp.json()["id"]

        # Delete the comment
        resp = client.delete(f"/api/v1/comments/{comment_id}", params={"author_id": sample_user["id"]})
        assert resp.status_code == 204

        # Verify it's gone
        resp = client.get(f"/api/v1/tasks/{sample_task['id']}/comments/")
        data = resp.json()
        assert data["total"] == 0

    def test_delete_comment_by_different_user(self, client, sample_user, sample_task):
        # Create another user
        other_user = client.post("/api/v1/users/", json={
            "email": "bob@example.com",
            "name": "Bob Smith",
            "role": "member",
        })
        assert other_user.status_code == 201
        other_user_id = other_user.json()["id"]

        # Create a comment
        resp = client.post(f"/api/v1/tasks/{sample_task['id']}/comments/", json={
            "body": "Comment to delete",
            "task_id": sample_task["id"],
            "author_id": sample_user["id"],
        })
        assert resp.status_code == 201
        comment_id = resp.json()["id"]

        # Try to delete the comment as different user
        resp = client.delete(f"/api/v1/comments/{comment_id}", params={"author_id": other_user_id})
        assert resp.status_code == 403

    def test_delete_comment_nonexistent(self, client, sample_user):
        resp = client.delete("/api/v1/comments/9999", params={"author_id": sample_user["id"]})
        assert resp.status_code == 404
