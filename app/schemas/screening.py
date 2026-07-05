from datetime import datetime
import json

from pydantic import BaseModel, ConfigDict, Field, field_validator


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


def _parse_json_list(value: object) -> list[str]:
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            return parsed if isinstance(parsed, list) else []
        except (json.JSONDecodeError, TypeError):
            return []
    return []


class ScreeningResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    candidate_summary: str
    fit_score: float
    strengths: list[str]
    risks: list[str]
    follow_up_questions: list[str]
    confidence: float
    trace_id: str | None = None
    processing_time_ms: int | None = None
    resume_text: str | None = None
    job_description: str | None = None
    created_at: datetime | None = None

    @field_validator("strengths", "risks", "follow_up_questions", mode="before")
    @classmethod
    def parse_json_list_fields(cls, value: object) -> list[str]:
        return _parse_json_list(value)

