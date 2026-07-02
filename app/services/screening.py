import json
import logging
import time
from typing import Any

from app.clients.llm_factory import llm_client
from app.clients.observability_factory import observability
from app.config import settings
from app.schemas.screening import ScreeningResponse, ScreeningResult
from app.utils.json_mode import supports_json_mode

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an expert HR screening assistant. Analyze the candidate's resume against the job description and provide structured output.

Be objective, concise, and evidence-based. Do not make assumptions not supported by the resume.
Always provide confidence in your assessment."""

USER_PROMPT_TEMPLATE = """Resume:
{resume_text}

Job Description:
{job_description}

Analyze the fit and return a JSON object with:
- candidate_summary: 1-2 sentence summary
- fit_score: float 0.0-1.0
- strengths: list of up to 5 strengths
- risks: list of up to 5 risks
- follow_up_questions: list of up to 5 questions
- confidence: float 0.0-1.0 (your confidence in this assessment)
"""

DETERMINISTIC_FALLBACK_TEMPLATE = """Resume:
{resume_text}

Job Description:
{job_description}

Provide a basic screening assessment. Return ONLY a JSON object with:
- candidate_summary: brief summary
- fit_score: 0.5 (neutral assessment due to parsing failure)
- strengths: []
- risks: ["Unable to perform detailed assessment - structured output failed"]
- follow_up_questions: ["Please verify resume format and completeness"]
- confidence: 0.1
"""


def build_messages(resume_text: str, job_description: str, fallback: bool = False) -> list[dict]:
    if fallback:
        template = DETERMINISTIC_FALLBACK_TEMPLATE
    else:
        template = USER_PROMPT_TEMPLATE
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": template.format(
                resume_text=resume_text, job_description=job_description
            ),
        },
    ]


def parse_json_response(raw: str) -> dict[str, Any]:
    try:
        data = json.loads(raw)
        ScreeningResult(**data)
        return data
    except (json.JSONDecodeError, Exception) as exc:
        raise ValueError(f"Failed to parse LLM response: {exc}") from exc


async def screen_candidate(resume_text: str, job_description: str) -> ScreeningResult:
    start = time.perf_counter()

    temperatures = [
        settings.openai_temperature,
        0.0,
    ]

    for i, temp in enumerate(temperatures):
        try:
            messages = build_messages(resume_text, job_description)
            response_format = None
            if supports_json_mode(settings.llm_provider):
                response_format = {"type": "json_object"}
            raw = await llm_client.chat(
                messages=messages,
                response_format=response_format,
                temperature=temp,
            )
            data = parse_json_response(raw)
            result = ScreeningResult(**data)
            latency_ms = int((time.perf_counter() - start) * 1000)
            logger.warning(
                "screening_success attempt=%s latency_ms=%s", i + 1, latency_ms
            )
            return result
        except Exception as exc:
            logger.warning(
                "screening_attempt_failed attempt=%s error=%s", i + 1, str(exc)
            )
            if i == len(temperatures) - 1:
                break

    # Deterministic fallback: temperature=0 with explicit low-confidence template
    try:
        logger.warning("screening_fallback_to_deterministic_template")
        messages = build_messages(resume_text, job_description, fallback=True)
        response_format = None
        if supports_json_mode(settings.llm_provider):
            response_format = {"type": "json_object"}
        raw = await llm_client.chat(
            messages=messages,
            response_format=response_format,
            temperature=0.0,
        )
        data = parse_json_response(raw)
        result = ScreeningResult(**data)
        latency_ms = int((time.perf_counter() - start) * 1000)
        logger.info(
            "screening_fallback_success latency_ms=%s", latency_ms
        )
        return result
    except Exception as exc:
        logger.error("screening_all_attempts_failed error=%s", str(exc))
        raise RuntimeError(f"All screening attempts failed, including deterministic fallback: {exc}") from exc


async def run_screening(
    resume_text: str, job_description: str
) -> ScreeningResponse:
    start_time = time.perf_counter()

    # Create trace (root span)
    trace = observability.trace(name="screening")
    trace_id = trace.id if hasattr(trace, "id") else str(id(trace))

    # Span: input_parsing
    input_span = observability.span(
        trace,
        name="input_parsing",
        metadata={"resume_length": len(resume_text), "jd_length": len(job_description)},
    )
    input_span.update(
        metadata={"resume_length": len(resume_text), "jd_length": len(job_description)}
    )
    input_span.end()

    # Span: prompt_construction
    prompt_span = observability.span(
        trace,
        name="prompt_construction",
        metadata={"template": "USER_PROMPT_TEMPLATE"}
    )
    messages = build_messages(resume_text, job_description)
    prompt_span.update(
        metadata={"message_count": len(messages), "system_prompt_length": len(SYSTEM_PROMPT)}
    )
    prompt_span.end()

    # Span: llm_call
    llm_span = observability.span(
        trace,
        name="llm_call",
        metadata={"resume_length": len(resume_text)}
    )

    try:
        result = await screen_candidate(resume_text, job_description)

        llm_span.update(
            metadata=result.model_dump(),
            data={
                "model": settings.llm_provider + "/" + settings.openai_model,
                "temperature": settings.openai_temperature,
            },
        )
        llm_span.end()

        # Span: output_parsing
        parse_span = observability.span(
            trace,
            name="output_parsing",
            metadata={"raw_response": "parsed"}
        )
        parse_span.update(metadata={"schema_valid": True, "fields_parsed": len(result.model_dump())})
        parse_span.end()

        # Span: post_processing
        post_span = observability.span(
            trace,
            name="post_processing",
            metadata={"result": result.model_dump()}
        )

        latency_ms = int((time.perf_counter() - start_time) * 1000)

        post_span.update(
            metadata={
                "trace_id": trace_id,
                "processing_time_ms": latency_ms,
            }
        )
        post_span.end()

        # Scores
        try:
            observability.score_trace(
                trace_id=trace_id, name="fit_score", value=result.fit_score
            )
            observability.score_trace(
                trace_id=trace_id, name="confidence", value=result.confidence
            )
        except Exception as score_exc:
            logger.warning("failed_to_score_trace error=%s", str(score_exc))

        return ScreeningResponse(
            id=trace_id,
            candidate_summary=result.candidate_summary,
            fit_score=result.fit_score,
            strengths=result.strengths,
            risks=result.risks,
            follow_up_questions=result.follow_up_questions,
            confidence=result.confidence,
            trace_id=trace_id,
            processing_time_ms=latency_ms,
        )
    except Exception as exc:
        llm_span.update(metadata={"error": str(exc)})
        llm_span.end()
        raise
