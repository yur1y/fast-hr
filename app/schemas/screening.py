from pydantic import BaseModel, Field, field_validator


class ScreeningRequest(BaseModel):
    resume_text: str = Field(..., min_length=50, max_length=5000)
    job_description: str = Field(..., min_length=20, max_length=5000)


class ScreeningResult(BaseModel):
    candidate_summary: str = Field(..., max_length=500)
    fit_score: float = Field(..., ge=0.0, le=1.0)
    strengths: list[str] = Field(..., max_length=5)
    risks: list[str] = Field(..., max_length=5)
    follow_up_questions: list[str] = Field(..., max_length=5)
    confidence: float = Field(..., ge=0.0, le=1.0)

    @field_validator("fit_score", "confidence")
    @classmethod
    def round_scores(cls, v: float) -> float:
        return round(v, 2)


class ScreeningResponse(BaseModel):
    id: str
    candidate_summary: str
    fit_score: float
    strengths: list[str]
    risks: list[str]
    follow_up_questions: list[str]
    confidence: float
    trace_id: str | None = None
    processing_time_ms: int
