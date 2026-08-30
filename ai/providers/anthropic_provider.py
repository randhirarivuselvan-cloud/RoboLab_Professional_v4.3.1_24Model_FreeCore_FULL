from ai.base import AIProvider

class AnthropicProvider(AIProvider):
    """Import-compatible disabled stub. It never sends a request."""
    name = "disabled_external"
    def available(self) -> bool: return False
    def generate(self, system: str, prompt: str, model: str | None = None):
        return {"status": "failed", "error_code": "EXTERNAL_PROVIDER_DISABLED", "message": "External AI providers are disabled. Train and use a local RoboLab checkpoint instead.", "recoverable": False}
