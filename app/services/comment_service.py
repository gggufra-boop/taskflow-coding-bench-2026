"""Business logic for comment operations."""

from datetime import datetime

from sqlalchemy.orm import Session

from app.models.comment import Comment
from app.models.task import Task
from app.models.user import User
from app.schemas import CommentCreate, CommentUpdate


class CommentNotFoundError(Exception):
    pass


class TaskNotFoundError(Exception):
    pass


class UserNotFoundError(Exception):
    pass


class PermissionError(Exception):
    """Raised when a user tries to modify a comment they don't own."""
    pass


class EmptyCommentBodyError(Exception):
    """Raised when comment body is empty."""
    pass


def _validate_comment_body(body: str) -> None:
    """Ensure the comment body is not empty."""
    if not body or not body.strip():
        raise EmptyCommentBodyError("Comment body cannot be empty")


def create_comment(db: Session, comment_data: CommentCreate) -> Comment:
    """Create a new comment after validating task and author exist."""
    # Validate comment body is not empty
    _validate_comment_body(comment_data.body)

    # Verify task exists
    task = db.query(Task).filter(Task.id == comment_data.task_id).first()
    if not task:
        raise TaskNotFoundError(f"Task with id {comment_data.task_id} not found")

    # Verify author exists
    author = db.query(User).filter(User.id == comment_data.author_id).first()
    if not author:
        raise UserNotFoundError(f"User with id {comment_data.author_id} not found")

    comment = Comment(**comment_data.model_dump())
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


def get_comment(db: Session, comment_id: int) -> Comment:
    """Get a single comment by ID."""
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise CommentNotFoundError(f"Comment with id {comment_id} not found")
    return comment


def list_comments(
    db: Session,
    task_id: int,
    skip: int = 0,
    limit: int = 50,
) -> tuple[list[Comment], int]:
    """List comments for a task with pagination, ordered by created_at ascending."""
    query = db.query(Comment).filter(Comment.task_id == task_id)
    total = query.count()
    comments = query.order_by(Comment.created_at.asc()).offset(skip).limit(limit).all()
    return comments, total


def update_comment(
    db: Session, comment_id: int, author_id: int, data: CommentUpdate
) -> Comment:
    """Update a comment. Only the original author can edit their comment."""
    comment = get_comment(db, comment_id)

    # Check permission - only original author can edit
    if comment.author_id != author_id:
        raise PermissionError("Only the original author can edit this comment")

    # Validate comment body is not empty
    _validate_comment_body(data.body)

    comment.body = data.body
    comment.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(comment)
    return comment


def delete_comment(db: Session, comment_id: int, author_id: int) -> None:
    """Delete a comment. Only the original author can delete their comment."""
    comment = get_comment(db, comment_id)

    # Check permission - only original author can delete
    if comment.author_id != author_id:
        raise PermissionError("Only the original author can delete this comment")

    db.delete(comment)
    db.commit()
