import logging

from fastapi import APIRouter, HTTPException, status

from app.tasks.celery import celery_app, run_canary_task, submit_task

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/canary", status_code=status.HTTP_202_ACCEPTED)
async def run_canary():
    """Queue a canary drift detection run as a background Celery task."""
    try:
        task = submit_task(
            "app.tasks.celery.run_canary_task",
            args=[],
            fallback=run_canary_task,
        )
        logger.info("canary_task_queued task_id=%s", task.id)
        return {
            "task_id": task.id,
            "status": "queued",
            "message": "Canary drift detection task has been queued.",
        }
    except Exception as exc:
        logger.exception("canary_async_queue_failed")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Failed to queue canary task. Celery may not be available.",
        ) from exc


@router.get("/{task_id}")
async def get_task_status(task_id: str):
    """Get the status of a Celery background task."""
    try:
        result = celery_app.AsyncResult(task_id)
        return {
            "task_id": task_id,
            "status": result.status,
            "ready": result.ready(),
            "result": result.result if result.ready() else None,
        }
    except Exception as exc:
        logger.exception("task_status_lookup_failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to look up task status.",
        ) from exc
