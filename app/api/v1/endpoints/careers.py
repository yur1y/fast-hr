import io
import logging
import re
from pathlib import Path

from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.models.screening import Application
from app.repositories.application import ApplicationRepository
from app.repositories.job import JobRepository
from app.schemas.job import JobPublic, JobPublicDetail
from app.services.email import send_application_confirmation
from app.tasks.celery import screen_application_task, submit_task

logger = logging.getLogger(__name__)

router = APIRouter()

MAX_RESUME_SIZE = 10 * 1024 * 1024  # 10 MB

_EMAIL_RE = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")


def _validate_email(email: str) -> str:
    if not _EMAIL_RE.match(email):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid email address.",
        )
    return email


@router.get("/jobs")
async def list_jobs(db: AsyncSession = Depends(get_db)):
    repo = JobRepository(db)
    jobs = await repo.list_active()
    return [JobPublic.model_validate(job) for job in jobs]


@router.get("/jobs/{job_id}", response_model=JobPublicDetail)
async def get_job(job_id: str, db: AsyncSession = Depends(get_db)):
    repo = JobRepository(db)
    job = await repo.get_by_id(job_id)
    if job is None or job.status != "active":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Job not found."
        )
    return JobPublicDetail.model_validate(job)


@router.post("/apply", status_code=status.HTTP_201_CREATED)
async def apply(
    job_id: str = Form(...),
    name: str = Form(...),
    email: str = Form(...),
    resume: UploadFile = Form(...),
    cover_letter: str | None = Form(None),
    linkedin_url: str | None = Form(None),
    db: AsyncSession = Depends(get_db),
):
    _validate_email(email)
    job_repo = JobRepository(db)
    job = await job_repo.get_by_id(job_id)
    if job is None or job.status != "active":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Job not found."
        )

    content = await resume.read()
    if len(content) > MAX_RESUME_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=(
            "Resume file too large. "
            f"Maximum size is {MAX_RESUME_SIZE // (1024 * 1024)} MB."
            ),
        )
    try:
        resume_text = await _extract_resume_text(resume.filename, content)
    except Exception as exc:
        logger.exception("resume_parse_failed")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to parse resume: {exc}",
        ) from exc

    application = Application(
        job_id=job_id,
        candidate_name=name,
        candidate_email=email,
        resume_text=resume_text,
        cover_letter=cover_letter,
        linkedin_url=linkedin_url,
    )
    db.add(application)
    await db.flush()
    await db.refresh(application)

    try:
        await send_application_confirmation(
            email_to=email,
            application_id=str(application.id),
            job_title=job.title,
        )
    except Exception:
        logger.exception("send_application_confirmation_failed")

    try:
        submit_task(
            "app.tasks.celery.screen_application_task",
            args=[str(application.id)],
            fallback=screen_application_task,
        )
    except Exception:
        logger.exception("enqueue_screening_failed")

    return {
        "application_id": str(application.id),
        "status": application.status,
        "job_title": job.title,
    }


@router.get("/status/{application_id}")
async def application_status(application_id: str, db: AsyncSession = Depends(get_db)):
    repo = ApplicationRepository(db)
    app = await repo.get_by_id(application_id)
    if app is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found.",
        )

    job = await JobRepository(db).get_by_id(app.job_id)
    return {
        "id": str(app.id),
        "candidate_name": app.candidate_name,
        "candidate_email": app.candidate_email,
        "status": app.status,
        "job_title": job.title if job else None,
        "screening_id": app.screening_id,
        "created_at": app.created_at.isoformat() if app.created_at else None,
    }


async def _extract_resume_text(filename: str, content: bytes) -> str:
    suffix = Path(filename).suffix.lower()
    if suffix == ".pdf":
        import fitz

        doc = fitz.open(stream=content, filetype="pdf")
        return "\n".join(page.get_text() for page in doc)
    if suffix in {".docx"}:
        from docx import Document

        doc = Document(io.BytesIO(content))
        return "\n".join(p.text for p in doc.paragraphs)
    return content.decode("utf-8", errors="ignore")
