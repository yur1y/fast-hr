# TracePilot — Testing Guide & LLM Provider Setup

> This guide covers everything needed to test the project locally, which LLM providers work, and how to configure them.

---

## What You Need to Test the Project

### 1. API Keys (Pick One or More)

| Provider                        | Why Use It                                      | API Key Format | Base URL (if needed)                                      |
| ------------------------------- | ----------------------------------------------- | -------------- | --------------------------------------------------------- |
| **OpenAI**                      | Most compatible, best structured output support | `sk-...`       | Default (none needed)                                     |
| **Groq**                        | Very fast inference, cheap, OpenAI-compatible   | `gsk_...`      | `https://api.groq.com/openai/v1`                          |
| **Local Model (Ollama/vLLM)**   | Free, private, no rate limits                   | N/A            | `http://localhost:11434/v1` or `http://localhost:8000/v1` |
| **Any Other OpenAI-Compatible** | LiteLLM proxy, Azure, Together, etc.            | Varies         | Provider-specific                                         |

**Recommendation for demo:** Use **Groq** as primary (fast, cheap, good enough for structured output) and keep **OpenAI** as fallback for complex cases. Or just use **OpenAI** if you already have credits.

### 2. Langfuse Setup

**Option A: Langfuse Cloud (Recommended for Demo)**
1. Sign up at [langfuse.com](https://langfuse.com)
2. Create a project
3. Get API keys from Project Settings → API Keys

```env
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_BASE_URL=https://cloud.langfuse.com
```

**Option B: Self-Hosted Langfuse (via Docker Compose)**
Already included in the project's `docker-compose.yml`:

```bash
docker-compose up -d langfuse
# Access at http://localhost:3000
# Default keys: see docker/langfuse.yml
```

```env
LANGFUSE_PUBLIC_KEY=pk-local-...
LANGFUSE_SECRET_KEY=sk-local-...
LANGFUSE_BASE_URL=http://localhost:3000
```

### 3. Database & Cache (Docker Compose)

```bash
# Start all infrastructure
docker-compose up -d

# This starts:
# - PostgreSQL (port 5432)
# - Redis (port 6379)
# - Langfuse (port 3000)
```

### 4. Environment File

Create `.env` from `.env.example`:

```env
# === LLM Provider ===
# Primary: Groq (fast, cheap, OpenAI-compatible)
LLM_PROVIDER=groq
LLM_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxx
LLM_BASE_URL=https://api.groq.com/openai/v1
LLM_MODEL=llama-3.1-70b-versatile

# Fallback: OpenAI (for complex structured output)
LLM_FALLBACK_PROVIDER=openai
LLM_FALLBACK_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
LLM_FALLBACK_MODEL=gpt-4o-mini

# === Langfuse ===
LANGFUSE_PUBLIC_KEY=pk-lf-xxxxxxxx
LANGFUSE_SECRET_KEY=sk-lf-xxxxxxxx
LANGFUSE_BASE_URL=https://cloud.langfuse.com

# === Database ===
DATABASE_URL=postgresql+asyncpg://tracepilot:tracepilot@localhost:5432/tracepilot

# === Redis / Celery ===
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0

# === App ===
APP_ENV=development
LOG_LEVEL=INFO
```

---

## LLM Provider Deep Dive

### Groq (Recommended for Speed)

```python
# app/clients/llm.py
from openai import AsyncOpenAI

class LLMClient:
    def __init__(self, provider: str, api_key: str, base_url: str | None, model: str):
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        self.model = model
        self.provider = provider
    
    async def generate_structured(self, prompt: str, schema: type[BaseModel]) -> BaseModel:
        response = await self.client.beta.chat.completions.parse(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            response_format=schema,
        )
        return response.choices[0].message.parsed
```

**Groq models that work well:**
- `llama-3.1-70b-versatile` — good structured output, fast
- `llama-3.1-8b-instant` — cheaper, slightly less reliable for complex schemas
- `mixtral-8x7b-32768` — good for longer contexts

**Groq limitations:**
- Rate limits: 20 requests/minute on free tier, higher on paid
- No `gpt-4o` level reasoning for very complex screening
- Good enough for 90% of demo scenarios

### Local Models (Ollama)

```bash
# Install Ollama
ollama pull llama3.1:70b
ollama serve
```

```env
LLM_PROVIDER=ollama
LLM_API_KEY=ollama  # dummy key
LLM_BASE_URL=http://localhost:11434/v1
LLM_MODEL=llama3.1:70b
```

**Local model notes:**
- Free, no rate limits, fully private
- Requires powerful GPU for 70B models (or use 8B with quality tradeoff)
- Structured output (`response_format`) may not work — use manual JSON parsing with retry
- Great for CI/CD (no API costs for fuzzer/canary runs)

### Multi-Provider Setup (Advanced)

```python
# app/services/llm_router.py
class LLMRouter:
    """Routes to best provider based on task complexity and availability."""
    
    PROVIDERS = {
        "groq": LLMClient(...),
        "openai": LLMClient(...),
        "ollama": LLMClient(...),
    }
    
    async def screen_candidate(self, resume: str, jd: str) -> ScreeningResult:
        # Try Groq first (fast, cheap)
        try:
            return await self.PROVIDERS["groq"].generate_structured(...)
        except (RateLimitError, BadRequestError):
            # Fallback to OpenAI for reliability
            return await self.PROVIDERS["openai"].generate_structured(...)
```

---

## Testing Checklist

### Local Development Tests

```bash
# 1. Start infrastructure
docker-compose up -d

# 2. Run migrations
alembic upgrade head

# 3. Start app
uvicorn app.main:app --reload

# 4. Test health check
curl http://localhost:8000/api/v1/health

# 5. Test screening endpoint
curl -X POST http://localhost:8000/api/v1/screenings \
  -H "Content-Type: application/json" \
  -d '{
    "resume_text": "Senior Python developer with 5 years experience in FastAPI, PostgreSQL, and AWS. Built microservices handling 10k RPS. Led team of 3 engineers.",
    "job_description": "Looking for a senior backend engineer with FastAPI experience, PostgreSQL, and cloud infrastructure. Team leadership experience preferred."
  }'

# 6. Check Langfuse trace
# Open http://localhost:3000 (or cloud.langfuse.com) and verify trace appears

# 7. Test fuzzer
curl -X POST http://localhost:8000/api/v1/fuzzer/run \
  -H "Content-Type: application/json" \
  -d '{"lie_types": ["date_overlap", "skill_inflation"], "count": 5}'

# 8. Test validation error capture (adversarial test middleware)
curl -X POST http://localhost:8000/api/v1/screenings \
  -H "Content-Type: application/json" \
  -d '{"invalid_field": "test"}'
# Should return 422 and capture error in Langfuse dataset
```

### CI/CD Tests (GitHub Actions)

```bash
# Run all tests
pytest -v --cov=app --cov-report=term-missing

# Run fuzzer in CI mode
python scripts/run_fuzzer_ci.py --lie-types all --count 20

# Run canary locally
python scripts/canary_run.py

# Check drift
python scripts/check_drift.py
```

### Manual Verification Steps

| Feature                  | How to Verify               | Expected Result                                                  |
| ------------------------ | --------------------------- | ---------------------------------------------------------------- |
| Screening API            | POST `/api/v1/screenings`   | Returns structured result with `trace_id`                        |
| Langfuse Traces          | Open Langfuse UI            | Trace shows full pipeline: input → prompt → LLM → parse → output |
| Fuzzer                   | POST `/api/v1/fuzzer/run`   | Returns detection rates per lie type                             |
| Fuzzer Badges            | Check README                | SVG badges show detection rates                                  |
| Validation Error Capture | POST invalid JSON           | Error appears in Langfuse `adversarial-tests` dataset            |
| Canary                   | Run `scripts/canary_run.py` | Compares against baseline, exits 0 if no drift                   |
| Drift Detection          | Modify prompt, run canary   | GitHub Action opens issue on drift (in CI)                       |
| Retry Cascade            | Temporarily break schema    | System retries with temp=0, then template fallback               |

### Frontend Pages

| Page            | URL                                  | Description                                 |
| --------------- | ------------------------------------ | ------------------------------------------- |
| Admin Dashboard | `/admin/dashboard`                   | View hiring metrics, top candidates, funnel |
| Jobs            | `/admin/jobs`                        | Create and close job openings               |
| Applications    | `/admin/applications`                | Filter and update application status        |
| Candidates      | `/admin/candidates`                  | View candidate list                         |
| Compare         | `/admin/compare`                     | Compare candidates by screening IDs         |
| Screenings      | `/screenings` or `/admin/screenings` | View all screenings or lookup by ID         |
| Fuzzer          | `/fuzzer`                            | Run fuzzer and view detection results       |
| HR              | `/hr`                                | Batch screening and HR dashboard            |
| Tasks           | `/tasks`                             | Queue canary tasks and check task status    |

### New API Endpoints

| Method | Path                                   | Description                         |
| ------ | -------------------------------------- | ----------------------------------- |
| POST   | `/api/v1/admin/jobs`                   | Create job opening                  |
| PUT    | `/api/v1/admin/jobs/{job_id}`          | Update job (status, fields)         |
| GET    | `/api/v1/admin/analytics/dashboard`    | JSON analytics dashboard            |
| POST   | `/api/v1/admin/compare`                | Compare candidates by screening IDs |
| GET    | `/api/v1/admin/candidates`             | List candidates                     |
| POST   | `/api/v1/admin/candidates/{id}/status` | Update application status           |
| GET    | `/api/v1/admin/candidates/{id}`        | Get candidate detail                |
| GET    | `/api/v1/screenings`                   | List recent screenings              |
| GET    | `/api/v1/screenings/all`               | List all screenings                 |
| GET    | `/api/v1/screenings/{id}/trace`        | Redirect to observability trace     |
| POST   | `/api/v1/fuzzer/run`                   | Run fuzzer synchronously            |
| POST   | `/api/v1/fuzzer/run-async`             | Queue fuzzer as Celery task         |
| GET    | `/api/v1/fuzzer/runs/{run_id}`         | Get fuzzer run result               |
| GET    | `/api/v1/fuzzer/badges`                | Get detection rate badges           |
| POST   | `/api/v1/hr/batch`                     | Batch screen multiple resumes       |
| GET    | `/api/v1/hr/dashboard`                 | HR screening dashboard metrics      |
| POST   | `/api/v1/hr/compare`                   | Compare multiple screenings         |
| GET    | `/api/v1/hr/reports/{screening_id}`    | HTML screening report               |
| POST   | `/api/v1/tasks/canary`                 | Queue canary drift detection        |
| GET    | `/api/v1/tasks/{task_id}`              | Get Celery task status              |

---

## Cost Estimates for Testing

| Provider           | Cost per Screening | Cost per Fuzzer Run (10 resumes) | Cost per Canary Run (20 candidates) | Free Tier       |
| ------------------ | ------------------ | -------------------------------- | ----------------------------------- | --------------- |
| OpenAI GPT-4o-mini | ~$0.003            | ~$0.03                           | ~$0.06                              | $5-18 credit    |
| Groq Llama 3.1 70B | ~$0.0005           | ~$0.005                          | ~$0.01                              | $200/month free |
| Ollama (local)     | $0                 | $0                               | $0                                  | Unlimited       |

**Recommendation:** Use **Groq** for development/testing (very cheap, fast) and **OpenAI** as fallback for complex cases. For CI/CD, consider **Ollama** (local) to avoid API costs entirely.

---

## Troubleshooting

### "No module named 'app'"
```bash
export PYTHONPATH=/path/to/tracepilot
# Or install in editable mode:
pip install -e .
```

### Langfuse traces not appearing
1. Check `LANGFUSE_BASE_URL` is correct (cloud vs local)
2. Verify API keys are valid
3. Check Langfuse project ID matches
4. Look for `langfuse.flush()` in code (traces may be buffered)

### Groq rate limits
```python
# Add rate limit handling in LLM client
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry=retry_if_exception_type(RateLimitError)
)
async def generate_with_retry(...):
    ...
```

### Structured output fails with local model
```python
# Fallback to manual JSON parsing
if not supports_response_format(model):
    response = await client.chat.completions.create(...)
    raw_json = extract_json(response.choices[0].message.content)
    return schema.model_validate_json(raw_json)
```

### Database connection issues
```bash
# Check PostgreSQL is running
docker-compose ps

# Check connection string format
# Must use asyncpg driver: postgresql+asyncpg://...
```

---

## Quick Start for Testing (Copy-Paste)

```bash
# 1. Clone and setup
git clone <repo-url>
cd tracepilot
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 2. Copy and fill env
cp .env.example .env
# Edit .env with your API keys

# 3. Start infrastructure
docker-compose up -d

# 4. Run migrations
alembic upgrade head

# 5. Start app
uvicorn app.main:app --reload

# 6. Test everything
curl http://localhost:8000/api/v1/health
curl -X POST http://localhost:8000/api/v1/screenings \
  -H "Content-Type: application/json" \
  -d '{"resume_text": "Python developer with 3 years experience", "job_description": "Looking for Python developer"}'

# 7. Open Langfuse
open http://localhost:3000  # or cloud.langfuse.com
```

---

*Last updated: 2024-01-XX*
