# RoboLab Copilot

RoboLab Copilot is a first-class assistant inside the workspace, inspired by the workflow of modern code copilots without copying proprietary implementation details.

It accepts:

- natural-language questions
- project context
- review/debug/test actions
- engineering-specific context such as board, code, circuit or requirements

When an external/provider model is enabled it routes through the model provider; with `AI_PROVIDER=none` it uses a deterministic safety-oriented baseline and explicitly says it is not a frontier model.

The next upgrade path is tool execution: repository search, file diffs, patch proposals, test execution, compile checks, and stage-aware project context. Those tools should be permissioned and auditable before being enabled for production users.
