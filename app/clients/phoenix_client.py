import logging
from typing import Any

from app.config import settings

logger = logging.getLogger(__name__)


class PhoenixClient:
    def __init__(self) -> None:
        self._tracer = None

    @property
    def tracer(self):
        if self._tracer is None:
            import os as _os

            _os.environ["PHOENIX_API_KEY"] = settings.phoenix_api_key
            _os.environ["PHOENIX_HOST"] = settings.phoenix_host
            _os.environ["PHOENIX_PROJECT_NAME"] = settings.phoenix_project_name

            from phoenix.trace import tracer as phoenix_tracer

            self._tracer = phoenix_tracer
        return self._tracer

    def trace(self, name: str, **kwargs: Any):
        return self.tracer.trace(
            name=name,
            attributes=kwargs.get("metadata", {}),
        )

    def span(self, parent: Any, name: str, **kwargs: Any):
        with self.tracer.start_span(name=name, parent=parent) as span:
            span.set_attributes(kwargs.get("input", {}))
            return span

    def score_trace(self, trace_id: str, name: str, value: float, **kwargs: Any):
        spans = list(self.tracer.get_trace(trace_id))
        if spans:
            spans[0].set_attributes({"score_name": name, "score_value": value})

    def flush(self) -> None:
        return None
