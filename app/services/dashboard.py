
import json

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.application import ApplicationRepository
from app.repositories.screening import ScreeningRepository


async def get_dashboard_data(db: AsyncSession) -> dict:
    app_repo = ApplicationRepository(db)
    screening_repo = ScreeningRepository(db)

    agg = await app_repo.get_aggregates()
    screenings = await screening_repo.list_recent(limit=1000)
    recent_apps = await app_repo.list_all(limit=1000)

    funnel = {
        "applied": len(recent_apps),
        "screening": sum(1 for a in recent_apps if a.screening_id is not None),
        "interview": sum(1 for a in recent_apps if a.status == "interview"),
        "offer": sum(1 for a in recent_apps if a.status == "offer"),
        "hired": sum(1 for a in recent_apps if a.status == "hired"),
    }

    top_candidates = []
    if screenings:
        top5 = sorted(screenings, key=lambda s: s.fit_score, reverse=True)[:5]
        top_candidates = [
            {
                "id": str(s.id),
                "name": s.candidate_summary,
                "fit_score": s.fit_score,
                "job": s.job_description[:50],
            }
            for s in top5
        ]

    data = {
        "total_jobs": agg.get("total_jobs", 0),
        "active_jobs": agg.get("active_jobs", 0),
        "total_candidates": agg.get("total_applications", 0),
        "candidates_this_month": len(recent_apps),
        "average_fit_score": round(
            sum(s.fit_score for s in screenings) / len(screenings), 2
        )
        if screenings
        else None,
        "top_candidates": top_candidates,
        "hiring_funnel": funnel,
        "detection_rate": None,
        "screenings": [
            {
                "id": str(s.id),
                "trace_id": s.trace_id,
                "candidate_summary": s.candidate_summary,
                "fit_score": s.fit_score,
                "confidence": s.confidence,
                "strengths": json.loads(s.strengths) if s.strengths else [],
                "risks": json.loads(s.risks) if s.risks else [],
                "follow_up_questions": json.loads(s.follow_up_questions)
                if s.follow_up_questions
                else [],
                "job_description": s.job_description[:80],
                "created_at": s.created_at.isoformat() if s.created_at else None,
            }
            for s in screenings
        ],
    }
    return data


async def compare_screenings(db: AsyncSession, screening_ids: list[str]) -> dict:
    repo = ScreeningRepository(db)
    candidates = []
    for sid in screening_ids:
        screening = await repo.get_by_id(sid)
        if screening is None:
            continue
        candidates.append(
            {
                "id": str(screening.id),
                "candidate_summary": screening.candidate_summary,
                "fit_score": screening.fit_score,
                "strengths": screening.strengths,
                "risks": screening.risks,
                "follow_up_questions": screening.follow_up_questions,
                "confidence": screening.confidence,
            }
        )
    return {"candidates": candidates}
