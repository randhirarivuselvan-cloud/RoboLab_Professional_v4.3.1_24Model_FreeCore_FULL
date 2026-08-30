from typing import Any
from ai.base import AIProvider

class NoneProvider(AIProvider):
    name = "none"
    def available(self) -> bool:
        return False
    def generate(self, system: str, prompt: str, model: str | None = None) -> dict[str, Any]:
        return {"status": "failed", "error_code": "AI_PROVIDER_NOT_CONFIGURED", "message": "No AI model provider is configured.", "recoverable": True}
