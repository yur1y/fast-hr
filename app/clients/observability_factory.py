import logging

from app.clients.noop_client import NoopClient
from app.config import settings

logger = logging.getLogger(__name__)


class ObservabilityClientFactory:
    @staticmethod
    def create():
        provider = settings.observability_provider
        if provider == "langfuse":
            from app.clients.langfuse_client import LangfuseClient

            return LangfuseClient()
        elif provider == "langsmith":
            from app.clients.langsmith_client import LangsmithClient

            return LangsmithClient()
        elif provider == "phoenix":
            from app.clients.phoenix_client import PhoenixClient

            return PhoenixClient()
        elif provider == "none":
            return NoopClient()
        else:
            raise ValueError(f"Unknown observability provider: {provider}")


try:
    observability = ObservabilityClientFactory.create()
except Exception as exc:
    logger.error("Observability client failed to initialize: %s", exc)
    observability = NoopClient()
