# RoboLab Model Suite Training Guide

RoboLab is structured as a **14-role neural-model suite**. The package contains training recipes, starter datasets, evaluation hooks, and serving infrastructure; it does not claim that the starter examples constitute meaningful model training.

## Roles

1. Architect — requirements, system decomposition and interfaces.
2. Component — component choice, constraints and alternatives.
3. Circuit — electrical topology, pin mapping, power and interfaces.
4. Code — firmware/software generation and tests.
5. CAD — parametric mechanical specifications.
6. Simulation — test plans, scenarios and interpretation.
7. BOM — structured bill of materials and sourcing data.
8. Debug — diagnosis, repair plans and regression tests.
9. Documentation — engineering reports and handoff documents.
10. Verifier #1 — independent requirements and consistency check.
11. Verifier #2 — independent adversarial verification.
12. Compiler #1 — independent project compilation/packaging check.
13. Compiler #2 — independent reproducibility/audit check.
14. Consensus — evidence aggregation and final review decision.

## Training requirements

Use a strong pretrained causal code/instruction model as `base_model`, then fine-tune each role independently with role-specific data. Build evaluation data separately from training data and include adversarial cases, malformed inputs, regressions, and robotics-specific safety checks.

The environment running the training script must have an appropriate GPU. The repository intentionally does not download a proprietary or frontier model by default.
