# FunSearch Framework - Data Models

## Overview

This document specifies data models for:
- **Backend (Python)**: Pydantic v2 models for API validation
- **Frontend (TypeScript)**: TypeScript interfaces for type safety
- **Shared**: Configuration schemas

---

## Python Models (Pydantic)

### Base Configuration

```python
# backend/models/base.py
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from uuid import UUID
from typing import Optional, Literal

class BaseSchema(BaseModel):
    """Base schema with common configuration"""
    model_config = ConfigDict(
        from_attributes=True,  # Pydantic v2 (was orm_mode)
        populate_by_name=True,
        str_strip_whitespace=True
    )
```

---

### Project Models

```python
# backend/models/project.py
from enum import Enum
from pydantic import Field, field_validator

class ProjectStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"

class ProjectBase(BaseSchema):
    """Base project fields"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    problem_type: str = Field(..., min_length=1, max_length=50)

class ProjectCreate(ProjectBase):
    """Create new project"""
    template: Optional[str] = None
    specification: dict = Field(
        ...,
        description="Specification with file_content, evolve_function, evaluate_function"
    )

    @field_validator('specification')
    @classmethod
    def validate_specification(cls, v):
        required_fields = {'file_content', 'evolve_function', 'evaluate_function'}
        if not all(field in v for field in required_fields):
            raise ValueError(f"Specification must contain: {required_fields}")
        return v

class ProjectUpdate(BaseSchema):
    """Update existing project"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[ProjectStatus] = None

class ProjectResponse(ProjectBase):
    """Project response with metadata"""
    id: UUID
    status: ProjectStatus
    spec_file_path: str
    created_at: datetime
    updated_at: datetime
    experiment_count: int = 0
    best_score: Optional[float] = None

class ProjectDetail(ProjectResponse):
    """Detailed project with experiments"""
    experiments: list["ExperimentResponse"] = []
    config: dict = {}
```

---

### Experiment Models

```python
# backend/models/experiment.py
from typing import Literal

class ExperimentStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    STOPPED = "stopped"

# Configuration sub-models
class LLMConfig(BaseSchema):
    """LLM configuration"""
    provider: Literal["lm_studio", "mock", "template_mock"] = "lm_studio"
    model: str = Field(..., min_length=1)
    base_url: str = "http://localhost:1234/v1"
    temperature: float = Field(1.0, ge=0.0, le=2.0)
    max_tokens: int = Field(512, ge=50, le=4096)
    timeout: int = Field(30, ge=5, le=300)

class SandboxConfig(BaseSchema):
    """Sandbox configuration"""
    provider: Literal["docker", "subprocess", "mock"] = "docker"
    max_workers: int = Field(8, ge=1, le=64)
    timeout: int = Field(30, ge=5, le=300)
    image: str = "funsearch-sandbox:latest"
    limits: dict = {
        "memory": "256m",
        "cpu_cores": 1
    }

class FunSearchConfig(BaseSchema):
    """FunSearch algorithm configuration"""
    samples_per_prompt: int = Field(4, ge=1, le=16)
    num_islands: int = Field(10, ge=1, le=20)
    reset_period: int = Field(80000, ge=1000)
    cluster_sampling_temperature_init: float = Field(0.1, ge=0.01, le=1.0)
    cluster_sampling_temperature_period: int = Field(20000, ge=1000)

class ExecutionConfig(BaseSchema):
    """Execution configuration"""
    max_iterations: int = Field(100000, ge=100)
    checkpoint_interval: int = Field(1000, ge=100)
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"

class ExperimentConfig(BaseSchema):
    """Complete experiment configuration"""
    llm: LLMConfig
    sandbox: SandboxConfig
    funsearch: FunSearchConfig
    execution: ExecutionConfig

# Experiment CRUD models
class ExperimentCreate(BaseSchema):
    """Create new experiment"""
    name: str = Field(..., min_length=1, max_length=255)
    config: ExperimentConfig

class ExperimentResponse(BaseSchema):
    """Experiment response"""
    id: UUID
    project_id: UUID
    name: str
    status: ExperimentStatus
    config: ExperimentConfig
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    paused_at: Optional[datetime] = None
    iterations_completed: int = 0
    best_score: Optional[float] = None
    mlflow_run_id: Optional[str] = None
    task_id: Optional[str] = None

class ExperimentDetail(ExperimentResponse):
    """Detailed experiment with metrics"""
    current_score: Optional[float] = None
    best_program: Optional[str] = None
    metrics: "MetricsTimeSeries" = None
    island_states: list["IslandStateResponse"] = []
    error_message: Optional[str] = None
```

---

### Metrics Models

```python
# backend/models/metrics.py

class MetricPoint(BaseSchema):
    """Single metric data point"""
    iteration: int
    timestamp: datetime
    best_score: float
    avg_score: Optional[float] = None
    diversity: Optional[float] = None
    samples_generated: Optional[int] = None
    successful_evaluations: Optional[int] = None

class MetricsTimeSeries(BaseSchema):
    """Time-series metrics"""
    iterations: list[int]
    best_score: list[float]
    avg_score: list[float]
    diversity: list[float]
    samples_generated: list[int]
    successful_evaluations: list[int]

class IslandStateResponse(BaseSchema):
    """Island state snapshot"""
    island_id: int
    population_size: int
    best_score: float
    avg_score: Optional[float] = None
    worst_score: Optional[float] = None
    diversity: Optional[float] = None
    num_clusters: Optional[int] = None
    timestamp: datetime
    top_programs: list["ProgramResponse"] = []

class ProgramResponse(BaseSchema):
    """Generated program"""
    id: UUID
    score: Optional[float]
    code: str
    signature: Optional[str] = None
    created_at: datetime
```

---

### Model (LLM) Models

```python
# backend/models/llm.py

class ModelInfo(BaseSchema):
    """LLM model information"""
    id: str
    name: str
    size: Optional[str] = None
    type: Optional[str] = None
    loaded: bool = False

class ModelListResponse(BaseSchema):
    """List of available models"""
    models: list[ModelInfo]
    provider: str
    base_url: str
```

---

### Template Models

```python
# backend/models/template.py

class TemplateInfo(BaseSchema):
    """Project template information"""
    id: str
    name: str
    description: str
    example_problems: list[str] = []

class TemplateDetail(TemplateInfo):
    """Detailed template with code"""
    specification_template: str
    default_config: ExperimentConfig
    example: dict = {}
```

---

### WebSocket Models

```python
# backend/models/websocket.py

class WSMessage(BaseSchema):
    """Base WebSocket message"""
    type: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class WSSubscribe(WSMessage):
    """Subscribe to channels"""
    type: Literal["subscribe"] = "subscribe"
    channels: list[str] = ["metrics", "islands", "best_program", "logs"]

class WSMetricsUpdate(WSMessage):
    """Metrics update message"""
    type: Literal["metrics_update"] = "metrics_update"
    data: MetricPoint

class WSBestProgramUpdate(WSMessage):
    """Best program update message"""
    type: Literal["best_program_update"] = "best_program_update"
    data: dict  # Contains iteration, score, improvement, code

class WSStatusChange(WSMessage):
    """Experiment status change"""
    type: Literal["status_change"] = "status_change"
    old_status: ExperimentStatus
    new_status: ExperimentStatus
    reason: Optional[str] = None

class WSError(WSMessage):
    """Error message"""
    type: Literal["error"] = "error"
    error_code: str
    message: str
    details: Optional[dict] = None
```

---

### Error Models

```python
# backend/models/error.py

class ErrorResponse(BaseSchema):
    """Standard error response"""
    error: str
    message: str
    details: Optional[dict] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    request_id: Optional[str] = None

class ValidationErrorDetail(BaseSchema):
    """Validation error detail"""
    field: str
    error: str

class ValidationErrorResponse(ErrorResponse):
    """Validation error with field details"""
    error: Literal["validation_error"] = "validation_error"
    details: list[ValidationErrorDetail] = []
```

---

## TypeScript Models (Frontend)

### Base Types

```typescript
// frontend/src/types/base.ts

export type UUID = string;
export type Timestamp = string; // ISO 8601 format

export interface BaseModel {
  id: UUID;
  created_at: Timestamp;
  updated_at: Timestamp;
}
```

---

### Project Types

```typescript
// frontend/src/types/project.ts

export enum ProjectStatus {
  DRAFT = "draft",
  ACTIVE = "active",
  PAUSED = "paused",
  COMPLETED = "completed",
  ARCHIVED = "archived"
}

export interface Project extends BaseModel {
  name: string;
  description: string | null;
  problem_type: string;
  status: ProjectStatus;
  spec_file_path: string;
  experiment_count: number;
  best_score: number | null;
}

export interface ProjectDetail extends Project {
  experiments: Experiment[];
  config: Record<string, any>;
}

export interface CreateProjectRequest {
  name: string;
  description?: string;
  problem_type: string;
  template?: string;
  specification: {
    file_content: string;
    evolve_function: string;
    evaluate_function: string;
  };
}

export interface UpdateProjectRequest {
  name?: string;
  description?: string;
  status?: ProjectStatus;
}
```

---

### Experiment Types

```typescript
// frontend/src/types/experiment.ts

export enum ExperimentStatus {
  PENDING = "pending",
  RUNNING = "running",
  PAUSED = "paused",
  COMPLETED = "completed",
  FAILED = "failed",
  STOPPED = "stopped"
}

export interface LLMConfig {
  provider: "lm_studio" | "mock" | "template_mock";
  model: string;
  base_url: string;
  temperature: number;
  max_tokens: number;
  timeout: number;
}

export interface SandboxConfig {
  provider: "docker" | "subprocess" | "mock";
  max_workers: number;
  timeout: number;
  image: string;
  limits: {
    memory: string;
    cpu_cores: number;
  };
}

export interface FunSearchConfig {
  samples_per_prompt: number;
  num_islands: number;
  reset_period: number;
  cluster_sampling_temperature_init: number;
  cluster_sampling_temperature_period: number;
}

export interface ExecutionConfig {
  max_iterations: number;
  checkpoint_interval: number;
  log_level: "DEBUG" | "INFO" | "WARNING" | "ERROR";
}

export interface ExperimentConfig {
  llm: LLMConfig;
  sandbox: SandboxConfig;
  funsearch: FunSearchConfig;
  execution: ExecutionConfig;
}

export interface Experiment {
  id: UUID;
  project_id: UUID;
  name: string;
  status: ExperimentStatus;
  config: ExperimentConfig;
  started_at: Timestamp | null;
  completed_at: Timestamp | null;
  paused_at: Timestamp | null;
  iterations_completed: number;
  best_score: number | null;
  mlflow_run_id: string | null;
  task_id: string | null;
}

export interface ExperimentDetail extends Experiment {
  current_score: number | null;
  best_program: string | null;
  metrics: MetricsTimeSeries | null;
  island_states: IslandState[];
  error_message: string | null;
}

export interface CreateExperimentRequest {
  name: string;
  config: ExperimentConfig;
}
```

---

### Metrics Types

```typescript
// frontend/src/types/metrics.ts

export interface MetricPoint {
  iteration: number;
  timestamp: Timestamp;
  best_score: number;
  avg_score: number | null;
  diversity: number | null;
  samples_generated: number | null;
  successful_evaluations: number | null;
}

export interface MetricsTimeSeries {
  iterations: number[];
  best_score: number[];
  avg_score: number[];
  diversity: number[];
  samples_generated: number[];
  successful_evaluations: number[];
}

export interface IslandState {
  island_id: number;
  population_size: number;
  best_score: number;
  avg_score: number | null;
  worst_score: number | null;
  diversity: number | null;
  num_clusters: number | null;
  timestamp: Timestamp;
  top_programs: Program[];
}

export interface Program {
  id: UUID;
  score: number | null;
  code: string;
  signature: string | null;
  created_at: Timestamp;
}
```

---

### WebSocket Types

```typescript
// frontend/src/types/websocket.ts

export type WSMessageType =
  | "subscribe"
  | "unsubscribe"
  | "ping"
  | "pong"
  | "metrics_update"
  | "island_update"
  | "best_program_update"
  | "log"
  | "status_change"
  | "error";

export interface WSMessage {
  type: WSMessageType;
  timestamp: Timestamp;
}

export interface WSSubscribe extends WSMessage {
  type: "subscribe";
  channels: string[];
}

export interface WSMetricsUpdate extends WSMessage {
  type: "metrics_update";
  data: MetricPoint;
}

export interface WSBestProgramUpdate extends WSMessage {
  type: "best_program_update";
  data: {
    iteration: number;
    score: number;
    previous_score: number;
    improvement: number;
    code: string;
  };
}

export interface WSStatusChange extends WSMessage {
  type: "status_change";
  old_status: ExperimentStatus;
  new_status: ExperimentStatus;
  reason?: string;
}

export interface WSError extends WSMessage {
  type: "error";
  error_code: string;
  message: string;
  details?: Record<string, any>;
}

export interface WSLogMessage extends WSMessage {
  type: "log";
  level: "debug" | "info" | "warning" | "error";
  message: string;
}
```

---

### API Response Types

```typescript
// frontend/src/types/api.ts

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  limit: number;
  offset: number;
}

export interface ErrorResponse {
  error: string;
  message: string;
  details?: Record<string, any>;
  timestamp: Timestamp;
  request_id?: string;
}

export interface HealthResponse {
  status: "healthy" | "degraded";
  version: string;
  timestamp: Timestamp;
  services: {
    database: "connected" | "disconnected";
    redis: "connected" | "disconnected";
    mlflow: "connected" | "disconnected";
    lm_studio: "connected" | "disconnected";
    docker: "available" | "unavailable";
  };
  config_mode: string;
  errors?: string[];
}
```

---

### Model (LLM) Types

```typescript
// frontend/src/types/model.ts

export interface ModelInfo {
  id: string;
  name: string;
  size?: string;
  type?: string;
  loaded: boolean;
}

export interface ModelListResponse {
  models: ModelInfo[];
  provider: string;
  base_url: string;
}
```

---

### Template Types

```typescript
// frontend/src/types/template.ts

export interface TemplateInfo {
  id: string;
  name: string;
  description: string;
  example_problems: string[];
}

export interface TemplateDetail extends TemplateInfo {
  specification_template: string;
  default_config: ExperimentConfig;
  example: Record<string, any>;
}
```

---

## Validation Examples

### Python Validation

```python
# Example: Validate experiment creation
from backend.models.experiment import ExperimentCreate
from pydantic import ValidationError

try:
    experiment = ExperimentCreate(
        name="Test Experiment",
        config={
            "llm": {
                "provider": "lm_studio",
                "model": "qwen/qwen3-vl-8b",
                "temperature": 1.0,
                "max_tokens": 512,
                "timeout": 30,
                "base_url": "http://localhost:1234/v1"
            },
            "sandbox": {
                "provider": "docker",
                "max_workers": 16,
                "timeout": 30,
                "image": "funsearch-sandbox:latest",
                "limits": {"memory": "256m", "cpu_cores": 1}
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
                "checkpoint_interval": 1000,
                "log_level": "INFO"
            }
        }
    )
    print("Valid!")
except ValidationError as e:
    print(f"Validation error: {e}")
```

### TypeScript Validation (with Zod)

```typescript
// frontend/src/utils/validation.ts
import { z } from 'zod';

const ExperimentConfigSchema = z.object({
  llm: z.object({
    provider: z.enum(["lm_studio", "mock", "template_mock"]),
    model: z.string().min(1),
    temperature: z.number().min(0).max(2),
    max_tokens: z.number().min(50).max(4096),
    timeout: z.number().min(5).max(300),
    base_url: z.string().url()
  }),
  sandbox: z.object({
    provider: z.enum(["docker", "subprocess", "mock"]),
    max_workers: z.number().min(1).max(64),
    timeout: z.number().min(5).max(300),
    image: z.string(),
    limits: z.object({
      memory: z.string(),
      cpu_cores: z.number()
    })
  }),
  funsearch: z.object({
    samples_per_prompt: z.number().min(1).max(16),
    num_islands: z.number().min(1).max(20),
    reset_period: z.number().min(1000),
    cluster_sampling_temperature_init: z.number().min(0.01).max(1.0),
    cluster_sampling_temperature_period: z.number().min(1000)
  }),
  execution: z.object({
    max_iterations: z.number().min(100),
    checkpoint_interval: z.number().min(100),
    log_level: z.enum(["DEBUG", "INFO", "WARNING", "ERROR"])
  })
});

// Usage
function validateConfig(config: unknown): ExperimentConfig {
  return ExperimentConfigSchema.parse(config);
}
```

---

## Type Conversions

### Database → Pydantic

```python
# Automatic with from_attributes=True
from sqlalchemy.orm import Session
from backend.models.db import Project as DBProject
from backend.models.project import ProjectResponse

def get_project(session: Session, project_id: UUID) -> ProjectResponse:
    db_project = session.query(DBProject).filter(DBProject.id == project_id).one()
    return ProjectResponse.model_validate(db_project)
```

### Pydantic → JSON (for API)

```python
# Automatic serialization
from fastapi import FastAPI
from backend.models.project import ProjectResponse

app = FastAPI()

@app.get("/api/v1/projects/{project_id}", response_model=ProjectResponse)
def get_project(project_id: UUID):
    project = get_project_from_db(project_id)
    return project  # Automatically serialized to JSON
```

### TypeScript Type Guards

```typescript
// frontend/src/utils/typeGuards.ts

export function isErrorResponse(obj: any): obj is ErrorResponse {
  return obj && typeof obj.error === 'string' && typeof obj.message === 'string';
}

export function isWSMetricsUpdate(msg: WSMessage): msg is WSMetricsUpdate {
  return msg.type === 'metrics_update' && 'data' in msg;
}

// Usage
if (isErrorResponse(response)) {
  console.error(`Error: ${response.message}`);
}
```

---

**Last Updated**: 2025-11-16
**Version**: 1.0
**Status**: Specification
