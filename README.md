# TracePilot — AI Screening Observability Platform

![Python](https://img.shields.io/badge/python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-green)
![Langfuse](https://img.shields.io/badge/Langfuse-observability-purple)
![License](https://img.shields.io/badge/license-MIT-brightgreen)

**TracePilot** is a production-grade FastAPI service that screens candidates via LLM — but the real product is the observability, testing, and guardrail infrastructure around it. The screening is the excuse; the production-minded engineering is the demo.

Built to impress hiring managers reviewing your GitHub.

---

## Key Features

### 1. Core Screening API with Langfuse Tracing
- Structured Pydantic output with retry cascade
- Full Langfuse trace per screening: input parsing → prompt construction → LLM call → output parsing
- Confidence scoring and trace propagation
- Self-hosted or cloud Langfuse

### 2. Adversarial Resume Fuzzer ⭐
- Generates synthetic resumes with 8 types of subtle deceptions
- Tests LLM detection rates and publishes README badges
- GitHub Action integration for PR validation

### 3. Auto-Growing Adversarial Test Suite
- FastAPI middleware intercepts Pydantic `ValidationError`s
- Deposits malformed payloads into a Langfuse dataset
- Weekly GitHub Action auto-generates regression tests from real errors

### 4. Model Drift Canary ⭐
- Frozen benchmark candidates re-screened on every deployment
- Auto-opens GitHub issues if scores drift by >15%
- Live canary status badge in README

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI + Pydantic v2 |
| Database | PostgreSQL + SQLAlchemy 2.0 |
| LLM | OpenAI GPT-4o |
| Observability | Langfuse (cloud or self-hosted) |
| Async | Celery + Redis |
| Testing | pytest + pytest-asyncio |
| CI/CD | GitHub Actions |
| Containerization | Docker Compose |

---

## Quick Start

```bash
# Clone
git clone https://github.com/your-username/tracepilot.git
cd tracepilot

# Setup
cp .env.example .env
# Edit .env with your API keys

# Start everything
docker compose -f docker/docker-compose.yml up --build

# Or run locally
pip install -e ".[dev]"
uvicorn app.main:app --reload
```

### Sample Request

```bash
curl -X POST http://localhost:8000/api/v1/screenings \
  -H "Content-Type: application/json" \
  -d '{
    "resume_text": "Senior Python developer with 5 years of experience building FastAPI services...",
    "job_description": "Looking for a backend engineer with FastAPI and PostgreSQL experience..."
  }'
```

Response includes `trace_id` → click to see full Langfuse trace.

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/screenings` | Screen a candidate |
| GET | `/api/v1/fuzzer/run` | Run adversarial fuzzer |
| GET | `/health` | Health check |

Full OpenAPI docs at `/docs`.

---

## Architecture

```
TracePilot
├── Screening API (FastAPI)
│   ├── Pydantic validation
│   └── Retry cascade (default temp → temp=0 → template)
├── Langfuse Observability
│   ├── Traces per LLM call
│   ├── Datasets for adversarial tests
│   └── Score tracking & drift
├── Adversarial Resume Fuzzer
│   ├── 8 lie types
│   ├── Detection rate tracking
│   └── GitHub Action on PR
└── Model Drift Canary
    ├── 20 benchmark candidates
    ├── Auto-open GitHub issues on drift
    └── Live README badge
```

---

## Project Structure

```
tracepilot/
├── app/
│   ├── api/v1/           # FastAPI endpoints
│   ├── core/             # Middleware, logging, exceptions
│   ├── models/           # SQLAlchemy ORM
│   ├── schemas/          # Pydantic schemas
│   ├── services/         # Business logic (screening, fuzzer)
│   ├── clients/          # Langfuse & OpenAI wrappers
│   └── main.py           # FastAPI app factory
├── canary/               # Benchmark candidates
├── data/adversarial/     # Fuzzer corpus
├── scripts/              # CI/CD scripts
├── tests/                # pytest suite
├── docker/               # Dockerfile & compose
├── .github/workflows/    # CI, canary, fuzzer
└── pyproject.toml
```

---

## Langfuse Datasets

| Dataset | Purpose | Populated By |
|---------|---------|--------------|
| `adversarial-tests` | Regression suite from validation errors | Middleware |
| `fuzzer-corpus` | Adversarial resume test cases | Fuzzer runs |
| `canary-benchmark` | Frozen benchmark candidates | Manual seeding |
| `production-screenings` | All production traces | Screening API |

---

## Why This Project Stands Out

1. **Production-minded code:** Structured logging, trace propagation, retry cascades
2. **Observability-native design:** Langfuse traces are first-class, not bolted-on
3. **Testing creativity:** Adversarial fuzzing, auto-growing test suites, drift detection
4. **CI/CD integration:** GitHub Actions that do real work (fuzzer, canary, badge updates)
5. **Documentation quality:** README that explains *why*, not just *how*

---

## Setup

```bash
pip install -e ".[dev]"
uvicorn app.main:app --reload
```

### Required Environment Variables

- `OPENAI_API_KEY` — OpenAI API key
- `LANGFUSE_PUBLIC_KEY` — Langfuse public key
- `LANGFUSE_SECRET_KEY` — Langfuse secret key

---

## License

MIT
