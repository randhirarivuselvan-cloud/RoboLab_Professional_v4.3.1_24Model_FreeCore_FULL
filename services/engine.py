from __future__ import annotations
from typing import Any
import os
from ai.agents import AGENTS
from ai.providers import build_provider
from ai.consensus import evaluate
from ai.model_registry import model_for
from ai.engines import ENGINE
from ai.engines.specialists import SPECIALISTS

class AIOrchestrator:
    def __init__(self):
        self.provider = build_provider(os.getenv("AI_PROVIDER", "none"))

    def provider_status(self):
        return {"provider": self.provider.name, "available": self.provider.available()}

    def run(self, stage: str, payload: dict[str, Any]) -> dict[str, Any]:
        stage = stage.lower()
        if stage == "consensus":
            return {"stage":"consensus", "mode":"native-consensus", "result":evaluate(payload.get("project", payload))}
        if stage in {"bom","debug"} or stage in SPECIALISTS:
            if self.provider.available() and stage in SPECIALISTS:
                return self._remote(stage, payload)
            if stage == "bom":
                return {"stage":"bom","mode":"native-engine","result":ENGINE.bom(str(payload.get("description") or payload.get("idea") or ""))}
            if stage == "debug":
                return {"stage":"debug","mode":"native-engine","result":ENGINE.debug(str(payload.get("code") or ""), str(payload.get("language") or "Arduino C++"))}
            return SPECIALISTS[stage](payload)
        if stage not in AGENTS:
            raise ValueError(f"Unknown stage: {stage}")
        agent = AGENTS[stage]
        description = str(payload.get("description") or payload.get("idea") or "")
        if self.provider.available():
            remote = self.provider.generate(agent.system_prompt, f"Return structured JSON for the {stage} stage. Project input: {payload}", model_for(stage))
            if remote.get("status") == "passed":
                return {"stage":stage,"mode":"model","result":remote.get("data",{}),"provider":self.provider.name,"model":model_for(stage)}
        if stage == "code":
            result = agent.native(description, payload.get("board","Arduino Uno"), payload.get("language","Arduino C++"))
        elif stage in {"compile","audit"}: result = agent.native(payload)
        else: result = agent.native(description)
        return {"stage":stage,"mode":"native-engine","result":result,"provider":"native","warnings":["No external neural model was used; this deterministic engine is a baseline."]}

    def _remote(self, stage: str, payload: dict[str, Any]) -> dict[str, Any]:
        system = f"Act as RoboLab {stage} specialist. Return structured JSON only."
        remote = self.provider.generate(system, f"Stage={stage}; project={payload}", model_for(stage))
        if remote.get("status") == "passed":
            return {"stage":stage,"mode":"model","result":remote.get("data",{}),"provider":self.provider.name,"model":model_for(stage)}
        return SPECIALISTS[stage](str(payload.get("description") or payload.get("idea") or payload.get("code") or payload))

orchestrator = AIOrchestrator()
