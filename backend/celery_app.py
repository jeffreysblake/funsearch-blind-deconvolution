"""Celery application for distributed task execution."""

import os
from celery import Celery

# Create Celery app
celery_app = Celery(
    "funsearch",
    broker=os.getenv("CELERY_BROKER_URL", "redis://localhost:7353/0"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:7353/0"),
)

# Configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600 * 12,  # 12 hours max
    task_soft_time_limit=3600 * 11,  # 11 hours soft limit
    worker_prefetch_multiplier=1,  # One task per worker at a time
    worker_max_tasks_per_child=50,  # Restart worker after 50 tasks (memory cleanup)
    result_expires=3600 * 24,  # Results expire after 24 hours
)

# Auto-discover tasks
celery_app.autodiscover_tasks(["backend.tasks"])

# Task routes
celery_app.conf.task_routes = {
    "backend.tasks.experiments.*": {"queue": "experiments"},
    "backend.tasks.sampling.*": {"queue": "sampling"},
    "backend.tasks.evaluation.*": {"queue": "evaluation"},
}

if __name__ == "__main__":
    celery_app.start()
