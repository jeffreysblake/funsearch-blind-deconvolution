# Port Configuration & Service Endpoints

## Port Allocation Scheme

We use the **7350s range** for FunSearch services (mnemonic: **F**un**S**earch → FS → 73xx):

| Service | Port | Protocol | Description |
|---------|------|----------|-------------|
| **React Frontend** | `7350` | HTTP | Web dashboard UI |
| **FastAPI Backend** | `7351` | HTTP/WS | REST API + WebSocket |
| **MLflow Tracking** | `7352` | HTTP | Experiment tracking UI |
| **Redis** | `7353` | TCP | Task queue for Celery |
| **LM Studio** | `1234` | HTTP | Local LLM API (on host machine) |

## Service URLs

### Development (All services on localhost)

```bash
# Frontend
http://localhost:7350

# Backend API
http://localhost:7351
http://localhost:7351/docs          # Swagger UI (auto-generated)
http://localhost:7351/redoc         # ReDoc (alternative docs)

# MLflow
http://localhost:7352               # MLflow tracking UI

# LM Studio
http://localhost:1234/v1            # OpenAI-compatible API
http://localhost:1234/v1/models     # List available models
```

### WebSocket Endpoints

```bash
# Real-time experiment updates
ws://localhost:7351/ws/experiments/{experiment_id}

# Live metrics stream
ws://localhost:7351/ws/metrics/{experiment_id}
```

## Environment Variables

```bash
# Backend (.env or docker-compose.yml)
PORT=7351
FRONTEND_URL=http://localhost:7350
REDIS_URL=redis://localhost:7353
MLFLOW_TRACKING_URI=http://localhost:7352
LM_STUDIO_URL=http://localhost:1234/v1

# Frontend (.env.local)
REACT_APP_API_URL=http://localhost:7351
REACT_APP_WS_URL=ws://localhost:7351
```

## Docker Compose Configuration

```yaml
# docker-compose.yml
version: '3.8'

services:
  # Main application (FastAPI + React)
  funsearch-app:
    build: .
    ports:
      - "7351:7351"  # Backend API
      - "7350:7350"  # Frontend dev server (development only)
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - ./data:/app/data
    environment:
      - PORT=7351
      - FRONTEND_PORT=7350
      - REDIS_URL=redis://redis:6379  # Internal container port
      - MLFLOW_TRACKING_URI=http://mlflow:5000  # Internal container port
      - LM_STUDIO_URL=http://host.docker.internal:1234/v1
    depends_on:
      - redis
      - mlflow

  # Redis (task queue for Celery)
  redis:
    image: redis:7-alpine
    ports:
      - "7353:6379"  # Map internal 6379 to external 7353
    volumes:
      - redis-data:/data

  # MLflow tracking server
  mlflow:
    image: ghcr.io/mlflow/mlflow:latest
    ports:
      - "7352:5000"  # Map internal 5000 to external 7352
    volumes:
      - ./mlflow:/mlflow
    command: >
      mlflow server
      --host 0.0.0.0
      --port 5000
      --backend-store-uri sqlite:///mlflow/mlflow.db
      --default-artifact-root /mlflow/artifacts

  # Celery worker (async experiment execution)
  celery-worker:
    build: .
    command: celery -A backend.tasks worker --loglevel=info
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    environment:
      - REDIS_URL=redis://redis:6379  # Internal container port
      - LM_STUDIO_URL=http://host.docker.internal:1234/v1
    depends_on:
      - redis

volumes:
  redis-data:
```

## Running on Host (Development Mode)

When running all services directly on your host machine:

```bash
# Terminal 1: Start Redis
docker run -p 7353:6379 redis:7-alpine

# Terminal 2: Start MLflow
mlflow server \
  --host 0.0.0.0 \
  --port 7352 \
  --backend-store-uri sqlite:///mlflow/mlflow.db \
  --default-artifact-root ./mlflow/artifacts

# Terminal 3: Start Backend
cd backend
uvicorn main:app --host 0.0.0.0 --port 7351 --reload

# Terminal 4: Start Frontend
cd frontend
PORT=7350 npm start

# Terminal 5: Start Celery Worker (optional, for async tasks)
celery -A backend.tasks worker --loglevel=info
```

## LM Studio Configuration

Your LM Studio instance should be running on `http://localhost:1234`:

```bash
# Test LM Studio connection
curl http://localhost:1234/v1/models

# Example response:
# {
#   "object": "list",
#   "data": [
#     {"id": "qwen/qwen3-vl-8b", ...},
#     {"id": "mistralai/magistral-small-2509", ...}
#   ]
# }
```

### Backend Configuration

```yaml
# .funsearch/config.prod.yaml
llm:
  provider: "lm_studio"
  base_url: "http://localhost:1234/v1"
  model: "qwen/qwen3-vl-8b"
```

## Firewall Configuration

If running on a remote server and need external access:

```bash
# Ubuntu/Debian (ufw)
sudo ufw allow 7350/tcp comment "FunSearch Frontend"
sudo ufw allow 7351/tcp comment "FunSearch Backend"
sudo ufw allow 7352/tcp comment "FunSearch MLflow"

# Or allow entire range
sudo ufw allow 7350:7352/tcp comment "FunSearch Services"
```

## Port Conflict Resolution

If ports are already in use, check and kill existing processes:

```bash
# Check what's using a port
lsof -i :7351
# or
netstat -tlnp | grep 7351

# Kill process using port
kill -9 $(lsof -t -i:7351)
```

## Production Deployment

For production, consider using a reverse proxy:

### Nginx Configuration

```nginx
# /etc/nginx/sites-available/funsearch
server {
    listen 80;
    server_name funsearch.yourdomain.com;

    # Frontend
    location / {
        proxy_pass http://localhost:7350;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:7351/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # WebSocket (for live updates)
    location /ws/ {
        proxy_pass http://localhost:7351/ws/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }

    # MLflow
    location /mlflow/ {
        proxy_pass http://localhost:7352/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Then access everything via:
- Frontend: `http://funsearch.yourdomain.com`
- API: `http://funsearch.yourdomain.com/api`
- MLflow: `http://funsearch.yourdomain.com/mlflow`

## Health Checks

### Backend Health Check

```bash
# Check backend is running
curl http://localhost:7351/health

# Expected response:
# {
#   "status": "healthy",
#   "version": "0.1.0",
#   "services": {
#     "redis": "connected",
#     "mlflow": "connected",
#     "lm_studio": "connected"
#   }
# }
```

### Frontend Health Check

```bash
# Check frontend is running
curl http://localhost:7350

# Should return HTML
```

### MLflow Health Check

```bash
# Check MLflow is running
curl http://localhost:7352/health

# Should return {"status": "OK"}
```

## Service Dependencies

```
┌─────────────────────────────────────────────┐
│  LM Studio (localhost:1234)                 │
│  - Runs on host machine                     │
│  - Needs GPU access                         │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│  FastAPI Backend (localhost:7351)           │
│  - REST API + WebSocket                     │
│  - Spawns sandbox containers via Docker     │
└──┬───────────────┬──────────────────────────┘
   │               │
   │          ┌────▼─────────────────────────┐
   │          │  Redis (localhost:6379)      │
   │          │  - Task queue for Celery     │
   │          └──────────────────────────────┘
   │
   │          ┌──────────────────────────────┐
   └─────────►│  MLflow (localhost:7352)     │
              │  - Experiment tracking       │
              └──────────────────────────────┘

┌─────────────────────────────────────────────┐
│  React Frontend (localhost:7350)            │
│  - Connects to Backend API (7351)           │
│  - WebSocket for live updates               │
└─────────────────────────────────────────────┘
```

## Troubleshooting

### "Connection refused" errors

```bash
# 1. Check service is running
ps aux | grep uvicorn
ps aux | grep mlflow
ps aux | grep redis

# 2. Check port is listening
netstat -tlnp | grep 7351
netstat -tlnp | grep 7352

# 3. Check firewall
sudo ufw status

# 4. Check Docker (if using containers)
docker ps
docker logs <container_name>
```

### "Port already in use" errors

```bash
# Find and kill the process
lsof -ti:7351 | xargs kill -9

# Or use different ports in config
PORT=7361 uvicorn main:app
```

### WebSocket connection fails

```bash
# Check CORS settings in backend
# Ensure WebSocket upgrade headers are allowed

# Test WebSocket connection
websocat ws://localhost:7351/ws/test
```

## Quick Reference Card

```
╔═══════════════════════════════════════════════╗
║         FunSearch Service Ports              ║
╠═══════════════════════════════════════════════╣
║  Service          Port      URL              ║
╠═══════════════════════════════════════════════╣
║  Frontend         7350      localhost:7350   ║
║  Backend          7351      localhost:7351   ║
║  MLflow           7352      localhost:7352   ║
║  Redis            7353      localhost:7353   ║
║  LM Studio        1234      localhost:1234   ║
╠═══════════════════════════════════════════════╣
║  Mnemonic: FS (FunSearch) = 7350-7353        ║
╚═══════════════════════════════════════════════╝
```

---

**Last Updated**: 2025-11-16
**Port Scheme**: 7350-7353 (FunSearch services)
