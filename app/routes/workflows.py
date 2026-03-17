"""Workflow API endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import WorkflowCreate, WorkflowResponse
from app.services.workflow_service import (
    DuplicateWorkflowNameError,
    InvalidWorkflowDefinitionError,
    WorkflowNotFoundError,
    create_workflow,
    get_workflow,
    list_workflows,
)

router = APIRouter(prefix="/workflows", tags=["workflows"])


@router.post("/", response_model=WorkflowResponse, status_code=201)
def create_workflow_endpoint(workflow_data: WorkflowCreate, db: Session = Depends(get_db)):
    """Create a new workflow."""
    try:
        return create_workflow(db, workflow_data.name, workflow_data.definition)
    except DuplicateWorkflowNameError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except InvalidWorkflowDefinitionError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.get("/", response_model=list[WorkflowResponse])
def list_workflows_endpoint(db: Session = Depends(get_db)):
    """List all workflows."""
    return list_workflows(db)


@router.get("/{workflow_id}", response_model=WorkflowResponse)
def get_workflow_endpoint(workflow_id: int, db: Session = Depends(get_db)):
    """Get a workflow by ID."""
    try:
        return get_workflow(db, workflow_id)
    except WorkflowNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
