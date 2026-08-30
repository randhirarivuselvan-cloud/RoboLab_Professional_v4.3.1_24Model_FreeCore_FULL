from __future__ import annotations
from typing import Any

def evaluate(project: dict[str, Any]) -> dict[str, Any]:
    stages = project.get("stages", {}) or {}
    failed = [k for k,v in stages.items() if isinstance(v,dict) and v.get("status")=="failed"]
    warnings = [k for k,v in stages.items() if isinstance(v,dict) and v.get("status") in {"warning","review"}]
    passed = [k for k,v in stages.items() if isinstance(v,dict) and v.get("status")=="passed"]
    status = "REVIEW_REQUIRED" if failed or warnings else ("PASS_WITH_REVIEW" if passed else "REVIEW_REQUIRED")
    return {
        "status": status,
        "failed_stages": failed,
        "warning_stages": warnings,
        "passed_stages": passed,
        "evidence_count": len(stages),
        "principle": "Consensus is a cross-stage consistency decision; it never substitutes for physical validation.",
    }
