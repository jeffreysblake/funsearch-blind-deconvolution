"""FastAPI application for FunSearch framework."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api import experiments, health, models, projects, templates, websocket
from backend.models import init_db

# Create FastAPI app
app = FastAPI(
    title="FunSearch Framework API",
    description="REST API for program synthesis using evolutionary algorithms + LLMs",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:7350",  # React dev server
        "http://127.0.0.1:7350",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(projects.router, prefix="/api/v1", tags=["Projects"])
app.include_router(experiments.router, prefix="/api/v1", tags=["Experiments"])
app.include_router(models.router, prefix="/api/v1", tags=["Models"])
app.include_router(templates.router, prefix="/api/v1", tags=["Templates"])
app.include_router(websocket.router, tags=["WebSocket"])


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    init_db()
    print("✓ Database initialized")
    print("✓ FunSearch API ready")
    print("  - Docs: http://localhost:7351/docs")
    print("  - Health: http://localhost:7351/health")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "FunSearch Framework API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health",
    }
