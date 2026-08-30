from __future__ import annotations
from .schema import EngineeringProject


def validate_project(project: EngineeringProject) -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    ids = {c.id for c in project.components}
    names = {c.name for c in project.components}
    if len(ids) != len(project.components): errors.append("Duplicate component IDs")
    if len(names) != len(project.components): warnings.append("Duplicate component names")
    total_current = 0.0
    for c in project.components:
        if c.current_ma is not None: total_current += max(0.0, c.current_ma)
        if c.voltage_min is not None and c.voltage_max is not None and c.voltage_min > c.voltage_max:
            errors.append(f"Invalid voltage range for {c.name}")
        if not c.pins: warnings.append(f"{c.name} has no declared pins")
    for x in project.connections:
        if x.source_component not in ids: errors.append(f"Unknown source component: {x.source_component}")
        if x.target_component not in ids: errors.append(f"Unknown target component: {x.target_component}")
    if total_current > float(project.metadata.get("supply_current_ma", 10_000_000)):
        errors.append("Declared load exceeds supply current budget")
    return {"status": "VALID" if not errors else "INVALID", "errors": errors, "warnings": warnings,
            "power": {"estimated_load_ma": total_current}, "tested": True}
