from .schema import EngineeringProject
from .validator import validate_project


def run_engineering_pipeline(project: EngineeringProject) -> dict:
    validation = validate_project(project)
    checks = {
        "builder": "READY" if project.name and project.requirements else "NEEDS_REQUIREMENTS",
        "circuit": validation["status"],
        "code": "NOT_TESTED" if not project.firmware else "STATIC_INPUT_RECEIVED",
        "simulation": "NOT_IMPLEMENTED",
        "compilation": "NOT_TESTED",
        "cross_domain": "PASS" if validation["status"] == "VALID" else "BLOCKED",
    }
    return {"project_id": project.id, "checks": checks, "validation": validation,
            "success": all(v in {"READY", "VALID", "STATIC_INPUT_RECEIVED", "PASS"} for v in checks.values())}
