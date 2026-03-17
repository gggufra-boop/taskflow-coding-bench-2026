# Feature: Add Task Comments System

## Summary

Add a commenting system to tasks. Users should be able to add comments to tasks, list comments on a task, and delete their own comments. This is a core collaboration feature that touches models, schemas, services, routes, and tests.

## Requirements

### 1. Data Model (`app/models/comment.py`)
- Create a `Comment` model with:
  - `id` (Integer, primary key)
  - `body` (Text, required, non-empty)
  - `task_id` (ForeignKey to tasks.id, required)
  - `author_id` (ForeignKey to users.id, required)
  - `created_at` (DateTime, auto-set)
  - `updated_at` (DateTime, auto-set on create and update)
- Add appropriate relationships to the `Task` and `User` models
- Export the model from `app/models/__init__.py`

### 2. Schemas (`app/schemas.py`)
- `CommentCreate`: body (str), task_id (int), author_id (int)
- `CommentUpdate`: body (str)
- `CommentResponse`: all fields including author_id, task_id, timestamps
- `CommentListResponse`: list of comments + total count

### 3. Service Layer (`app/services/comment_service.py`)
- `create_comment(db, comment_data)` — validate that both the task and author exist before creating
- `list_comments(db, task_id, skip, limit)` — paginated, ordered by created_at ascending (oldest first)
- `update_comment(db, comment_id, author_id, data)` — only the original author can edit their comment; raise a `PermissionError` (custom exception) if someone else tries
- `delete_comment(db, comment_id, author_id)` — only the original author can delete their comment; same permission check
- Define appropriate custom exceptions (CommentNotFoundError, etc.)

### 4. API Routes (`app/routes/comments.py`)
- `POST /api/v1/tasks/{task_id}/comments/` — create a comment on a task
- `GET /api/v1/tasks/{task_id}/comments/` — list comments for a task (paginated)
- `PATCH /api/v1/comments/{comment_id}` — update a comment (pass author_id in body or query)
- `DELETE /api/v1/comments/{comment_id}` — delete a comment (pass author_id as query param)
- Register the router in `app/main.py`
- Use proper HTTP status codes (201 for create, 204 for delete, 403 for permission denied, 404 for not found)

### 5. Tests (`tests/test_comments.py`)
Write comprehensive tests covering:
- Creating a comment on an existing task
- Creating a comment with invalid task_id (404)
- Creating a comment with invalid author_id (404)
- Listing comments for a task (check ordering and pagination)
- Updating a comment by the original author (succeeds)
- Attempting to update a comment by a different user (403)
- Deleting a comment by the original author (succeeds)
- Attempting to delete a comment by a different user (403)
- Deleting a nonexistent comment (404)

### 6. Constraints
- All existing tests (23 tests in `tests/`) MUST continue to pass
- Follow the same patterns used in the existing codebase (service layer exceptions, HTTP error mapping, etc.)
- Do NOT modify any existing model fields or break existing API contracts
- The comment body must not be empty — validate this and return 422 if it is
