"""Business logic for task operations."""

from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.models.task import Task, TaskPriority, TaskStatus
from app.models.project import Project
from app.models.user import User
from app.schemas import TaskCreate, TaskUpdate


class TaskNotFoundError(Exception):
    pass


class ProjectNotFoundError(Exception):
    pass


class UserNotFoundError(Exception):
    pass


class InvalidTransitionError(Exception):
    """Raised when a task status transition is not allowed."""
    pass


# Valid status transitions
VALID_TRANSITIONS: dict[TaskStatus, list[TaskStatus]] = {
    TaskStatus.TODO: [TaskStatus.IN_PROGRESS],
    TaskStatus.IN_PROGRESS: [TaskStatus.IN_REVIEW, TaskStatus.TODO],
    TaskStatus.IN_REVIEW: [TaskStatus.DONE, TaskStatus.IN_PROGRESS],
    TaskStatus.DONE: [TaskStatus.TODO],  # reopen
}


def _validate_status_transition(current: TaskStatus, new: TaskStatus) -> None:
    """Ensure the status transition is allowed."""
    allowed = VALID_TRANSITIONS.get(current, [])
    if new not in allowed:
        raise InvalidTransitionError(
            f"Cannot transition from '{current.value}' to '{new.value}'. "
            f"Allowed transitions: {[s.value for s in allowed]}"
        )


def create_task(db: Session, task_data: TaskCreate) -> Task:
    """Create a new task after validating references."""
    # Verify project exists
    project = db.query(Project).filter(Project.id == task_data.project_id).first()
    if not project:
        raise ProjectNotFoundError(f"Project with id {task_data.project_id} not found")

    # Verify creator exists
    creator = db.query(User).filter(User.id == task_data.creator_id).first()
    if not creator:
        raise UserNotFoundError(f"User with id {task_data.creator_id} not found")

    # Verify assignee exists (if provided)
    if task_data.assignee_id:
        assignee = db.query(User).filter(User.id == task_data.assignee_id).first()
        if not assignee:
            raise UserNotFoundError(f"User with id {task_data.assignee_id} not found")

    task = Task(**task_data.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def get_task(db: Session, task_id: int) -> Task:
    """Get a single task by ID."""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise TaskNotFoundError(f"Task with id {task_id} not found")
    return task


def list_tasks(
    db: Session,
    project_id: int | None = None,
    status: TaskStatus | None = None,
    assignee_id: int | None = None,
    priority: TaskPriority | None = None,
    skip: int = 0,
    limit: int = 50,
) -> tuple[list[Task], int]:
    """List tasks with optional filters and pagination."""
    query = db.query(Task)

    if project_id is not None:
        query = query.filter(Task.project_id == project_id)
    if status is not None:
        query = query.filter(Task.status == status)
    if assignee_id is not None:
        query = query.filter(Task.assignee_id == assignee_id)
    if priority is not None:
        query = query.filter(Task.priority == priority)

    total = query.count()
    tasks = query.order_by(Task.created_at.desc()).offset(skip).limit(limit).all()
    return tasks, total


def update_task(db: Session, task_id: int, task_data: TaskUpdate) -> Task:
    """Update a task, enforcing status transition rules."""
    task = get_task(db, task_id)

    update_dict = task_data.model_dump(exclude_unset=True)

    # Validate status transition if status is being changed
    if "status" in update_dict and update_dict["status"] is not None:
        _validate_status_transition(task.status, update_dict["status"])

    for key, value in update_dict.items():
        setattr(task, key, value)

    task.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(task)
    return task


def delete_task(db: Session, task_id: int) -> None:
    """Delete a task."""
    task = get_task(db, task_id)
    db.delete(task)
    db.commit()


def get_project_stats(db: Session, project_id: int) -> dict:
    """Get task count breakdown by status for a project."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise ProjectNotFoundError(f"Project with id {project_id} not found")

    counts = (
        db.query(Task.status, func.count(Task.id))
        .filter(Task.project_id == project_id)
        .group_by(Task.status)
        .all()
    )
    stats = {status.value: 0 for status in TaskStatus}
    for status, count in counts:
        stats[status.value] = count

    stats["total"] = sum(stats.values())
    return stats
