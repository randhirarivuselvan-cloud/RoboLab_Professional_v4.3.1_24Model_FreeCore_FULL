from __future__ import annotations
import os
from pathlib import Path

ROLE_ENV = {
    "architect":"ROBO_MODEL_PATH_ARCHITECT","component":"ROBO_MODEL_PATH_COMPONENT",
    "circuit":"ROBO_MODEL_PATH_CIRCUIT","code":"ROBO_MODEL_PATH_CODE","cad":"ROBO_MODEL_PATH_CAD",
    "simulation":"ROBO_MODEL_PATH_SIMULATION","bom":"ROBO_MODEL_PATH_BOM","debug":"ROBO_MODEL_PATH_DEBUG",
    "documentation":"ROBO_MODEL_PATH_DOCUMENTATION","verifier_1":"ROBO_MODEL_PATH_VERIFIER_1",
    "verifier_2":"ROBO_MODEL_PATH_VERIFIER_2","compiler_1":"ROBO_MODEL_PATH_COMPILER_1",
    "compiler_2":"ROBO_MODEL_PATH_COMPILER_2","consensus":"ROBO_MODEL_PATH_CONSENSUS",
    "copilot":"ROBO_MODEL_PATH_COPILOT","requirements":"ROBO_MODEL_PATH_REQUIREMENTS",
    "feasibility":"ROBO_MODEL_PATH_FEASIBILITY","power":"ROBO_MODEL_PATH_POWER",
    "thermal":"ROBO_MODEL_PATH_THERMAL","mechanical":"ROBO_MODEL_PATH_MECHANICAL",
    "control_systems":"ROBO_MODEL_PATH_CONTROL_SYSTEMS","firmware_architecture":"ROBO_MODEL_PATH_FIRMWARE_ARCHITECTURE",
    "pcb":"ROBO_MODEL_PATH_PCB","sensor_fusion":"ROBO_MODEL_PATH_SENSOR_FUSION",
}
def model_path(role: str) -> str:
    env=ROLE_ENV.get(role)
    if not env:
        raise KeyError(f"Unknown role: {role}")
    return os.getenv(env) or os.getenv("ROBO_MODEL_PATH","")
