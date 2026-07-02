import os

os.environ["DEBUG"] = "True"
os.environ.setdefault("APP_NAME", "TracePilot")
os.environ.setdefault("APP_VERSION", "0.1.0")
os.environ.setdefault("LOG_LEVEL", "info")
os.environ.setdefault("API_V1_STR", "/api/v1")
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://tracepilot:tracepilot@localhost:5432/tracepilot")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("OPENAI_API_KEY", "ollama")
os.environ.setdefault("OPENAI_BASE_URL", "http://localhost:11434/v1")
os.environ.setdefault("OPENAI_MODEL", "llama3.1:8b")
os.environ.setdefault("OPENAI_TEMPERATURE", "0.7")
os.environ.setdefault("LLM_PROVIDER", "openai")
os.environ.setdefault("OBSERVABILITY_PROVIDER", "none")
os.environ.setdefault("CELERY_BROKER_URL", "redis://localhost:6379/0")
os.environ.setdefault("CELERY_RESULT_BACKEND", "redis://localhost:6379/1")
os.environ.setdefault("FUZZER_DEFAULT_COUNT", "10")
os.environ.setdefault("FUZZER_DETECTION_THRESHOLD", "0.7")
os.environ.setdefault("CANARY_THRESHOLD", "0.15")
os.environ.setdefault("CANARY_CANDIDATES_DIR", "canary/candidates")

import pytest

pytest_plugins = ["pytest_asyncio"]


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture(autouse=True)
def mock_llm_client(monkeypatch):
    import app.clients.llm_factory as llm_factory

    class MockLLMClient:
        async def chat(self, messages, response_format=None, temperature=None):
            return '{"candidate_summary": "Mock", "fit_score": 0.8, "strengths": [], "risks": [], "follow_up_questions": [], "confidence": 0.9}'

    monkeypatch.setattr(llm_factory, "llm_client", MockLLMClient())


@pytest.fixture(autouse=True)
def mock_observability(monkeypatch):
    import app.clients.observability_factory as obs_factory

    class MockSpan:
        def update(self, **kwargs):
            return None

        def end(self):
            return None

    class MockTrace(MockSpan):
        id = "mock-trace-id"

    class MockObservability:
        def trace(self, name, **kwargs):
            return MockTrace()

        def span(self, parent, name, **kwargs):
            return MockSpan()

        def score_trace(self, trace_id, name, value, **kwargs):
            return None

        def flush(self):
            return None

    monkeypatch.setattr(obs_factory, "observability", MockObservability())
