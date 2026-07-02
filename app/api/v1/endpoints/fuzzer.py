import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, status

from app.clients.observability_factory import observability
from app.config import settings
from app.schemas.fuzzer import FuzzerRunRequest, FuzzerRunResponse
from app.services.fuzzer import FuzzerEngine

logger = logging.getLogger(__name__)

router = APIRouter()
engine = FuzzerEngine()
RUN_RESULTS: dict[str, FuzzerRunResponse] = {}
LAST_FUZZER_RUN_ID: Optional[str] = None


@router.post("/run", response_model=FuzzerRunResponse)
async def run_fuzzer(request: FuzzerRunRequest):
    try:
        result = await engine.run(
            lie_types=[lt.value for lt in request.lie_types],
            count=request.count,
        )

        observability.trace(
            name="fuzzer_run",
            metadata={
                "lie_types": [lt.value for lt in request.lie_types],
                "count": request.count,
                "run_id": result.run_id,
            },
            input={"run_id": result.run_id, "lie_types": [lt.value for lt in request.lie_types]},
        )

        RUN_RESULTS[result.run_id] = result
        global LAST_FUZZER_RUN_ID
        LAST_FUZZER_RUN_ID = result.run_id

        return result
    except Exception as exc:
        logger.exception("fuzzer_run_failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Fuzzer run failed.",
        ) from exc


@router.get("/runs/{run_id}", response_model=FuzzerRunResponse)
async def get_fuzzer_run(run_id: str):
    result = RUN_RESULTS.get(run_id)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Fuzzer run {run_id} not found",
        )
    return result


@router.get("/badges")
async def get_fuzzer_badges():
    if not LAST_FUZZER_RUN_ID:
        return {"badges": []}

    result = RUN_RESULTS.get(LAST_FUZZER_RUN_ID)
    if not result:
        return {"badges": []}

    badges = []
    for detection in result.detection_results:
        color = "green" if detection.detection_rate >= settings.fuzzer_detection_threshold else "yellow"
        badges.append(
            {
                "lie_type": detection.lie_type,
                "detection_rate": detection.detection_rate,
                "badge_url": (
                    f"https://img.shields.io/badge/{detection.lie_type}-"
                    f"{int(detection.detection_rate * 100)}%25-{color}"
                ),
            }
        )

    return {"badges": badges}
