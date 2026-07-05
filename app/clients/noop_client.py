import logging
from typing import Any

logger = logging.getLogger(__name__)


class NoopClient:
    def trace(self, name: str, **kwargs: Any):
        return _NoopSpan()

    def span(self, parent: Any, name: str, **kwargs: Any):
        return _NoopSpan()

    def score_trace(self, trace_id: str, name: str, value: float, **kwargs: Any):
        return None

    def create_dataset(self, name: str, **kwargs: Any):
        return None

    def create_dataset_item(self, **kwargs: Any):
        return None

    def flush(self) -> None:
        return None


class _NoopSpan:
    def update(self, **kwargs: Any) -> None:
        return None

    def end(self) -> None:
        return None


class NoopLLMClient:
    async def chat(
        self,
        messages: list[dict[str, str]],
        response_format: dict[str, str] | None = None,
        temperature: float | None = None,
    ) -> str:
        return '{"candidate_summary":"N/A","fit_score":0.5,"strengths":[],"risks":[],"follow_up_questions":[],"confidence":0.5}'
