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


class _InlineTaskResult:
    def __init__(self, id: str, result):
        self.id = id
        self.result = result


def _run_inline(name: str, args, func):
    import logging
    import uuid

    logger = logging.getLogger(__name__)
    task_id = str(uuid.uuid4())
    logger.info("running_task_inline name=%s task_id=%s", name, task_id)
    result = func(*args)
    return _InlineTaskResult(id=task_id, result=result)


import logging

from app.core.redis import is_redis_available

logger = logging.getLogger(__name__)


def submit_task(name: str, args, fallback):
    if not is_redis_available():
        logger.warning("celery_submit_task unavailable redis")
        return _run_inline(name, args, fallback)
    try:
        return celery_app.send_task(name, args=args)
    except Exception as exc:
        logger.warning("celery_submit_failed: %s", exc)
        return _run_inline(name, args, fallback)


@celery_app.task(name="app.tasks.celery.run_fuzzer_task")
def run_fuzzer_task(lie_types: list[str], count: int) -> dict:
    import asyncio

    from app.services.fuzzer import FuzzerEngine

    engine = FuzzerEngine()
    try:
        result = asyncio.run(engine.run(lie_types=lie_types, count=count))
    except RuntimeError as exc:
        if "cannot be called from a running event loop" in str(exc):
            loop = asyncio.get_event_loop()
            result = loop.run_until_complete(
                engine.run(lie_types=lie_types, count=count)
            )
        else:
            raise
    return result.model_dump()


@celery_app.task(name="app.tasks.celery.run_canary_task")
def run_canary_task() -> dict:
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


@celery_app.task(name="app.tasks.celery.screen_application_task")
def screen_application_task(application_id: str) -> dict:
    import asyncio
    import logging

    from sqlalchemy.ext.asyncio import (
        AsyncSession,
        async_sessionmaker,
        create_async_engine,
    )

    from app.config import settings
    from app.repositories.application import ApplicationRepository
    from app.repositories.job import JobRepository
    from app.repositories.screening import ScreeningRepository
    from app.services.email import send_screening_result
    from app.services.screening import run_screening

    logger = logging.getLogger(__name__)

    from app.api.deps import normalize_db_url

    async def _run():
        db_url, connect_args = normalize_db_url(settings.database_url)
        engine_kwargs = dict(
            url=db_url,
        )
        if connect_args:
            engine_kwargs["connect_args"] = connect_args
        engine = create_async_engine(**engine_kwargs)
        session_maker = async_sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )
        try:
            async with session_maker() as session:
                app_repo = ApplicationRepository(session)
                job_repo = JobRepository(session)
                screening_repo = ScreeningRepository(session)

                app = await app_repo.get_by_id(application_id)
                if not app:
                    return {"status": "not_found"}

                job = await job_repo.get_by_id(app.job_id)
                job_description = job.description if job else "General screening"
                job_title = job.title if job else "General screening"

                try:
                    screening = await run_screening(app.resume_text, job_description)
                except Exception as exc:
                    logger.error(
                        "screening_failed application_id=%s error=%s",
                        application_id,
                        str(exc),
                    )
                    app.status = "screening_failed"
                    await session.commit()
                    try:
                        await send_screening_result(
                            email_to=app.candidate_email,
                            application_id=application_id,
                            job_title=job_title,
                            failed=True,
                        )
                    except Exception:
                        logger.exception("send_failed_screening_notification_failed")
                    return {
                        "application_id": application_id,
                        "status": "screening_failed",
                        "error": str(exc),
                    }
                persisted = await screening_repo.create(
                    trace_id=screening.trace_id,
                    resume_text=app.resume_text,
                    job_description=job_description,
                    candidate_summary=screening.candidate_summary,
                    fit_score=screening.fit_score,
                    strengths=screening.strengths,
                    risks=screening.risks,
                    follow_up_questions=screening.follow_up_questions,
                    confidence=screening.confidence,
                    processing_time_ms=screening.processing_time_ms,
                )
                app.screening_id = persisted.id
                app.status = "screening"
                await session.commit()
                try:
                    await send_screening_result(
                        email_to=app.candidate_email,
                        application_id=application_id,
                        job_title=job_title,
                        fit_score=screening.fit_score,
                        confidence=screening.confidence,
                        failed=False,
                    )
                except Exception:
                    logger.exception("send_screening_result_failed")
                return {
                    "application_id": application_id,
                    "screening_id": str(persisted.id),
                    "status": "screening_complete",
                }
        finally:
            await engine.dispose()

    try:
        return asyncio.run(_run())
    except RuntimeError as exc:
        if "cannot be called from a running event loop" in str(exc):
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(_run())
        raise
