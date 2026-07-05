import logging

from app.config import settings

logger = logging.getLogger(__name__)


class OpenAIClient:
    def __init__(self) -> None:
        from openai import AsyncOpenAI

        # Auto-configure for Ollama provider
        if settings.llm_provider == "ollama":
            api_key = "ollama"  # Ollama doesn't require auth
            base_url = settings.ollama_base_url
            if not base_url.endswith("/v1"):
                base_url = base_url.rstrip("/") + "/v1"
            model = settings.ollama_model
            logger.info(
                "ollama_auto_configured base_url=%s model=%s num_ctx=%s",
                base_url, model, settings.ollama_num_ctx,
            )
        else:
            api_key = settings.openai_api_key
            base_url = settings.openai_base_url
            model = settings.openai_model

        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url,
        )
        self.model = model
        self.temperature = settings.openai_temperature

    async def chat(
        self,
        messages: list[dict[str, str]],
        response_format: dict[str, str] | None = None,
        temperature: float | None = None,
    ) -> str:
        kwargs: dict[str, object] = {
            "model": self.model,
            "messages": messages,
        }
        if response_format is not None:
            kwargs["response_format"] = response_format
        if temperature is not None:
            kwargs["temperature"] = temperature

        response = await self.client.chat.completions.create(**kwargs)
        content = response.choices[0].message.content
        if content is None:
            raise ValueError("Empty LLM response")
        return content


openai_client = OpenAIClient()
