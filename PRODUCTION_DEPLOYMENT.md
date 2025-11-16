# Production Deployment Guide

Complete guide for deploying FunSearch in production with Docker, Celery, and distributed execution.

---

## 📋 Prerequisites

### Required
- **Docker** >= 20.10
- **Docker Compose** >= 2.0
- **8GB RAM minimum** (16GB+ recommended)
- **20GB disk space** (for images, data, MLflow artifacts)

### Optional
- **NVIDIA GPU** with CUDA (for faster LLM inference)
- **Domain name** (for HTTPS deployment)
- **SSL certificate** (Let's Encrypt recommended)

---

## 🚀 Quick Start

### 1. Clone and Configure

```bash
# Clone repository
git clone https://github.com/yourorg/funsearch.git
cd funsearch

# Create environment file
cp .env.example .env

# Edit .env with your settings
nano .env
```

**Critical .env settings:**
- `POSTGRES_PASSWORD`: Strong password for PostgreSQL
- `SECRET_KEY`: Random secret key for sessions
- `ALLOWED_HOSTS`: Your domain names

### 2. Build and Start

```bash
# Build all containers
./deploy.sh build

# Initialize sandbox image
./deploy.sh init-sandbox

# Start all services
./deploy.sh up
```

### 3. Verify Deployment

```bash
# Check service status
./deploy.sh status

# View logs
./deploy.sh logs

# Test health endpoint
curl http://localhost:7351/health
```

**Expected output:**
```json
{
  "status": "healthy",
  "services": {
    "database": "connected",
    "redis": "connected",
    "mlflow": "connected",
    "lm_studio": "disconnected"
  }
}
```

---

## 🏗️ Architecture

### Service Overview

```
┌─────────────┐
│   Frontend  │  (React + Nginx)
│   :7350     │
└──────┬──────┘
       │
┌──────▼──────┐     ┌──────────┐
│   Backend   │────▶│PostgreSQL│
│   :7351     │     │  :5432   │
└──────┬──────┘     └──────────┘
       │
       ├─────────▶┌─────────┐
       │          │  Redis  │
       │          │  :6379  │
       │          └─────────┘
       │                ▲
       │                │
┌──────▼──────┐  ┌─────┴──────┐
│  Worker x2  │  │   Flower   │
│   (Celery)  │  │   :5555    │
└─────────────┘  └────────────┘
       │
┌──────▼──────┐
│   MLflow    │
│   :5000     │
└─────────────┘
```

### Data Flow

1. **User → Frontend** (port 7350)
2. **Frontend → Backend** (REST API or WebSocket)
3. **Backend → Celery** (via Redis queue)
4. **Worker → PostgreSQL** (experiment data)
5. **Worker → MLflow** (metrics tracking)
6. **Worker → Docker** (code execution in sandbox)

---

## ⚙️ Configuration

### Environment Variables

#### Database
```bash
POSTGRES_PASSWORD=your_secure_password
DATABASE_URL=postgresql://funsearch:password@postgres:5432/funsearch
```

#### Redis / Celery
```bash
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
```

#### MLflow
```bash
MLFLOW_TRACKING_URI=http://mlflow:5000
```

#### LM Studio (Host)
```bash
# Access LM Studio running on host machine
LM_STUDIO_URL=http://host.docker.internal:1234/v1
```

#### Security
```bash
SECRET_KEY=$(openssl rand -hex 32)
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

### Docker Compose Scaling

```yaml
# In docker-compose.yml, adjust worker replicas:
worker:
  deploy:
    replicas: 4  # Scale to 4 workers
```

Or dynamically:
```bash
./deploy.sh scale-workers 4
```

---

## 🔒 Security

### 1. Database Security

```yaml
# Use strong passwords
POSTGRES_PASSWORD=$(openssl rand -base64 32)

# Restrict network access
postgres:
  networks:
    - funsearch  # Internal network only
```

### 2. Docker Sandbox Isolation

The sandbox provides multiple security layers:

- ✅ **No network access**: `network_disabled: true`
- ✅ **Read-only filesystem**: `read_only: true`
- ✅ **Memory limits**: `mem_limit: 256m`
- ✅ **CPU limits**: `nano_cpus: 1000000000`
- ✅ **Non-root user**: Runs as UID 2000
- ✅ **Execution timeout**: 30 seconds default

### 3. API Security

```python
# Add authentication middleware (optional)
from fastapi import Security, HTTPBearer

security = HTTPBearer()

@app.middleware("http")
async def authenticate(request: Request, call_next):
    # Your authentication logic
    pass
```

### 4. Nginx Security Headers

Already configured in `docker/nginx.conf`:
```nginx
add_header X-Frame-Options "SAMEORIGIN";
add_header X-Content-Type-Options "nosniff";
add_header X-XSS-Protection "1; mode=block";
```

---

## 📊 Monitoring

### Flower (Celery Tasks)

Access at `http://localhost:5555`

Features:
- View active/completed/failed tasks
- Monitor worker status
- Task execution times
- Worker resource usage

### MLflow (Experiments)

Access at `http://localhost:7352`

Features:
- Compare experiments
- View metrics over time
- Download best programs
- Track model parameters

### Application Logs

```bash
# All services
./deploy.sh logs

# Specific service
./deploy.sh logs backend
./deploy.sh logs worker

# Follow logs in real-time
docker-compose logs -f backend worker
```

### Health Checks

```bash
# Backend health
curl http://localhost:7351/health

# PostgreSQL health
docker-compose exec postgres pg_isready -U funsearch

# Redis health
docker-compose exec redis redis-cli ping
```

---

## 🔄 Backup & Restore

### Automatic Backups

```bash
# Create backup
./deploy.sh backup

# Backups stored in ./backups/YYYYMMDD_HHMMSS/
```

**Backup includes:**
- PostgreSQL database dump
- MLflow artifacts
- Configuration files

### Manual Backups

```bash
# Database only
docker-compose exec postgres pg_dump -U funsearch funsearch > backup.sql

# MLflow artifacts only
docker cp funsearch-mlflow:/mlflow/artifacts ./mlflow_backup
```

### Restore

```bash
# Restore from backup
./deploy.sh restore ./backups/20250116_120000/
```

---

## 🚦 Scaling

### Horizontal Scaling (Multiple Workers)

```bash
# Scale to 4 workers
./deploy.sh scale-workers 4

# Or in docker-compose.yml:
worker:
  deploy:
    replicas: 4
```

**When to scale:**
- Running multiple experiments concurrently
- Large islands (10+ islands)
- High sampling rate (10+ samples/prompt)

**Resource calculation:**
- Each worker: ~2GB RAM
- 4 workers = 8GB RAM minimum

### Vertical Scaling (Larger Machines)

Update resource limits in `docker-compose.yml`:

```yaml
worker:
  deploy:
    resources:
      limits:
        cpus: '4.0'
        memory: 8G
      reservations:
        cpus: '2.0'
        memory: 4G
```

### GPU Support

For GPU-accelerated LLM inference:

```yaml
worker:
  deploy:
    resources:
      reservations:
        devices:
          - driver: nvidia
            count: 1
            capabilities: [gpu]
```

Requires:
- NVIDIA GPU
- nvidia-docker2 installed
- CUDA-compatible LM Studio model

---

## 🐛 Troubleshooting

### "Cannot connect to Docker daemon"

**Problem**: Docker not running or permission issues

**Solution**:
```bash
# Start Docker
sudo systemctl start docker

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

### "Port already in use"

**Problem**: Another service using ports 7350-7353

**Solution**:
```bash
# Find process using port
sudo lsof -i :7351

# Change ports in .env
BACKEND_PORT=8351
FRONTEND_PORT=8350
```

### "Worker not picking up tasks"

**Problem**: Celery workers not connected to Redis

**Solution**:
```bash
# Check worker logs
./deploy.sh logs worker

# Restart workers
docker-compose restart worker

# Check Redis connection
docker-compose exec worker celery -A backend.celery_app inspect ping
```

### "Out of memory"

**Problem**: Too many workers or large experiments

**Solution**:
```bash
# Reduce worker count
./deploy.sh scale-workers 1

# Increase swap space
sudo dd if=/dev/zero of=/swapfile bs=1G count=4
sudo mkswap /swapfile
sudo swapon /swapfile

# Or reduce island count in experiments
{
  "funsearch": {
    "num_islands": 5  # Instead of 10
  }
}
```

### "Database migration failed"

**Problem**: Schema mismatch

**Solution**:
```bash
# Run migrations
./deploy.sh migrate

# If that fails, reset database (DESTRUCTIVE!)
docker-compose down -v
./deploy.sh up
```

---

## 🔧 Maintenance

### Regular Tasks

**Daily:**
- Monitor disk space: `df -h`
- Check service health: `./deploy.sh status`
- Review error logs: `./deploy.sh logs | grep ERROR`

**Weekly:**
- Create backup: `./deploy.sh backup`
- Update dependencies: `docker-compose pull`
- Clean old containers: `docker system prune -f`

**Monthly:**
- Rotate logs
- Archive old experiments
- Update SSL certificates (if using HTTPS)

### Updates

```bash
# Pull latest code
git pull origin main

# Rebuild containers
./deploy.sh build

# Restart services
./deploy.sh restart

# Run migrations if needed
./deploy.sh migrate
```

---

## 🌐 HTTPS Setup (Production)

### Using Let's Encrypt

```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d yourdomain.com

# Update nginx.conf
server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # ... rest of config
}

# Auto-renewal
sudo certbot renew --dry-run
```

---

## 📈 Performance Tuning

### PostgreSQL

```yaml
postgres:
  command: postgres -c shared_buffers=256MB -c max_connections=200
```

### Redis

```yaml
redis:
  command: redis-server --maxmemory 512mb --maxmemory-policy allkeys-lru
```

### Celery Workers

```yaml
worker:
  command: >
    celery -A backend.celery_app worker
    --concurrency=4
    --max-tasks-per-child=100
    --loglevel=info
```

### Nginx

```nginx
# Enable caching
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=my_cache:10m;
proxy_cache_valid 200 60m;
```

---

## ✅ Production Checklist

Before going live:

- [ ] Strong passwords set in .env
- [ ] SECRET_KEY is random and secure
- [ ] ALLOWED_HOSTS configured
- [ ] SSL certificate installed
- [ ] Firewall rules configured
- [ ] Backup system tested
- [ ] Monitoring alerts configured
- [ ] Worker count appropriate for load
- [ ] Disk space sufficient (20GB+)
- [ ] Resource limits set
- [ ] Health checks passing
- [ ] Load testing completed
- [ ] Security audit done
- [ ] Documentation updated

---

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Celery Documentation](https://docs.celeryproject.org/)
- [MLflow Documentation](https://mlflow.org/docs/latest/index.html)
- [FastAPI Production](https://fastapi.tiangolo.com/deployment/)
- [PostgreSQL Tuning](https://wiki.postgresql.org/wiki/Tuning_Your_PostgreSQL_Server)

---

## 🆘 Support

For issues:
1. Check logs: `./deploy.sh logs`
2. Review health: `curl http://localhost:7351/health`
3. Consult troubleshooting section above
4. Check GitHub issues
5. Contact support team

---

**Version**: 1.0
**Last Updated**: 2025-01-16
**Status**: Production Ready ✅
