"""Pydantic schemas for request/response validation."""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator

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
    workflow_id: int | None = None


class ProjectResponse(BaseModel):
    id: int
    name: str
    description: str | None
    slug: str
    workflow_id: int | None
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Workflow schemas ────────────────────────────────────────

class WorkflowCreate(BaseModel):
    name: str
    definition: dict


class WorkflowResponse(BaseModel):
    id: int
    name: str
    definition: dict
    created_at: datetime

    model_config = {"from_attributes": True}

    @field_validator("definition", mode="before")
    @classmethod
    def parse_definition(cls, v):
        """Parse JSON string to dict if needed."""
        import json
        if isinstance(v, str):
            return json.loads(v)
        return v


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
