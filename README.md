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

| Layer            | Technology                                      |
| ---------------- | ----------------------------------------------- |
| Backend          | FastAPI + Pydantic v2                           |
| Database         | PostgreSQL + SQLAlchemy 2.0                     |
| LLM              | OpenAI GPT-4o / Ollama / Groq / Claude / Gemini |
| Observability    | Langfuse (cloud or self-hosted)                 |
| Async            | Celery + Redis                                  |
| Testing          | pytest + pytest-asyncio                         |
| CI/CD            | GitHub Actions                                  |
| Containerization | Docker Compose                                  |
| Frontend         | React + Vite + Tailwind CSS (SPA served by FastAPI) |

---

## Quick Start

### Backend

```bash
# Clone
git clone https://github.com/your-username/tracepilot.git
cd tracepilot

# Setup
cp .env.example .env

# Switch to local LLM (Ollama) in one command
make use-llm-ollama

# Switch to Groq (fast cloud)
make use-llm-groq

# Switch observability to "none" (disable)
make use-obs-none

# Start everything
docker compose -f docker/docker-compose.yml up --build

# Or run locally
pip install -e ".[dev]"
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run build
```

The React SPA is served by FastAPI from `frontend/dist/`. For development with hot reload, run `npm run dev` and use the Vite proxy.

### Switching Providers

Use `make use-llm-<provider>` to switch LLM providers:

```bash
make use-llm-ollama   # Local Ollama (default http://localhost:11434)
make use-llm-groq     # Groq cloud (fast, needs OPENAI_API_KEY=gsk_...)
make use-llm-openai   # OpenAI cloud
make use-llm-anthropic # Claude/Anthropic
make use-llm-google   # Google Gemini
make use-llm-vllm     # Local vLLM

make use-obs-langfuse # Langfuse observability (default)
make use-obs-langsmith # LangSmith observability
make use-obs-phoenix  # Arize Phoenix
make use-obs-none     # Disable observability

make current          # Show active LLM + observability config
make list             # List all available providers
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

For local LLM setup (Ollama, vLLM, Groq), see [LOCAL_LLM_SETUP.md](LOCAL_LLM_SETUP.md).

---

## API Endpoints

| Method | Path                            | Description                  |
| ------ | ------------------------------- | ---------------------------- |
| POST   | `/api/v1/screenings`            | Screen a candidate           |
| GET    | `/api/v1/screenings`            | List recent screenings       |
| GET    | `/api/v1/screenings/all`        | List all screenings          |
| GET    | `/api/v1/screenings/{id}`       | Get screening result         |
| GET    | `/api/v1/screenings/{id}/trace` | Redirect to trace UI         |
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
| GET    | `/api/v1/hr/reports/{id}`       | HTML screening report        |
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
├── frontend/
│   └── src/
│       ├── pages/        # React pages (Dashboard, AdminJobs, Screenings, etc.)
│       ├── App.tsx       # Routes + responsive navbar
│       └── lib/api.ts    # Axios client
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

| Dataset                 | Purpose                                 | Populated By   |
| ----------------------- | --------------------------------------- | -------------- |
| `adversarial-tests`     | Regression suite from validation errors | Middleware     |
| `fuzzer-corpus`         | Adversarial resume test cases           | Fuzzer runs    |
| `canary-benchmark`      | Frozen benchmark candidates             | Manual seeding |
| `production-screenings` | All production traces                   | Screening API  |

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

- `LLM_PROVIDER` — `openai`, `ollama`, `groq`, `anthropic`, `google`, `openai_compatible`
- `OBSERVABILITY_PROVIDER` — `langfuse`, `langsmith`, `phoenix`, `none`
- `OPENAI_API_KEY` — API key for OpenAI-compatible LLM
- `OPENAI_BASE_URL` — Base URL for OpenAI-compatible API (e.g. `http://localhost:11434/v1` for Ollama)
- `LANGFUSE_PUBLIC_KEY` — Langfuse public key
- `LANGFUSE_SECRET_KEY` — Langfuse secret key

Local LLM options:
- **Ollama**: `LLM_PROVIDER=ollama`, `OPENAI_BASE_URL=http://localhost:11434/v1`
- **Groq**: `LLM_PROVIDER=groq`, `OPENAI_API_KEY=gsk_...`, `OPENAI_BASE_URL=https://api.groq.com/openai/v1`

See `.env.example` for full list of supported providers.

---

## License

MIT

---

## Fuzzer — How to Use It

The Fuzzer is a simple QA tool for the AI screening feature. It creates fake resumes with small problems and checks whether the AI notices them.

Think of it as a **mock test for the recruiter bot**.

### Step by step

1. Open `/fuzzer` in the React UI.
2. Pick the kinds of resume tricks you want to test, for example:
   - `date_overlap` — hidden gaps or overlapping jobs
   - `skill_inflation` — skills that sound bigger than they are
   - `phantom_company` — companies that do not really exist
3. Choose how many fake resumes to test (`count`).
4. Click **Run sync** to see results immediately.
   - Use **Queue async** if you want it to run in the background.
5. Check:
   - **Detection rate** — how often the AI found the problem
   - **Badges** — quick visual summary per trick type

### Good numbers to aim for

- **80% or more** — the AI is catching most tricks
- **50–80%** — okay, but review some resumes yourself
- **Less than 50%** — the AI is too trusting; tighten the screening prompt or rules

### Why this matters for HR

- It shows whether the screening is actually filtering out questionable resumes.
- It is cheap and repeatable, so you can test after any prompt or model change.
- It does not touch real candidates, so it is safe to experiment with.
