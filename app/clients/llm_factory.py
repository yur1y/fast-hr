import logging

from app.clients.noop_client import NoopLLMClient
from app.config import settings

logger = logging.getLogger(__name__)


class LLMClient:
    @staticmethod
    def create():
        provider = settings.llm_provider
        if provider in (
            "openai",
            "openai_compatible",
            "ollama",
            "groq",
            "together",
            "vllm",
            "litellm",
            "grok",
        ):
            from app.clients.openai_client import OpenAIClient

            return OpenAIClient()
        elif provider == "anthropic":
            from app.clients.anthropic_client import AnthropicClient

            return AnthropicClient()
        elif provider == "google":
            from app.clients.google_client import GoogleClient

            return GoogleClient()
        else:
            raise ValueError(f"Unknown LLM provider: {provider}")


try:
    llm_client = LLMClient.create()
except Exception as exc:
    logger.error("LLM client failed to initialize: %s", exc)
    llm_client = NoopLLMClient()
