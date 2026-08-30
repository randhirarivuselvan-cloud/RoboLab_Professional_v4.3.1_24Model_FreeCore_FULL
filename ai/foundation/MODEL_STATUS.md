# 48-model neural training status

The repository now contains a genuine decoder-only Transformer implementation with random initialization and a gradient-training script. This is an architecture/training pipeline, not evidence that 48 frontier-quality models have already been trained.

## Current truth
- Model roles: 48
- Neural architecture: implemented
- Random initialization: implemented
- Next-token gradient training: implemented
- Pretrained weights: none
- Remote AI APIs: none
- Adequate frontier-scale corpus: NOT_AVAILABLE
- Frontier-scale compute: NOT_AVAILABLE
- 48 frontier-quality checkpoints: NOT_TRAINED
- Independent benchmark proof: NOT_TESTED

Run one specialist with `python -m ai.foundation.train_from_scratch --role nlu --steps 1000` after installing PyTorch and supplying a sufficiently large licensed/owned corpus. Use `--role all` only on hardware sized for the resulting workload.

A checkpoint is never labelled frontier-quality by configuration alone; benchmark results and reproducible training evidence are required.
