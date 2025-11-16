"""Tests for project API endpoints."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.main import app
from backend.models import Base, get_db

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    """Create test database before each test and drop after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_create_project():
    """Test creating a new project."""
    response = client.post(
        "/api/v1/projects",
        json={
            "name": "Test Project",
            "description": "A test project",
            "problem_type": "optimization",
            "specification": {
                "file_path": "examples/knapsack/specification.py",
                "evolve_function": "priority",
                "evaluate_function": "evaluate",
            },
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Project"
    assert data["description"] == "A test project"
    assert data["problem_type"] == "optimization"
    assert "id" in data


def test_list_projects():
    """Test listing projects."""
    # Create a project first
    client.post(
        "/api/v1/projects",
        json={
            "name": "Project 1",
            "description": "First project",
            "problem_type": "optimization",
            "specification": {
                "file_path": "test.py",
                "evolve_function": "func",
                "evaluate_function": "eval",
            },
        },
    )

    # List projects
    response = client.get("/api/v1/projects")
    assert response.status_code == 200

    data = response.json()
    assert data["total"] == 1
    assert len(data["projects"]) == 1
    assert data["projects"][0]["name"] == "Project 1"


def test_get_project():
    """Test getting a single project."""
    # Create project
    create_response = client.post(
        "/api/v1/projects",
        json={
            "name": "Get Test",
            "description": "Test",
            "problem_type": "synthesis",
            "specification": {
                "file_path": "test.py",
                "evolve_function": "func",
                "evaluate_function": "eval",
            },
        },
    )
    project_id = create_response.json()["id"]

    # Get project
    response = client.get(f"/api/v1/projects/{project_id}")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == project_id
    assert data["name"] == "Get Test"


def test_get_nonexistent_project():
    """Test getting a project that doesn't exist."""
    response = client.get("/api/v1/projects/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


def test_update_project():
    """Test updating a project."""
    # Create project
    create_response = client.post(
        "/api/v1/projects",
        json={
            "name": "Original Name",
            "description": "Original",
            "problem_type": "optimization",
            "specification": {
                "file_path": "test.py",
                "evolve_function": "func",
                "evaluate_function": "eval",
            },
        },
    )
    project_id = create_response.json()["id"]

    # Update project
    response = client.put(
        f"/api/v1/projects/{project_id}",
        json={
            "name": "Updated Name",
            "description": "Updated description",
        },
    )
    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "Updated Name"
    assert data["description"] == "Updated description"


def test_delete_project():
    """Test deleting a project."""
    # Create project
    create_response = client.post(
        "/api/v1/projects",
        json={
            "name": "To Delete",
            "description": "Will be deleted",
            "problem_type": "optimization",
            "specification": {
                "file_path": "test.py",
                "evolve_function": "func",
                "evaluate_function": "eval",
            },
        },
    )
    project_id = create_response.json()["id"]

    # Delete project
    response = client.delete(f"/api/v1/projects/{project_id}")
    assert response.status_code == 204

    # Verify it's gone
    get_response = client.get(f"/api/v1/projects/{project_id}")
    assert get_response.status_code == 404


def test_create_project_duplicate_name():
    """Test that duplicate project names are rejected."""
    client.post(
        "/api/v1/projects",
        json={
            "name": "Duplicate",
            "description": "First",
            "problem_type": "optimization",
            "specification": {
                "file_path": "test.py",
                "evolve_function": "func",
                "evaluate_function": "eval",
            },
        },
    )

    # Try to create another with same name
    response = client.post(
        "/api/v1/projects",
        json={
            "name": "Duplicate",
            "description": "Second",
            "problem_type": "optimization",
            "specification": {
                "file_path": "test2.py",
                "evolve_function": "func2",
                "evaluate_function": "eval2",
            },
        },
    )

    assert response.status_code == 400
