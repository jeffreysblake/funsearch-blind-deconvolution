"""Experiments API endpoints."""

import asyncio
import logging
from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.models import Experiment, ExperimentStatus, Project, get_db
from backend.services.experiment_runner import run_experiment

# Try to import Celery
try:
    from backend.tasks.experiments import run_experiment_task, stop_experiment_task
    CELERY_AVAILABLE = True
except ImportError:
    CELERY_AVAILABLE = False

logger = logging.getLogger(__name__)
router = APIRouter()


# Request/Response Models
class ExperimentConfig(BaseModel):
    """Experiment configuration."""

    llm: dict
    sandbox: dict
    funsearch: dict
    execution: dict


class ExperimentCreate(BaseModel):
    """Create new experiment."""

    name: str = Field(..., min_length=1, max_length=255)
    config: ExperimentConfig


class ExperimentResponse(BaseModel):
    """Experiment response."""

    id: UUID
    project_id: UUID
    name: str
    status: ExperimentStatus
    config: dict
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    paused_at: Optional[datetime] = None
    iterations_completed: int
    best_score: Optional[float] = None
    mlflow_run_id: Optional[str] = None
    task_id: Optional[str] = None
    error_message: Optional[str] = None

    class Config:
        from_attributes = True


class ExperimentListResponse(BaseModel):
    """List of experiments."""

    experiments: list[ExperimentResponse]
    total: int


# Endpoints


@router.get("/projects/{project_id}/experiments", response_model=ExperimentListResponse)
async def list_experiments(project_id: UUID, db: Session = Depends(get_db)):
    """
    List all experiments for a project.
    """
    # Verify project exists
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Get experiments
    experiments = (
        db.query(Experiment)
        .filter(Experiment.project_id == project_id)
        .order_by(Experiment.created_at.desc())
        .all()
    )

    return ExperimentListResponse(
        experiments=[
            ExperimentResponse(
                id=exp.id,
                project_id=exp.project_id,
                name=exp.name,
                status=exp.status,
                config=exp.config,
                started_at=exp.started_at,
                completed_at=exp.completed_at,
                paused_at=exp.paused_at,
                iterations_completed=exp.iterations_completed,
                best_score=exp.best_score,
                mlflow_run_id=exp.mlflow_run_id,
                task_id=exp.task_id,
                error_message=exp.error_message,
            )
            for exp in experiments
        ],
        total=len(experiments),
    )


@router.post(
    "/projects/{project_id}/experiments",
    response_model=ExperimentResponse,
    status_code=202,
)
async def create_experiment(
    project_id: UUID,
    experiment_data: ExperimentCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    Create and start a new experiment.

    Returns 202 Accepted as experiment runs asynchronously.
    """
    # Verify project exists
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Verify project has specification file
    if not project.specification_file:
        raise HTTPException(
            status_code=400, detail="Project has no specification file"
        )

    # Create experiment
    experiment = Experiment(
        project_id=project_id,
        name=experiment_data.name,
        status=ExperimentStatus.PENDING,
        config=experiment_data.config.model_dump(),
        iterations_completed=0,
        specification_file=project.specification_file,
    )

    db.add(experiment)
    db.commit()
    db.refresh(experiment)

    # Run experiment in background (Celery if available, otherwise BackgroundTasks)
    if CELERY_AVAILABLE:
        # Use Celery for distributed execution
        task = run_experiment_task.delay(str(experiment.id))
        experiment.task_id = task.id
        db.commit()
        logger.info(f"Experiment {experiment.id} queued with Celery task {task.id}")
    else:
        # Fallback to FastAPI BackgroundTasks
        background_tasks.add_task(run_experiment, experiment.id)
        logger.info(f"Experiment {experiment.id} started with BackgroundTasks")

    return ExperimentResponse(
        id=experiment.id,
        project_id=experiment.project_id,
        name=experiment.name,
        status=experiment.status,
        config=experiment.config,
        started_at=experiment.started_at,
        completed_at=experiment.completed_at,
        paused_at=experiment.paused_at,
        iterations_completed=experiment.iterations_completed,
        best_score=experiment.best_score,
        mlflow_run_id=experiment.mlflow_run_id,
        task_id=experiment.task_id,
        error_message=experiment.error_message,
    )


@router.get("/experiments/{experiment_id}", response_model=ExperimentResponse)
async def get_experiment(experiment_id: UUID, db: Session = Depends(get_db)):
    """
    Get experiment details.
    """
    experiment = db.query(Experiment).filter(Experiment.id == experiment_id).first()

    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")

    return ExperimentResponse(
        id=experiment.id,
        project_id=experiment.project_id,
        name=experiment.name,
        status=experiment.status,
        config=experiment.config,
        started_at=experiment.started_at,
        completed_at=experiment.completed_at,
        paused_at=experiment.paused_at,
        iterations_completed=experiment.iterations_completed,
        best_score=experiment.best_score,
        mlflow_run_id=experiment.mlflow_run_id,
        task_id=experiment.task_id,
        error_message=experiment.error_message,
    )


@router.post("/experiments/{experiment_id}/stop", response_model=ExperimentResponse)
async def stop_experiment(experiment_id: UUID, db: Session = Depends(get_db)):
    """
    Stop a running experiment.
    """
    experiment = db.query(Experiment).filter(Experiment.id == experiment_id).first()

    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")

    if experiment.status not in [ExperimentStatus.RUNNING, ExperimentStatus.PAUSED]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot stop experiment with status: {experiment.status}",
        )

    # Stop experiment (Celery if available)
    if CELERY_AVAILABLE and experiment.task_id:
        try:
            stop_experiment_task.delay(str(experiment_id))
            logger.info(f"Sent stop request for experiment {experiment_id}")
        except Exception as e:
            logger.error(f"Failed to stop Celery task: {e}")

    # Update status
    experiment.status = ExperimentStatus.STOPPED
    experiment.completed_at = datetime.utcnow()

    db.commit()
    db.refresh(experiment)

    return ExperimentResponse(
        id=experiment.id,
        project_id=experiment.project_id,
        name=experiment.name,
        status=experiment.status,
        config=experiment.config,
        started_at=experiment.started_at,
        completed_at=experiment.completed_at,
        paused_at=experiment.paused_at,
        iterations_completed=experiment.iterations_completed,
        best_score=experiment.best_score,
        mlflow_run_id=experiment.mlflow_run_id,
        task_id=experiment.task_id,
        error_message=experiment.error_message,
    )


@router.post("/experiments/{experiment_id}/pause", response_model=ExperimentResponse)
async def pause_experiment(experiment_id: UUID, db: Session = Depends(get_db)):
    """
    Pause a running experiment.
    """
    experiment = db.query(Experiment).filter(Experiment.id == experiment_id).first()

    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")

    if experiment.status != ExperimentStatus.RUNNING:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot pause experiment with status: {experiment.status}",
        )

    # TODO: Pause Celery task
    experiment.status = ExperimentStatus.PAUSED
    experiment.paused_at = datetime.utcnow()

    db.commit()
    db.refresh(experiment)

    return ExperimentResponse(
        id=experiment.id,
        project_id=experiment.project_id,
        name=experiment.name,
        status=experiment.status,
        config=experiment.config,
        started_at=experiment.started_at,
        completed_at=experiment.completed_at,
        paused_at=experiment.paused_at,
        iterations_completed=experiment.iterations_completed,
        best_score=experiment.best_score,
        mlflow_run_id=experiment.mlflow_run_id,
        task_id=experiment.task_id,
        error_message=experiment.error_message,
    )


@router.post("/experiments/{experiment_id}/resume", response_model=ExperimentResponse)
async def resume_experiment(experiment_id: UUID, db: Session = Depends(get_db)):
    """
    Resume a paused experiment.
    """
    experiment = db.query(Experiment).filter(Experiment.id == experiment_id).first()

    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")

    if experiment.status != ExperimentStatus.PAUSED:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot resume experiment with status: {experiment.status}",
        )

    # TODO: Resume Celery task
    experiment.status = ExperimentStatus.RUNNING
    experiment.paused_at = None

    db.commit()
    db.refresh(experiment)

    return ExperimentResponse(
        id=experiment.id,
        project_id=experiment.project_id,
        name=experiment.name,
        status=experiment.status,
        config=experiment.config,
        started_at=experiment.started_at,
        completed_at=experiment.completed_at,
        paused_at=experiment.paused_at,
        iterations_completed=experiment.iterations_completed,
        best_score=experiment.best_score,
        mlflow_run_id=experiment.mlflow_run_id,
        task_id=experiment.task_id,
        error_message=experiment.error_message,
    )
