"""End-to-end integration tests."""

import pytest
import time
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.main import app
from backend.models import Base, get_db

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_integration.db"
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


def test_full_experiment_workflow():
    """Test complete workflow: create project -> create experiment -> monitor."""
    # 1. Create a project
    project_response = client.post(
        "/api/v1/projects",
        json={
            "name": "Integration Test Project",
            "description": "Testing end-to-end workflow",
            "problem_type": "optimization",
            "specification": {
                "file_path": "examples/number_sequence/specification.py",
                "evolve_function": "generate_number",
                "evaluate_function": "evaluate",
            },
        },
    )
    assert project_response.status_code == 201
    project_id = project_response.json()["id"]

    # 2. Verify project was created
    get_project_response = client.get(f"/api/v1/projects/{project_id}")
    assert get_project_response.status_code == 200
    assert get_project_response.json()["name"] == "Integration Test Project"

    # 3. Create an experiment (will run in background)
    experiment_response = client.post(
        f"/api/v1/projects/{project_id}/experiments",
        json={
            "name": "Test Experiment",
            "config": {
                "llm": {
                    "provider": "mock",
                    "temperature": 1.0,
                },
                "sandbox": {
                    "provider": "subprocess",
                },
                "funsearch": {
                    "samples_per_prompt": 2,
                    "num_islands": 2,
                    "reset_period": 1800,
                },
                "execution": {
                    "max_iterations": 10,  # Short test
                },
            },
        },
    )
    assert experiment_response.status_code == 202  # Accepted
    experiment_id = experiment_response.json()["id"]

    # 4. Wait a bit for experiment to start
    time.sleep(2)

    # 5. Check experiment status
    exp_status_response = client.get(f"/api/v1/experiments/{experiment_id}")
    assert exp_status_response.status_code == 200
    exp_data = exp_status_response.json()

    # Should be pending or running
    assert exp_data["status"] in ["pending", "running", "completed"]

    # 6. List experiments for the project
    list_exp_response = client.get(f"/api/v1/projects/{project_id}/experiments")
    assert list_exp_response.status_code == 200
    assert list_exp_response.json()["total"] >= 1


def test_project_crud_workflow():
    """Test complete CRUD workflow for projects."""
    # Create
    create_response = client.post(
        "/api/v1/projects",
        json={
            "name": "CRUD Test",
            "description": "Testing CRUD",
            "problem_type": "synthesis",
            "specification": {
                "file_path": "test.py",
                "evolve_function": "func",
                "evaluate_function": "eval",
            },
        },
    )
    assert create_response.status_code == 201
    project_id = create_response.json()["id"]

    # Read
    read_response = client.get(f"/api/v1/projects/{project_id}")
    assert read_response.status_code == 200
    assert read_response.json()["name"] == "CRUD Test"

    # Update
    update_response = client.put(
        f"/api/v1/projects/{project_id}",
        json={
            "name": "CRUD Test Updated",
            "description": "Updated description",
        },
    )
    assert update_response.status_code == 200
    assert update_response.json()["name"] == "CRUD Test Updated"

    # Verify update persisted
    verify_response = client.get(f"/api/v1/projects/{project_id}")
    assert verify_response.json()["description"] == "Updated description"

    # Delete
    delete_response = client.delete(f"/api/v1/projects/{project_id}")
    assert delete_response.status_code == 204

    # Verify deletion
    get_deleted_response = client.get(f"/api/v1/projects/{project_id}")
    assert get_deleted_response.status_code == 404


def test_models_endpoint():
    """Test models listing endpoint."""
    response = client.get("/api/v1/models")
    assert response.status_code == 200

    data = response.json()
    assert "models" in data
    assert len(data["models"]) > 0


def test_templates_endpoint():
    """Test templates listing endpoint."""
    response = client.get("/api/v1/templates")
    assert response.status_code == 200

    data = response.json()
    assert "templates" in data
    assert len(data["templates"]) >= 3  # We have 3 built-in templates


def test_template_detail_endpoint():
    """Test getting template details."""
    response = client.get("/api/v1/templates/algorithm_synthesis")
    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "algorithm_synthesis"
    assert "description" in data
    assert "config_template" in data


def test_pagination():
    """Test pagination in project listing."""
    # Create multiple projects
    for i in range(5):
        client.post(
            "/api/v1/projects",
            json={
                "name": f"Project {i}",
                "description": f"Project number {i}",
                "problem_type": "optimization",
                "specification": {
                    "file_path": f"test{i}.py",
                    "evolve_function": "func",
                    "evaluate_function": "eval",
                },
            },
        )

    # Test pagination
    response = client.get("/api/v1/projects?limit=2&offset=0")
    assert response.status_code == 200
    data = response.json()
    assert len(data["projects"]) == 2
    assert data["total"] == 5

    # Get next page
    response2 = client.get("/api/v1/projects?limit=2&offset=2")
    assert response2.status_code == 200
    data2 = response2.json()
    assert len(data2["projects"]) == 2

    # Ensure different results
    assert data["projects"][0]["id"] != data2["projects"][0]["id"]
