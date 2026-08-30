from __future__ import annotations

import os
from typing import Any

from ai.agents import AGENTS
from ai.consensus import evaluate
from ai.engines import ENGINE
from ai.engines.specialists import SPECIALISTS
from ai.model_registry import MODEL_SPECS, model_for
from ai.providers import build_provider

ROLE_ALIASES = {"verify": "verifier_1", "compile": "compiler_1", "audit": "verifier_2"}


class AIOrchestrator:
    """Routes only to local checkpoints or transparent deterministic fallbacks."""

    def __init__(self):
        self.provider = build_provider(os.getenv("AI_PROVIDER", "local"))

    def provider_status(self):
        return {
            "provider": self.provider.name,
            "available": self.provider.available(),
            "network_used": False,
            "external_ai_providers_disabled": True,
        }

    def _role(self, stage: str) -> str | None:
        role = ROLE_ALIASES.get(stage, stage)
        return role if role in MODEL_SPECS else None

    def _run_local(self, stage: str, payload: dict[str, Any]) -> dict[str, Any] | None:
        role = self._role(stage)
        if role is None or not self.provider.available():
            return None
        local = self.provider.generate(
            f"You are RoboLab's local {role} model. Return a concise evidence-first engineering response.",
            f"Stage={stage}; project={payload}",
            model_for(role),
        )
        if local.get("status") == "passed":
            return {
                "stage": stage,
                "mode": "local-trained-model",
                "result": local["data"],
                "provider": local["provider"],
                "model": local["model"],
                "network_used": False,
            }
        return None

    def run(self, stage: str, payload: dict[str, Any]) -> dict[str, Any]:
        stage = stage.lower()
        local = self._run_local(stage, payload)
        if local:
            return local
        if stage == "consensus":
            return {
                "stage": "consensus",
                "mode": "native-consensus",
                "result": evaluate(payload.get("project", payload)),
                "warnings": ["Local consensus checkpoint is not ready; deterministic consensus was used."],
                "network_used": False,
            }
        if stage == "bom":
            return {"stage": "bom", "mode": "native-engine", "result": ENGINE.bom(str(payload.get("description") or payload.get("idea") or "")), "network_used": False}
        if stage == "debug":
            return {"stage": "debug", "mode": "native-engine", "result": ENGINE.debug(str(payload.get("code") or ""), str(payload.get("language") or "Arduino C++")), "network_used": False}
        if stage in SPECIALISTS:
            result = SPECIALISTS[stage](payload)
            result["network_used"] = False
            return result
        if stage not in AGENTS:
            raise ValueError(f"Unknown stage: {stage}")
        agent = AGENTS[stage]
        description = str(payload.get("description") or payload.get("idea") or "")
        if stage == "code":
            result = agent.native(description, payload.get("board", "Arduino Uno"), payload.get("language", "Arduino C++"))
        elif stage in {"compile", "audit"}:
            result = agent.native(payload)
        else:
            result = agent.native(description)
        return {
            "stage": stage,
            "mode": "native-engine",
            "result": result,
            "provider": "native",
            "warnings": ["A local checkpoint is not ready; this deterministic engineering baseline is not an AI-model result."],
            "network_used": False,
        }


orchestrator = AIOrchestrator()
