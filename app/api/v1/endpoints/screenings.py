import logging
from typing import Union
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.repositories.screening import ScreeningRepository
from app.schemas.screening import ScreeningRequest, ScreeningResponse
from app.services.screening import run_screening
from app.utils.observability import get_trace_url

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "", response_model=ScreeningResponse, status_code=status.HTTP_200_OK
)
async def create_screening(
    request: ScreeningRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        response = await run_screening(
            resume_text=request.resume_text,
            job_description=request.job_description,
        )
    except Exception as exc:
        logger.exception("screening_failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Screening failed. Please try again.",
        ) from exc

    if db is not None:
        try:
            repo = ScreeningRepository(db)
            screening = await repo.create(
                trace_id=response.trace_id,
                resume_text=request.resume_text,
                job_description=request.job_description,
                candidate_summary=response.candidate_summary,
                fit_score=response.fit_score,
                strengths=response.strengths,
                risks=response.risks,
                follow_up_questions=response.follow_up_questions,
                confidence=response.confidence,
                processing_time_ms=response.processing_time_ms,
            )
            response.id = screening.id
        except Exception as exc:
            logger.warning("screening_persistence_failed error=%s", str(exc))

    return response


@router.get("", response_model=list[ScreeningResponse])
@router.get("/", response_model=list[ScreeningResponse])
async def list_screenings(
    limit: int = Query(default=100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
):
    """List screenings."""
    if db is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not configured.",
        )
    repo = ScreeningRepository(db)
    screenings = await repo.list_recent(limit=limit)
    return [ScreeningResponse(**repo.to_dict(s)) for s in screenings]


@router.get(
    "/{screening_id}", response_model=Union[ScreeningResponse, list[ScreeningResponse]]
)
async def get_screening(
    screening_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get a screening result by ID, or all screenings if id is 'all' or empty."""
    if db is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not configured.",
        )

    repo = ScreeningRepository(db)

    if not screening_id or screening_id.lower() == "all":
        screenings = await repo.list_all()
        return [ScreeningResponse(**repo.to_dict(s)) for s in screenings]

    try:
        screening_uuid = UUID(screening_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid screening_id: {screening_id}. Use 'all' or a valid UUID.",
        )

    screening = await repo.get_by_id(str(screening_uuid))
    if screening is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Screening {screening_id} not found.",
        )

    data = repo.to_dict(screening)
    return ScreeningResponse(**data)


@router.get("/{screening_id}/trace")
async def get_screening_trace(screening_id: str, db: AsyncSession = Depends(get_db)):
    """Redirect to the observability trace for this screening."""
    from fastapi.responses import RedirectResponse

    if db is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not configured.",
        )

    try:
        screening_uuid = UUID(screening_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid screening_id: {screening_id}. Use a valid UUID.",
        )

    repo = ScreeningRepository(db)
    screening = await repo.get_by_id(str(screening_uuid))
    if screening is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Screening {screening_id} not found.",
        )

    url = get_trace_url(screening.trace_id)
    if url is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Observability provider is not configured.",
        )

    return RedirectResponse(url=url)
