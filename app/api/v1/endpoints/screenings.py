import logging

from fastapi import APIRouter, HTTPException, status

from app.schemas.screening import ScreeningRequest, ScreeningResponse
from app.services.screening import run_screening

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "", response_model=ScreeningResponse, status_code=status.HTTP_200_OK
)
async def create_screening(request: ScreeningRequest):
    try:
        return await run_screening(
            resume_text=request.resume_text,
            job_description=request.job_description,
        )
    except Exception as exc:
        logger.exception("screening_failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Screening failed. Please try again.",
        ) from exc


@router.get("/{screening_id}", response_model=ScreeningResponse)
async def get_screening(screening_id: str):
    """Get a screening result by ID."""
    # TODO: Implement database retrieval
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Database retrieval not yet implemented. Screening results are stored in Langfuse traces.",
    )


@router.get("/{screening_id}/trace")
async def get_screening_trace(screening_id: str):
    """Redirect to Langfuse trace for this screening."""
    from fastapi.responses import RedirectResponse

    from app.config import settings

    trace_url = f"{settings.langfuse_host}/trace/{screening_id}"
    return RedirectResponse(url=trace_url)
