"""Shared test fixtures."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app


@pytest.fixture
def db_session():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestSession()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db_session):
    """Create a test client with overridden DB dependency."""

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def sample_user(client):
    """Create a sample user for testing."""
    resp = client.post("/api/v1/users/", json={
        "email": "alice@example.com",
        "name": "Alice Johnson",
        "role": "member",
    })
    assert resp.status_code == 201
    return resp.json()


@pytest.fixture
def sample_project(client):
    """Create a sample project for testing."""
    resp = client.post("/api/v1/projects/", json={
        "name": "Backend Revamp",
        "description": "Rewrite the legacy backend",
        "slug": "backend-revamp",
    })
    assert resp.status_code == 201
    return resp.json()


@pytest.fixture
def sample_task(client, sample_user, sample_project):
    """Create a sample task for testing."""
    resp = client.post("/api/v1/tasks/", json={
        "title": "Set up CI pipeline",
        "description": "Configure GitHub Actions for the project",
        "priority": "high",
        "project_id": sample_project["id"],
        "creator_id": sample_user["id"],
        "assignee_id": sample_user["id"],
    })
    assert resp.status_code == 201
    return resp.json()
