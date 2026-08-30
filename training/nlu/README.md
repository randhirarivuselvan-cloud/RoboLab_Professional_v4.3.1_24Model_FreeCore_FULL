# RoboLab Neural NLU

RoboLab now includes a compact custom-trained neural multi-label NLU model for English robotics/component descriptions.

It was trained on synthetic paraphrases generated from the RoboLab component ontology. The bootstrap model recognizes 68 common component classes and uses exact-alias boosting for particularly important hardware names.

This is a **small task-specific neural model**, not a general-purpose frontier language model. It is intentionally lightweight enough for CPU inference and free-tier hosting.

## Training

The committed `ai/nlu/model.json` contains the bootstrap weights so the application can run without a model download. To retrain or expand the model, use `train_nlu.py` on a development machine with Python and NumPy, then replace the generated model artifact after evaluation.

Recommended next dataset expansion:
- vendor part numbers
- common misspellings
- conversational descriptions
- multiple components per sentence
- units and quantities
- board-specific terminology
- negative examples (e.g. “do not use a servo”)
- regional wording
