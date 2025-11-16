# FunSearch Framework - Database Schema

## Overview

**Database**: SQLite (development) → PostgreSQL (production)
**ORM**: SQLAlchemy 2.0
**Migrations**: Alembic

---

## Schema Diagram

```
┌─────────────────┐
│    projects     │
│─────────────────│
│ id (PK)         │
│ name            │
│ description     │
│ problem_type    │
│ status          │
│ spec_file_path  │
│ created_at      │
│ updated_at      │
└────────┬────────┘
         │
         │ 1:N
         │
┌────────▼────────────────┐
│     experiments         │
│─────────────────────────│
│ id (PK)                 │
│ project_id (FK)         │
│ name                    │
│ status                  │
│ config (JSON)           │
│ started_at              │
│ completed_at            │
│ paused_at               │
│ iterations_completed    │
│ best_score              │
│ best_program            │
│ mlflow_run_id           │
│ task_id                 │
└────────┬────────────────┘
         │
         │ 1:N
         │
┌────────▼─────────────┐       ┌──────────────────┐
│  experiment_metrics  │       │  island_states   │
│──────────────────────│       │──────────────────│
│ id (PK)              │       │ id (PK)          │
│ experiment_id (FK)   │       │ experiment_id (FK)│
│ iteration            │       │ island_id        │
│ timestamp            │       │ iteration        │
│ best_score           │       │ population_size  │
│ avg_score            │       │ best_score       │
│ diversity            │       │ avg_score        │
│ samples_generated    │       │ diversity        │
│ successful_evals     │       │ timestamp        │
└──────────────────────┘       └──────────────────┘

┌──────────────────────┐
│   generated_programs │
│──────────────────────│
│ id (PK)              │
│ experiment_id (FK)   │
│ island_id            │
│ iteration            │
│ code                 │
│ score                │
│ signature            │
│ parent_program_id    │
│ created_at           │
└──────────────────────┘
```

---

## Table Definitions

### `projects`

Stores project configurations and metadata.

```sql
CREATE TABLE projects (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name              VARCHAR(255) NOT NULL UNIQUE,
    description       TEXT,
    problem_type      VARCHAR(50) NOT NULL,
    status            VARCHAR(20) NOT NULL DEFAULT 'draft',
    spec_file_path    VARCHAR(500) NOT NULL,
    created_at        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT projects_status_check
        CHECK (status IN ('draft', 'active', 'paused', 'completed', 'archived'))
);

CREATE INDEX idx_projects_status ON projects(status);
CREATE INDEX idx_projects_created_at ON projects(created_at DESC);
```

**SQLAlchemy Model**:

```python
from sqlalchemy import Column, String, Text, Enum, DateTime, UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

class ProjectStatus(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"

class Project(Base):
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text)
    problem_type = Column(String(50), nullable=False)
    status = Column(Enum(ProjectStatus), nullable=False, default=ProjectStatus.DRAFT, index=True)
    spec_file_path = Column(String(500), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    experiments = relationship("Experiment", back_populates="project", cascade="all, delete-orphan")
```

---

### `experiments`

Stores experiment runs and their configurations.

```sql
CREATE TABLE experiments (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id              UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    name                    VARCHAR(255) NOT NULL,
    status                  VARCHAR(20) NOT NULL DEFAULT 'pending',
    config                  JSONB NOT NULL,
    started_at              TIMESTAMP,
    completed_at            TIMESTAMP,
    paused_at               TIMESTAMP,
    iterations_completed    INTEGER NOT NULL DEFAULT 0,
    best_score              FLOAT,
    best_program            TEXT,
    mlflow_run_id           VARCHAR(100),
    task_id                 VARCHAR(100),
    error_message           TEXT,
    created_at              TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT experiments_status_check
        CHECK (status IN ('pending', 'running', 'paused', 'completed', 'failed', 'stopped')),
    CONSTRAINT experiments_unique_name_per_project
        UNIQUE (project_id, name)
);

CREATE INDEX idx_experiments_project_id ON experiments(project_id);
CREATE INDEX idx_experiments_status ON experiments(status);
CREATE INDEX idx_experiments_started_at ON experiments(started_at DESC);
CREATE INDEX idx_experiments_mlflow_run_id ON experiments(mlflow_run_id);
```

**SQLAlchemy Model**:

```python
from sqlalchemy import Column, String, Text, Integer, Float, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

class ExperimentStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    STOPPED = "stopped"

class Experiment(Base):
    __tablename__ = "experiments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    status = Column(Enum(ExperimentStatus), nullable=False, default=ExperimentStatus.PENDING, index=True)
    config = Column(JSONB, nullable=False)  # Use JSON for SQLite compatibility
    started_at = Column(DateTime, index=True)
    completed_at = Column(DateTime)
    paused_at = Column(DateTime)
    iterations_completed = Column(Integer, nullable=False, default=0)
    best_score = Column(Float)
    best_program = Column(Text)
    mlflow_run_id = Column(String(100), index=True)
    task_id = Column(String(100))
    error_message = Column(Text)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="experiments")
    metrics = relationship("ExperimentMetric", back_populates="experiment", cascade="all, delete-orphan")
    island_states = relationship("IslandState", back_populates="experiment", cascade="all, delete-orphan")
    programs = relationship("GeneratedProgram", back_populates="experiment", cascade="all, delete-orphan")
```

**Config JSON Structure**:

```json
{
  "llm": {
    "provider": "lm_studio",
    "model": "qwen/qwen3-vl-8b",
    "temperature": 1.0,
    "max_tokens": 512
  },
  "sandbox": {
    "provider": "docker",
    "max_workers": 16,
    "timeout": 30,
    "image": "funsearch-sandbox:latest"
  },
  "funsearch": {
    "samples_per_prompt": 4,
    "num_islands": 10,
    "reset_period": 80000,
    "cluster_sampling_temperature_init": 0.1,
    "cluster_sampling_temperature_period": 20000
  },
  "execution": {
    "max_iterations": 100000,
    "checkpoint_interval": 1000
  }
}
```

---

### `experiment_metrics`

Time-series metrics for experiments.

```sql
CREATE TABLE experiment_metrics (
    id                      BIGSERIAL PRIMARY KEY,
    experiment_id           UUID NOT NULL REFERENCES experiments(id) ON DELETE CASCADE,
    iteration               INTEGER NOT NULL,
    timestamp               TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    best_score              FLOAT NOT NULL,
    avg_score               FLOAT,
    diversity               FLOAT,
    samples_generated       INTEGER,
    successful_evaluations  INTEGER,

    CONSTRAINT experiment_metrics_unique_iteration
        UNIQUE (experiment_id, iteration)
);

CREATE INDEX idx_metrics_experiment_id ON experiment_metrics(experiment_id);
CREATE INDEX idx_metrics_iteration ON experiment_metrics(experiment_id, iteration);
CREATE INDEX idx_metrics_timestamp ON experiment_metrics(timestamp);
```

**SQLAlchemy Model**:

```python
from sqlalchemy import Column, BigInteger, Integer, Float, DateTime, ForeignKey, UniqueConstraint

class ExperimentMetric(Base):
    __tablename__ = "experiment_metrics"

    id = Column(BigInteger, primary_key=True)
    experiment_id = Column(UUID(as_uuid=True), ForeignKey("experiments.id", ondelete="CASCADE"), nullable=False, index=True)
    iteration = Column(Integer, nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    best_score = Column(Float, nullable=False)
    avg_score = Column(Float)
    diversity = Column(Float)
    samples_generated = Column(Integer)
    successful_evaluations = Column(Integer)

    # Relationships
    experiment = relationship("Experiment", back_populates="metrics")

    __table_args__ = (
        UniqueConstraint('experiment_id', 'iteration', name='uq_experiment_iteration'),
    )
```

---

### `island_states`

State snapshots of each island population.

```sql
CREATE TABLE island_states (
    id                  BIGSERIAL PRIMARY KEY,
    experiment_id       UUID NOT NULL REFERENCES experiments(id) ON DELETE CASCADE,
    island_id           INTEGER NOT NULL,
    iteration           INTEGER NOT NULL,
    population_size     INTEGER NOT NULL,
    best_score          FLOAT NOT NULL,
    avg_score           FLOAT,
    worst_score         FLOAT,
    diversity           FLOAT,
    num_clusters        INTEGER,
    timestamp           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT island_states_unique
        UNIQUE (experiment_id, island_id, iteration)
);

CREATE INDEX idx_island_states_experiment_id ON island_states(experiment_id);
CREATE INDEX idx_island_states_iteration ON island_states(experiment_id, iteration);
```

**SQLAlchemy Model**:

```python
class IslandState(Base):
    __tablename__ = "island_states"

    id = Column(BigInteger, primary_key=True)
    experiment_id = Column(UUID(as_uuid=True), ForeignKey("experiments.id", ondelete="CASCADE"), nullable=False, index=True)
    island_id = Column(Integer, nullable=False)
    iteration = Column(Integer, nullable=False)
    population_size = Column(Integer, nullable=False)
    best_score = Column(Float, nullable=False)
    avg_score = Column(Float)
    worst_score = Column(Float)
    diversity = Column(Float)
    num_clusters = Column(Integer)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    experiment = relationship("Experiment", back_populates="island_states")

    __table_args__ = (
        UniqueConstraint('experiment_id', 'island_id', 'iteration', name='uq_island_iteration'),
    )
```

---

### `generated_programs`

All programs generated during evolution.

```sql
CREATE TABLE generated_programs (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    experiment_id       UUID NOT NULL REFERENCES experiments(id) ON DELETE CASCADE,
    island_id           INTEGER NOT NULL,
    iteration           INTEGER NOT NULL,
    code                TEXT NOT NULL,
    score               FLOAT,
    signature           VARCHAR(500),
    parent_program_id   UUID REFERENCES generated_programs(id),
    created_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT generated_programs_score_check
        CHECK (score IS NULL OR score > -1e308)
);

CREATE INDEX idx_programs_experiment_id ON generated_programs(experiment_id);
CREATE INDEX idx_programs_score ON generated_programs(experiment_id, score DESC);
CREATE INDEX idx_programs_iteration ON generated_programs(experiment_id, iteration);
CREATE INDEX idx_programs_parent_id ON generated_programs(parent_program_id);
```

**SQLAlchemy Model**:

```python
class GeneratedProgram(Base):
    __tablename__ = "generated_programs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    experiment_id = Column(UUID(as_uuid=True), ForeignKey("experiments.id", ondelete="CASCADE"), nullable=False, index=True)
    island_id = Column(Integer, nullable=False)
    iteration = Column(Integer, nullable=False)
    code = Column(Text, nullable=False)
    score = Column(Float)
    signature = Column(String(500))
    parent_program_id = Column(UUID(as_uuid=True), ForeignKey("generated_programs.id"))
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    experiment = relationship("Experiment", back_populates="programs")
    parent = relationship("GeneratedProgram", remote_side=[id], backref="children")
```

---

## Migrations

### Initial Migration (Alembic)

```python
# alembic/versions/001_initial_schema.py

def upgrade():
    # Create projects table
    op.create_table(
        'projects',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('problem_type', sa.String(50), nullable=False),
        sa.Column('status', sa.Enum('draft', 'active', 'paused', 'completed', 'archived', name='projectstatus'), nullable=False),
        sa.Column('spec_file_path', sa.String(500), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_projects_status', 'projects', ['status'])
    op.create_index('idx_projects_created_at', 'projects', ['created_at'])

    # Create experiments table
    op.create_table(
        'experiments',
        # ... (similar structure)
    )

    # Create metrics tables
    # ...

def downgrade():
    op.drop_table('generated_programs')
    op.drop_table('island_states')
    op.drop_table('experiment_metrics')
    op.drop_table('experiments')
    op.drop_table('projects')
```

---

## Queries

### Common Query Patterns

#### Get Project with Latest Experiments

```python
from sqlalchemy import select
from sqlalchemy.orm import selectinload

stmt = (
    select(Project)
    .where(Project.id == project_id)
    .options(
        selectinload(Project.experiments)
        .selectinload(Experiment.metrics)
    )
)
project = session.execute(stmt).scalar_one()
```

#### Get Running Experiments

```python
stmt = (
    select(Experiment)
    .where(Experiment.status == ExperimentStatus.RUNNING)
    .order_by(Experiment.started_at.desc())
)
running_experiments = session.execute(stmt).scalars().all()
```

#### Get Metrics for Time Range

```python
from datetime import datetime, timedelta

stmt = (
    select(ExperimentMetric)
    .where(
        ExperimentMetric.experiment_id == experiment_id,
        ExperimentMetric.timestamp >= datetime.utcnow() - timedelta(hours=1)
    )
    .order_by(ExperimentMetric.iteration)
)
recent_metrics = session.execute(stmt).scalars().all()
```

#### Get Top Programs by Score

```python
stmt = (
    select(GeneratedProgram)
    .where(GeneratedProgram.experiment_id == experiment_id)
    .order_by(GeneratedProgram.score.desc())
    .limit(10)
)
top_programs = session.execute(stmt).scalars().all()
```

#### Get Island Evolution History

```python
stmt = (
    select(IslandState)
    .where(
        IslandState.experiment_id == experiment_id,
        IslandState.island_id == island_id
    )
    .order_by(IslandState.iteration)
)
island_history = session.execute(stmt).scalars().all()
```

---

## Performance Optimization

### Indexes

All foreign keys have indexes by default. Additional indexes:

```sql
-- Composite index for time-series queries
CREATE INDEX idx_metrics_exp_iter ON experiment_metrics(experiment_id, iteration DESC);

-- Index for program score queries
CREATE INDEX idx_programs_exp_score ON generated_programs(experiment_id, score DESC NULLS LAST);

-- Index for active experiments
CREATE INDEX idx_experiments_active ON experiments(status) WHERE status IN ('running', 'paused');
```

### Partitioning (PostgreSQL)

For large-scale deployments, partition by experiment:

```sql
-- Partition metrics by experiment (range partitioning by experiment_id hash)
CREATE TABLE experiment_metrics_partitioned (
    LIKE experiment_metrics INCLUDING ALL
) PARTITION BY HASH (experiment_id);

-- Create partitions
CREATE TABLE experiment_metrics_p0 PARTITION OF experiment_metrics_partitioned
    FOR VALUES WITH (MODULUS 4, REMAINDER 0);
CREATE TABLE experiment_metrics_p1 PARTITION OF experiment_metrics_partitioned
    FOR VALUES WITH (MODULUS 4, REMAINDER 1);
-- ... etc
```

### Cleanup Strategy

**Archival Policy**:
- Keep raw metrics for 30 days
- Downsample older metrics (every 100th iteration)
- Archive completed experiments after 90 days

```sql
-- Downsample old metrics (run periodically)
DELETE FROM experiment_metrics
WHERE timestamp < NOW() - INTERVAL '30 days'
  AND iteration % 100 != 0;

-- Archive old experiments
UPDATE experiments
SET status = 'archived'
WHERE status = 'completed'
  AND completed_at < NOW() - INTERVAL '90 days';
```

---

## Database Configuration

### SQLite (Development)

```python
# backend/core/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./funsearch.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # SQLite specific
    echo=True  # Log SQL queries in dev
)
```

### PostgreSQL (Production)

```python
DATABASE_URL = "postgresql://user:password@localhost/funsearch"

engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=0,
    pool_pre_ping=True,  # Verify connections before use
    echo=False
)
```

### Connection Pooling

```python
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=3600,  # Recycle connections after 1 hour
)
```

---

## Backup & Recovery

### SQLite Backup

```bash
# Simple file copy (stop app first)
cp funsearch.db funsearch.db.backup

# Online backup (while app running)
sqlite3 funsearch.db ".backup funsearch.db.backup"
```

### PostgreSQL Backup

```bash
# Full database dump
pg_dump -h localhost -U user funsearch > backup.sql

# Compressed backup
pg_dump -h localhost -U user funsearch | gzip > backup.sql.gz

# Restore
psql -h localhost -U user funsearch < backup.sql
```

---

## Testing

### Test Database Setup

```python
# tests/conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

@pytest.fixture
def test_db():
    """Create a fresh test database for each test"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    yield session

    session.close()
    engine.dispose()
```

### Seed Data

```python
# tests/seed_data.py
def create_test_project(session):
    project = Project(
        name="Test Project",
        description="Test description",
        problem_type="optimization",
        status=ProjectStatus.ACTIVE,
        spec_file_path="/tmp/test_spec.py"
    )
    session.add(project)
    session.commit()
    return project
```

---

**Last Updated**: 2025-11-16
**Version**: 1.0
**Status**: Specification
