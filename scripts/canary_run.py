#!/usr/bin/env python3
import asyncio
import json
import os
import sys

import structlog

from app.clients.observability_factory import observability
from app.services.screening import run_screening

logger = structlog.get_logger(__name__)


def load_benchmark_candidates(dir_path: str):
    candidates = []
    if not os.path.isdir(dir_path):
        return candidates
    for name in sorted(os.listdir(dir_path)):
        if name.endswith(".json"):
            with open(os.path.join(dir_path, name)) as f:
                candidates.append(json.load(f))
    return candidates


def load_baseline(path: str):
    if not os.path.exists(path):
        return {}
    with open(path) as f:
        return json.load(f)


def load_thresholds(path: str):
    if not os.path.exists(path):
        return {}
    with open(path) as f:
        return json.load(f)


async def main():
    logger.info("canary_run_started")

    dir_path = os.environ.get("TP_CANARY_CANDIDATES_DIR", os.environ.get("CANARY_CANDIDATES_DIR", "canary/candidates"))
    baseline_path = os.path.join(os.path.dirname(dir_path), "baseline_scores.json")
    thresholds_path = os.path.join(os.path.dirname(dir_path), "thresholds.json")
    output_path = os.environ.get("TP_CANARY_LOG", os.environ.get("CANARY_LOG", "canary_output.json"))

    candidates = load_benchmark_candidates(dir_path)
    baseline = load_baseline(baseline_path)
    thresholds = load_thresholds(thresholds_path)

    if not candidates:
        logger.warning("no_candidates_found", dir=dir_path)

    drift_detected = False
    results = []

    for candidate in candidates:
        cid = str(candidate.get("id", ""))
        if not cid:
            logger.warning("candidate_missing_id", candidate=candidate)
            continue

        resume_text = candidate.get("resume_text", "")
        job_description = candidate.get("job_description", "")
        baseline_entry = baseline.get(cid, {})
        baseline_score = float(baseline_entry.get("fit_score", 0.0))
        threshold = float(thresholds.get(cid, 0.15))

        try:
            screening = await run_screening(resume_text=resume_text, job_description=job_description)
            current_score = screening.fit_score
        except Exception as exc:
            logger.warning("canary_screening_failed", candidate_id=cid, error=str(exc))
            current_score = 0.0

        diff = abs(current_score - baseline_score)
        drift = diff > threshold
        level = "warning" if drift else "info"

        observability.trace(
            name="canary_run",
            metadata={
                "candidate_id": cid,
                "baseline_score": baseline_score,
                "current_score": current_score,
                "threshold": threshold,
                "drift_detected": drift,
            },
            input={"resume_text": resume_text, "job_description": job_description},
        )

        if drift:
            logger.warning(
                "drift_detected",
                candidate_id=cid,
                baseline=baseline_score,
                current=current_score,
                diff=diff,
            )
            drift_detected = True
        else:
            logger.info("canary_ok", candidate_id=cid, diff=diff)

        results.append(
            {
                "id": cid,
                "baseline": baseline_score,
                "current": current_score,
                "threshold": threshold,
                "diff": diff,
                "drift": drift,
            }
        )

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({"candidates": results}, f, indent=2)

    if drift_detected:
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())