from __future__ import annotations
from typing import Any
from ai.model_registry import model_for
from services.engine import AIOrchestrator

COPILOT_SYSTEM = """You are RoboLab Copilot, a safety-conscious engineering coding assistant.
Help users understand, modify, test and improve robotics/software projects.
Never claim code is hardware-safe without verification. Prefer small reviewable changes,
explicit assumptions, tests, and rollback instructions."""

class RoboLabCopilot:
    def __init__(self, orchestrator: AIOrchestrator | None = None):
        self.orchestrator = orchestrator or AIOrchestrator()

    def status(self) -> dict[str, Any]:
        return {
            "available": self.orchestrator.provider.available(),
            "provider": self.orchestrator.provider.name,
            "model": model_for("code"),
        }

    def chat(self, message: str, context: dict[str, Any] | None = None, action: str = "chat") -> dict[str, Any]:
        context = context or {}
        prompt = (
            f"ACTION: {action}\n"
            f"USER REQUEST:\n{message}\n\n"
            f"PROJECT CONTEXT:\n{context}\n\n"
            "Return a concise engineering response. If changing code, include a patch plan, "
            "affected files, validation steps, and risks."
        )
        if self.orchestrator.provider.available():
            result = self.orchestrator.provider.generate(COPILOT_SYSTEM, prompt, model_for("code"))
            if result.get("status") == "passed":
                return {
                    "status": "passed",
                    "mode": "model",
                    "provider": result.get("provider"),
                    "model": result.get("model"),
                    "data": result.get("data", {}),
                }
        return self._native(message, context, action)

    def _native(self, message: str, context: dict[str, Any], action: str) -> dict[str, Any]:
        lower = message.lower()
        suggestions: list[str] = []
        if any(x in lower for x in ("test", "bug", "error", "fail")):
            suggestions += [
                "Reproduce the issue with a minimal test",
                "Check the failing stack trace before changing behavior",
                "Run the full test suite after the fix",
            ]
        if any(x in lower for x in ("pin", "motor", "power", "circuit")):
            suggestions += [
                "Verify voltage/current and logic-level compatibility",
                "Keep motor power off MCU GPIO pins",
                "Validate the pin map against the actual board",
            ]
        if not suggestions:
            suggestions = [
                "Break the request into a small, reviewable change",
                "Add a regression test for the intended behavior",
                "Run validation before hardware deployment",
            ]
        return {
            "status": "passed",
            "mode": "native-assistant",
            "data": {
                "response": "RoboLab Copilot is running in no-external-model mode. It provides structured engineering guidance but is not a frontier model.",
                "action": action,
                "suggestions": suggestions,
                "context_keys": sorted(context.keys()),
            },
            "warnings": ["External AI provider is not configured; this is a deterministic assistant baseline."],
        }

copilot = RoboLabCopilot()
