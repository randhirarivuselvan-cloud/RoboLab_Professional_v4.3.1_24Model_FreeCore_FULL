from __future__ import annotations

from ai.base import AIProvider
from ai.local_models.registry import MODEL_SPECS, model_for
from ai.local_models.runtime import LocalModelRuntime


class LocalProvider(AIProvider):
    """Runs only checkpoint files produced by RoboLab's from-scratch trainer."""

    name = "local_scratch"

    def __init__(self):
        self.runtime = LocalModelRuntime()

    def available(self) -> bool:
        return any(self.runtime.status(role)["state"] == "TRAINED_LOCAL" for role in MODEL_SPECS)

    @staticmethod
    def _role_for(model: str | None) -> str:
        if model in MODEL_SPECS:
            return str(model)
        for role in MODEL_SPECS:
            if model_for(role) == model:
                return role
        return "code"

    def generate(self, system: str, prompt: str, model: str | None = None):
        role = self._role_for(model)
        result = self.runtime.generate(role, f"{system}\n\n{prompt}")
        if result["state"] != "COMPLETED":
            return {"status": "failed", "error_code": result.get("code", result["state"]), "message": result.get("message", "Local model is not ready."), "recoverable": result["state"] == "NOT_IMPLEMENTED", "provider": self.name, "model": model_for(role)}
        return {"status": "passed", "data": {"text": result["response"], "similarity": result["similarity"], "limitations": result["limitations"]}, "provider": self.name, "model": result["model"], "network_used": False}
