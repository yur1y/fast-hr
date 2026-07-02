import logging

from app.config import settings

logger = logging.getLogger(__name__)


class OpenAIClient:
    def __init__(self) -> None:
        from openai import AsyncOpenAI

        self.client = AsyncOpenAI(
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url,
        )
        self.model = settings.openai_model
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
