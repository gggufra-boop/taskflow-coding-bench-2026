"""Comment API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import CommentCreate, CommentListResponse, CommentResponse, CommentUpdate
from app.services.comment_service import (
    CommentNotFoundError,
    EmptyCommentBodyError,
    PermissionError,
    TaskNotFoundError,
    UserNotFoundError,
    create_comment,
    delete_comment,
    list_comments,
    update_comment,
)

router = APIRouter(tags=["comments"])


@router.post("/tasks/{task_id}/comments/", response_model=CommentResponse, status_code=201)
def create_comment_endpoint(
    task_id: int, comment_data: CommentCreate, db: Session = Depends(get_db)
):
    """Create a new comment on a task."""
    # Ensure task_id in path matches task_id in body
    if comment_data.task_id != task_id:
        raise HTTPException(
            status_code=400,
            detail=f"Task ID in path ({task_id}) does not match task_id in body ({comment_data.task_id})"
        )
    try:
        comment = create_comment(db, comment_data)
        return comment
    except TaskNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except EmptyCommentBodyError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.get("/tasks/{task_id}/comments/", response_model=CommentListResponse)
def list_comments_endpoint(
    task_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """List comments for a task with pagination."""
    comments, total = list_comments(db, task_id=task_id, skip=skip, limit=limit)
    return CommentListResponse(comments=comments, total=total)


@router.patch("/comments/{comment_id}", response_model=CommentResponse)
def update_comment_endpoint(
    comment_id: int,
    comment_data: CommentUpdate,
    author_id: int = Query(..., description="ID of the user attempting to update the comment"),
    db: Session = Depends(get_db),
):
    """Update a comment. Only the original author can update."""
    try:
        comment = update_comment(db, comment_id, author_id, comment_data)
        return comment
    except CommentNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except EmptyCommentBodyError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.delete("/comments/{comment_id}", status_code=204)
def delete_comment_endpoint(
    comment_id: int,
    author_id: int = Query(..., description="ID of the user attempting to delete the comment"),
    db: Session = Depends(get_db),
):
    """Delete a comment. Only the original author can delete."""
    try:
        delete_comment(db, comment_id, author_id)
    except CommentNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
