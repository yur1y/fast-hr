import logging

from app.config import settings

logger = logging.getLogger(__name__)


class LangsmithClient:
    def __init__(self) -> None:
        self._client = None

    @property
    def client(self):
        if self._client is None:
            from langsmith import Client as LangSmithClient

            self._client = LangSmithClient(
                api_key=settings.langsmith_api_key,
                api_url=settings.langsmith_host,
            )
        return self._client

    def trace(self, name: str, **kwargs: Any):
        from langsmith.run_trees import RunTree

        return RunTree(name=name, run_type="chain", inputs=kwargs.get("input", {}))

    def span(self, parent: Any, name: str, **kwargs: Any):
        return parent.create_child(
            name=name, run_type="span", inputs=kwargs.get("input", {})
        )

    def score_trace(self, trace_id: str, name: str, value: float, **kwargs: Any):
        self.client.create_feedback(
            run_id=trace_id,
            key=name,
            score=value,
            comment=kwargs.get("comment", ""),
        )

    def create_dataset(self, name: str, **kwargs: Any):
        return None

    def create_dataset_item(self, **kwargs: Any):
        return None

    def flush(self) -> None:
        return None
