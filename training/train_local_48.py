"""Train RoboLab's 48 lightweight local specialist models from scratch.

No pretrained weights, remote APIs, or network calls are used. The resulting models are
small TF-IDF/cosine retrieval specialists; they are intentionally NOT presented as LLMs.
"""
from pathlib import Path
from ai.local_models.registry import MODEL_SPECS, checkpoint_path
from ai.local_models.runtime import bootstrap_examples, train_model
import json

ROOT = Path(__file__).resolve().parent.parent / 'training_48_models' / 'artifacts'


def main() -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    for role, spec in MODEL_SPECS.items():
        payload = train_model(spec, bootstrap_examples(spec))
        out = checkpoint_path(role, ROOT)
        out.write_text(json.dumps(payload, indent=2, sort_keys=True) + '\n', encoding='utf-8')
        print(f'TRAINED_LOCAL {role} -> {out}')
    print(f'Completed {len(MODEL_SPECS)} local specialist checkpoints.')


if __name__ == '__main__':
    main()
