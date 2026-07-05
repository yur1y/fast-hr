import logging

from app.config import settings

logger = logging.getLogger(__name__)


class GoogleClient:
    def __init__(self) -> None:
        import google.generativeai as genai

        genai.configure(api_key=settings.google_api_key)
        self.model_name = settings.google_model
        self.temperature = settings.google_temperature
        self.model = genai.GenerativeModel(self.model_name)

    async def chat(
        self,
        messages: list[dict[str, str]],
        response_format: dict[str, str] | None = None,
        temperature: float | None = None,
    ) -> str:
        system_instruction = ""
        parts: list[str] = []
        for m in messages:
            role = m.get("role", "")
            content = m.get("content", "") or ""
            if role == "system":
                system_instruction += content + "\n"
            else:
                parts.append(content)

        if system_instruction:
            parts.insert(0, system_instruction.strip())

        if response_format is not None:
            parts[0] = (parts[0] or "") + "\n\nReturn ONLY valid JSON."

        response = await self.model.generate_content_async(
            parts,
            generation_config={
                "temperature": temperature
                if temperature is not None
                else self.temperature,
                "max_output_tokens": 4096,
            },
        )
        return response.text
