# TracePilot — AI Screening with Observability

![Python](https://img.shields.io/badge/python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-green)
![Langfuse](https://img.shields.io/badge/Langfuse-observability-purple)
![License](https://img.shields.io/badge/license-MIT-brightgreen)

A FastAPI service that screens candidates via LLM, with tracing, testing, and a React frontend.

---

## What It Does

- **Screen candidates** — POST a resume + job description, get a structured score with strengths, risks, and fit score
- **Trace every call** — Langfuse traces show the full pipeline: input parsing → prompt construction → LLM call → output parsing
- **Fuzzer** — Generate fake resumes with subtle problems (date gaps, skill inflation, etc.) and test whether the LLM catches them
- **Canary drift detection** — Re-screen benchmark candidates on every deploy to catch model drift
- **HR portal** — React SPA for managing jobs, applications, batch screening, and comparing candidates

---

## Tech Stack

| Layer            | Technology                                      |
| ---------------- | ----------------------------------------------- |
| Backend          | FastAPI + Pydantic v2                           |
| Database         | PostgreSQL + SQLAlchemy 2.0 (async)           |
| LLM              | OpenAI / Ollama / Groq / Claude / Gemini      |
| Observability    | Langfuse (cloud or self-hosted)               |
| Async tasks      | Celery + Redis                                  |
| Testing          | pytest + pytest-asyncio                         |
| Frontend         | React + Vite + Tailwind CSS                     |

---

## Quick Start

```bash
# Clone
git clone https://github.com/your-username/tracepilot.git
cd tracepilot

# Setup
cp .env.example .env
# Edit .env with your API keys

# Install
pip install -e ".[dev]"

# Start backend
uvicorn app.main:app --reload

# Build frontend (optional — served by FastAPI)
cd frontend
npm install
npm run build
```

### Switching Providers

Edit `.env`:

```bash
# LLM
LLM_PROVIDER=openai              # or ollama, groq, anthropic, google
OPENAI_API_KEY=sk-...
OPENAI_BASE_URL=https://api.openai.com/v1

# Observability
OBSERVABILITY_PROVIDER=langfuse  # or langsmith, phoenix, none
LANGFUSE_PUBLIC_KEY=pk-...
LANGFUSE_SECRET_KEY=sk-...
```

---

## API Endpoints

| Method | Path                            | Description                  |
| ------ | ------------------------------- | ---------------------------- |
| POST   | `/api/v1/screenings`            | Screen a candidate           |
| GET    | `/api/v1/screenings`            | List recent screenings       |
| GET    | `/api/v1/screenings/{id}`       | Get screening result         |
| GET    | `/api/v1/screenings/{id}/trace` | Redirect to Langfuse trace     |
| POST   | `/api/v1/fuzzer/run`            | Run adversarial fuzzer       |
| POST   | `/api/v1/fuzzer/run-async`      | Queue fuzzer in Celery       |
| GET    | `/api/v1/fuzzer/runs/{run_id}`  | Get fuzzer run details       |
| GET    | `/api/v1/fuzzer/badges`         | Get detection badges         |
| POST   | `/api/v1/admin/jobs`            | Create job opening           |
| PUT    | `/api/v1/admin/jobs/{job_id}`   | Update job                   |
| GET    | `/api/v1/admin/analytics/dashboard` | JSON analytics dashboard |
| POST   | `/api/v1/admin/compare`         | Compare candidates by IDs    |
| GET    | `/api/v1/admin/candidates`      | List candidates              |
| POST   | `/api/v1/admin/candidates/{id}/status` | Update application status |
| GET    | `/api/v1/admin/candidates/{id}` | Get candidate detail         |
| GET    | `/api/v1/careers/jobs`          | List active jobs             |
| GET    | `/api/v1/careers/jobs/{id}`     | Get job detail               |
| POST   | `/api/v1/careers/apply`         | Submit application           |
| GET    | `/api/v1/careers/status/{id}`   | Application status           |
| POST   | `/api/v1/hr/batch`              | Batch screen resumes         |
| GET    | `/api/v1/hr/dashboard`          | HR screening metrics         |
| POST   | `/api/v1/hr/compare`            | Compare screenings           |
| GET    | `/api/v1/hr/reports/{id}`       | Screening report             |
| POST   | `/api/v1/tasks/canary`          | Queue canary drift detection |
| GET    | `/api/v1/tasks/{task_id}`       | Get Celery task status       |
| GET    | `/health`                       | Health check                 |

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
│   └── Detection rate tracking
└── Model Drift Canary
    └── 20 benchmark candidates
```

---

## Project Structure

```
tracepilot/
├── app/
│   ├── api/v1/           # FastAPI endpoints
│   ├── core/             # Middleware, logging, Redis
│   ├── models/           # SQLAlchemy ORM
│   ├── schemas/          # Pydantic schemas
│   ├── services/         # Business logic (screening, fuzzer)
│   ├── clients/          # LLM & observability factories
│   └── main.py           # FastAPI app factory
├── frontend/
│   └── src/
│       ├── pages/        # React pages
│       ├── App.tsx       # Routes + navbar
│       └── lib/api.ts    # Axios client
├── canary/               # Benchmark candidates
├── data/adversarial/     # Fuzzer corpus
├── tests/                # pytest suite
├── docker/               # Dockerfile & compose
└── pyproject.toml
```

---

## Sample Request

```bash
curl -X POST http://localhost:8000/api/v1/screenings \
  -H "Content-Type: application/json" \
  -d '{
    "resume_text": "Senior Python developer with 5 years of experience...",
    "job_description": "Looking for a backend engineer with FastAPI..."
  }'
```

Response includes `trace_id` → view the full trace in Langfuse.

---

## Fuzzer

The Fuzzer is a QA tool for the screening feature. It creates fake resumes with small problems and checks whether the LLM notices them.

1. Open `/fuzzer` in the UI.
2. Pick lie types to test (e.g. `date_overlap`, `skill_inflation`).
3. Choose how many resumes to test.
4. Run sync or queue async.
5. Check detection rate and badges.

**Good numbers:**
- 80%+ — LLM catches most tricks
- 50–80% — okay, but review manually
- <50% — LLM is too trusting; tighten the prompt

**Lie types:**
- `date_overlap` — hidden gaps or overlapping jobs
- `skill_inflation` — skills that sound bigger than they are
- `phantom_company` — companies that do not really exist
- `backdated_title` — promotion dates that do not match
- `degree_mismatch` — claimed degree does not match the school
- `location_lie` — remote work framed as on-site
- `salary_inflation` — previous pay overstated
- `reference_fake` — references that cannot be reached

---

## Setup

```bash
pip install -e ".[dev]"
uvicorn app.main:app --reload
```

### Required Environment Variables

- `LLM_PROVIDER` — `openai`, `ollama`, `groq`, `anthropic`, `google`
- `OBSERVABILITY_PROVIDER` — `langfuse`, `langsmith`, `phoenix`, `none`
- `OPENAI_API_KEY` — API key for OpenAI-compatible LLM
- `OPENAI_BASE_URL` — Base URL (e.g. `http://localhost:11434/v1` for Ollama)
- `LANGFUSE_PUBLIC_KEY` / `LANGFUSE_SECRET_KEY` — Langfuse keys

See `.env.example` for full list.

---

## License

MIT
