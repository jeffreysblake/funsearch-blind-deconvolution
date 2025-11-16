"""Celery tasks for experiment execution."""

import asyncio
import logging
from uuid import UUID

from backend.celery_app import celery_app
from backend.models import Experiment, ExperimentStatus, get_db
from backend.services.experiment_runner import run_experiment

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="backend.tasks.experiments.run_experiment")
def run_experiment_task(self, experiment_id: str):
    """Run a FunSearch experiment as a Celery task.

    Args:
        self: Celery task instance
        experiment_id: UUID of experiment to run

    Returns:
        Dict with experiment results
    """
    logger.info(f"Starting experiment task: {experiment_id}")

    try:
        # Update task ID in database
        db = next(get_db())
        experiment = db.query(Experiment).filter(Experiment.id == experiment_id).first()
        if experiment:
            experiment.task_id = self.request.id
            db.commit()

        # Run the experiment (async function)
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        loop.run_until_complete(run_experiment(UUID(experiment_id)))

        logger.info(f"Experiment task completed: {experiment_id}")

        return {
            "status": "completed",
            "experiment_id": experiment_id,
            "task_id": self.request.id,
        }

    except Exception as e:
        logger.exception(f"Experiment task failed: {experiment_id}")

        # Mark experiment as failed
        try:
            db = next(get_db())
            experiment = db.query(Experiment).filter(Experiment.id == experiment_id).first()
            if experiment:
                experiment.status = ExperimentStatus.FAILED
                experiment.error_message = str(e)
                db.commit()
        except Exception as db_error:
            logger.error(f"Failed to update experiment status: {db_error}")

        raise


@celery_app.task(bind=True, name="backend.tasks.experiments.stop_experiment")
def stop_experiment_task(self, experiment_id: str):
    """Stop a running experiment.

    Args:
        self: Celery task instance
        experiment_id: UUID of experiment to stop

    Returns:
        Dict with stop status
    """
    logger.info(f"Stopping experiment: {experiment_id}")

    try:
        db = next(get_db())
        experiment = db.query(Experiment).filter(Experiment.id == experiment_id).first()

        if not experiment:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Revoke the task if it's running
        if experiment.task_id:
            celery_app.control.revoke(experiment.task_id, terminate=True)
            logger.info(f"Revoked task {experiment.task_id}")

        # Update status
        experiment.status = ExperimentStatus.STOPPED
        db.commit()

        return {
            "status": "stopped",
            "experiment_id": experiment_id,
        }

    except Exception as e:
        logger.exception(f"Failed to stop experiment: {experiment_id}")
        raise
