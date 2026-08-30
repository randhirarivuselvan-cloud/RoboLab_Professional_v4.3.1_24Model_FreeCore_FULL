from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from ai.local_models.registry import MODEL_SPECS
from ai.local_models.runtime import write_checkpoint


def main() -> int:
    parser = argparse.ArgumentParser(description="Train all 48 RoboLab local-only role models from scratch.")
    parser.add_argument("--output", default=str(ROOT / "training_48_models" / "artifacts"))
    parser.add_argument("--roles", nargs="*", choices=sorted(MODEL_SPECS), default=sorted(MODEL_SPECS))
    args = parser.parse_args()
    output = Path(args.output)
    manifest = {"format": "robolab-local-suite-v1", "count": 0, "models": [], "network_used": False}
    for role in args.roles:
        path = write_checkpoint(role, output)
        payload = json.loads(path.read_text(encoding="utf-8"))
        manifest["models"].append({"role": role, "model": payload["model_id"], "checkpoint": path.name, "training_data_sha256": payload["training_data_sha256"]})
        print(f"TRAINED_LOCAL {role}: {path}")
    manifest["count"] = len(manifest["models"])
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if len(args.roles) == len(MODEL_SPECS) and manifest["count"] != 48:
        raise RuntimeError("48-model training invariant failed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
