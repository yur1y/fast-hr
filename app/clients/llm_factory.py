import logging

from app.config import settings

logger = logging.getLogger(__name__)


class LLMClient:
    @staticmethod
    def create():
        provider = settings.llm_provider
        if provider == "openai" or provider == "openai_compatible":
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


llm_client = LLMClient.create()
