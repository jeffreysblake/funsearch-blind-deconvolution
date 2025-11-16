"""Project database model."""

import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, Enum, String, Text, UUID
from sqlalchemy.orm import relationship

from .base import Base

if TYPE_CHECKING:
    from .experiment import Experiment


class ProjectStatus(str, enum.Enum):
    """Project status enum."""

    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class Project(Base):
    """Project model."""

    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text)
    problem_type = Column(String(50), nullable=False)
    status = Column(
        Enum(ProjectStatus), nullable=False, default=ProjectStatus.DRAFT, index=True
    )
    spec_file_path = Column(String(500), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    experiments = relationship(
        "Experiment", back_populates="project", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Project(id={self.id}, name='{self.name}', status={self.status})>"
