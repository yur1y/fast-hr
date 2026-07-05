import logging
import random
import uuid
from pathlib import Path

from app.clients.observability_factory import observability
from app.schemas.fuzzer import (
    DetectionResult,
    FuzzerRunResponse,
    LieType,
)
from app.services.screening import screen_candidate

logger = logging.getLogger(__name__)

ADVERSARIAL_DIR = Path(__file__).resolve().parents[2] / "data" / "adversarial"

# Resume templates for synthetic generation
RESUME_TEMPLATES = {
    LieType.DATE_OVERLAP: {
        "template": """John Doe
Software Engineer

Experience:
- Senior Developer at TechCorp (Jan 2022 - Dec 2023)
- Lead Developer at StartupXYZ (Jun 2023 - Present)

Skills: Python, FastAPI, PostgreSQL""",
        "lie_description": "Overlapping employment dates (Jun 2023 - Dec 2023 overlap)"
    },
    LieType.SKILL_INFLATION: {
        "template": """Jane Smith
Data Scientist

Experience:
- Data Analyst at DataCorp (2022 - 2024)

Skills: Python (expert), Machine Learning (expert), Deep Learning (expert), TensorFlow (expert), PyTorch (expert)

Projects: Completed a 2-week online course on ML fundamentals""",
        "lie_description": "Claims expertise in multiple advanced skills after only a 2-week course"
    },
    LieType.PHANTOM_COMPANY: {
        "template": """Bob Johnson
Full Stack Developer

Experience:
- Senior Engineer at QuantumSoft Solutions (2021 - 2023)
- Tech Lead at NexGen Innovations LLC (2023 - Present)

Skills: React, Node.js, MongoDB

Education: BS Computer Science, State University""",
        "lie_description": "Companies QuantumSoft Solutions and NexGen Innovations LLC do not exist"
    },
    LieType.BACKDATED_TITLE: {
        "template": """Alice Williams
Engineering Manager

Experience:
- Engineering Manager at BigTech (2019 - Present)
- Senior Developer at BigTech (2017 - 2019)

Led team of 15 engineers since 2019""",
        "lie_description": "Claims Engineering Manager title from 2019 but was Senior Developer until 2019"
    },
    LieType.DEGREE_MISMATCH: {
        "template": """Charlie Brown
Backend Developer

Education:
- PhD in Computer Science from MIT (2018)
- MS in Software Engineering from Stanford (2015)

Experience:
- Backend Developer at various startups (2018 - Present)""",
        "lie_description": "Claims PhD from MIT but works as a backend developer with no research publications"
    },
    LieType.LOCATION_LIE: {
        "template": """Diana Prince
Remote Software Engineer

Experience:
- On-site Senior Engineer at LocalCorp, San Francisco (2020 - 2022)
- Remote Consultant for GlobalTech (2022 - Present)

Location: San Francisco, CA (willing to relocate)

Skills: Java, Spring Boot, AWS""",
        "lie_description": "Claims remote work experience but all positions listed are on-site or location-specific"
    },
    LieType.SALARY_INFLATION: {
        "template": """Evan Wright
Senior Developer

Experience:
- Senior Developer at MidSizeCorp (2021 - 2024)
- Previous salary: $250,000/year

Skills: Python, Django, PostgreSQL

Note: Expecting $300,000+ for next role""",
        "lie_description": "Claims $250k salary at MidSizeCorp where market rate is $120-150k for this role"
    },
    LieType.REFERENCE_FAKE: {
        "template": """Fiona Gallagher
Frontend Developer

References:
- John Smith, CTO at TechCorp, john.smith@techcorp.com
- Jane Doe, VP Engineering at StartupXYZ, jane.doe@startupxyz.com
- Bob Wilson, Engineering Manager at BigTech, bob.wilson@bigtech.com

Experience:
- Frontend Developer at WebAgency (2022 - Present)""",
        "lie_description": "References provided do not exist or are not verifiable"
    },
}


class FuzzerEngine:
    async def run(self, lie_types: list[str], count: int) -> FuzzerRunResponse:
        run_id = str(uuid.uuid4())
        dataset_id = f"fuzzer-corpus-{run_id}"

        # Create dataset for this run
        try:
            observability.create_dataset(
                name=dataset_id,
                description=f"Fuzzer run {run_id} - adversarial resume corpus",
                metadata={"run_id": run_id, "lie_types": lie_types, "count": count},
            )
        except Exception as e:
            logger.warning("failed_to_create_fuzzer_dataset: %s", str(e))

        resumes = self._generate_resumes(lie_types, count)
        detection = await self._run_detection(resumes, dataset_id)

        results = []
        for lt, stats in detection.items():
            total, detected, false_positives = stats
            results.append(
                DetectionResult(
                    lie_type=lt,
                    total=total,
                    detected=detected,
                    detection_rate=detected / total if total > 0 else 0.0,
                    false_positive_rate=false_positives / total if total > 0 else 0.0,
                )
            )

        # Log fuzzer run trace
        trace = observability.trace(
            name="fuzzer_run",
            metadata={
                "run_id": run_id,
                "lie_types": lie_types,
                "count": count,
                "dataset_id": dataset_id,
            },
            input={
                "detection_results": [r.model_dump() for r in results],
                "overall_detection_rate": sum(r.detection_rate for r in results) / len(results) if results else 0,
            },
        )

        return FuzzerRunResponse(
            run_id=run_id,
            total_generated=count,
            detection_results=results,
            langfuse_dataset_id=dataset_id,
        )

    def _generate_resumes(self, lie_types: list[str], count: int) -> list[dict]:
        samples: list[dict[str, str]] = []
        if not lie_types:
            return samples

        for index in range(count):
            lie_type_str = lie_types[index % len(lie_types)]
            try:
                lie_type = LieType(lie_type_str)
                template_data = RESUME_TEMPLATES.get(lie_type, {
                    "template": f"[{lie_type_str}] Generic resume with subtle deception for testing.",
                    "lie_description": f"Unknown lie type: {lie_type_str}"
                })
            except ValueError:
                template_data = {
                    "template": f"[{lie_type_str}] Generic resume with subtle deception for testing.",
                    "lie_description": f"Unknown lie type: {lie_type_str}"
                }

            samples.append(
                {
                    "lie_type": lie_type_str,
                    "resume_text": template_data["template"],
                    "lie_description": template_data["lie_description"],
                }
            )

        random.shuffle(samples)
        return samples

    async def _run_detection(
        self, resumes: list[dict], dataset_id: str
    ) -> dict[str, tuple[int, int, int]]:
        from collections import defaultdict

        stats: dict[str, list[tuple[int, int]]] = defaultdict(list)

        for r in resumes:
            lie_type = r["lie_type"]
            resume_text = r["resume_text"]
            lie_description = r.get("lie_description", "")

            # Create a job description that would normally pass this resume
            job_description = "Looking for a software engineer with relevant experience."

            try:
                # Run actual screening
                result = await screen_candidate(resume_text, job_description)

                # Check if the LLM detected the lie
                # Detection heuristic: low confidence OR risks mention inconsistencies
                detected = False
                false_positive = False

                if result.confidence < 0.5:
                    detected = True
                elif result.risks and any(
                    keyword in risk.lower()
                    for risk in result.risks
                    for keyword in ["inconsistenc", "overlap", "unverified", "questionable", "unclear", "mismatch"]
                ):
                    detected = True
                elif result.fit_score < 0.3:
                    # Might be false positive - rejected for wrong reasons
                    false_positive = True

                # Add to dataset
                try:
                    observability.create_dataset_item(
                        dataset_name=dataset_id,
                        input={
                            "resume_text": resume_text,
                            "lie_type": lie_type,
                            "lie_description": lie_description,
                        },
                        expected_output={
                            "should_detect": True,
                            "lie_description": lie_description,
                        },
                        metadata={
                            "detected": detected,
                            "confidence": result.confidence,
                            "fit_score": result.fit_score,
                            "risks": result.risks,
                        },
                    )
                except Exception as e:
                    logger.warning("failed_to_create_fuzzer_dataset_item: %s", str(e))

                stats[lie_type].append((1 if detected else 0, 1 if false_positive else 0))

            except Exception as e:
                logger.warning("fuzzer_screening_failed: lie_type=%s error=%s", lie_type, str(e))
                stats[lie_type].append((0, 0))

        return {
            lt: (len(v), sum(d for d, _ in v), sum(fp for _, fp in v))
            for lt, v in stats.items()
        }
