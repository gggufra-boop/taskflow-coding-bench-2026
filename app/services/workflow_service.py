"""Business logic for workflow operations."""

import json
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.task import TaskStatus
from app.models.workflow import Workflow


class WorkflowNotFoundError(Exception):
    pass


class DuplicateWorkflowNameError(Exception):
    pass


class InvalidWorkflowDefinitionError(Exception):
    pass


def _validate_workflow_definition(definition: dict) -> None:
    """Validate the workflow definition structure.
    
    - The definition must be a dict
    - All keys must be valid TaskStatus values
    - All values must be lists of valid TaskStatus values
    - Every status referenced in any transition list must also exist as a key
    - The definition must include at least one status
    """
    if not isinstance(definition, dict):
        raise InvalidWorkflowDefinitionError("Workflow definition must be a dictionary")
    
    if len(definition) == 0:
        raise InvalidWorkflowDefinitionError("Workflow definition must include at least one status")
    
    # Get valid status values
    valid_statuses = {status.value for status in TaskStatus}
    
    # Validate all keys are valid TaskStatus values
    for key in definition.keys():
        if key not in valid_statuses:
            raise InvalidWorkflowDefinitionError(
                f"Invalid status '{key}' in workflow definition. Must be one of: {valid_statuses}"
            )
    
    # Validate all values are lists of valid TaskStatus values
    # and check for orphan targets
    defined_statuses = set(definition.keys())
    
    for key, transitions in definition.items():
        if not isinstance(transitions, list):
            raise InvalidWorkflowDefinitionError(
                f"Transitions for '{key}' must be a list"
            )
        
        for target in transitions:
            if target not in valid_statuses:
                raise InvalidWorkflowDefinitionError(
                    f"Invalid target status '{target}' in transitions for '{key}'. "
                    f"Must be one of: {valid_statuses}"
                )
            
            # Check for orphan targets - target must be defined as a key
            if target not in defined_statuses:
                raise InvalidWorkflowDefinitionError(
                    f"Orphan target '{target}' in transitions for '{key}' - "
                    f"target status must be defined as a key in the workflow"
                )


def create_workflow(db: Session, name: str, definition: dict) -> Workflow:
    """Create a new workflow with validated definition."""
    # Check for duplicate name
    existing = db.query(Workflow).filter(Workflow.name == name).first()
    if existing:
        raise DuplicateWorkflowNameError(f"Workflow with name '{name}' already exists")
    
    # Validate the definition
    _validate_workflow_definition(definition)
    
    # Create the workflow
    workflow = Workflow(
        name=name,
        definition=json.dumps(definition),
        created_at=datetime.utcnow()
    )
    db.add(workflow)
    db.commit()
    db.refresh(workflow)
    return workflow


def get_workflow(db: Session, workflow_id: int) -> Workflow:
    """Get a workflow by ID."""
    workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not workflow:
        raise WorkflowNotFoundError(f"Workflow with id {workflow_id} not found")
    return workflow


def list_workflows(db: Session) -> list[Workflow]:
    """List all workflows."""
    return db.query(Workflow).order_by(Workflow.name).all()


def get_workflow_definition(db: Session, workflow_id: int) -> dict:
    """Get the parsed definition for a workflow."""
    workflow = get_workflow(db, workflow_id)
    return workflow.get_definition_dict()
