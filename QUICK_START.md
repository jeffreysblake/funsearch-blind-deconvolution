# Quick Start Guide

Get the FunSearch framework running in minutes!

---

## 🚀 Start Backend API

```bash
# Option 1: Use startup script
./start-api.sh

# Option 2: Manual start
uvicorn backend.main:app --host 0.0.0.0 --port 7351 --reload
```

**Backend will be available at:**
- API: http://localhost:7351
- Interactive Docs: http://localhost:7351/docs
- Health Check: http://localhost:7351/health

---

## 🎨 Start Frontend

```bash
cd frontend
npm run dev
```

**Frontend will be available at:**
- http://localhost:7350

---

## 🧪 Test the API

### Using the Interactive Docs

1. Visit http://localhost:7351/docs
2. Try these endpoints:
   - GET `/health` - Check system status
   - GET `/api/v1/templates` - View available templates
   - GET `/api/v1/models` - List available LLM models
   - POST `/api/v1/projects` - Create a new project

### Using cURL

```bash
# Health check
curl http://localhost:7351/health | jq

# List templates
curl http://localhost:7351/api/v1/templates | jq

# List models
curl http://localhost:7351/api/v1/models | jq

# Create a project
curl -X POST http://localhost:7351/api/v1/projects \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Project",
    "description": "My first FunSearch project",
    "problem_type": "optimization",
    "specification": {
      "file_content": "# Test specification",
      "evolve_function": "priority",
      "evaluate_function": "evaluate"
    }
  }' | jq

# List projects
curl http://localhost:7351/api/v1/projects | jq
```

### Test WebSocket

```bash
# Install websocat if needed
# cargo install websocat

# Connect to experiment WebSocket (replace UUID with actual experiment ID)
websocat ws://localhost:7351/ws/experiments/YOUR-EXPERIMENT-ID

# Send ping
{"type": "ping"}

# Subscribe to channels
{"type": "subscribe", "channels": ["metrics", "logs", "status"]}
```

---

## 🧪 Test with CLI

```bash
# Test configuration
python -m cli.main test

# Check system info
python -m cli.main info

# Initialize a project
python -m cli.main init my-project
```

---

## 📊 Test Full Stack

With both backend and frontend running:

1. Open http://localhost:7350 in your browser
2. You should see the FunSearch homepage
3. Click "New Project" to create a project
4. The frontend will call the backend API
5. View the project in the dashboard

---

## 🧪 Run Convergence Tests (NEW!)

Test the complete FunSearch flow **without LM Studio**:

```bash
# Automated test with monitoring
./test_convergence.sh

# Choose between:
# 1. Number Sequence (5-10 min, quick test)
# 2. Knapsack Heuristic (15-30 min, realistic test)
```

The script will:
- ✅ Create a project
- ✅ Start an experiment
- ✅ Monitor progress in real-time
- ✅ Show final results

**Manual test alternative:**

```bash
# Start backend
./start-api.sh

# In another terminal, create project
curl -X POST http://localhost:7351/api/v1/projects \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Project",
    "description": "Convergence test",
    "problem_type": "optimization",
    "specification": {
      "file_path": "examples/knapsack/specification.py",
      "evolve_function": "priority",
      "evaluate_function": "evaluate"
    }
  }' | jq

# Start experiment (replace PROJECT_ID)
curl -X POST http://localhost:7351/api/v1/projects/{PROJECT_ID}/experiments \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Quick Test",
    "config": {
      "llm": {"provider": "mock"},
      "sandbox": {"provider": "subprocess"},
      "funsearch": {
        "samples_per_prompt": 4,
        "num_islands": 10,
        "reset_period": 1800
      },
      "execution": {"max_iterations": 1000}
    }
  }' | jq

# Monitor via WebSocket
websocat ws://localhost:7351/ws/experiments/{EXPERIMENT_ID}
# Send: {"type": "subscribe", "channels": ["metrics", "logs"]}
```

---

## 🔍 Verify Everything Works

Run this checklist:

- [ ] Backend starts without errors
- [ ] Can access http://localhost:7351/docs
- [ ] Health endpoint returns status
- [ ] Can list templates
- [ ] Can create a project
- [ ] Frontend starts without errors
- [ ] Can access http://localhost:7350
- [ ] Frontend connects to backend API

---

## 🐛 Troubleshooting

### "ModuleNotFoundError"
```bash
# Install dependencies
pip install -e ".[dev]"
cd frontend && npm install
```

### "Port already in use"
```bash
# Kill process on port 7351
lsof -ti:7351 | xargs kill -9

# Or use different port
uvicorn backend.main:app --port 8000 --reload
```

### "Cannot connect to database"
```bash
# Database is created automatically on first run
# If issues, delete and restart:
rm funsearch.db
./start-api.sh
```

### Frontend can't reach backend
```bash
# Check CORS settings in backend/main.py
# Ensure frontend URL is in allow_origins list
```

---

## 📖 Next Steps

- **Test without LM Studio**: Run `./test_convergence.sh` (see examples above)
- **Read examples**: Check `examples/number_sequence/` and `examples/knapsack/`
- **Understand features**: See [FEATURES_WITHOUT_LM_STUDIO.md](FEATURES_WITHOUT_LM_STUDIO.md)
- **Plan ahead**: Read [FRAMEWORK_PLAN.md](FRAMEWORK_PLAN.md) for the complete roadmap
- **Browse specs**: Check [specs/](specs/) for detailed technical documentation
- **API reference**: See [API_SPECIFICATION.md](specs/API_SPECIFICATION.md) for all endpoints
- **UI design**: View [FRONTEND_DESIGN.md](specs/FRONTEND_DESIGN.md) for UI components

---

## 🎯 What's Available Now

### Backend (Phase 1 ✅)
- Complete REST API (16 endpoints)
- 5 endpoint groups (Health, Projects, Experiments, Models, Templates)
- WebSocket for real-time updates
- Auto-generated OpenAPI docs
- CORS configured for frontend
- SQLite database with SQLAlchemy
- **NEW**: Experiment runner service (works without LM Studio!)

### Frontend (Phase 0 ✅)
- Complete React app with TypeScript
- All pages implemented
- API client configured
- State management (React Query + Zustand)
- Ant Design UI components
- Responsive design

### Core (Phase 0 ✅)
- Configuration system
- Mock LLM and evaluator (template-based)
- Factory pattern
- Database models
- CLI tool
- **NEW**: Core FunSearch algorithm (from Google DeepMind)

### Examples (NEW! ✅)
- Number Sequence: 5-10 min convergence test
- Knapsack Heuristic: 15-30 min realistic test
- Both work with mock LLM (no LM Studio needed)

---

**Status**: Phases 0 & 1 Complete ✅ + **Working End-to-End Tests**
**Ready for**:
- ✅ **Testing the full framework with mock LLM**
- ⏭️ Local testing with LM Studio + Docker (Phase 2)
