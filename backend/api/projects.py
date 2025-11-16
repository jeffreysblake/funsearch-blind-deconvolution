"""Projects API endpoints."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.models import Project, ProjectStatus, get_db

router = APIRouter()


# Request/Response Models
class ProjectBase(BaseModel):
    """Base project fields."""

    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    problem_type: str = Field(..., min_length=1, max_length=50)


class ProjectCreate(ProjectBase):
    """Create new project."""

    specification: dict = Field(
        ..., description="Specification with file_content, evolve_function, evaluate_function"
    )


class ProjectUpdate(BaseModel):
    """Update existing project."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[ProjectStatus] = None


class ProjectResponse(ProjectBase):
    """Project response with metadata."""

    id: UUID
    status: ProjectStatus
    spec_file_path: str
    created_at: datetime
    updated_at: datetime
    experiment_count: int = 0
    best_score: Optional[float] = None

    class Config:
        from_attributes = True


class ProjectListResponse(BaseModel):
    """List of projects with pagination."""

    projects: list[ProjectResponse]
    total: int
    limit: int
    offset: int


# Endpoints


@router.get("/projects", response_model=ProjectListResponse)
async def list_projects(
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=100, description="Page size"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    db: Session = Depends(get_db),
):
    """
    List all projects with optional filtering and pagination.
    """
    query = db.query(Project)

    # Filter by status if provided
    if status:
        try:
            status_enum = ProjectStatus(status)
            query = query.filter(Project.status == status_enum)
        except ValueError:
            raise HTTPException(
                status_code=400, detail=f"Invalid status: {status}"
            )

    # Get total count
    total = query.count()

    # Get paginated results
    projects = query.order_by(Project.created_at.desc()).offset(offset).limit(limit).all()

    # Convert to response models
    project_responses = []
    for project in projects:
        project_responses.append(
            ProjectResponse(
                id=project.id,
                name=project.name,
                description=project.description,
                problem_type=project.problem_type,
                status=project.status,
                spec_file_path=project.spec_file_path,
                created_at=project.created_at,
                updated_at=project.updated_at,
                experiment_count=len(project.experiments),
                best_score=None,  # TODO: Calculate from experiments
            )
        )

    return ProjectListResponse(
        projects=project_responses, total=total, limit=limit, offset=offset
    )


@router.post("/projects", response_model=ProjectResponse, status_code=201)
async def create_project(
    project_data: ProjectCreate, db: Session = Depends(get_db)
):
    """
    Create a new project.
    """
    # Check if project with same name exists
    existing = db.query(Project).filter(Project.name == project_data.name).first()
    if existing:
        raise HTTPException(
            status_code=400, detail=f"Project with name '{project_data.name}' already exists"
        )

    # Create project
    from pathlib import Path

    spec_path = Path(f".funsearch/projects/{project_data.name}/spec.py")
    spec_path.parent.mkdir(parents=True, exist_ok=True)

    # Write specification file
    spec_path.write_text(project_data.specification.get("file_content", ""))

    # Create database record
    project = Project(
        name=project_data.name,
        description=project_data.description,
        problem_type=project_data.problem_type,
        status=ProjectStatus.DRAFT,
        spec_file_path=str(spec_path),
    )

    db.add(project)
    db.commit()
    db.refresh(project)

    return ProjectResponse(
        id=project.id,
        name=project.name,
        description=project.description,
        problem_type=project.problem_type,
        status=project.status,
        spec_file_path=project.spec_file_path,
        created_at=project.created_at,
        updated_at=project.updated_at,
        experiment_count=0,
        best_score=None,
    )


@router.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: UUID, db: Session = Depends(get_db)):
    """
    Get project by ID.
    """
    project = db.query(Project).filter(Project.id == project_id).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return ProjectResponse(
        id=project.id,
        name=project.name,
        description=project.description,
        problem_type=project.problem_type,
        status=project.status,
        spec_file_path=project.spec_file_path,
        created_at=project.created_at,
        updated_at=project.updated_at,
        experiment_count=len(project.experiments),
        best_score=None,  # TODO: Calculate from experiments
    )


@router.patch("/projects/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: UUID, updates: ProjectUpdate, db: Session = Depends(get_db)
):
    """
    Update project.
    """
    project = db.query(Project).filter(Project.id == project_id).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Update fields
    if updates.name is not None:
        # Check for name conflicts
        existing = (
            db.query(Project)
            .filter(Project.name == updates.name, Project.id != project_id)
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=400, detail=f"Project with name '{updates.name}' already exists"
            )
        project.name = updates.name

    if updates.description is not None:
        project.description = updates.description

    if updates.status is not None:
        project.status = updates.status

    project.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(project)

    return ProjectResponse(
        id=project.id,
        name=project.name,
        description=project.description,
        problem_type=project.problem_type,
        status=project.status,
        spec_file_path=project.spec_file_path,
        created_at=project.created_at,
        updated_at=project.updated_at,
        experiment_count=len(project.experiments),
        best_score=None,
    )


@router.delete("/projects/{project_id}", status_code=204)
async def delete_project(project_id: UUID, db: Session = Depends(get_db)):
    """
    Delete project and all associated experiments.
    """
    project = db.query(Project).filter(Project.id == project_id).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Check if there are running experiments
    from backend.models import Experiment, ExperimentStatus

    running_experiments = (
        db.query(Experiment)
        .filter(
            Experiment.project_id == project_id,
            Experiment.status.in_([ExperimentStatus.RUNNING, ExperimentStatus.PENDING]),
        )
        .count()
    )

    if running_experiments > 0:
        raise HTTPException(
            status_code=409, detail="Cannot delete project with running experiments"
        )

    db.delete(project)
    db.commit()

    return None
