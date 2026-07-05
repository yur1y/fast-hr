import logging
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.api.deps import get_db
from app.models.screening import Application
from app.repositories.application import ApplicationRepository
from app.repositories.job import JobRepository
from app.repositories.screening import ScreeningRepository
from app.schemas.job import (
    CandidateDetail,
    CandidateList,
    JobAdmin,
    JobCreate,
)
from app.schemas.screening import ScreeningResponse
from app.services.dashboard import compare_screenings, get_dashboard_data
from app.services.screening import run_screening
from app.tasks.celery import screen_application_task, submit_task

logger = logging.getLogger(__name__)

router = APIRouter()


class JobUpdate(BaseModel):
    status: Literal["active", "closed", "draft"] | None = None
    title: str | None = None
    department: str | None = None
    description: str | None = None
    requirements: str | None = None
    location: str | None = None
    salary_range: str | None = None


class ApplicationStatusUpdate(BaseModel):
    status: (
        Literal[
            "new",
            "screening",
            "interview",
            "offer",
            "hired",
            "rejected",
            "screening_failed",
        ]
        | None
    ) = None
    notes: str | None = None


class ApplicationStatusResponse(BaseModel):
    id: str
    status: str


@router.get("/analytics/dashboard")
async def admin_analytics_dashboard(db: AsyncSession = Depends(get_db)):
    from app.services.dashboard import get_dashboard_data

    data = await get_dashboard_data(db)
    return data


@router.get("/jobs", response_model=list[JobAdmin])
async def list_jobs(db: AsyncSession = Depends(get_db)):
    repo = JobRepository(db)
    jobs = await repo.list_all()
    return [JobAdmin.model_validate(job) for job in jobs]


@router.post("/jobs", response_model=JobAdmin)
async def create_job(payload: JobCreate, db: AsyncSession = Depends(get_db)):
    repo = JobRepository(db)
    job = await repo.create(**payload.model_dump())
    await db.flush()
    await db.refresh(job)
    return JobAdmin.model_validate(job)


@router.put("/jobs/{job_id}", response_model=JobAdmin)
async def update_job(
    job_id: str,
    payload: JobUpdate,
    db: AsyncSession = Depends(get_db),
):
    repo = JobRepository(db)
    job = await repo.get_by_id(job_id)
    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Job not found."
        )
    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(job, key, value)
    await db.flush()
    await db.refresh(job)
    return JobAdmin.model_validate(job)


@router.get("/candidates", response_model=list[CandidateList])
async def list_candidates(
    job_id: str | None = None,
    status: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    query = (
        select(Application)
        .options(joinedload(Application.job), joinedload(Application.screening))
    )
    if job_id:
        query = query.where(Application.job_id == job_id)
    if status:
        query = query.where(Application.status == status)
    result = await db.execute(
        query.order_by(Application.created_at.desc())
    )
    apps = result.scalars().unique().all()
    return [CandidateList.model_validate(app) for app in apps]


@router.post(
    "/candidates/{candidate_id}/status",
    response_model=ApplicationStatusResponse,
)
async def update_status(
    candidate_id: str,
    payload: ApplicationStatusUpdate,
    db: AsyncSession = Depends(get_db),
):
    repo = ApplicationRepository(db)
    app = await repo.get_by_id(candidate_id)
    if app is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found.",
        )
    app.status = payload.status
    await db.flush()
    return {"id": str(app.id), "status": app.status}


@router.post("/candidates/{candidate_id}/screen")
async def screen_candidate(
    candidate_id: str,
    db: AsyncSession = Depends(get_db),
):
    repo = ApplicationRepository(db)
    app = await repo.get_by_id(candidate_id)
    if app is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found.",
        )

    try:
        submit_task(
            "app.tasks.celery.screen_application_task",
            args=[candidate_id],
            fallback=screen_application_task,
        )
    except Exception:
        logger.exception("enqueue_screening_failed")

    return {"status": "queued", "application_id": candidate_id}


@router.get("/candidates/{candidate_id}", response_model=CandidateDetail)
async def get_candidate_detail(
    candidate_id: str,
    db: AsyncSession = Depends(get_db),
):
    repo = ApplicationRepository(db)
    app = await repo.get_by_id(candidate_id)
    if app is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found.",
        )

    job = await JobRepository(db).get_by_id(app.job_id)
    screening = None
    if app.screening_id:
        screening = await ScreeningRepository(db).get_by_id(app.screening_id)

    screening_dict = None
    if screening:
        from app.utils.observability import get_trace_url
        screening_dict = ScreeningResponse.model_validate(screening).model_dump()
        screening_dict.setdefault("trace_url", get_trace_url(screening.trace_id))

    return CandidateDetail.model_validate({
        "id": str(app.id),
        "candidate_name": app.candidate_name,
        "candidate_email": app.candidate_email,
        "resume_text": app.resume_text,
        "cover_letter": app.cover_letter,
        "linkedin_url": app.linkedin_url,
        "status": app.status,
        "job_title": job.title if job else None,
        "screening": screening_dict,
        "created_at": app.created_at.isoformat() if app.created_at else None,
    })

