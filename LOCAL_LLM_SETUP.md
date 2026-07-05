# TracePilot — Local LLM Setup Guide

> Run TracePilot with **Ollama** (local) or **vLLM** — no API keys, no cloud costs, fully private.

---

## Quick Start (Ollama)

### 1. Install Ollama

```bash
# macOS / Linux
curl -fsSL https://ollama.com/install.sh | sh

# Or download from https://ollama.com/download
```

### 2. Pull a Model

```bash
# Recommended: llama3.1 8B (fast, good structured output)
ollama pull llama3.1:4b

# Alternative: llama3.1 70B (better quality, needs more GPU)
# ollama pull llama3.1:70b

# Alternative: mistral 7B (good for JSON)
# ollama pull mistral:7b

# Alternative: qwen2.5 7B (excellent multilingual)
# ollama pull qwen2.5:7b
```

### 3. Start Ollama Server

```bash
ollama serve
# Server runs on http://localhost:11434
```

### 4. Configure TracePilot

Your `.env` is already configured for local use:

```env
OPENAI_API_KEY=ollama
OPENAI_BASE_URL=http://localhost:11434/v1
OPENAI_MODEL=llama3.1:8b
OPENAI_TEMPERATURE=0.7
```

### 5. Start Infrastructure

```bash
# Terminal 1: Start PostgreSQL + Redis + Langfuse
docker-compose -f docker/docker-compose.yml up db redis langfuse

# Terminal 2: Start TracePilot app
source .venv/bin/activate
uvicorn app.main:app --reload

# Terminal 3: Start Celery worker (optional, for background tasks)
celery -A app.tasks.celery worker --loglevel=info
```

### 6. Test

```bash
curl -X POST http://localhost:8000/api/v1/screenings \
  -H "Content-Type: application/json" \
  -d '{
    "resume_text": "Python developer with 5 years experience in FastAPI and PostgreSQL",
    "job_description": "Looking for senior Python backend developer"
  }'
```

---

## Model Recommendations

| Model | Size | Speed | Quality | VRAM Required |
|-------|------|-------|---------|---------------|
| **llama3.1:b** | 8B | Fast | Good | 6-8 GB |
| llama3.1:70b | 70B | Slow | Excellent | 40-48 GB |
| mistral:7b | 7B | Fast | Good | 6-8 GB |
| qwen2.5:7b | 7B | Fast | Good | 6-8 GB |
| qwen2.5:14b | 14B | Medium | Better | 10-12 GB |

**Note:** Structured JSON output (`response_format`) may not work with all local models. If you get parsing errors, the app will retry with `temperature=0` and fallback to deterministic template.

---

## Alternative: vLLM (Higher Throughput)

### 1. Install vLLM

```bash
pip install vllm
```

### 2. Start vLLM Server

```bash
python -m vllm.entrypoints.openai.api_server \
  --model meta-llama/Llama-3.1-8B-Instruct \
  --port 8001
```

### 3. Update `.env`

```env
OPENAI_API_KEY=vllm
OPENAI_BASE_URL=http://localhost:8001/v1
OPENAI_MODEL=meta-llama/Llama-3.1-8B-Instruct
```

---

## Alternative: Groq (Fast Cloud, Free Tier)

If local model is too slow, use Groq (free tier: $200/month credits):

```env
OPENAI_API_KEY=gsk_your_groq_key
OPENAI_BASE_URL=https://api.groq.com/openai/v1
OPENAI_MODEL=llama-3.1-70b-versatile
```

Sign up: https://console.groq.com

---

## Langfuse Setup (Self-Hosted)

The docker-compose already includes Langfuse self-hosted:

```bash
docker-compose -f docker/docker-compose.yml up langfuse
```

Access at http://localhost:3000

Default credentials (from `.env`):
- Email: `admin@tracepilot.local`
- Password: `admin123`

---

## Performance Tips

### CPU-Only (No GPU)

```bash
# Ollama with CPU optimization
OLLAMA_NUM_PARALLEL=4 ollama serve

# Use smaller model for CPU
ollama pull llama3.1:4b
```

### GPU Acceleration

```bash
# NVIDIA GPU
ollama serve
# Automatically uses CUDA if available

# Check GPU usage
nvidia-smi
```

### Memory Optimization

```bash
# Limit Ollama memory
OLLAMA_MAX_LOADED_MODELS=1 ollama serve

# Use quantized model (smaller, faster)
ollama pull llama3.1:4b-q4_0
```

---

## Troubleshooting

### "Connection refused" to Ollama

```bash
# Check Ollama is running
curl http://localhost:11434/api/tags

# Restart Ollama
ollama serve
```

### JSON parsing errors with local model

Local models may not support `response_format: {type: "json_object"}`. The app handles this:
1. Retry with `temperature=0`
2. Fallback to deterministic template with low confidence
3. If all fail, return 500 error

To improve JSON reliability:
- Use **llama3.1** or **qwen2.5** (better instruction following)
- Increase model size (14B+ more reliable)
- Use vLLM with `--guided-decoding-backend outlines`

### Slow responses

```bash
# Check if GPU is used
ollama ps
# Should show GPU usage, not just CPU

# Use smaller model
ollama pull llama3.1:4b
```

### Langfuse connection errors

```bash
# Check Langfuse is running
curl http://localhost:3000/api/public/health

# Or disable Langfuse for testing
# Set LANGFUSE_BASE_URL to empty in .env
```

---

## Full Local Stack

```bash
# Terminal 1: Infrastructure
docker-compose -f docker/docker-compose.yml up

# Terminal 2: Ollama
ollama serve

# Terminal 3: App
source .venv/bin/activate
uvicorn app.main:app --reload

# Terminal 4: Celery (optional)
celery -A app.tasks.celery worker --loglevel=info
```

All services running locally:
- App: http://localhost:8000
- Langfuse: http://localhost:3000
- PostgreSQL: localhost:5432
- Redis: localhost:6379
- Ollama: http://localhost:11434

---

*No cloud APIs needed. Fully private, fully local.*
