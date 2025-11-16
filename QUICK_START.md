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

- Read [FRAMEWORK_PLAN.md](FRAMEWORK_PLAN.md) for the complete roadmap
- Browse [specs/](specs/) for detailed technical documentation
- Check [API_SPECIFICATION.md](specs/API_SPECIFICATION.md) for all endpoints
- View [FRONTEND_DESIGN.md](specs/FRONTEND_DESIGN.md) for UI components

---

## 🎯 What's Available Now

### Backend (Phase 1 ✅)
- Complete REST API
- 5 endpoint groups (Health, Projects, Experiments, Models, Templates)
- WebSocket for real-time updates
- Auto-generated OpenAPI docs
- CORS configured for frontend
- SQLite database with SQLAlchemy

### Frontend (Phase 0 ✅)
- Complete React app with TypeScript
- All pages implemented
- API client configured
- State management (React Query + Zustand)
- Ant Design UI components
- Responsive design

### Core (Phase 0 ✅)
- Configuration system
- Mock LLM and evaluator
- Factory pattern
- Database models
- CLI tool

---

**Status**: Phases 0 & 1 Complete ✅
**Ready for**: Local testing with LM Studio + Docker (Phase 2)
