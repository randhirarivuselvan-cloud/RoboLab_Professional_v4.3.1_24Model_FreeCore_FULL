# RoboLab Model Suite

The model suite is deliberately modular so the underlying neural model can be upgraded after release without changing the product API.

## Independence rules

- Verifier 1 and Verifier 2 receive independent inference calls.
- Compiler 1 and Compiler 2 receive independent inference calls.
- Consensus consumes the evidence produced by upstream stages and should not silently overwrite disagreements.
- A final result must remain marked for review whenever required evidence is missing or stages disagree.

## Model paths

For a separately hosted model gateway, set variables such as:

`ROBO_MODEL_PATH_CODE=/models/code`

`ROBO_MODEL_PATH_CIRCUIT=/models/circuit`

`ROBO_MODEL_PATH_VERIFIER_1=/models/verifier-1`

`ROBO_MODEL_PATH_COMPILER_2=/models/compiler-2`

or set a single `ROBO_MODEL_PATH` shared by all roles.

These paths point to actual model directories after training and export. The repository does not ship trained weights.
