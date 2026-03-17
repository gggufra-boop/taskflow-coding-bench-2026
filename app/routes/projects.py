"""Project API endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import ProjectCreate, ProjectResponse
from app.services.project_service import (
    DuplicateSlugError,
    ProjectNotFoundError,
    create_project,
    get_project,
    list_projects,
)

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("/", response_model=ProjectResponse, status_code=201)
def create_project_endpoint(project_data: ProjectCreate, db: Session = Depends(get_db)):
    """Create a new project."""
    try:
        return create_project(db, project_data)
    except DuplicateSlugError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.get("/", response_model=list[ProjectResponse])
def list_projects_endpoint(db: Session = Depends(get_db)):
    """List all projects."""
    return list_projects(db)


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project_endpoint(project_id: int, db: Session = Depends(get_db)):
    """Get a project by ID."""
    try:
        return get_project(db, project_id)
    except ProjectNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
