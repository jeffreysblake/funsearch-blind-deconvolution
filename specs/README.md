# FunSearch Framework - Technical Specifications

This directory contains comprehensive technical specifications for the FunSearch framework evolution.

## 📋 Documentation Index

### Architecture & Planning

1. **[FRAMEWORK_PLAN.md](../FRAMEWORK_PLAN.md)** (Root directory)
   - 12-week implementation roadmap
   - Complete system architecture
   - Technology stack decisions
   - 5-phase development plan
   - Risk mitigation strategies

2. **[DOCKER_SANDBOX_ARCHITECTURE.md](../DOCKER_SANDBOX_ARCHITECTURE.md)** (Root directory)
   - Docker sibling container security architecture
   - Parallel execution strategy
   - Resource limits and hardening
   - Performance optimization

3. **[MOCK_IMPLEMENTATIONS.md](../MOCK_IMPLEMENTATIONS.md)** (Root directory)
   - Mock LLM and sandbox for development
   - Factory pattern for component switching
   - Auto-detection of available services
   - Testing strategies

4. **[IMPLEMENTATION_SUMMARY.md](../IMPLEMENTATION_SUMMARY.md)** (Root directory)
   - Final decisions summary
   - Port configuration (7350-7353)
   - Development workflow
   - Next steps guidance

5. **[PORTS_AND_SERVICES.md](../PORTS_AND_SERVICES.md)** (Root directory)
   - Complete port allocation scheme
   - Docker Compose configuration
   - Health checks and monitoring
   - Troubleshooting guide

### Backend Specifications

6. **[API_SPECIFICATION.md](./API_SPECIFICATION.md)**
   - REST API endpoints (projects, experiments, metrics)
   - WebSocket protocol for real-time updates
   - Request/response schemas
   - Error handling patterns
   - OpenAPI/Swagger documentation

7. **[DATABASE_SCHEMA.md](./DATABASE_SCHEMA.md)**
   - Complete database schema (PostgreSQL/SQLite)
   - SQLAlchemy 2.0 models
   - Migration strategy with Alembic
   - Query patterns and optimization
   - Backup and recovery procedures

8. **[DATA_MODELS.md](./DATA_MODELS.md)**
   - Pydantic v2 models for Python/FastAPI
   - TypeScript interfaces for React
   - Configuration schemas
   - Validation examples
   - Type conversions and guards

9. **[COMPONENT_INTERFACES.md](./COMPONENT_INTERFACES.md)**
   - Abstract interfaces (Sampler, Evaluator, ProgramsDatabase)
   - Service interfaces (ProjectService, ExperimentService)
   - Factory pattern for dependency injection
   - Test doubles (mocks, spies, fakes)
   - Contract specifications

### Frontend Specifications

10. **[FRONTEND_DESIGN.md](./FRONTEND_DESIGN.md)**
    - Complete page wireframes
    - Component hierarchy
    - Design system (colors, typography, spacing)
    - Responsive behavior
    - Accessibility guidelines (WCAG AA)

11. **[COMPONENT_CATALOG.md](./COMPONENT_CATALOG.md)**
    - Complete React component catalog
    - TypeScript prop interfaces
    - Usage examples
    - Custom hooks
    - State management patterns

---

## 🏗️ Technology Stack

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Database**: SQLite (dev) → PostgreSQL (prod)
- **ORM**: SQLAlchemy 2.0
- **Validation**: Pydantic v2
- **Task Queue**: Celery + Redis
- **Experiment Tracking**: MLflow (self-hosted)
- **LLM Integration**: LM Studio Python SDK
- **Sandboxing**: Docker (sibling containers)

### Frontend
- **Framework**: React 18+ with TypeScript
- **UI Library**: Ant Design 5.x
- **Charts**: Plotly.js
- **State Management**: Zustand (client), React Query (server)
- **Routing**: React Router
- **Build Tool**: Vite

### Infrastructure
- **Ports**: 7350-7353 (Frontend, Backend, MLflow, Redis)
- **Deployment**: Docker Compose
- **LLM**: LM Studio (localhost:1234)

---

## 📊 Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                   React Frontend                        │
│                   (Port 7350)                           │
│  - Project Management  - Experiment Runner              │
│  - Real-time Monitoring  - Metrics Visualization        │
└────────────────┬────────────────────────────────────────┘
                 │ HTTP + WebSocket
┌────────────────▼────────────────────────────────────────┐
│              FastAPI Backend                            │
│              (Port 7351)                                │
│  - REST API  - WebSocket  - Business Logic              │
└─┬──────────┬──────────┬──────────┬──────────────────────┘
  │          │          │          │
  ▼          ▼          ▼          ▼
┌───────┐┌────────┐┌────────┐┌──────────────────────────┐
│SQLite ││MLflow  ││Redis   ││ LM Studio                │
│(7350) ││(7352)  ││(7353)  ││ (1234)                   │
└───────┘└────────┘└────────┘└──────────────────────────┘
                              │
                              ▼
                   ┌──────────────────────┐
                   │  FunSearch Core      │
                   │  - Sampler (LLM)     │
                   │  - Evaluator (Sandbox)│
                   │  - Evolution Engine  │
                   └──────────────────────┘
                              │
                              ▼
                   ┌──────────────────────┐
                   │  Docker Sandboxes    │
                   │  (Parallel execution)│
                   └──────────────────────┘
```

---

## 🚀 Implementation Phases

### ✅ Phase 0: Specifications (Completed)
- Architecture planning
- API design
- Database schema
- Frontend mockups

### 🔨 Phase 1: Foundation (Weeks 1-2)
- Project structure
- Configuration system (YAML)
- Mock LLM and sandbox
- Factory pattern
- CLI tools
- Database setup

### 🔨 Phase 2: Backend API (Weeks 3-4)
- FastAPI application
- REST endpoints
- WebSocket support
- Project/Experiment CRUD
- Celery tasks
- MLflow integration

### 🎨 Phase 3: Frontend (Weeks 5-6)
- React application
- Ant Design integration
- Project browser
- Experiment runner
- Live monitoring dashboard
- Charts and visualizations

### 🐳 Phase 4: Production (Week 7)
- LM Studio integration
- Docker evaluator
- Security hardening
- Performance optimization

### 📊 Phase 5: Advanced Features (Weeks 8-10)
- Hyperparameter search
- Model comparison
- Export/import
- Report generation

---

## 🎯 Key Decisions

### Port Allocation
All services use the **7350-7353** range (mnemonic: **FS** = FunSearch):
- 7350: React Frontend
- 7351: FastAPI Backend
- 7352: MLflow Tracking
- 7353: Redis

### Security Architecture
- **App runs on host or in container**
- **Sandboxing via Docker sibling containers** (not nested)
- **Network disabled, resource limited, read-only filesystem**
- **RestrictedPython rejected** (not secure enough)

### Development Strategy
- **Mocks for web instance development** (template-based LLM, subprocess sandbox)
- **Real services for local testing** (LM Studio, Docker)
- **Factory pattern for seamless switching**

### LLM Models
- Primary: `qwen/qwen3-vl-8b`
- Secondary: `mistralai/magistral-small-2509`

### Problem Domains
- Algorithm synthesis
- Mathematical optimization
- (Future: Signal processing, neural architecture search)

---

## 📝 How to Use These Specs

### For Implementation
1. Read **FRAMEWORK_PLAN.md** for overall vision
2. Review **API_SPECIFICATION.md** for endpoint contracts
3. Check **DATABASE_SCHEMA.md** for data models
4. Reference **COMPONENT_INTERFACES.md** for abstractions
5. Follow **FRONTEND_DESIGN.md** for UI implementation

### For Review
1. **Architecture decisions**: FRAMEWORK_PLAN.md, DOCKER_SANDBOX_ARCHITECTURE.md
2. **API contracts**: API_SPECIFICATION.md, DATA_MODELS.md
3. **Database design**: DATABASE_SCHEMA.md
4. **Frontend design**: FRONTEND_DESIGN.md, COMPONENT_CATALOG.md

### For Testing
1. **Component interfaces**: COMPONENT_INTERFACES.md
2. **Mock implementations**: MOCK_IMPLEMENTATIONS.md
3. **Test data**: DATABASE_SCHEMA.md (seed data)

---

## 🧪 Testing Strategy

### Unit Tests
- Mock all external dependencies (LM Studio, Docker, MLflow)
- Test core FunSearch algorithm with deterministic mocks
- Test API endpoints with FastAPI TestClient
- Test React components with React Testing Library

### Integration Tests
- Test with real LM Studio + Docker (local only)
- Test WebSocket communication
- Test database migrations
- Test full experiment lifecycle

### E2E Tests
- Cypress for frontend flows
- Test project creation → experiment start → monitoring
- Test pause/resume/stop functionality

---

## 📦 Deliverables

Each phase produces working, tested code:

1. **Phase 1**: Working CLI that runs experiments with mocks
2. **Phase 2**: Working API with Swagger docs
3. **Phase 3**: Working UI with all pages
4. **Phase 4**: Production-ready system with real LLMs
5. **Phase 5**: Feature-complete platform

---

## 🔗 Related Documentation

- **Existing Code**: `/home/user/funsearch-blind-deconvolution/implementation/`
- **Lucy-Richardson Example**: `/home/user/funsearch-blind-deconvolution/blind_deconvolution/`
- **Google DeepMind FunSearch**: https://github.com/google-deepmind/funsearch
- **LM Studio Docs**: https://lmstudio.ai/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **Ant Design Docs**: https://ant.design

---

## 💡 Quick Reference

### Start Development Server (Future)
```bash
# Backend
uvicorn backend.main:app --port 7351 --reload

# Frontend
cd frontend && PORT=7350 npm start

# Redis
docker run -p 7353:6379 redis:7-alpine

# MLflow
mlflow server --port 7352 --backend-store-uri sqlite:///mlflow.db
```

### Run Tests (Future)
```bash
# Backend tests
pytest backend/tests/

# Frontend tests
cd frontend && npm test

# E2E tests
cd frontend && npm run test:e2e
```

### Access Services
- Frontend: http://localhost:7350
- Backend API: http://localhost:7351/docs
- MLflow: http://localhost:7352
- LM Studio: http://localhost:1234

---

**Documentation Version**: 1.0
**Last Updated**: 2025-11-16
**Status**: Complete - Ready for Implementation
**Next Step**: Begin Phase 1 (Foundation)
