from enum import Enum

from pydantic import BaseModel, Field


class LieType(str, Enum):
    DATE_OVERLAP = "date_overlap"
    SKILL_INFLATION = "skill_inflation"
    PHANTOM_COMPANY = "phantom_company"
    BACKDATED_TITLE = "backdated_title"
    DEGREE_MISMATCH = "degree_mismatch"
    LOCATION_LIE = "location_lie"
    SALARY_INFLATION = "salary_inflation"
    REFERENCE_FAKE = "reference_fake"


class FuzzerRunRequest(BaseModel):
    lie_types: list[LieType] = Field(..., min_length=1, max_length=8)
    count: int = Field(default=10, ge=1, le=50)


class DetectionResult(BaseModel):
    lie_type: str
    total: int
    detected: int
    detection_rate: float
    false_positive_rate: float


class FuzzerRunResponse(BaseModel):
    run_id: str
    total_generated: int
    detection_results: list[DetectionResult]
    langfuse_dataset_id: str


class FuzzerRunDetail(BaseModel):
    run_id: str
    resume_text: str
    lie_type: str
    detected: bool
    llm_notes: str | None = None
