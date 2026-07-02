from celery import Celery

from app.config import settings

celery_app = Celery(
    "tracepilot",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery_app.conf.task_routes = {
    "app.tasks.celery.*": {"queue": "tracepilot"}
}


@celery_app.task(name="app.tasks.celery.run_fuzzer_task")
def run_fuzzer_task(lie_types: list[str], count: int) -> dict:
    """Run fuzzer in background and store results."""
    import asyncio

    from app.services.fuzzer import FuzzerEngine

    engine = FuzzerEngine()
    result = asyncio.run(engine.run(lie_types=lie_types, count=count))
    return result.model_dump()


@celery_app.task(name="app.tasks.celery.run_canary_task")
def run_canary_task() -> dict:
    """Run canary drift detection in background."""
    import subprocess
    import sys

    result = subprocess.run(
        [sys.executable, "scripts/canary_run.py"],
        capture_output=True,
        text=True,
    )

    return {
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "drift_detected": result.returncode != 0,
    }
