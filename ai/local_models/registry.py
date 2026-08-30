from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os


@dataclass(frozen=True)
class ModelSpec:
    key: str
    role: str
    purpose: str
    seed_terms: tuple[str, ...]

    @property
    def model_id(self) -> str:
        return f"robolab-{self.key}-scratch-v1"


_ROLE_ROWS = [
    ("architect", "Architect AI", "System decomposition, interfaces, requirements, and constraints.", ("architecture", "interface", "requirement")),
    ("component", "Component AI", "Component selection, ratings, compatibility, and alternatives.", ("component", "rating", "compatibility")),
    ("circuit", "Circuit AI", "Circuit paths, pin maps, logic levels, protection, and electrical constraints.", ("circuit", "pin", "voltage")),
    ("code", "Code AI", "Embedded code structure, error handling, and testable behavior.", ("firmware", "code", "test")),
    ("cad", "CAD AI", "Mechanical parameters, assemblies, dimensions, and manufacturability.", ("cad", "dimension", "assembly")),
    ("simulation", "Simulation AI", "Scenarios, assumptions, evidence, and result interpretation.", ("simulation", "scenario", "evidence")),
    ("bom", "BOM AI", "Bill of materials normalization, quantities, and sourcing uncertainty.", ("bom", "quantity", "supplier")),
    ("debug", "Debug AI", "Failure isolation, repair planning, and regression tests.", ("debug", "failure", "regression")),
    ("documentation", "Documentation AI", "Build notes, specifications, and engineering handoff.", ("documentation", "handoff", "specification")),
    ("requirements", "Requirements AI", "Measurable requirements, acceptance criteria, and constraints.", ("acceptance", "requirement", "constraint")),
    ("feasibility", "Feasibility AI", "Dependencies, assumptions, risks, and experimental evidence.", ("feasibility", "risk", "assumption")),
    ("power", "Power AI", "Voltage, current, energy, battery, and peak-load budgets.", ("power", "current", "battery")),
    ("thermal", "Thermal AI", "Heat sources, derating, cooling, and thermal margins.", ("thermal", "temperature", "cooling")),
    ("mechanical", "Mechanical AI", "Loads, torque, mechanisms, tolerances, and structure.", ("mechanical", "torque", "tolerance")),
    ("control_systems", "Control Systems AI", "Feedback, stability, PID, and closed-loop validation.", ("control", "pid", "stability")),
    ("firmware_architecture", "Firmware Architecture AI", "Tasks, states, interfaces, and hardware abstraction.", ("task", "state", "abstraction")),
    ("pcb", "PCB AI", "Layout, routing, interfaces, manufacturing, and power integrity.", ("pcb", "routing", "layout")),
    ("sensor_fusion", "Sensor Fusion AI", "Estimation, uncertainty, sensor streams, and calibration.", ("sensor", "fusion", "uncertainty")),
    ("verifier_1", "Verifier AI #1", "Independent requirement and evidence consistency checks.", ("verify", "evidence", "consistency")),
    ("verifier_2", "Verifier AI #2", "Adversarial review for contradictions and unsafe assumptions.", ("adversarial", "contradiction", "safety")),
    ("compiler_1", "Compiler AI #1", "Build readiness, missing dependencies, and reproducibility checks.", ("compile", "dependency", "build")),
    ("compiler_2", "Compiler AI #2", "Independent compilation audit and artifact traceability.", ("compile", "audit", "artifact")),
    ("consensus", "Consensus AI", "Evidence-based decision across independently produced results.", ("consensus", "decision", "evidence")),
    ("copilot", "RoboLab Copilot", "Project-aware local engineering guidance.", ("copilot", "project", "guidance")),
    ("safety", "Safety AI", "Hazard analysis, interlocks, safe states, and test controls.", ("hazard", "interlock", "safe")),
    ("test_planning", "Test Planning AI", "Test cases, fixtures, pass criteria, and traceability.", ("test", "fixture", "criterion")),
    ("integration", "Integration AI", "Subsystem interfaces, sequencing, and integration risks.", ("integration", "subsystem", "interface")),
    ("reliability", "Reliability AI", "Failure modes, derating, lifecycle, and resilience.", ("reliability", "failure", "derating")),
    ("security", "Security AI", "Threat boundaries, credentials, update paths, and hardening.", ("security", "threat", "credential")),
    ("telemetry", "Telemetry AI", "Signals, logging, observability, and diagnostics.", ("telemetry", "logging", "diagnostic")),
    ("wireless", "Wireless AI", "Radio links, interference, range, and protocol constraints.", ("wireless", "radio", "protocol")),
    ("autonomy", "Autonomy AI", "Behavior planning, safeguards, and runtime decision boundaries.", ("autonomy", "behavior", "safeguard")),
    ("motion_planning", "Motion Planning AI", "Kinematics, path constraints, collision margins, and control.", ("motion", "path", "kinematics")),
    ("embedded_linux", "Embedded Linux AI", "Linux services, device interfaces, deployment, and monitoring.", ("linux", "service", "device")),
    ("realtime", "Real-Time AI", "Timing budgets, scheduling, jitter, and deadline verification.", ("realtime", "deadline", "jitter")),
    ("computer_vision", "Computer Vision AI", "Image pipelines, calibration, evaluation, and deployment limits.", ("vision", "image", "calibration")),
    ("battery", "Battery AI", "Cell limits, protection, charging, and runtime estimation.", ("battery", "charging", "runtime")),
    ("motor_control", "Motor Control AI", "Drivers, current limits, feedback, and failsafes.", ("motor", "driver", "feedback")),
    ("manufacturing", "Manufacturing AI", "Assembly, testability, tolerance, and process risks.", ("manufacturing", "assembly", "process")),
    ("compliance", "Compliance AI", "Standards mapping, evidence, and review gates.", ("compliance", "standard", "review")),
    ("calibration", "Calibration AI", "Calibration procedures, uncertainty, and validation records.", ("calibration", "offset", "uncertainty")),
    ("system_identification", "System Identification AI", "Measurements, model fitting, and validation experiments.", ("identification", "measurement", "model")),
    ("data_logging", "Data Logging AI", "Data schema, retention, integrity, and analysis readiness.", ("data", "logging", "retention")),
    ("field_testing", "Field Testing AI", "Operational scenarios, instrumentation, and exit criteria.", ("field", "scenario", "instrumentation")),
    ("maintainability", "Maintainability AI", "Service access, diagnostics, replacement, and documentation.", ("maintenance", "service", "diagnostic")),
    ("supply_chain", "Supply Chain AI", "Alternate parts, lead time, procurement, and obsolescence.", ("supply", "lead", "alternate")),
    ("human_factors", "Human Factors AI", "Operator interaction, controls, clarity, and error prevention.", ("operator", "interaction", "usability")),
    ("failure_analysis", "Failure Analysis AI", "Root cause, containment, corrective action, and verification.", ("root", "cause", "corrective")),
]

MODEL_SPECS = {key: ModelSpec(key, role, purpose, tuple(terms)) for key, role, purpose, terms in _ROLE_ROWS}
assert len(MODEL_SPECS) == 48


def model_for(role: str) -> str:
    return MODEL_SPECS[role].model_id


def checkpoint_path(role: str, root: str | Path | None = None) -> Path:
    base = Path(root or os.getenv("ROBO_LOCAL_MODEL_DIR", "training_48_models/artifacts"))
    return base / f"{role}.json"


def public_registry(root: str | Path | None = None) -> list[dict[str, str | bool]]:
    rows = []
    for spec in MODEL_SPECS.values():
        path = checkpoint_path(spec.key, root)
        rows.append({
            "key": spec.key,
            "role": spec.role,
            "model": spec.model_id,
            "description": spec.purpose,
            "local_only": True,
            "checkpoint_present": path.is_file(),
        })
    return rows
