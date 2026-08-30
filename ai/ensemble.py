from __future__ import annotations
from typing import Any
from ai.model_registry import model_for
from ai.consensus import evaluate


def dual_verification(orchestrator, payload: dict[str, Any]) -> dict[str, Any]:
    results=[]
    for role in ('verifier_1','verifier_2'):
        r=orchestrator.run(role,payload)
        results.append(r)
    return {"verifiers":results,"agreement":_agreement(results),"status":"PASS_WITH_REVIEW"}


def dual_compilation(orchestrator, payload: dict[str, Any]) -> dict[str, Any]:
    results=[]
    for role in ('compiler_1','compiler_2'):
        results.append(orchestrator.run(role,payload))
    return {"compilers":results,"agreement":_agreement(results),"status":"PASS_WITH_REVIEW"}


def _agreement(results: list[dict[str, Any]]) -> bool:
    if len(results) < 2: return False
    a=results[0].get('result'); b=results[1].get('result')
    return a == b
