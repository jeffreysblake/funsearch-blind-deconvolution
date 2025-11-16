"""Experiment database model."""

import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, Enum, Float, ForeignKey, Integer, String, Text, UUID
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.orm import relationship

from .base import Base

if TYPE_CHECKING:
    from .project import Project


class ExperimentStatus(str, enum.Enum):
    """Experiment status enum."""

    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    STOPPED = "stopped"


class Experiment(Base):
    """Experiment model."""

    __tablename__ = "experiments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name = Column(String(255), nullable=False)
    status = Column(
        Enum(ExperimentStatus), nullable=False, default=ExperimentStatus.PENDING, index=True
    )
    config = Column(JSON, nullable=False)  # Store entire experiment config as JSON
    started_at = Column(DateTime, index=True)
    completed_at = Column(DateTime)
    paused_at = Column(DateTime)
    iterations_completed = Column(Integer, nullable=False, default=0)
    best_score = Column(Float)
    best_program = Column(Text)
    mlflow_run_id = Column(String(100), index=True)
    task_id = Column(String(100))  # Celery task ID
    error_message = Column(Text)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="experiments")

    def __repr__(self) -> str:
        return f"<Experiment(id={self.id}, name='{self.name}', status={self.status})>"
