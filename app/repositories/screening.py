import json
import logging
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.screening import Screening

logger = logging.getLogger(__name__)


class ScreeningRepository:
    """Async repository for Screening persistence."""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(
        self,
        *,
        trace_id: str | None,
        resume_text: str,
        job_description: str,
        candidate_summary: str,
        fit_score: float,
        strengths: list[str] | None = None,
        risks: list[str] | None = None,
        follow_up_questions: list[str] | None = None,
        confidence: float,
        processing_time_ms: int | None = None,
    ) -> Screening:
        """Persist a new screening record."""
        screening = Screening(
            trace_id=trace_id,
            resume_text=resume_text,
            job_description=job_description,
            candidate_summary=candidate_summary,
            fit_score=fit_score,
            strengths=json.dumps(strengths) if strengths else None,
            risks=json.dumps(risks) if risks else None,
            follow_up_questions=json.dumps(follow_up_questions) if follow_up_questions else None,
            confidence=confidence,
            processing_time_ms=processing_time_ms,
        )
        self._session.add(screening)
        await self._session.flush()
        await self._session.refresh(screening)
        logger.info("screening_created id=%s trace_id=%s", screening.id, trace_id)
        return screening

    async def get_by_id(self, screening_id: str) -> Screening | None:
        """Fetch a screening by its UUID primary key."""
        result = await self._session.execute(
            select(Screening).where(Screening.id == screening_id)
        )
        return result.scalar_one_or_none()

    async def list_recent(self, limit: int = 50) -> list[Screening]:
        """Return recent screenings ordered by creation time descending."""
        result = await self._session.execute(
            select(Screening).order_by(Screening.created_at.desc()).limit(limit)
        )
        return list(result.scalars().all())

    async def list_all(self) -> list[Screening]:
        """Return all screenings ordered by creation time descending."""
        result = await self._session.execute(
            select(Screening).order_by(Screening.created_at.desc())
        )
        return list(result.scalars().all())

    def to_dict(self, screening: Screening) -> dict[str, Any]:
        """Convert a Screening ORM instance to a dict matching ScreeningResponse schema."""
        return {
            "id": screening.id,
            "trace_id": screening.trace_id,
            "resume_text": screening.resume_text,
            "job_description": screening.job_description,
            "candidate_summary": screening.candidate_summary,
            "fit_score": screening.fit_score,
            "strengths": json.loads(screening.strengths) if screening.strengths else [],
            "risks": json.loads(screening.risks) if screening.risks else [],
            "follow_up_questions": json.loads(screening.follow_up_questions) if screening.follow_up_questions else [],
            "confidence": screening.confidence,
            "processing_time_ms": int(screening.processing_time_ms) if screening.processing_time_ms else None,
            "created_at": screening.created_at.isoformat() if screening.created_at else None,
        }
