from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from ai.model_registry import MODEL_SPECS, model_for

@dataclass(frozen=True)
class RouteDecision:
    role: str
    model: str
    reason: str


def route(role: str) -> RouteDecision:
    role = role.lower()
    if role not in MODEL_SPECS:
        role = "code"
    return RouteDecision(role=role, model=model_for(role), reason="specialist role routing")


def all_routes() -> list[dict[str, Any]]:
    return [{"role": r, "model": model_for(r)} for r in MODEL_SPECS]
