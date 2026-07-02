import logging

from app.config import settings

logger = logging.getLogger(__name__)


class AnthropicClient:
    def __init__(self) -> None:
        import anthropic

        self.client = anthropic.AsyncAnthropic(
            api_key=settings.anthropic_api_key,
        )
        self.model = settings.anthropic_model
        self.temperature = settings.anthropic_temperature

    async def chat(
        self,
        messages: list[dict[str, str]],
        response_format: dict[str, str] | None = None,
        temperature: float | None = None,
    ) -> str:
        system = ""
        non_system = []
        for m in messages:
            if m["role"] == "system":
                system = m["content"]
            else:
                non_system.append(m)

        if response_format is not None:
            system = (system or "") + "\n\nReturn ONLY valid JSON."

        response = await self.client.messages.create(
            model=self.model,
            system=system,
            messages=non_system,
            temperature=temperature
            if temperature is not None
            else self.temperature,
            max_tokens=4096,
        )
        return response.content[0].text
