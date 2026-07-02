import logging

from app.config import settings

logger = logging.getLogger(__name__)


class LangfuseClient:
    def __init__(self) -> None:
        self._client = None

    @property
    def client(self):
        if self._client is None:
            from langfuse import Langfuse

            self._client = Langfuse(
                public_key=settings.langfuse_public_key,
                secret_key=settings.langfuse_secret_key,
                host=settings.langfuse_host,
                flush_at=settings.langfuse_flush_at,
                flush_interval=settings.langfuse_flush_interval,
            )
        return self._client

    def trace(self, name: str, **kwargs):
        return self.client.start_observation(name=name, as_type="span", **kwargs)

    def span(self, parent, name: str, **kwargs):
        if hasattr(parent, "trace_id"):
            trace_context = {
                "trace_id": parent.trace_id,
                "parent_observation_id": parent.id,
            }
        else:
            trace_context = parent

        return self.client.start_observation(
            trace_context=trace_context,
            name=name,
            as_type="span",
            **kwargs,
        )

    def score_trace(self, trace_id: str, name: str, value: float, **kwargs):
        self.client.create_score(
            trace_id=trace_id,
            name=name,
            value=value,
            **kwargs,
        )

    def flush(self) -> None:
        self.client.flush()
