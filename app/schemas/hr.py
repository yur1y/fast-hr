from pydantic import BaseModel, Field


class BatchRequest(BaseModel):
    job_description: str = Field(..., min_length=20, max_length=5000)
    resumes: list[str] = Field(..., min_length=1, max_length=100)


class BatchResponse(BaseModel):
    batch_id: str
    total: int
    ranked_by_fit: list[dict]


class DashboardMetrics(BaseModel):
    total_screenings: int
    avg_fit_score: float | None = None
    avg_confidence: float | None = None
    top_candidates: list[dict]
    risk_distribution: dict[str, int]


class CompareRequest(BaseModel):
    screening_ids: list[str] = Field(..., min_length=2, max_length=5)


class CompareResponse(BaseModel):
    candidates: list[dict]
