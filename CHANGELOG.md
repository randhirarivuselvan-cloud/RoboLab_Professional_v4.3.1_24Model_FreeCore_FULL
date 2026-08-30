# RoboLab Professional Changelog

## v4.2.0 — Multi-Model + Copilot Architecture

- Added 14-role model registry: Architect, Component, Circuit, Code, CAD, Simulation, BOM, Debug, Documentation, Verifier 1/2, Compiler 1/2, Consensus.
- Added role-specific model environment variables and model listing endpoint.
- Added dual independent verifier and compiler routes.
- Added RoboLab Copilot UI and API with model-backed and deterministic fallback modes.
- Added custom model gateway support for role-specific checkpoints.
- Added training suite configuration, per-role datasets, and QLoRA recipe launcher.
- Kept no-key deployment mode functional with explicit baseline labeling.
- Fixed prior startup/runtime issues and expanded tests.

### Transparency

This release contains **training infrastructure and serving code, not trained frontier weights**. A real neural model must be trained on a suitable pretrained base model and high-quality domain data using GPU compute. The release never claims the native baseline is equivalent to Codex or another frontier model.
