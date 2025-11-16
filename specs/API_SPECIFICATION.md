# FunSearch Framework - API Specification

## Overview

This document specifies the RESTful API and WebSocket protocol for the FunSearch framework.

**Base URL**: `http://localhost:7351`
**API Version**: `v1`
**Protocol**: REST + WebSocket
**Format**: JSON

---

## Authentication

**Phase 1**: No authentication (single-user local deployment)
**Future**: Optional JWT tokens for multi-user deployments

---

## REST API Endpoints

### Health & System

#### `GET /health`

Check system health and service connectivity.

**Response** `200 OK`:
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "timestamp": "2025-11-16T12:00:00Z",
  "services": {
    "database": "connected",
    "redis": "connected",
    "mlflow": "connected",
    "lm_studio": "connected",
    "docker": "available"
  },
  "config_mode": "production"
}
```

**Response** `503 Service Unavailable`:
```json
{
  "status": "degraded",
  "version": "0.1.0",
  "timestamp": "2025-11-16T12:00:00Z",
  "services": {
    "database": "connected",
    "redis": "disconnected",
    "mlflow": "connected",
    "lm_studio": "disconnected",
    "docker": "unavailable"
  },
  "errors": [
    "Redis connection failed: Connection refused",
    "LM Studio not responding at http://localhost:1234"
  ]
}
```

---

### Projects

#### `GET /api/v1/projects`

List all projects.

**Query Parameters**:
- `status` (optional): Filter by status (`active`, `paused`, `completed`, `draft`)
- `sort` (optional): Sort field (`created_at`, `updated_at`, `name`)
- `order` (optional): Sort order (`asc`, `desc`)
- `limit` (optional): Page size (default: 50)
- `offset` (optional): Pagination offset (default: 0)

**Response** `200 OK`:
```json
{
  "projects": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "Lucy-Richardson Optimization",
      "description": "Optimize convergence of blind deconvolution",
      "problem_type": "signal_processing",
      "status": "active",
      "created_at": "2025-11-15T10:00:00Z",
      "updated_at": "2025-11-16T12:00:00Z",
      "experiment_count": 5,
      "best_score": 245.67,
      "specification_file": ".funsearch/projects/lucy-richardson/spec.py"
    }
  ],
  "total": 1,
  "limit": 50,
  "offset": 0
}
```

---

#### `POST /api/v1/projects`

Create a new project.

**Request Body**:
```json
{
  "name": "Lucy-Richardson Optimization",
  "description": "Optimize convergence of blind deconvolution",
  "problem_type": "signal_processing",
  "template": "optimization",  // optional
  "specification": {
    "file_content": "# Python code with @funsearch decorators",
    "evolve_function": "stopping_criterion",
    "evaluate_function": "evaluate"
  }
}
```

**Response** `201 Created`:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Lucy-Richardson Optimization",
  "description": "Optimize convergence of blind deconvolution",
  "problem_type": "signal_processing",
  "status": "draft",
  "created_at": "2025-11-16T12:00:00Z",
  "updated_at": "2025-11-16T12:00:00Z",
  "specification_file": ".funsearch/projects/lucy-richardson-optimization/spec.py"
}
```

**Response** `400 Bad Request`:
```json
{
  "error": "validation_error",
  "message": "Invalid project data",
  "details": [
    {
      "field": "name",
      "error": "Project name already exists"
    }
  ]
}
```

---

#### `GET /api/v1/projects/{project_id}`

Get project details.

**Response** `200 OK`:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Lucy-Richardson Optimization",
  "description": "Optimize convergence of blind deconvolution",
  "problem_type": "signal_processing",
  "status": "active",
  "created_at": "2025-11-15T10:00:00Z",
  "updated_at": "2025-11-16T12:00:00Z",
  "specification_file": ".funsearch/projects/lucy-richardson/spec.py",
  "experiments": [
    {
      "id": "660e8400-e29b-41d4-a716-446655440001",
      "name": "Experiment 1 - Qwen 8B",
      "status": "completed",
      "best_score": 245.67,
      "started_at": "2025-11-16T10:00:00Z",
      "completed_at": "2025-11-16T11:30:00Z"
    }
  ],
  "config": {
    "funsearch": {
      "samples_per_prompt": 4,
      "num_islands": 10,
      "reset_period": 80000
    }
  }
}
```

**Response** `404 Not Found`:
```json
{
  "error": "not_found",
  "message": "Project not found"
}
```

---

#### `PATCH /api/v1/projects/{project_id}`

Update project.

**Request Body**:
```json
{
  "name": "Updated Project Name",
  "description": "New description",
  "status": "paused"
}
```

**Response** `200 OK`: (updated project object)

---

#### `DELETE /api/v1/projects/{project_id}`

Delete project and all associated experiments.

**Response** `204 No Content`

**Response** `409 Conflict`:
```json
{
  "error": "conflict",
  "message": "Cannot delete project with running experiments"
}
```

---

### Experiments

#### `GET /api/v1/projects/{project_id}/experiments`

List experiments for a project.

**Query Parameters**:
- `status` (optional): Filter by status
- `limit`, `offset`: Pagination

**Response** `200 OK`:
```json
{
  "experiments": [
    {
      "id": "660e8400-e29b-41d4-a716-446655440001",
      "project_id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "Experiment 1 - Qwen 8B",
      "status": "completed",
      "config": {
        "llm": {
          "model": "qwen/qwen3-vl-8b",
          "temperature": 1.0
        },
        "funsearch": {
          "samples_per_prompt": 4,
          "num_islands": 10
        }
      },
      "started_at": "2025-11-16T10:00:00Z",
      "completed_at": "2025-11-16T11:30:00Z",
      "iterations_completed": 10000,
      "best_score": 245.67,
      "mlflow_run_id": "abc123def456"
    }
  ],
  "total": 1
}
```

---

#### `POST /api/v1/projects/{project_id}/experiments`

Start a new experiment.

**Request Body**:
```json
{
  "name": "Experiment 2 - Mistral Small",
  "config": {
    "llm": {
      "provider": "lm_studio",
      "model": "mistralai/magistral-small-2509",
      "temperature": 1.0,
      "max_tokens": 512
    },
    "sandbox": {
      "provider": "docker",
      "max_workers": 16,
      "timeout": 30
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
}
```

**Response** `202 Accepted`:
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440002",
  "project_id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Experiment 2 - Mistral Small",
  "status": "pending",
  "created_at": "2025-11-16T12:00:00Z",
  "config": { /* ... */ },
  "task_id": "celery-task-abc123"
}
```

**Response** `400 Bad Request`:
```json
{
  "error": "validation_error",
  "message": "Invalid configuration",
  "details": [
    {
      "field": "config.llm.model",
      "error": "Model 'invalid-model' not available in LM Studio"
    }
  ]
}
```

---

#### `GET /api/v1/experiments/{experiment_id}`

Get experiment details with full history.

**Response** `200 OK`:
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "project_id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Experiment 1 - Qwen 8B",
  "status": "running",
  "config": { /* ... */ },
  "started_at": "2025-11-16T10:00:00Z",
  "completed_at": null,
  "iterations_completed": 5000,
  "best_score": 245.67,
  "current_score": 243.12,
  "best_program": "def stopping_criterion(iteration, psnr, psnr_delta):\n    return iteration > 50 and psnr_delta < 0.01",
  "mlflow_run_id": "abc123def456",
  "metrics": {
    "iterations": [0, 1000, 2000, 3000, 4000, 5000],
    "best_scores": [100, 150, 200, 230, 242, 245.67],
    "diversity": [0.8, 0.7, 0.6, 0.5, 0.4, 0.35]
  },
  "island_states": [
    {
      "island_id": 0,
      "population_size": 42,
      "best_score": 245.67,
      "avg_score": 220.5,
      "diversity": 0.42
    }
    // ... 9 more islands
  ]
}
```

---

#### `POST /api/v1/experiments/{experiment_id}/stop`

Stop a running experiment.

**Response** `200 OK`:
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "status": "stopped",
  "stopped_at": "2025-11-16T12:00:00Z",
  "iterations_completed": 5432
}
```

---

#### `POST /api/v1/experiments/{experiment_id}/pause`

Pause a running experiment (can resume later).

**Response** `200 OK`:
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "status": "paused",
  "paused_at": "2025-11-16T12:00:00Z",
  "checkpoint_saved": true
}
```

---

#### `POST /api/v1/experiments/{experiment_id}/resume`

Resume a paused experiment.

**Response** `200 OK`:
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "status": "running",
  "resumed_at": "2025-11-16T12:05:00Z"
}
```

---

### Metrics

#### `GET /api/v1/experiments/{experiment_id}/metrics`

Get real-time metrics for an experiment.

**Query Parameters**:
- `from_iteration` (optional): Start iteration
- `to_iteration` (optional): End iteration
- `interval` (optional): Sample interval (e.g., every 100 iterations)

**Response** `200 OK`:
```json
{
  "experiment_id": "660e8400-e29b-41d4-a716-446655440001",
  "metrics": {
    "iterations": [0, 100, 200, 300, /* ... */],
    "best_score": [100, 120, 145, 160, /* ... */],
    "avg_score": [50, 70, 90, 110, /* ... */],
    "diversity": [0.9, 0.85, 0.8, 0.75, /* ... */],
    "samples_generated": [400, 800, 1200, 1600, /* ... */],
    "successful_evaluations": [320, 680, 1020, 1380, /* ... */]
  }
}
```

---

#### `GET /api/v1/experiments/{experiment_id}/islands`

Get current state of all islands.

**Response** `200 OK`:
```json
{
  "experiment_id": "660e8400-e29b-41d4-a716-446655440001",
  "timestamp": "2025-11-16T12:00:00Z",
  "islands": [
    {
      "island_id": 0,
      "population_size": 42,
      "best_score": 245.67,
      "avg_score": 220.5,
      "worst_score": 150.2,
      "diversity": 0.42,
      "num_clusters": 8,
      "programs": [
        {
          "score": 245.67,
          "code": "def stopping_criterion(...):\n    return iteration > 50",
          "signature": "(50, 0.01, True)",
          "created_at": "2025-11-16T11:45:00Z"
        }
        // Top 10 programs per island
      ]
    }
    // ... 9 more islands
  ]
}
```

---

### Models (LM Studio)

#### `GET /api/v1/models`

List available models from LM Studio.

**Response** `200 OK`:
```json
{
  "models": [
    {
      "id": "qwen/qwen3-vl-8b",
      "name": "Qwen 3 VL 8B",
      "size": "8B",
      "type": "code-generation",
      "loaded": true
    },
    {
      "id": "mistralai/magistral-small-2509",
      "name": "Mistral Small",
      "size": "22B",
      "type": "code-generation",
      "loaded": false
    }
  ],
  "provider": "lm_studio",
  "base_url": "http://localhost:1234/v1"
}
```

**Response** `503 Service Unavailable`:
```json
{
  "error": "service_unavailable",
  "message": "LM Studio is not responding",
  "base_url": "http://localhost:1234/v1"
}
```

---

### Templates

#### `GET /api/v1/templates`

List available project templates.

**Response** `200 OK`:
```json
{
  "templates": [
    {
      "id": "algorithm_synthesis",
      "name": "Algorithm Synthesis",
      "description": "Generate and optimize algorithms (e.g., bin packing)",
      "example_problems": ["bin_packing", "online_scheduling"]
    },
    {
      "id": "mathematical_optimization",
      "name": "Mathematical Optimization",
      "description": "Optimize mathematical functions",
      "example_problems": ["cap_set", "admissible_set"]
    },
    {
      "id": "signal_processing",
      "name": "Signal Processing",
      "description": "Optimize signal processing algorithms",
      "example_problems": ["lucy_richardson", "wiener_filter"]
    }
  ]
}
```

---

#### `GET /api/v1/templates/{template_id}`

Get template details with example code.

**Response** `200 OK`:
```json
{
  "id": "algorithm_synthesis",
  "name": "Algorithm Synthesis",
  "description": "Generate and optimize algorithms",
  "specification_template": "# Python template with placeholders",
  "default_config": {
    "funsearch": {
      "samples_per_prompt": 4,
      "num_islands": 10
    }
  },
  "example": {
    "problem": "bin_packing",
    "code": "# Example implementation"
  }
}
```

---

### Export/Import

#### `GET /api/v1/projects/{project_id}/export`

Export project with all experiments and results.

**Response** `200 OK`:
```json
{
  "export_id": "export-abc123",
  "download_url": "/api/v1/downloads/export-abc123.zip",
  "size_bytes": 1048576,
  "created_at": "2025-11-16T12:00:00Z",
  "expires_at": "2025-11-16T13:00:00Z"
}
```

---

#### `POST /api/v1/projects/import`

Import a project from exported zip file.

**Request**: `multipart/form-data`
- `file`: Zip file

**Response** `201 Created`:
```json
{
  "project_id": "770e8400-e29b-41d4-a716-446655440003",
  "imported_experiments": 5,
  "status": "imported"
}
```

---

## WebSocket Protocol

### Connection

**URL**: `ws://localhost:7351/ws/experiments/{experiment_id}`

**Authentication**: None (Phase 1)

---

### Client → Server Messages

#### Subscribe to Metrics

```json
{
  "type": "subscribe",
  "channels": ["metrics", "islands", "best_program", "logs"]
}
```

#### Unsubscribe

```json
{
  "type": "unsubscribe",
  "channels": ["logs"]
}
```

#### Ping

```json
{
  "type": "ping"
}
```

---

### Server → Client Messages

#### Pong

```json
{
  "type": "pong",
  "timestamp": "2025-11-16T12:00:00Z"
}
```

#### Metrics Update

```json
{
  "type": "metrics_update",
  "timestamp": "2025-11-16T12:00:00Z",
  "data": {
    "iteration": 5000,
    "best_score": 245.67,
    "current_score": 243.12,
    "diversity": 0.42,
    "samples_generated": 20000,
    "successful_evaluations": 16543
  }
}
```

#### Island State Update

```json
{
  "type": "island_update",
  "timestamp": "2025-11-16T12:00:00Z",
  "data": {
    "island_id": 3,
    "best_score": 240.5,
    "population_size": 45,
    "diversity": 0.38
  }
}
```

#### Best Program Update

```json
{
  "type": "best_program_update",
  "timestamp": "2025-11-16T12:00:00Z",
  "data": {
    "iteration": 5432,
    "score": 246.89,
    "previous_score": 245.67,
    "improvement": 1.22,
    "code": "def stopping_criterion(iteration, psnr, psnr_delta):\n    return iteration > 45 and psnr_delta < 0.008"
  }
}
```

#### Log Message

```json
{
  "type": "log",
  "timestamp": "2025-11-16T12:00:00Z",
  "level": "info",
  "message": "Island 3 reset with best programs from island 0"
}
```

#### Experiment Status Change

```json
{
  "type": "status_change",
  "timestamp": "2025-11-16T12:00:00Z",
  "old_status": "running",
  "new_status": "completed",
  "reason": "max_iterations_reached"
}
```

#### Error

```json
{
  "type": "error",
  "timestamp": "2025-11-16T12:00:00Z",
  "error_code": "sandbox_timeout",
  "message": "Sandbox evaluation timed out after 30s",
  "details": {
    "program_id": "prog-123",
    "iteration": 5432
  }
}
```

---

## Error Handling

### Error Response Format

All errors follow this structure:

```json
{
  "error": "error_code",
  "message": "Human-readable error message",
  "details": {
    // Optional additional context
  },
  "timestamp": "2025-11-16T12:00:00Z",
  "request_id": "req-abc123"
}
```

### HTTP Status Codes

| Code | Meaning | When Used |
|------|---------|-----------|
| 200 | OK | Successful GET/PATCH |
| 201 | Created | Successful POST |
| 202 | Accepted | Async operation started |
| 204 | No Content | Successful DELETE |
| 400 | Bad Request | Invalid input data |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | Resource conflict (e.g., name already exists) |
| 422 | Unprocessable Entity | Validation failed |
| 500 | Internal Server Error | Server error |
| 503 | Service Unavailable | Dependency unavailable (LM Studio, Docker) |

### Common Error Codes

- `validation_error`: Input validation failed
- `not_found`: Resource not found
- `conflict`: Resource conflict
- `service_unavailable`: External service unavailable
- `internal_error`: Unexpected server error
- `unauthorized`: Authentication required (future)
- `forbidden`: Insufficient permissions (future)

---

## Rate Limiting

**Phase 1**: No rate limiting (single-user)
**Future**: 100 requests/minute per client

---

## Pagination

All list endpoints support pagination:

**Query Parameters**:
- `limit`: Items per page (default: 50, max: 100)
- `offset`: Number of items to skip (default: 0)

**Response Headers**:
- `X-Total-Count`: Total number of items
- `X-Limit`: Current page size
- `X-Offset`: Current offset

---

## Versioning

API version is included in URL: `/api/v1/...`

Breaking changes will increment the major version (`v2`, `v3`, etc.)

---

## CORS

**Development**: Allow all origins
**Production**: Whitelist specific origins

```python
# FastAPI CORS configuration
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:7350"],  # Frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## OpenAPI Documentation

Auto-generated documentation available at:

- **Swagger UI**: `http://localhost:7351/docs`
- **ReDoc**: `http://localhost:7351/redoc`
- **OpenAPI JSON**: `http://localhost:7351/openapi.json`

---

**Last Updated**: 2025-11-16
**Version**: 1.0
**Status**: Specification
