# RoboLab Professional v4.3.1

RoboLab is a robotics engineering workspace with a provider-neutral AI gateway, specialized engineering stages, independent verifier/compiler passes, consensus review, and an integrated Copilot-style assistant.

## AI model architecture

The release defines 14 specialist model roles: Architect, Component, Circuit, Code, CAD, Simulation, BOM, Debug, Documentation, Verifier 1, Verifier 2, Compiler 1, Compiler 2, and Consensus.

The repository includes **training recipes and serving infrastructure**, not pretrained frontier weights. Training a genuinely competitive neural model requires a strong pretrained base model, a large high-quality domain dataset, GPU compute, and evaluation. RoboLab therefore avoids claiming that its deterministic native engine is equivalent to Codex or another frontier model.

## Copilot

The web app exposes `/api/copilot/chat` and `/api/copilot/status`. When a configured provider is available, Copilot uses the Code-model route; otherwise it falls back to a clearly labeled deterministic baseline.

## Custom model gateway

`robolab_model_api` provides:

- `GET /health`
- `GET /v1/models`
- `POST /generate`
- `POST /v1/chat/completions`

The gateway can serve different role-specific checkpoints using `ROBO_MODEL_PATH_<ROLE>` variables, with `ROBO_MODEL_PATH` as a shared fallback. Start it from the project root with `uvicorn robolab_model_api.server:app --host 0.0.0.0 --port $PORT` on a machine with the model-serving dependencies installed.

## Training

`training/model_suite.json` and `training/configs/*.json` define independent LoRA/QLoRA recipes. Replace the placeholder `base_model` with a real pretrained model, supply role-specific training and evaluation data, and run `python training/train_suite.py --role all` on a suitable GPU machine.

## Current no-key deployment

The normal Render service can run with `AI_PROVIDER=none`. This proves the platform shell, native engineering baseline, API routing, and Copilot UI without requiring external model credentials.
