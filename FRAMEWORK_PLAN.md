# FunSearch Framework Evolution Plan

## Executive Summary

Transform the current funsearch-blind-deconvolution implementation into a **general-purpose program synthesis framework** with local LLM integration, web-based UI dashboard, and comprehensive experiment tracking capabilities.

---

## Current State Analysis

### What We Have
- **Core FunSearch Implementation** (900 lines, 6 core components)
  - Island-based evolutionary algorithm (10 populations)
  - AST-based code manipulation and program synthesis
  - Abstract LLM and Sandbox interfaces
  - Lucy-Richardson blind deconvolution as proof-of-concept
  - 80% test coverage, 6 example problem domains

### Key Strengths
✓ Clean modular architecture with clear separation of concerns
✓ Robust code manipulation using Python AST
✓ Proven evolutionary algorithm (Google DeepMind research)
✓ Flexible decorator-based problem specification (`@funsearch.run`, `@funsearch.evolve`)
✓ Temperature-scheduled exploration-exploitation balance

### Production Gaps
✗ No CLI or configuration file system (programmatic only)
✗ Abstract interfaces not implemented (Sandbox, LLM)
✗ No experiment persistence or monitoring
✗ Single-threaded execution
✗ No project management system
✗ No web UI for interaction

---

## Target Architecture

### Vision Statement
A **self-hosted, agent-enabled program synthesis platform** that allows researchers to:
1. Define optimization problems via Python decorators
2. Run evolutionary searches using local LLMs (LM Studio)
3. Monitor experiments in real-time via web dashboard
4. Manage multiple concurrent projects
5. Track and compare results across experiments

### Core Principles
- **Local-First**: All LLMs run locally via LM Studio (privacy, cost control)
- **Agent-Friendly**: Built for pairing with AI coding agents
- **Framework-Agnostic**: Support any problem domain with fitness evaluation
- **Observable**: Real-time monitoring and comprehensive logging
- **Reproducible**: Full experiment tracking and versioning

---

## Technical Architecture

### 1. System Components

```
┌─────────────────────────────────────────────────────────────┐
│                     Web Dashboard (React)                    │
│  - Model Selection  - Project Browser  - Live Monitoring   │
└────────────────────┬────────────────────────────────────────┘
                     │ REST API
┌────────────────────▼────────────────────────────────────────┐
│              Backend API Server (FastAPI)                    │
│  - Project Management  - Experiment Control  - Metrics API  │
└────┬───────────────┬──────────────────┬─────────────────────┘
     │               │                  │
┌────▼──────┐  ┌────▼─────────┐  ┌─────▼──────────────────┐
│  Project  │  │  FunSearch   │  │  LM Studio Client      │
│  Database │  │  Core Engine │  │  (OpenAI-compatible)   │
│ (SQLite)  │  │  (existing)  │  │  http://localhost:1234 │
└───────────┘  └──────────────┘  └────────────────────────┘
                     │
              ┌──────▼──────┐
              │  Experiment │
              │   Tracking  │
              │  (MLflow)   │
              └─────────────┘
```

### 2. Technology Stack

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| **Frontend** | React + TypeScript | Rich ecosystem, component reusability |
| **UI Framework** | Ant Design / Material-UI | Pre-built dashboard components |
| **Backend API** | FastAPI | Async support, auto-docs, WebSocket for live updates |
| **Database** | SQLite → PostgreSQL | Start simple, scale as needed |
| **LLM Integration** | LM Studio Python SDK | Official SDK with OpenAI compatibility |
| **Experiment Tracking** | MLflow | Open-source, self-hosted, industry standard |
| **Task Queue** | Celery + Redis | Async experiment execution |
| **Visualization** | Plotly.js / D3.js | Interactive charts for metrics |

### 3. Data Models

#### Project
```python
class Project(BaseModel):
    id: UUID
    name: str
    description: str
    problem_type: str  # "optimization", "synthesis", "search"
    specification_file: Path  # Python file with @funsearch decorators
    created_at: datetime
    updated_at: datetime
    status: Literal["draft", "active", "paused", "completed"]
```

#### Experiment
```python
class Experiment(BaseModel):
    id: UUID
    project_id: UUID
    name: str
    config: FunSearchConfig  # All 15 tunable parameters
    llm_config: LLMConfig  # Model name, temperature, etc.
    status: Literal["pending", "running", "completed", "failed"]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    best_score: Optional[float]
    iterations_completed: int
```

#### LLMConfig
```python
class LLMConfig(BaseModel):
    model_name: str  # e.g., "mistral-7b-instruct"
    base_url: str = "http://localhost:1234/v1"
    temperature: float = 1.0
    max_tokens: int = 512
    timeout: int = 30
```

---

## Implementation Roadmap

### Phase 1: Core Infrastructure (Weeks 1-2)

**Goal**: Build foundation for multi-project framework

#### 1.1 Project Management System
- [ ] Create SQLite database schema (projects, experiments, runs)
- [ ] Implement Project CRUD operations
- [ ] Add file-based configuration loader (YAML/TOML)
- [ ] Create CLI for project initialization (`funsearch init <project-name>`)

#### 1.2 Configuration System
- [ ] Extend `config.py` to support file loading
- [ ] Add validation using Pydantic models
- [ ] Support environment variable overrides
- [ ] Create config templates for common problem types

#### 1.3 Experiment Persistence
- [ ] Implement database models for experiments
- [ ] Add checkpoint/resume capability for long runs
- [ ] Store program evolution history
- [ ] Track metrics over time (scores, diversity, island states)

**Deliverable**: CLI tool that can manage multiple projects with persistent storage

---

### Phase 2: LM Studio Integration (Weeks 3-4)

**Goal**: Replace abstract LLM interface with working local models

#### 2.1 LLM Client Implementation
- [ ] Install and configure `lmstudio` Python SDK
- [ ] Implement concrete `Sampler` class using LM Studio API
- [ ] Add model discovery (query available models via API)
- [ ] Implement retry logic and error handling
- [ ] Add prompt template system (customize per problem type)

#### 2.2 Sandbox Implementation
- [ ] Implement safe code execution sandbox
- [ ] Options: `RestrictedPython`, Docker containers, or gVisor
- [ ] Add timeout and resource limits
- [ ] Capture stdout/stderr for debugging
- [ ] Security hardening for untrusted LLM-generated code

#### 2.3 Model Performance Optimization
- [ ] Benchmark different local models (Mistral, CodeLlama, DeepSeek)
- [ ] Implement caching for repeated prompt patterns
- [ ] Add batching support if LM Studio supports it
- [ ] Monitor token usage and generation speed

**Deliverable**: Fully functional FunSearch runs using local LLMs

---

### Phase 3: Web Dashboard (Weeks 5-7)

**Goal**: Build intuitive UI for managing and monitoring experiments

#### 3.1 Backend API (FastAPI)
- [ ] Implement REST endpoints:
  - `GET /api/projects` - List all projects
  - `POST /api/projects` - Create new project
  - `GET /api/projects/{id}/experiments` - List experiments
  - `POST /api/experiments` - Start new experiment
  - `GET /api/experiments/{id}/metrics` - Real-time metrics
  - `GET /api/lm-studio/models` - Available models
- [ ] Add WebSocket endpoint for live updates
- [ ] Implement CORS for local development
- [ ] Add authentication (optional, for multi-user deployments)

#### 3.2 Frontend Dashboard
- [ ] **Home Page**: Project overview cards with status indicators
- [ ] **Project Detail**: Experiment list, configuration viewer
- [ ] **Experiment Runner**:
  - Model selector dropdown (populated from LM Studio)
  - Parameter configuration form (15 FunSearch params)
  - Start/Stop/Pause controls
- [ ] **Live Monitoring**:
  - Real-time metrics charts (fitness over time, diversity)
  - Island population visualization
  - Best program display with syntax highlighting
  - Log stream viewer
- [ ] **Comparison View**: Side-by-side experiment comparison

#### 3.3 Visualization Components
- [ ] Fitness evolution line chart (all islands)
- [ ] Program diversity heatmap
- [ ] Best score leaderboard
- [ ] Resource usage (CPU, memory, LLM token count)
- [ ] Code diff viewer for program evolution

**Deliverable**: Full-featured web UI for managing experiments

---

### Phase 4: Experiment Tracking & Advanced Features (Weeks 8-10)

**Goal**: Production-grade tracking and collaboration features

#### 4.1 MLflow Integration
- [ ] Install and configure MLflow tracking server
- [ ] Log all experiment parameters automatically
- [ ] Track metrics at each iteration
- [ ] Store generated programs as artifacts
- [ ] Add tags and notes for experiments
- [ ] Enable experiment comparison in MLflow UI

#### 4.2 Advanced Experiment Features
- [ ] **Hyperparameter Search**: Grid/random search over FunSearch config
- [ ] **A/B Testing**: Compare different LLMs on same problem
- [ ] **Ensembling**: Combine best programs from multiple runs
- [ ] **Transfer Learning**: Initialize new projects from successful runs
- [ ] **Scheduled Runs**: Cron-like experiment scheduling

#### 4.3 Collaboration & Export
- [ ] Export experiment results (JSON, CSV)
- [ ] Generate report PDFs with best programs + metrics
- [ ] Share projects via export/import (zip with all configs)
- [ ] Add comments/annotations to experiments
- [ ] Version control integration (git commit on new best programs)

**Deliverable**: Production-ready platform with comprehensive tracking

---

### Phase 5: Multi-Domain Support (Weeks 11-12)

**Goal**: Make it easy to add new problem domains

#### 5.1 Problem Template System
- [ ] Create project templates for common domains:
  - Mathematical optimization (like cap set)
  - Algorithm synthesis (like bin packing)
  - Signal processing (like Lucy-Richardson)
  - Neural architecture search
  - Hyperparameter optimization
- [ ] CLI: `funsearch new --template=optimization my_problem`
- [ ] Template documentation generator

#### 5.2 Domain-Specific Evaluators
- [ ] Parallel evaluation support for batch problems
- [ ] GPU acceleration for compute-intensive evaluators
- [ ] Distributed evaluation across multiple machines
- [ ] Custom metric collectors per domain

#### 5.3 Example Gallery
- [ ] Create 10+ example problems with notebooks
- [ ] Video tutorials for common use cases
- [ ] Best practices guide
- [ ] Troubleshooting documentation

**Deliverable**: Easy onboarding for new problem domains

---

## Directory Structure (Proposed)

```
funsearch-framework/
├── backend/
│   ├── api/              # FastAPI endpoints
│   ├── core/             # Existing funsearch implementation
│   ├── models/           # Database models (SQLAlchemy)
│   ├── services/         # Business logic
│   │   ├── project_service.py
│   │   ├── experiment_service.py
│   │   └── llm_service.py
│   ├── config/           # Configuration schemas
│   └── tasks/            # Celery tasks for async execution
├── frontend/
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── pages/        # Dashboard pages
│   │   ├── api/          # API client
│   │   └── utils/        # Helpers
│   └── public/
├── cli/                  # Command-line interface
│   └── funsearch_cli.py
├── templates/            # Problem domain templates
│   ├── optimization/
│   ├── synthesis/
│   └── search/
├── examples/             # Example projects
│   ├── lucy_richardson/
│   ├── bin_packing/
│   └── cap_set/
├── tests/
├── docs/
├── scripts/              # Setup and deployment scripts
├── pyproject.toml
└── README.md
```

---

## Configuration File Format

### Project Configuration (`.funsearch/project.yaml`)

```yaml
project:
  name: "Lucy-Richardson Optimization"
  type: "signal_processing"
  description: "Optimize convergence of blind deconvolution"

specification:
  file: "problem_spec.py"
  evolve_function: "priority"
  run_function: "evaluate"

funsearch:
  samples_per_prompt: 4
  num_islands: 10
  reset_period: 8e4
  cluster_sampling_temperature_init: 0.1
  cluster_sampling_temperature_period: 2e4

llm:
  provider: "lm_studio"
  base_url: "http://localhost:1234/v1"
  model: "mistral-7b-instruct-v0.2"
  temperature: 1.0
  max_tokens: 512

execution:
  max_iterations: 100000
  checkpoint_interval: 1000
  log_level: "INFO"

evaluator:
  parallel: true
  num_workers: 4
  timeout: 30
```

---

## Key Technical Decisions

### 1. Why FastAPI over Flask?
- Built-in async support for WebSocket live updates
- Automatic OpenAPI docs (Swagger UI)
- Pydantic integration for validation
- Better performance for concurrent requests

### 2. Why MLflow over Weights & Biases?
- **Self-hosted**: No external dependencies or costs
- **Open-source**: Full control and customization
- **Lightweight**: SQLite backend for small projects
- **Industry standard**: 20k+ GitHub stars, used by Microsoft/Facebook

### 3. Why React over Vue/Svelte?
- Largest ecosystem for data visualization (Plotly, D3 bindings)
- More third-party dashboard components (Ant Design)
- Better TypeScript support
- Easier to find AI agents familiar with React

### 4. Why SQLite initially?
- Zero configuration
- Single file database (easy backups)
- Sufficient for single-user local deployment
- Easy migration to PostgreSQL later

---

## Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| **LLM code quality varies** | Poor program synthesis | Implement prompt engineering templates, benchmark models |
| **Long experiment runs** | UI unresponsive | Use Celery for async execution, WebSocket for updates |
| **Sandbox security** | Malicious LLM code | Use Docker/gVisor, strict resource limits, network isolation |
| **Concurrent experiments** | Resource exhaustion | Add queue system, max concurrent limit, resource monitoring |
| **Database scaling** | Slow queries | Index optimization, archive old experiments, PostgreSQL migration |

---

## Success Metrics

### Technical Metrics
- [ ] Support 10+ concurrent experiments
- [ ] Sub-100ms API response times
- [ ] 95%+ test coverage maintained
- [ ] Zero sandbox escapes
- [ ] Real-time updates <500ms latency

### User Experience Metrics
- [ ] New project setup <5 minutes
- [ ] Experiment start <10 seconds
- [ ] Intuitive UI (no documentation needed for basic tasks)
- [ ] Support 5+ different problem domains

### Research Metrics
- [ ] Reproduce Google DeepMind results on cap set problem
- [ ] Demonstrate improvement on Lucy-Richardson convergence
- [ ] Publish 3+ case studies with novel discoveries

---

## Next Steps

### Immediate Actions (Before Coding)
1. **Validate architecture** with stakeholder (you!)
2. **Choose specific technologies** (React vs Vue, etc.)
3. **Set up development environment**
   - Install LM Studio and test API
   - Choose and download a code-generation model
   - Set up Python virtual environment
4. **Create project repository structure**
5. **Write Phase 1 technical specifications**

### First Milestone (2 weeks)
- Working CLI that can create projects
- YAML configuration loading
- SQLite database with basic CRUD
- Single experiment runs with LM Studio
- Basic logging and checkpointing

---

## Open Questions for Discussion

1. **Frontend Framework**: React, Vue, or Svelte? (Recommendation: React)
2. **UI Component Library**: Ant Design, Material-UI, or Chakra UI?
3. **Authentication**: Do you need multi-user support initially?
4. **Deployment**: Docker-compose setup? Kubernetes for scaling?
5. **LLM Models**: Which models to benchmark first? (Mistral, CodeLlama, DeepSeek)
6. **Problem Domains**: Which 3 domains to prioritize after Lucy-Richardson?
7. **Sandbox Strategy**: Docker (heavier but secure) vs RestrictedPython (lighter but less secure)?

---

## References

### Research Papers
- [FunSearch: Mathematical discoveries from program search with LLMs (Nature 2024)](https://www.nature.com/articles/s41586-023-06924-6)
- [Deep-URL: Richardson-Lucy Deep Unfolding Network (arXiv)](https://arxiv.org/abs/2002.01053)

### Technical Documentation
- [Google DeepMind FunSearch Implementation](https://github.com/google-deepmind/funsearch)
- [LM Studio Python SDK](https://lmstudio.ai/docs/python)
- [MLflow Documentation](https://mlflow.org/docs/latest/index.html)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

### Community Resources
- [OpenFunSearch](https://github.com/Remmie0/OpenFunnsearch) - Alternative implementation
- [MLflow Experiment Tracking Guide](https://neptune.ai/blog/mlflow-guide)

---

**Document Version**: 1.0
**Last Updated**: 2025-11-16
**Author**: Claude (AI Planning Agent)
**Status**: Draft - Awaiting Review
