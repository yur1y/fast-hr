import logging
import uuid
from collections import Counter

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.repositories.screening import ScreeningRepository
from app.schemas.hr import (
    BatchRequest,
    BatchResponse,
    CompareRequest,
    CompareResponse,
    DashboardMetrics,
)
from app.services.dashboard import compare_screenings, get_dashboard_data
from app.services.screening import run_screening

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/batch", response_model=BatchResponse)
async def batch_screening(request: BatchRequest, db: AsyncSession = Depends(get_db)):
    if db is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not configured.",
        )

    batch_id = str(uuid.uuid4())
    results = []
    for resume_text in request.resumes:
        result = await run_screening(resume_text, request.job_description)
        repo = ScreeningRepository(db)
        screening = await repo.create(
            trace_id=result.trace_id,
            resume_text=resume_text,
            job_description=request.job_description,
            candidate_summary=result.candidate_summary,
            fit_score=result.fit_score,
            strengths=result.strengths,
            risks=result.risks,
            follow_up_questions=result.follow_up_questions,
            confidence=result.confidence,
            processing_time_ms=result.processing_time_ms,
        )
        result.id = screening.id
        results.append(result)

    ranked = sorted(results, key=lambda r: r.fit_score, reverse=True)
    return BatchResponse(batch_id=batch_id, total=len(results), ranked_by_fit=ranked)


@router.get("/dashboard", response_model=DashboardMetrics)
async def get_dashboard(db: AsyncSession = Depends(get_db)):
    if db is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not configured.",
        )

    data = await get_dashboard_data(db)
    screen_list = data.get("screenings", [])
    if not screen_list:
        return DashboardMetrics(
            total_screenings=0, top_candidates=[], risk_distribution={}
        )

    avg_fit = sum(s["fit_score"] for s in screen_list) / len(screen_list)
    avg_conf = sum(s["confidence"] for s in screen_list) / len(screen_list)
    top5 = sorted(screen_list, key=lambda s: s["fit_score"], reverse=True)[:5]

    risk_counter: Counter[str] = Counter()
    for s in screen_list:
        for risk in s.get("risks", []) or []:
            risk_counter[risk] += 1

    return DashboardMetrics(
        total_screenings=len(screen_list),
        avg_fit_score=round(avg_fit, 2),
        avg_confidence=round(avg_conf, 2),
        top_candidates=top5,
        risk_distribution=dict(risk_counter),
    )


@router.post("/compare", response_model=CompareResponse)
async def compare_candidates(
    request: CompareRequest,
    db: AsyncSession = Depends(get_db),
):
    if db is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not configured.",
        )

    data = await compare_screenings(db, request.screening_ids)
    return CompareResponse(**data)


@router.get("/reports/{screening_id}")
async def get_report(screening_id: str, db: AsyncSession = Depends(get_db)):
    if db is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not configured.",
        )

    repo = ScreeningRepository(db)
    screening = await repo.get_by_id(screening_id)
    if screening is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Screening {screening_id} not found.",
        )

    data = repo.to_dict(screening)
    trace_url = None
    if data.get("trace_id"):
        from app.utils.observability import get_trace_url

        trace_url = get_trace_url(data["trace_id"])

    return {**data, "trace_url": trace_url}
