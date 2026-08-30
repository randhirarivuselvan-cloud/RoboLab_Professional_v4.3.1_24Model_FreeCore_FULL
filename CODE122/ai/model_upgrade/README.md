# RoboLab CODE122 — Model Upgrade

This module defines the upgrade path for the 48 local-first specialists.

## Principles
- No OpenAI, Google, Anthropic, or other hosted model API is required.
- Models are randomly initialized for from-scratch training.
- Training, checkpoint, evaluation, and readiness are separate states.
- A model is never called frontier-quality without measured benchmark evidence.

## Specialist families
1. Builder / requirements / planning
2. Code generation / debugging / verification
3. Circuit synthesis / electrical validation
4. Robotics / control / kinematics
5. CAD / geometry / manufacturing
6. Simulation / physics
7. BOM / component / compatibility
8. Documentation / explanation / project management

The 48 roles should be independently configurable and trainable. Model size is configurable so local development can use small models while larger training runs can scale when compute is available.

## Quality pipeline
`dataset -> tokenizer -> pretrain from random initialization -> checkpoint -> held-out evaluation -> specialist benchmark -> regression suite -> READY`

`FRONTIER_TARGET_REACHED` is reserved for models whose measured results meet a documented target benchmark; it is not assigned by configuration alone.
