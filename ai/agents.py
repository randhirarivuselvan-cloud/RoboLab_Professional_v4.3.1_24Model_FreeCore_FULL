from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Callable
import os
from ai.engines import ENGINE

@dataclass(frozen=True)
class Agent:
    name: str
    system_prompt: str
    native: Callable[..., dict[str, Any]]
    model_key: str
    def model(self) -> str | None:
        return os.getenv(self.model_key) or os.getenv("AI_MODEL") or None

AGENTS = {
    "architect": Agent("architect", "Design the system architecture as structured engineering data.", ENGINE.architect, "ARCHITECT_MODEL"),
    "circuit": Agent("circuit", "Design a safe, checkable electronics architecture.", ENGINE.circuit, "CIRCUIT_MODEL"),
    "code": Agent("code", "Generate maintainable robotics firmware with explicit assumptions.", ENGINE.code, "CODE_MODEL"),
    "cad": Agent("cad", "Create a parametric mechanical design specification.", ENGINE.cad, "CAD_MODEL"),
    "verify": Agent("verify", "Check a robotics concept for consistency and missing assumptions.", ENGINE.verify, "VERIFIER_MODEL"),
    "compile": Agent("compile", "Assemble a validated RoboLab project manifest.", ENGINE.compile_project, "COMPILER_MODEL"),
    "audit": Agent("audit", "Audit project completeness, risks and unresolved assumptions.", ENGINE.audit, "AUDITOR_MODEL"),
}
