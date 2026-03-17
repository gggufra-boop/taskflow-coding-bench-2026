"""Task API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.task import TaskPriority, TaskStatus
from app.schemas import TaskCreate, TaskListResponse, TaskResponse, TaskUpdate
from app.services.task_service import (
    InvalidTransitionError,
    ProjectNotFoundError,
    TaskNotFoundError,
    UserNotFoundError,
    create_task,
    delete_task,
    get_project_stats,
    get_task,
    list_tasks,
    update_task,
)

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("/", response_model=TaskResponse, status_code=201)
def create_task_endpoint(task_data: TaskCreate, db: Session = Depends(get_db)):
    """Create a new task."""
    try:
        task = create_task(db, task_data)
        return task
    except ProjectNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/", response_model=TaskListResponse)
def list_tasks_endpoint(
    project_id: int | None = Query(None),
    status: TaskStatus | None = Query(None),
    assignee_id: int | None = Query(None),
    priority: TaskPriority | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """List tasks with optional filters."""
    tasks, total = list_tasks(
        db,
        project_id=project_id,
        status=status,
        assignee_id=assignee_id,
        priority=priority,
        skip=skip,
        limit=limit,
    )
    return TaskListResponse(tasks=tasks, total=total)


@router.get("/{task_id}", response_model=TaskResponse)
def get_task_endpoint(task_id: int, db: Session = Depends(get_db)):
    """Get a single task."""
    try:
        return get_task(db, task_id)
    except TaskNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.patch("/{task_id}", response_model=TaskResponse)
def update_task_endpoint(task_id: int, task_data: TaskUpdate, db: Session = Depends(get_db)):
    """Update a task."""
    try:
        return update_task(db, task_id, task_data)
    except TaskNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InvalidTransitionError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.delete("/{task_id}", status_code=204)
def delete_task_endpoint(task_id: int, db: Session = Depends(get_db)):
    """Delete a task."""
    try:
        delete_task(db, task_id)
    except TaskNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/projects/{project_id}/stats")
def project_stats_endpoint(project_id: int, db: Session = Depends(get_db)):
    """Get task statistics for a project."""
    try:
        return get_project_stats(db, project_id)
    except ProjectNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
