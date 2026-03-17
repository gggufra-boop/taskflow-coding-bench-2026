"""Tests for workflow endpoints and business logic."""

import pytest
from app.models.task import TaskStatus


class TestCreateWorkflow:
    def test_create_valid_workflow(self, client):
        """Test creating a valid workflow."""
        resp = client.post("/api/v1/workflows/", json={
            "name": "Custom Workflow",
            "definition": {
                "todo": ["in_progress"],
                "in_progress": ["in_review", "todo"],
                "in_review": ["done", "in_progress"],
                "done": ["todo"]
            }
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "Custom Workflow"
        assert "id" in data
        assert data["definition"]["todo"] == ["in_progress"]

    def test_create_workflow_invalid_status(self, client):
        """Test creating a workflow with invalid status in definition → 422."""
        resp = client.post("/api/v1/workflows/", json={
            "name": "Invalid Workflow",
            "definition": {
                "todo": ["in_progress"],
                "invalid_status": ["done"]  # Invalid status
            }
        })
        assert resp.status_code == 422
        assert "Invalid status" in resp.json()["detail"]

    def test_create_workflow_orphan_target(self, client):
        """Test creating a workflow with orphan target → 422."""
        resp = client.post("/api/v1/workflows/", json={
            "name": "Orphan Workflow",
            "definition": {
                "todo": ["in_progress", "done"],  # done is not a key
                "in_progress": ["todo"]
                # Note: done is referenced but not defined as a key
            }
        })
        assert resp.status_code == 422
        assert "Orphan target" in resp.json()["detail"]

    def test_create_duplicate_workflow_name(self, client):
        """Test creating a workflow with duplicate name."""
        # Create first workflow
        resp = client.post("/api/v1/workflows/", json={
            "name": "Duplicate Name",
            "definition": {
                "todo": ["in_progress"],
                "in_progress": ["todo"]
            }
        })
        assert resp.status_code == 201

        # Try to create second with same name
        resp = client.post("/api/v1/workflows/", json={
            "name": "Duplicate Name",
            "definition": {
                "todo": ["done"],
                "done": ["todo"]
            }
        })
        assert resp.status_code == 409


class TestListWorkflows:
    def test_list_workflows_empty(self, client):
        """Test listing workflows when none exist."""
        resp = client.get("/api/v1/workflows/")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_list_workflows(self, client):
        """Test listing workflows."""
        # Create a workflow first
        client.post("/api/v1/workflows/", json={
            "name": "Workflow A",
            "definition": {"todo": ["done"], "done": ["todo"]}
        })

        resp = client.get("/api/v1/workflows/")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["name"] == "Workflow A"


class TestGetWorkflow:
    def test_get_workflow(self, client):
        """Test getting a workflow by ID."""
        create_resp = client.post("/api/v1/workflows/", json={
            "name": "Get Test Workflow",
            "definition": {"todo": ["done"], "done": ["todo"]}
        })
        workflow_id = create_resp.json()["id"]

        resp = client.get(f"/api/v1/workflows/{workflow_id}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "Get Test Workflow"
        assert data["id"] == workflow_id

    def test_get_nonexistent_workflow(self, client):
        """Test getting a workflow that doesn't exist."""
        resp = client.get("/api/v1/workflows/9999")
        assert resp.status_code == 404


class TestAssignWorkflowToProject:
    def test_assign_workflow_to_project(self, client):
        """Test assigning a workflow to a project."""
        # Create workflow
        wf_resp = client.post("/api/v1/workflows/", json={
            "name": "Project Workflow",
            "definition": {"todo": ["done"], "done": ["todo"]}
        })
        workflow_id = wf_resp.json()["id"]

        # Create project with workflow
        proj_resp = client.post("/api/v1/projects/", json={
            "name": "Workflow Project",
            "slug": "workflow-project",
            "workflow_id": workflow_id
        })
        assert proj_resp.status_code == 201
        assert proj_resp.json()["workflow_id"] == workflow_id


class TestTaskTransitionWithCustomWorkflow:
    def test_custom_workflow_transition(self, client, sample_user):
        """Test task transition using project's custom workflow.
        
        Create workflow → assign to project → create task → verify custom transitions work.
        """
        # Create a custom workflow that allows todo -> done directly
        wf_resp = client.post("/api/v1/workflows/", json={
            "name": "Direct Done Workflow",
            "definition": {
                "todo": ["in_progress", "done"],  # Custom: allow direct todo->done
                "in_progress": ["done", "todo"],
                "done": ["todo"]
            }
        })
        workflow_id = wf_resp.json()["id"]

        # Create project with custom workflow
        proj_resp = client.post("/api/v1/projects/", json={
            "name": "Custom Workflow Project",
            "slug": "custom-wf-project",
            "workflow_id": workflow_id
        })
        project_id = proj_resp.json()["id"]

        # Create task in project
        task_resp = client.post("/api/v1/tasks/", json={
            "title": "Test Task",
            "project_id": project_id,
            "creator_id": sample_user["id"],
        })
        task_id = task_resp.json()["id"]

        # Verify custom transition works: todo -> done (not allowed in default)
        resp = client.patch(f"/api/v1/tasks/{task_id}", json={"status": "done"})
        assert resp.status_code == 200
        assert resp.json()["status"] == "done"

    def test_fallback_to_default_transitions(self, client, sample_project, sample_user):
        """Test that tasks use default transitions when project has no workflow."""
        # Create task in project without workflow (sample_project has no workflow)
        task_resp = client.post("/api/v1/tasks/", json={
            "title": "Fallback Task",
            "project_id": sample_project["id"],
            "creator_id": sample_user["id"],
        })
        task_id = task_resp.json()["id"]
        assert task_resp.status_code == 201

        # Verify default transition: todo -> in_progress (allowed)
        resp = client.patch(f"/api/v1/tasks/{task_id}", json={"status": "in_progress"})
        assert resp.status_code == 200

        # Verify default restriction: todo -> done directly (not allowed in default)
        # First create a new task
        task_resp2 = client.post("/api/v1/tasks/", json={
            "title": "Fallback Task 2",
            "project_id": sample_project["id"],
            "creator_id": sample_user["id"],
        })
        task_id2 = task_resp2.json()["id"]

        # This should fail with default workflow
        resp = client.patch(f"/api/v1/tasks/{task_id2}", json={"status": "done"})
        assert resp.status_code == 422

    def test_custom_workflow_allows_direct_transition(self, client, sample_user):
        """Test custom workflow allows a transition the default doesn't.
        
        Default: todo -> in_progress only
        Custom: todo -> done directly
        """
        # Create custom workflow allowing todo -> done
        wf_resp = client.post("/api/v1/workflows/", json={
            "name": "Quick Done",
            "definition": {
                "todo": ["done"],  # Skip in_progress
                "done": ["todo"]
            }
        })
        workflow_id = wf_resp.json()["id"]

        # Create project with custom workflow
        proj_resp = client.post("/api/v1/projects/", json={
            "name": "Quick Project",
            "slug": "quick-project",
            "workflow_id": workflow_id
        })
        project_id = proj_resp.json()["id"]

        # Create task
        task_resp = client.post("/api/v1/tasks/", json={
            "title": "Quick Task",
            "project_id": project_id,
            "creator_id": sample_user["id"],
        })
        task_id = task_resp.json()["id"]

        # Verify: todo -> done works (would fail with default)
        resp = client.patch(f"/api/v1/tasks/{task_id}", json={"status": "done"})
        assert resp.status_code == 200
        assert resp.json()["status"] == "done"

    def test_custom_workflow_blocks_default_transition(self, client, sample_user):
        """Test custom workflow blocks a transition the default allows.
        
        Default: todo -> in_progress allowed
        Custom: Remove todo -> in_progress
        """
        # Create custom workflow that blocks todo -> in_progress
        wf_resp = client.post("/api/v1/workflows/", json={
            "name": "No Progress",
            "definition": {
                "todo": ["done"],  # No in_progress
                "done": ["todo"]
            }
        })
        workflow_id = wf_resp.json()["id"]

        # Create project with custom workflow
        proj_resp = client.post("/api/v1/projects/", json={
            "name": "Blocked Project",
            "slug": "blocked-project",
            "workflow_id": workflow_id
        })
        project_id = proj_resp.json()["id"]

        # Create task
        task_resp = client.post("/api/v1/tasks/", json={
            "title": "Blocked Task",
            "project_id": project_id,
            "creator_id": sample_user["id"],
        })
        task_id = task_resp.json()["id"]

        # Verify: todo -> in_progress is blocked (would work with default)
        resp = client.patch(f"/api/v1/tasks/{task_id}", json={"status": "in_progress"})
        assert resp.status_code == 422

        # But todo -> done should work
        resp = client.patch(f"/api/v1/tasks/{task_id}", json={"status": "done"})
        assert resp.status_code == 200


class TestWorkflowValidation:
    def test_empty_definition(self, client):
        """Test creating a workflow with empty definition."""
        resp = client.post("/api/v1/workflows/", json={
            "name": "Empty Workflow",
            "definition": {}
        })
        assert resp.status_code == 422
        assert "at least one status" in resp.json()["detail"]

    def test_invalid_target_status(self, client):
        """Test creating a workflow with invalid target in transitions."""
        resp = client.post("/api/v1/workflows/", json={
            "name": "Invalid Target",
            "definition": {
                "todo": ["invalid_target"]
            }
        })
        assert resp.status_code == 422
        assert "Invalid target status" in resp.json()["detail"]

    def test_non_list_transitions(self, client):
        """Test creating a workflow where transitions is not a list."""
        resp = client.post("/api/v1/workflows/", json={
            "name": "Non List",
            "definition": {
                "todo": "in_progress"  # Should be a list
            }
        })
        assert resp.status_code == 422
        assert "must be a list" in resp.json()["detail"]
