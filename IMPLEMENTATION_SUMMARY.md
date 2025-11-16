# Implementation Summary & Next Steps

## Your Questions Answered ✅

### 1. **Frontend**: React ✓
### 2. **UI Library**: Ant Design ✓
### 3. **Sandbox**: Docker with specific architecture (see below)
### 4. **Auth**: Single-user ✓
### 5. **Models**: `qwen/qwen3-vl-8b` and `mistralai/magistral-small-2509` ✓
### 6. **Domains**: Algorithm synthesis + Mathematical optimization ✓
### 7. **Deployment**: Docker Compose ✓

---

## Docker Sandbox Architecture (Your Questions)

### ❓ "Can we re-use the container for running sandboxed code in parallel?"

**Answer: Yes, but with specific architecture:**

```
┌────────────────────────────────────────┐
│  Host Machine                          │
│  ├── LM Studio (localhost:1234)        │
│  ├── FunSearch App (container or host) │
│  │   └── Docker Socket Access          │
│  │       └── Spawns sandbox containers │
│  ├── Redis (container)                 │
│  └── MLflow (container)                │
│                                        │
│  Sandbox Containers (ephemeral pool)  │
│  ├── Eval #1 🔒 (isolated)             │
│  ├── Eval #2 🔒 (isolated)             │
│  ├── ... (8-16 parallel workers)       │
│  └── Eval #N 🔒 (isolated)             │
└────────────────────────────────────────┘
```

**Two patterns:**

1. **Create/Destroy (Recommended)**
   - Spawn new container for each evaluation
   - Destroy immediately after completion
   - ~500ms overhead but safest (no state leakage)

2. **Container Pool (Faster)**
   - Pre-create N containers
   - Reuse for multiple evaluations
   - ~50ms overhead but must restart periodically
   - Risk of state contamination

**Implementation:**
```python
# Parallel execution with docker-py
from concurrent.futures import ThreadPoolExecutor
import docker

class SandboxPool:
    def __init__(self, max_workers=8):
        self.client = docker.from_env()
        self.executor = ThreadPoolExecutor(max_workers)

    def evaluate_batch(self, programs: list[str]):
        futures = [
            self.executor.submit(self._run_in_container, prog)
            for prog in programs
        ]
        return [f.result() for f in futures]
```

### ❓ "Is RestrictedPython really secure for sandboxing?"

**Answer: NO - Not secure enough for LLM-generated code.**

**Why not:**
- Compile-time restrictions that can be bypassed
- Known exploits exist:
  ```python
  # Example bypass
  ().__class__.__bases__[0].__subclasses__()[104]
    .__init__.__globals__['sys'].modules['os'].system('rm -rf /')
  ```
- Only suitable for "friendly" code, not adversarial

**Verdict**: Use for quick dev/debugging only, never for production.

### ❓ "Can we use the app container as our built-in sandbox?"

**Answer: No - Security boundary violation.**

**Why not:**
- If malicious LLM code escapes, it compromises entire app
- Can't enforce strict resource limits without affecting app
- One bad program could kill the whole service

**Better approach:**
```
App Container (or host)
    │
    ├─ Mounts Docker socket (/var/run/docker.sock)
    │
    └─ Spawns SIBLING containers (not nested)
        └─ Each sandbox = isolated ephemeral container
```

**Security config:**
```python
container_config = {
    "network_disabled": True,       # No internet
    "mem_limit": "256m",            # Memory cap
    "nano_cpus": 1_000_000_000,     # 1 CPU core
    "read_only": True,              # Read-only FS
    "security_opt": ["no-new-privileges"],
    "cap_drop": ["ALL"],            # Drop capabilities
    "pids_limit": 50,               # Process limit
    "tmpfs": {"/tmp": "size=10m"},  # Temp storage
}
```

---

## Development Workflow

### In Web Instance (This Environment)

**What we CAN do:**
- ✅ Build core framework structure
- ✅ Implement mock LLM and sandbox
- ✅ Create CLI and config system
- ✅ Build FastAPI backend
- ✅ Develop React frontend
- ✅ Write comprehensive tests
- ✅ Test evolutionary algorithm with mocks

**What we CANNOT do:**
- ❌ Run LM Studio (needs local GPU)
- ❌ Run Docker (needs Docker daemon)
- ❌ Test real LLM integration
- ❌ Benchmark actual models

**Strategy:**
```yaml
# config.dev.yaml (for web instance)
llm:
  provider: "template_mock"  # Template-based code generation

sandbox:
  provider: "subprocess"     # Subprocess evaluation (safe enough for dev)
```

### On Local Machine (Your Setup)

**What you'll test:**
- ✅ Real LM Studio with `qwen/qwen3-vl-8b` and `mistralai/magistral-small-2509`
- ✅ Docker sandbox with security hardening
- ✅ GPU-accelerated LLM inference
- ✅ Full parallel execution (8-16 workers)
- ✅ Production-grade experiments

**Strategy:**
```yaml
# config.prod.yaml (for local)
llm:
  provider: "lm_studio"
  base_url: "http://localhost:1234/v1"
  model: "qwen/qwen3-vl-8b"

sandbox:
  provider: "docker"
  max_workers: 16
```

**Seamless switching:**
```python
# Auto-detects LM Studio + Docker availability
config = Config.auto_detect()
funsearch = FunSearchFactory.create_funsearch(config)

# Or explicit
config = Config.from_file(".funsearch/config.prod.yaml")
```

---

## Technology Stack (Finalized)

| Component | Technology | Notes |
|-----------|-----------|-------|
| **Frontend** | React + TypeScript | Component-based UI |
| **UI Library** | Ant Design | Dashboard components, tables, charts |
| **Backend** | FastAPI | Async API, WebSocket, auto-docs |
| **Database** | SQLite → PostgreSQL | Start simple, scale later |
| **LLM (Prod)** | LM Studio Python SDK | OpenAI-compatible local LLMs |
| **LLM (Dev)** | Template Mock | Realistic fake code generation |
| **Sandbox (Prod)** | Docker sibling containers | Secure isolation |
| **Sandbox (Dev)** | Python subprocess | Fast iteration |
| **Experiments** | MLflow | Self-hosted tracking |
| **Task Queue** | Celery + Redis | Async experiment execution |
| **Charts** | Plotly.js | Interactive metrics visualization |
| **State** | React Query + Zustand | Server state + client state |

---

## Implementation Phases (Updated)

### 🚀 Phase 0: Foundation (Week 1) - **START HERE IN WEB INSTANCE**

**Goal**: Core infrastructure with mocks for rapid development

- [ ] Project structure setup
- [ ] Configuration system (YAML + Pydantic validation)
- [ ] Mock LLM sampler (template-based)
- [ ] Mock evaluator (subprocess)
- [ ] Factory pattern for component selection
- [ ] Basic CLI (`funsearch init`, `funsearch run`)
- [ ] Database models (SQLite)
- [ ] Unit tests with mocks

**Deliverable**: Working FunSearch runs with mocks in web instance

---

### 🔧 Phase 1: Backend API (Week 2-3) - **WEB INSTANCE**

**Goal**: REST API and project management

- [ ] FastAPI application structure
- [ ] REST endpoints (projects, experiments, metrics)
- [ ] WebSocket for live updates
- [ ] CRUD operations for projects/experiments
- [ ] Celery tasks for async execution
- [ ] MLflow integration (basic)
- [ ] API tests with mocks

**Deliverable**: Working API you can test locally with real services

---

### 🎨 Phase 2: Frontend Dashboard (Week 4-5) - **WEB INSTANCE**

**Goal**: Web UI for managing experiments

- [ ] React app setup (Create React App or Vite)
- [ ] Ant Design integration
- [ ] Project browser page
- [ ] Experiment runner (model selector, config form)
- [ ] Live monitoring dashboard (mocked data initially)
- [ ] Metrics visualization (Plotly charts)
- [ ] API client with React Query

**Deliverable**: Fully functional UI (works with mocked backend)

---

### 🐳 Phase 3: Production Implementations (Week 6) - **LOCAL TESTING**

**Goal**: Replace mocks with real LM Studio and Docker

**You test locally:**
- [ ] LM Studio sampler implementation
- [ ] Test with `qwen/qwen3-vl-8b`
- [ ] Test with `mistralai/magistral-small-2509`
- [ ] Docker evaluator with security hardening
- [ ] Parallel execution pool (8-16 workers)
- [ ] Performance benchmarking
- [ ] Resource monitoring

**Deliverable**: Full production system running on your machine

---

### 📊 Phase 4: Advanced Features (Week 7-8)

**Goal**: Production-grade capabilities

- [ ] Hyperparameter search
- [ ] Model comparison (A/B testing)
- [ ] Experiment export/import
- [ ] Report generation
- [ ] Enhanced MLflow integration
- [ ] Git integration (auto-commit best programs)

**Deliverable**: Research-ready platform

---

### 🧬 Phase 5: Multi-Domain Support (Week 9-10)

**Goal**: Templates for different problem types

- [ ] Algorithm synthesis template
- [ ] Mathematical optimization template
- [ ] Template system and CLI
- [ ] Example gallery (10+ problems)
- [ ] Documentation and tutorials

**Deliverable**: Framework ready for any problem domain

---

## Proposed Directory Structure

```
funsearch-framework/
├── backend/
│   ├── api/                    # FastAPI routes
│   │   ├── projects.py
│   │   ├── experiments.py
│   │   └── metrics.py
│   ├── core/                   # FunSearch implementation
│   │   ├── funsearch.py        # Main algorithm (existing)
│   │   ├── sampler.py          # Abstract interface
│   │   ├── evaluator.py        # Abstract interface
│   │   ├── lm_studio_sampler.py    # LM Studio implementation
│   │   ├── docker_evaluator.py     # Docker sandbox
│   │   ├── mock_llm.py         # Mock LLM
│   │   ├── mock_sandbox.py     # Mock evaluator
│   │   ├── factory.py          # Component factory
│   │   └── config.py           # Configuration
│   ├── models/                 # Database models
│   │   ├── project.py
│   │   └── experiment.py
│   ├── services/               # Business logic
│   │   ├── project_service.py
│   │   └── experiment_service.py
│   └── tasks/                  # Celery tasks
│       └── run_experiment.py
├── frontend/
│   ├── src/
│   │   ├── components/         # React components
│   │   │   ├── ProjectCard.tsx
│   │   │   ├── ExperimentRunner.tsx
│   │   │   ├── MetricsChart.tsx
│   │   │   └── CodeViewer.tsx
│   │   ├── pages/              # Main pages
│   │   │   ├── HomePage.tsx
│   │   │   ├── ProjectDetail.tsx
│   │   │   └── ExperimentMonitor.tsx
│   │   ├── api/                # API client
│   │   │   └── client.ts
│   │   └── hooks/              # React hooks
│   │       └── useExperiment.ts
│   └── package.json
├── cli/                        # Command-line interface
│   └── main.py
├── templates/                  # Problem templates
│   ├── algorithm_synthesis/
│   └── mathematical_optimization/
├── examples/                   # Example projects
│   ├── lucy_richardson/
│   ├── bin_packing/
│   └── cap_set/
├── tests/
│   ├── test_funsearch.py
│   ├── test_api.py
│   └── test_sandbox.py
├── docker/
│   ├── Dockerfile              # Main app
│   ├── Dockerfile.sandbox      # Sandbox image
│   └── docker-compose.yml
├── docs/
│   ├── FRAMEWORK_PLAN.md       # ✅ Created
│   ├── DOCKER_SANDBOX_ARCHITECTURE.md  # ✅ Created
│   └── MOCK_IMPLEMENTATIONS.md # ✅ Created
├── .funsearch/
│   ├── config.dev.yaml         # Web instance config
│   ├── config.prod.yaml        # Local machine config
│   └── templates/              # Code templates for mocks
├── pyproject.toml
└── README.md
```

---

## Configuration Examples

### Development (Web Instance)

```yaml
# .funsearch/config.dev.yaml
mode: "development"

llm:
  provider: "template_mock"
  model: "mock-qwen-8b"

sandbox:
  provider: "subprocess"
  timeout: 10
  max_workers: 4

funsearch:
  samples_per_prompt: 2
  num_islands: 3
  reset_period: 10000

database:
  url: "sqlite:///dev.db"

mlflow:
  tracking_uri: "sqlite:///mlflow.db"
```

### Production (Your Local Machine)

```yaml
# .funsearch/config.prod.yaml
mode: "production"

llm:
  provider: "lm_studio"
  base_url: "http://localhost:1234/v1"
  model: "qwen/qwen3-vl-8b"
  temperature: 1.0
  max_tokens: 512

sandbox:
  provider: "docker"
  image: "funsearch-sandbox:latest"
  timeout: 30
  max_workers: 16
  limits:
    memory: "256m"
    cpu_cores: 1

funsearch:
  samples_per_prompt: 4
  num_islands: 10
  reset_period: 80000

database:
  url: "sqlite:///production.db"

mlflow:
  tracking_uri: "http://localhost:7352"
```

---

## Next Steps - What Should We Do First?

### Option A: Start with Phase 0 (Foundation)
**Build core infrastructure with mocks in this web instance**

I can immediately start:
1. Set up project structure
2. Implement configuration system
3. Create mock LLM and evaluator
4. Build factory pattern
5. Add CLI commands
6. Write tests

**Pros:**
- Can work entirely in web instance
- Fast iteration without waiting for local setup
- You test real implementations locally in parallel

**Timeline**: 2-3 days to working prototype

---

### Option B: Start with Documentation
**Write detailed specs for you to implement locally**

Create comprehensive docs:
1. API specification (OpenAPI/Swagger)
2. Database schema
3. Component interfaces
4. Step-by-step implementation guide

**Pros:**
- Clear roadmap for implementation
- You can work independently
- Better for understanding architecture

**Timeline**: 1 day for complete specs

---

### Option C: Build Frontend First
**Create UI mockups with fake data**

Build React dashboard:
1. Project browser
2. Experiment runner
3. Live monitoring (with mock data)

**Pros:**
- Visualize end goal
- UI drives API design
- Fun to see progress

**Timeline**: 3-4 days for working UI

---

## My Recommendation: Hybrid Approach

**Week 1 (Web Instance - Me):**
- Phase 0: Build foundation with mocks
- Get working CLI + config system
- Implement factory pattern
- Create comprehensive tests

**Week 1 (Local - You in Parallel):**
- Set up LM Studio
- Download and test models (`qwen3-vl-8b`, `magistral-small-2509`)
- Verify Docker setup
- Test basic LM Studio API calls

**Week 2 (Web Instance - Me):**
- Build FastAPI backend
- Implement REST endpoints
- Add WebSocket support

**Week 2 (Local - You):**
- Pull code from web instance
- Test with real LM Studio
- Implement Docker evaluator together

**Week 3+:**
- Build frontend
- Iterate on real experiments
- Add advanced features

---

## Questions Before We Start

1. **Do you want me to start building Phase 0 now?**
   - I can have a working prototype with mocks in 2-3 days

2. **What problem should we use as first test case?**
   - Lucy-Richardson (already familiar)
   - Bin packing (simpler, faster iteration)
   - New algorithm synthesis problem

3. **Any specific features you want prioritized?**
   - Live monitoring dashboard
   - Model comparison
   - Export/sharing
   - Something else

4. **Timeline constraints?**
   - Rush mode (2 weeks to MVP)
   - Steady pace (6-8 weeks to production)
   - Research mode (explore and experiment)

---

## Resources Created

✅ **FRAMEWORK_PLAN.md** - 12-week roadmap, architecture, tech stack
✅ **DOCKER_SANDBOX_ARCHITECTURE.md** - Security, parallel execution, implementation
✅ **MOCK_IMPLEMENTATIONS.md** - Dev/prod switching, factory pattern, testing
✅ **IMPLEMENTATION_SUMMARY.md** - This document

All committed and pushed to: `claude/learn-funsearch-01MqmhnueQkijA2ykhRQjzJt`

---

**Ready to start building?** Let me know which approach you prefer and I'll get started! 🚀
