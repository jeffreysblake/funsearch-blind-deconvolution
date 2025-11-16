# FunSearch Framework - Component Interfaces

## Overview

This document specifies the abstract interfaces and contracts for all major components in the FunSearch framework, enabling clean separation of concerns and easy testing.

---

## Core Interfaces (Python)

### Sampler Interface (LLM)

```python
# backend/core/interfaces/sampler.py
from abc import ABC, abstractmethod
from typing import List

class Sampler(ABC):
    """
    Abstract interface for LLM code generation.

    Implementations:
    - LMStudioSampler: Real LM Studio integration
    - MockSampler: Simple mock for testing
    - TemplateMockSampler: Template-based mock for dev
    """

    @abstractmethod
    def sample(self, prompt: str, num_samples: int = 1) -> List[str]:
        """
        Generate code samples from a prompt.

        Args:
            prompt: The code prompt (partial function to complete)
            num_samples: Number of samples to generate

        Returns:
            List of generated code strings

        Raises:
            SamplerError: If generation fails
            TimeoutError: If generation times out
        """
        pass

    @abstractmethod
    def get_stats(self) -> dict:
        """
        Get sampler statistics (tokens used, calls made, etc.)

        Returns:
            Dictionary with statistics
        """
        pass

    def __enter__(self):
        """Context manager support"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Cleanup resources"""
        pass
```

**Contract**:
- MUST return valid Python code strings
- MUST handle timeout gracefully
- MUST be thread-safe for parallel calls
- SHOULD cache responses for identical prompts
- MAY raise SamplerError for retryable errors

---

### Evaluator Interface (Sandbox)

```python
# backend/core/interfaces/evaluator.py
from abc import ABC, abstractmethod
from typing import Any, Optional

class Evaluator(ABC):
    """
    Abstract interface for code evaluation in sandboxed environment.

    Implementations:
    - DockerEvaluator: Secure Docker containers
    - SubprocessEvaluator: Subprocess execution
    - MockEvaluator: In-memory evaluation for testing
    """

    @abstractmethod
    def evaluate(self, program: str, test_input: Any) -> float:
        """
        Execute program and return fitness score.

        Args:
            program: Python code to execute
            test_input: Input data for evaluation

        Returns:
            Fitness score (higher is better)
            Returns -inf for failed evaluations

        Raises:
            EvaluatorError: If evaluation infrastructure fails
        """
        pass

    @abstractmethod
    def evaluate_batch(self, programs: List[str], test_inputs: List[Any]) -> List[float]:
        """
        Evaluate multiple programs in parallel.

        Args:
            programs: List of Python code strings
            test_inputs: List of test inputs (one per program)

        Returns:
            List of fitness scores (same length as programs)
        """
        pass

    @abstractmethod
    def close(self):
        """Cleanup resources (containers, processes, etc.)"""
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
```

**Contract**:
- MUST enforce timeout (default 30s)
- MUST isolate executions (no cross-contamination)
- MUST return -inf for syntax errors, timeouts, exceptions
- MUST be thread-safe for parallel execution
- SHOULD limit resources (CPU, memory, network)
- MUST clean up all resources on close()

---

### ProgramsDatabase Interface

```python
# backend/core/interfaces/programs_database.py
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Program:
    """Evolved program with metadata"""
    code: str
    score: float
    island_id: int
    signature: Optional[str] = None  # Tuple of evaluation results
    parent_id: Optional[str] = None

class ProgramsDatabase(ABC):
    """
    Interface for managing evolved programs across islands.

    Implementation:
    - IslandBasedDatabase: Island-based evolution with clustering
    """

    @abstractmethod
    def add_programs(self, programs: List[Program], island_id: int):
        """Add new programs to an island"""
        pass

    @abstractmethod
    def sample_program(self, island_id: int) -> Optional[Program]:
        """Sample a program from island using temperature-based selection"""
        pass

    @abstractmethod
    def get_best_programs(self, limit: int = 10) -> List[Program]:
        """Get top programs across all islands"""
        pass

    @abstractmethod
    def reset_island(self, island_id: int, seed_programs: List[Program]):
        """Reset an island with seed programs"""
        pass

    @abstractmethod
    def get_island_stats(self, island_id: int) -> dict:
        """Get statistics for an island (size, diversity, scores)"""
        pass
```

**Contract**:
- MUST maintain separate populations per island
- MUST group programs by signature (identical evaluation results)
- MUST implement temperature-scheduled sampling
- SHOULD track program lineage (parent relationships)

---

### CodeManipulator Interface

```python
# backend/core/interfaces/code_manipulator.py
from abc import ABC, abstractmethod
from typing import List, Tuple

class CodeManipulator(ABC):
    """
    Interface for parsing and manipulating Python code via AST.

    Implementation:
    - ASTCodeManipulator: AST-based implementation
    """

    @abstractmethod
    def parse_specification(self, code: str) -> dict:
        """
        Parse specification file to extract functions marked with decorators.

        Args:
            code: Python source code with @funsearch.run and @funsearch.evolve

        Returns:
            Dictionary with:
            - evolve_function: Name of function to evolve
            - run_function: Name of evaluation function
            - imports: Required imports
            - other_functions: Helper functions

        Raises:
            ParseError: If specification is invalid
        """
        pass

    @abstractmethod
    def create_prompt(self, specification: dict, program: Program) -> str:
        """
        Create LLM prompt from specification and existing program.

        Args:
            specification: Parsed specification
            program: Existing program to extend/modify

        Returns:
            Prompt string for LLM
        """
        pass

    @abstractmethod
    def merge_program(self, specification: dict, generated_code: str) -> str:
        """
        Merge LLM-generated code into full program.

        Args:
            specification: Parsed specification
            generated_code: LLM-generated function body

        Returns:
            Complete executable Python program

        Raises:
            MergeError: If generated code is invalid
        """
        pass

    @abstractmethod
    def extract_function_body(self, code: str, function_name: str) -> str:
        """Extract just the body of a function"""
        pass

    @abstractmethod
    def validate_code(self, code: str) -> Tuple[bool, Optional[str]]:
        """
        Validate Python code syntax.

        Returns:
            (is_valid, error_message)
        """
        pass
```

**Contract**:
- MUST preserve imports and helper functions
- MUST handle syntax errors gracefully
- MUST support Python 3.11+ syntax
- SHOULD cache parsed specifications

---

## Component Factory

```python
# backend/core/factory.py
from typing import Protocol
from .interfaces import Sampler, Evaluator
from ..models.experiment import ExperimentConfig

class ComponentFactory(Protocol):
    """Factory for creating FunSearch components"""

    @staticmethod
    def create_sampler(config: ExperimentConfig) -> Sampler:
        """
        Create LLM sampler based on configuration.

        Selects implementation based on config.llm.provider:
        - "lm_studio" → LMStudioSampler
        - "mock" → MockSampler
        - "template_mock" → TemplateMockSampler
        """
        pass

    @staticmethod
    def create_evaluator(config: ExperimentConfig) -> Evaluator:
        """
        Create code evaluator based on configuration.

        Selects implementation based on config.sandbox.provider:
        - "docker" → DockerEvaluator
        - "subprocess" → SubprocessEvaluator
        - "mock" → MockEvaluator
        """
        pass

    @staticmethod
    def create_programs_database(config: ExperimentConfig) -> ProgramsDatabase:
        """Create programs database for island-based evolution"""
        pass

    @staticmethod
    def create_code_manipulator() -> CodeManipulator:
        """Create code manipulation component"""
        pass
```

---

## Service Interfaces (Backend)

### ProjectService

```python
# backend/services/interfaces/project_service.py
from abc import ABC, abstractmethod
from uuid import UUID
from typing import List, Optional
from backend.models.project import (
    ProjectCreate, ProjectUpdate, ProjectResponse, ProjectDetail
)

class ProjectService(ABC):
    """Service for project CRUD operations"""

    @abstractmethod
    async def create_project(self, project: ProjectCreate) -> ProjectResponse:
        """Create new project"""
        pass

    @abstractmethod
    async def get_project(self, project_id: UUID) -> Optional[ProjectDetail]:
        """Get project by ID"""
        pass

    @abstractmethod
    async def list_projects(
        self,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> tuple[List[ProjectResponse], int]:
        """List projects with pagination"""
        pass

    @abstractmethod
    async def update_project(
        self, project_id: UUID, updates: ProjectUpdate
    ) -> ProjectResponse:
        """Update project"""
        pass

    @abstractmethod
    async def delete_project(self, project_id: UUID):
        """Delete project and all experiments"""
        pass
```

---

### ExperimentService

```python
# backend/services/interfaces/experiment_service.py
from abc import ABC, abstractmethod
from uuid import UUID
from backend.models.experiment import (
    ExperimentCreate, ExperimentResponse, ExperimentDetail
)

class ExperimentService(ABC):
    """Service for experiment lifecycle management"""

    @abstractmethod
    async def create_experiment(
        self, project_id: UUID, experiment: ExperimentCreate
    ) -> ExperimentResponse:
        """Create and start new experiment"""
        pass

    @abstractmethod
    async def get_experiment(self, experiment_id: UUID) -> Optional[ExperimentDetail]:
        """Get experiment details"""
        pass

    @abstractmethod
    async def stop_experiment(self, experiment_id: UUID) -> ExperimentResponse:
        """Stop running experiment"""
        pass

    @abstractmethod
    async def pause_experiment(self, experiment_id: UUID) -> ExperimentResponse:
        """Pause experiment (can resume)"""
        pass

    @abstractmethod
    async def resume_experiment(self, experiment_id: UUID) -> ExperimentResponse:
        """Resume paused experiment"""
        pass

    @abstractmethod
    async def get_experiment_metrics(
        self,
        experiment_id: UUID,
        from_iteration: Optional[int] = None,
        to_iteration: Optional[int] = None
    ) -> MetricsTimeSeries:
        """Get metrics for experiment"""
        pass
```

---

### MetricsCollector

```python
# backend/services/interfaces/metrics_collector.py
from abc import ABC, abstractmethod
from uuid import UUID
from backend.models.metrics import MetricPoint

class MetricsCollector(ABC):
    """Service for collecting and storing experiment metrics"""

    @abstractmethod
    async def record_metric(self, experiment_id: UUID, metric: MetricPoint):
        """Record a single metric point"""
        pass

    @abstractmethod
    async def record_batch(self, experiment_id: UUID, metrics: List[MetricPoint]):
        """Record multiple metrics efficiently"""
        pass

    @abstractmethod
    async def get_latest_metric(self, experiment_id: UUID) -> Optional[MetricPoint]:
        """Get most recent metric"""
        pass
```

---

## React Component Interfaces (TypeScript)

### API Client Interface

```typescript
// frontend/src/api/interface.ts
import {
  Project, ProjectDetail, CreateProjectRequest, UpdateProjectRequest,
  Experiment, ExperimentDetail, CreateExperimentRequest,
  MetricsTimeSeries, IslandState, ModelInfo
} from '../types';

export interface IAPIClient {
  // Projects
  getProjects(params?: {
    status?: string;
    limit?: number;
    offset?: number;
  }): Promise<{ projects: Project[]; total: number }>;

  getProject(id: string): Promise<ProjectDetail>;
  createProject(data: CreateProjectRequest): Promise<Project>;
  updateProject(id: string, data: UpdateProjectRequest): Promise<Project>;
  deleteProject(id: string): Promise<void>;

  // Experiments
  getExperiments(projectId: string): Promise<Experiment[]>;
  getExperiment(id: string): Promise<ExperimentDetail>;
  createExperiment(projectId: string, data: CreateExperimentRequest): Promise<Experiment>;
  stopExperiment(id: string): Promise<Experiment>;
  pauseExperiment(id: string): Promise<Experiment>;
  resumeExperiment(id: string): Promise<Experiment>;

  // Metrics
  getMetrics(experimentId: string, params?: {
    from_iteration?: number;
    to_iteration?: number;
  }): Promise<MetricsTimeSeries>;

  getIslandStates(experimentId: string): Promise<IslandState[]>;

  // Models
  getModels(): Promise<ModelInfo[]>;

  // Health
  getHealth(): Promise<HealthResponse>;
}
```

---

### WebSocket Client Interface

```typescript
// frontend/src/websocket/interface.ts
import { WSMessage } from '../types';

export interface IWebSocketClient {
  /**
   * Connect to WebSocket for experiment updates
   */
  connect(experimentId: string): Promise<void>;

  /**
   * Disconnect from WebSocket
   */
  disconnect(): void;

  /**
   * Subscribe to specific channels
   */
  subscribe(channels: string[]): void;

  /**
   * Register callback for message type
   */
  on(messageType: string, callback: (message: WSMessage) => void): void;

  /**
   * Remove callback
   */
  off(messageType: string, callback: (message: WSMessage) => void): void;

  /**
   * Check if connected
   */
  isConnected(): boolean;
}
```

---

### State Management Interface (Zustand)

```typescript
// frontend/src/store/interface.ts

export interface IProjectStore {
  // State
  projects: Project[];
  selectedProject: ProjectDetail | null;
  loading: boolean;
  error: string | null;

  // Actions
  fetchProjects(): Promise<void>;
  fetchProject(id: string): Promise<void>;
  createProject(data: CreateProjectRequest): Promise<void>;
  updateProject(id: string, data: UpdateProjectRequest): Promise<void>;
  deleteProject(id: string): Promise<void>;
  setSelectedProject(project: ProjectDetail | null): void;
}

export interface IExperimentStore {
  // State
  experiments: Map<string, Experiment>;  // experimentId → Experiment
  selectedExperiment: ExperimentDetail | null;
  liveMetrics: Map<string, MetricPoint[]>;  // experimentId → metrics
  loading: boolean;

  // Actions
  fetchExperiment(id: string): Promise<void>;
  createExperiment(projectId: string, data: CreateExperimentRequest): Promise<void>;
  stopExperiment(id: string): Promise<void>;
  pauseExperiment(id: string): Promise<void>;
  resumeExperiment(id: string): Promise<void>;

  // WebSocket updates
  handleMetricUpdate(experimentId: string, metric: MetricPoint): void;
  handleStatusChange(experimentId: string, newStatus: ExperimentStatus): void;
}
```

---

## Testing Interfaces

### Test Doubles

```python
# tests/doubles/mock_sampler.py
from backend.core.interfaces import Sampler

class MockSampler(Sampler):
    """Deterministic mock for testing"""

    def __init__(self, responses: List[List[str]]):
        """
        Args:
            responses: Pre-defined responses for each sample() call
        """
        self.responses = responses
        self.call_count = 0

    def sample(self, prompt: str, num_samples: int = 1) -> List[str]:
        if self.call_count >= len(self.responses):
            raise ValueError("Mock exhausted")

        result = self.responses[self.call_count]
        self.call_count += 1
        return result[:num_samples]

    def get_stats(self) -> dict:
        return {"calls": self.call_count, "type": "mock"}
```

```python
# tests/doubles/spy_evaluator.py
class SpyEvaluator(Evaluator):
    """Spy for tracking evaluation calls"""

    def __init__(self, delegate: Evaluator):
        self.delegate = delegate
        self.evaluations: List[tuple[str, Any, float]] = []

    def evaluate(self, program: str, test_input: Any) -> float:
        score = self.delegate.evaluate(program, test_input)
        self.evaluations.append((program, test_input, score))
        return score

    def get_evaluation_count(self) -> int:
        return len(self.evaluations)

    def was_program_evaluated(self, program: str) -> bool:
        return any(p == program for p, _, _ in self.evaluations)
```

---

## Dependency Injection

### Service Container

```python
# backend/core/container.py
from dataclasses import dataclass
from .interfaces import Sampler, Evaluator, ProgramsDatabase
from ..services.interfaces import ProjectService, ExperimentService

@dataclass
class ServiceContainer:
    """Dependency injection container"""

    # Core components
    sampler: Sampler
    evaluator: Evaluator
    programs_database: ProgramsDatabase
    code_manipulator: CodeManipulator

    # Services
    project_service: ProjectService
    experiment_service: ExperimentService
    metrics_collector: MetricsCollector

    # Infrastructure
    db_session: Session
    redis_client: Redis
    mlflow_client: MlflowClient

def create_container(config: ExperimentConfig) -> ServiceContainer:
    """Create fully configured service container"""

    # Create core components
    sampler = ComponentFactory.create_sampler(config)
    evaluator = ComponentFactory.create_evaluator(config)
    # ... etc

    return ServiceContainer(
        sampler=sampler,
        evaluator=evaluator,
        # ... etc
    )
```

**Usage**:

```python
# In FastAPI dependency injection
from fastapi import Depends

def get_container() -> ServiceContainer:
    """FastAPI dependency"""
    return create_container(load_config())

@app.get("/api/v1/projects")
async def list_projects(
    container: ServiceContainer = Depends(get_container)
):
    projects = await container.project_service.list_projects()
    return projects
```

---

## Error Handling

### Custom Exceptions

```python
# backend/core/exceptions.py

class FunSearchError(Exception):
    """Base exception for all FunSearch errors"""
    pass

class SamplerError(FunSearchError):
    """LLM sampler error"""
    pass

class EvaluatorError(FunSearchError):
    """Code evaluator error"""
    pass

class ParseError(FunSearchError):
    """Code parsing error"""
    pass

class ConfigurationError(FunSearchError):
    """Invalid configuration"""
    pass
```

---

## Interface Documentation Standards

All interfaces MUST include:

1. **Purpose**: What the interface represents
2. **Implementations**: Known implementations
3. **Method Contracts**: Pre/post conditions, exceptions
4. **Thread Safety**: Whether methods are thread-safe
5. **Resource Management**: Cleanup requirements
6. **Examples**: Usage examples

---

**Last Updated**: 2025-11-16
**Version**: 1.0
**Status**: Specification
