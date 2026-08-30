from __future__ import annotations
import os
from dataclasses import dataclass

@dataclass(frozen=True)
class ModelSpec:
    key: str
    role: str
    env_key: str
    description: str
    default_id: str

MODEL_SPECS = {
    "architect": ModelSpec("architect", "Architect AI", "ARCHITECT_MODEL", "System decomposition, requirements and interfaces", "robolab-architect"),
    "component": ModelSpec("component", "Component AI", "COMPONENT_MODEL", "Component selection, constraints and alternatives", "robolab-component"),
    "circuit": ModelSpec("circuit", "Circuit AI", "CIRCUIT_MODEL", "Schematics, pin maps, power and interface reasoning", "robolab-circuit"),
    "code": ModelSpec("code", "Code AI", "CODE_MODEL", "Robotics firmware and software generation", "robolab-code"),
    "cad": ModelSpec("cad", "CAD AI", "CAD_MODEL", "Parametric mechanical design planning", "robolab-cad"),
    "simulation": ModelSpec("simulation", "Simulation AI", "SIMULATION_MODEL", "Simulation plans, test cases and interpretation", "robolab-simulation"),
    "bom": ModelSpec("bom", "BOM AI", "BOM_MODEL", "Bill of materials normalization and sourcing structure", "robolab-bom"),
    "debug": ModelSpec("debug", "Debug AI", "DEBUG_MODEL", "Code diagnosis, repair plans and regression tests", "robolab-debug"),
    "documentation": ModelSpec("documentation", "Documentation AI", "DOCUMENTATION_MODEL", "Engineering reports, build notes and handoff", "robolab-documentation"),
    "verifier_1": ModelSpec("verifier_1", "Verifier AI #1", "VERIFIER_1_MODEL", "Independent consistency and requirements verification", "robolab-verifier-1"),
    "verifier_2": ModelSpec("verifier_2", "Verifier AI #2", "VERIFIER_2_MODEL", "Independent adversarial verification", "robolab-verifier-2"),
    "compiler_1": ModelSpec("compiler_1", "Compiler AI #1", "COMPILER_1_MODEL", "Independent project compilation and repair", "robolab-compiler-1"),
    "compiler_2": ModelSpec("compiler_2", "Compiler AI #2", "COMPILER_2_MODEL", "Independent compilation audit and reproducibility", "robolab-compiler-2"),
    "consensus": ModelSpec("consensus", "Consensus AI", "CONSENSUS_MODEL", "Evidence-based decision across independent results", "robolab-consensus"),
}


def model_for(role: str) -> str:
    spec = MODEL_SPECS.get(role)
    if not spec:
        return os.getenv("AI_MODEL", "") or ""
    return os.getenv(spec.env_key) or os.getenv("AI_MODEL", "") or spec.default_id


def public_registry() -> list[dict[str, str]]:
    return [
        {"key": s.key, "role": s.role, "env_key": s.env_key, "model": model_for(s.key), "description": s.description}
        for s in MODEL_SPECS.values()
    ]
