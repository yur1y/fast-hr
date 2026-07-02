import importlib.util

import pytest


def _module_available(name: str) -> bool:
    try:
        return importlib.util.find_spec(name) is not None
    except (ModuleNotFoundError, ValueError):
        return False


class TestLLMFactory:
    def test_create_openai_client(self, monkeypatch):
        from app.config import settings

        monkeypatch.setattr(settings, "llm_provider", "openai")
        from app.clients.llm_factory import LLMClient

        client = LLMClient.create()
        assert client is not None

    def test_create_openai_compatible_client(self, monkeypatch):
        from app.config import settings

        monkeypatch.setattr(settings, "llm_provider", "openai_compatible")
        from app.clients.llm_factory import LLMClient

        client = LLMClient.create()
        assert client is not None

    @pytest.mark.skipif(
        not _module_available("anthropic"),
        reason="anthropic not installed",
    )
    def test_create_anthropic_client(self, monkeypatch):
        from app.config import settings

        monkeypatch.setattr(settings, "llm_provider", "anthropic")
        monkeypatch.setattr(settings, "anthropic_api_key", "test-key")
        from app.clients.llm_factory import LLMClient

        client = LLMClient.create()
        assert client is not None

    @pytest.mark.skipif(
        not _module_available("google.generativeai"),
        reason="google-generativeai not installed",
    )
    def test_create_google_client(self, monkeypatch):
        from app.config import settings

        monkeypatch.setattr(settings, "llm_provider", "google")
        monkeypatch.setattr(settings, "google_api_key", "test-key")
        from app.clients.llm_factory import LLMClient

        client = LLMClient.create()
        assert client is not None

    def test_unknown_provider(self, monkeypatch):
        from app.config import settings

        monkeypatch.setattr(settings, "llm_provider", "unknown")
        from app.clients.llm_factory import LLMClient

        with pytest.raises(ValueError):
            LLMClient.create()
