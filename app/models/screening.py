from datetime import datetime
from typing import Optional
from uuid import uuid4

from sqlalchemy import (
    DateTime,
    Float,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Screening(Base):
    __tablename__ = "screenings"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    trace_id: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    resume_text: Mapped[str] = mapped_column(Text, nullable=False)
    job_description: Mapped[str] = mapped_column(Text, nullable=False)

    candidate_summary: Mapped[str] = mapped_column(Text, nullable=False)
    fit_score: Mapped[float] = mapped_column(Float, nullable=False)
    strengths: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    risks: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    follow_up_questions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)

    processing_time_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class FuzzerRun(Base):
    __tablename__ = "fuzzer_runs"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    run_id: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    lie_types: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    total_generated: Mapped[int] = mapped_column(Integer, nullable=False)
    detection_results: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    langfuse_dataset_id: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
