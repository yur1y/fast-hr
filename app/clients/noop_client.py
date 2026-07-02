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

    def flush(self) -> None:
        return None


class _NoopSpan:
    def update(self, **kwargs: Any) -> None:
        return None

    def end(self) -> None:
        return None
