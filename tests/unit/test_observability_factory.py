import importlib.util

import pytest


def _module_available(name: str) -> bool:
    try:
        return importlib.util.find_spec(name) is not None
    except (ModuleNotFoundError, ValueError):
        return False


class TestObservabilityFactory:
    def test_create_langfuse_client(self, monkeypatch):
        from app.config import settings

        monkeypatch.setattr(settings, "observability_provider", "langfuse")
        monkeypatch.setattr(settings, "langfuse_public_key", "test")
        monkeypatch.setattr(settings, "langfuse_secret_key", "test")
        from app.clients.observability_factory import ObservabilityClientFactory

        client = ObservabilityClientFactory.create()
        assert client is not None

    @pytest.mark.skipif(
        not _module_available("langsmith"),
        reason="langsmith not installed",
    )
    def test_create_langsmith_client(self, monkeypatch):
        from app.config import settings

        monkeypatch.setattr(settings, "observability_provider", "langsmith")
        monkeypatch.setattr(settings, "langsmith_api_key", "test")
        from app.clients.observability_factory import ObservabilityClientFactory

        client = ObservabilityClientFactory.create()
        assert client is not None

    @pytest.mark.skipif(
        not _module_available("phoenix.trace"),
        reason="phoenix not installed",
    )
    def test_create_phoenix_client(self, monkeypatch):
        from app.config import settings

        monkeypatch.setattr(settings, "observability_provider", "phoenix")
        monkeypatch.setattr(settings, "phoenix_api_key", "test")
        from app.clients.observability_factory import ObservabilityClientFactory

        client = ObservabilityClientFactory.create()
        assert client is not None

    def test_create_noop_client(self, monkeypatch):
        from app.config import settings

        monkeypatch.setattr(settings, "observability_provider", "none")
        from app.clients.observability_factory import ObservabilityClientFactory

        client = ObservabilityClientFactory.create()
        assert client is not None
        assert hasattr(client, "trace")
        assert hasattr(client, "span")
        assert hasattr(client, "score_trace")
        assert hasattr(client, "flush")

    def test_unknown_provider(self, monkeypatch):
        from app.config import settings

        monkeypatch.setattr(settings, "observability_provider", "unknown")
        from app.clients.observability_factory import ObservabilityClientFactory

        with pytest.raises(ValueError):
            ObservabilityClientFactory.create()
