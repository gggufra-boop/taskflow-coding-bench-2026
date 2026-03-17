"""Pydantic schemas for request/response validation."""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.models.task import TaskPriority, TaskStatus
from app.models.user import UserRole


# ── User schemas ──────────────────────────────────────────────

class UserCreate(BaseModel):
    email: str
    name: str
    role: UserRole = UserRole.MEMBER


class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    role: UserRole
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Project schemas ───────────────────────────────────────────

class ProjectCreate(BaseModel):
    name: str
    description: str | None = None
    slug: str


class ProjectResponse(BaseModel):
    id: int
    name: str
    description: str | None
    slug: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Task schemas ──────────────────────────────────────────────

class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    priority: TaskPriority = TaskPriority.MEDIUM
    project_id: int
    assignee_id: int | None = None
    creator_id: int
    due_date: datetime | None = None


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    assignee_id: int | None = None
    due_date: datetime | None = None


class TaskResponse(BaseModel):
    id: int
    title: str
    description: str | None
    status: TaskStatus
    priority: TaskPriority
    project_id: int
    assignee_id: int | None
    creator_id: int
    created_at: datetime
    updated_at: datetime
    due_date: datetime | None

    model_config = {"from_attributes": True}


class TaskListResponse(BaseModel):
    tasks: list[TaskResponse]
    total: int


# ── Comment schemas ───────────────────────────────────────────

class CommentCreate(BaseModel):
    body: str
    task_id: int
    author_id: int


class CommentUpdate(BaseModel):
    body: str


class CommentResponse(BaseModel):
    id: int
    body: str
    task_id: int
    author_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CommentListResponse(BaseModel):
    comments: list[CommentResponse]
    total: int
