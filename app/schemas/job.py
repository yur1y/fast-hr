from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict


class JobBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    title: str
    department: Optional[str] = None
    description: str
    requirements: Optional[str] = None
    location: Optional[str] = None
    salary_range: Optional[str] = None
    status: Literal["active", "closed", "draft"] = "active"


class JobCreate(JobBase):
    pass


class JobPublic(JobBase):
    id: str
    created_at: datetime | None = None


class JobPublicDetail(JobPublic):
    pass


class JobAdmin(JobPublic):
    closed_at: datetime | None = None


class ApplicationBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    job_id: str
    candidate_name: str
    candidate_email: str
    cover_letter: Optional[str] = None
    linkedin_url: Optional[str] = None


class ApplicationCreate(ApplicationBase):
    resume_text: str


class ApplicationPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    job_id: str
    candidate_name: str
    candidate_email: str
    cover_letter: Optional[str] = None
    linkedin_url: Optional[str] = None
    status: str
    screening_id: Optional[str] = None
    created_at: datetime | None = None


class ApplicationAdmin(ApplicationPublic):
    resume_text: str


class CandidateList(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    candidate_name: str
    candidate_email: str
    status: str
    job_title: Optional[str] = None
    fit_score: Optional[float] = None
    created_at: datetime | None = None


class CandidateDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    candidate_name: str
    candidate_email: str
    resume_text: str
    cover_letter: Optional[str] = None
    linkedin_url: Optional[str] = None
    status: str
    job_title: Optional[str] = None
    screening: Optional[dict] = None
    created_at: datetime | None = None
