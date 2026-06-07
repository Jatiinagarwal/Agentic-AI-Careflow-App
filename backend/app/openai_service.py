from __future__ import annotations

from app.config import get_settings


class OpenAIService:
    """Thin wrapper around OpenAI text generation with safe local fallbacks.

    The app never depends on OpenAI availability for the demo. If no key is configured
    or the SDK call fails, the supplied fallback text is returned.
    """

    def __init__(self) -> None:
        self.settings = get_settings()

    def generate_text(
        self,
        system_prompt: str,
        user_prompt: str,
        fallback: str,
        max_output_tokens: int = 700,
    ) -> str:
        if not self.settings.openai_api_key:
            return fallback

        try:
            from openai import OpenAI

            client = OpenAI(api_key=self.settings.openai_api_key)
            response = client.responses.create(
                model=self.settings.openai_model,
                input=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.2,
                max_output_tokens=max_output_tokens,
            )
            text = getattr(response, "output_text", "")
            return text.strip() if text and text.strip() else fallback
        except Exception as exc:  # noqa: BLE001 - demo must not break when API is unavailable.
            return f"{fallback}\n\n[Local fallback used: OpenAI generation unavailable during this run.]"
