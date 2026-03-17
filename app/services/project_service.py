"""Business logic for project operations."""

from sqlalchemy.orm import Session

from app.models.project import Project
from app.schemas import ProjectCreate


class ProjectNotFoundError(Exception):
    pass


class DuplicateSlugError(Exception):
    pass


def create_project(db: Session, project_data: ProjectCreate) -> Project:
    """Create a new project."""
    existing = db.query(Project).filter(Project.slug == project_data.slug).first()
    if existing:
        raise DuplicateSlugError(f"Project with slug '{project_data.slug}' already exists")

    project = Project(**project_data.model_dump())
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def get_project(db: Session, project_id: int) -> Project:
    """Get a project by ID."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise ProjectNotFoundError(f"Project with id {project_id} not found")
    return project


def list_projects(db: Session) -> list[Project]:
    """List all projects."""
    return db.query(Project).order_by(Project.name).all()
