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
                host=settings.langfuse_base_url or settings.langfuse_host,
                flush_at=settings.langfuse_flush_at,
                flush_interval=settings.langfuse_flush_interval,
            )
        return self._client

    def trace(self, name: str, **kwargs):
        """Create a root trace observation. Returns a LangfuseSpan with .id and .trace_id."""
        # Inject service metadata to identify the LLM provider/model in trace attributes
        metadata = kwargs.pop("metadata", {}) or {}
        metadata["service.name"] = f"tracepilot-{settings.llm_provider}"
        metadata["service.model"] = settings.openai_model
        metadata["service.provider"] = settings.llm_provider

        observation = self.client.start_observation(name=name, as_type="trace", metadata=metadata, **kwargs)
        # Ensure the observation has an id attribute for trace_id extraction
        if not hasattr(observation, "id"):
            observation.id = str(id(observation))
        return observation

    def span(self, parent, name: str, **kwargs):
        """Create a child span under a parent trace or span.

        Parent can be:
        - A trace/span object (has .trace_id and .id) -> child gets trace_id from parent.trace_id, parent_observation_id from parent.id
        - A dict with trace_id and parent_observation_id -> used directly as trace_context
        """
        if hasattr(parent, "trace_id") and hasattr(parent, "id"):
            trace_context = {
                "trace_id": parent.trace_id,
                "parent_observation_id": parent.id,
            }
        elif hasattr(parent, "id"):
            # Parent is a trace-level observation without trace_id, use its id as both
            trace_context = {
                "trace_id": parent.id,
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

    def create_dataset(self, name: str, **kwargs):
        return self.client.create_dataset(name=name, **kwargs)

    def create_dataset_item(self, **kwargs):
        return self.client.create_dataset_item(**kwargs)

    def flush(self) -> None:
        self.client.flush()
