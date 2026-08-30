# RoboLab Professional v4.3.0 — 24-Model Training Suite

This package contains the training/inference infrastructure for the **first 24 RoboLab specialist neural-model roles**.

## 24 roles

1. Architect AI
2. Component AI
3. Circuit AI
4. Code AI
5. CAD AI
6. Simulation AI
7. BOM AI
8. Debug AI
9. Documentation AI
10. Verifier AI #1
11. Verifier AI #2
12. Compiler AI #1
13. Compiler AI #2
14. Consensus AI
15. RoboLab Copilot
16. Requirements AI
17. Feasibility AI
18. Power AI
19. Thermal AI
20. Mechanical AI
21. Control Systems AI
22. Firmware Architecture AI
23. PCB AI
24. Sensor Fusion AI

## Important

This package contains **training code, role-specific configurations, starter datasets, and a model registry**. It does **not** contain 24 pre-trained frontier model weights.

A real training run requires:
- a strong pretrained base model
- a substantially larger, high-quality dataset per role
- GPU compute
- validation/evaluation benchmarks
- safety and engineering review

The included datasets are deliberately small starter datasets for wiring/testing the pipeline; they are not sufficient to create production-quality models.

## Train

Set a base model:

```bash
set ROBO_BASE_MODEL=<your-base-model>
```

Install the training dependencies:

```bash
pip install -r requirements-training.txt
```

Train one model:

```bash
python training/scripts/train_role.py code
```

Train the suite:

```bash
python training/scripts/train_24.py --workers 1
```

Use `--workers` only when the machine has enough GPU memory. Running 24 jobs concurrently on one GPU will usually be counterproductive.

## Model paths

After training, expose each role through its own environment variable, for example:

```text
ROBO_MODEL_PATH_CODE=models/code
ROBO_MODEL_PATH_CIRCUIT=models/circuit
ROBO_MODEL_PATH_VERIFIER_1=models/verifier_1
ROBO_MODEL_PATH_VERIFIER_2=models/verifier_2
ROBO_MODEL_PATH_COMPILER_1=models/compiler_1
ROBO_MODEL_PATH_COMPILER_2=models/compiler_2
ROBO_MODEL_PATH_CONSENSUS=models/consensus
ROBO_MODEL_PATH_COPILOT=models/copilot
```

The suite is designed to integrate with the RoboLab gateway without exposing model credentials to the browser.

## Benchmarking

Do not label these models as Codex-level until they pass a fixed independent benchmark covering:
- code correctness
- compile/test success
- robotics API correctness
- electrical/power consistency
- regression resistance
- adversarial failure detection
