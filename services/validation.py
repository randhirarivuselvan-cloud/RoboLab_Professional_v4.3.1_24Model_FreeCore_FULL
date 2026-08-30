from __future__ import annotations
from typing import Any

def validate_cross_stage(project: dict[str, Any]) -> list[str]:
    issues=[]
    if project.get("components") and not project.get("connections"): issues.append("components_present_without_connections")
    if project.get("firmware") and not project.get("pin_map"): issues.append("firmware_present_without_pin_map")
    return issues
