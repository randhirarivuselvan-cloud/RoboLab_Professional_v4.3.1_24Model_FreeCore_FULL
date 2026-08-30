from __future__ import annotations
import argparse, json, os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

roles = [x["id"] for x in json.loads(Path("training/model_suite_24.json").read_text())["roles"]]

def run(role):
    env=os.environ.copy()
    p=subprocess.run([sys.executable, "training/scripts/train_role.py", role], env=env)
    return role, p.returncode

if __name__ == "__main__":
    ap=argparse.ArgumentParser(description="Train the 24 RoboLab specialist adapters.")
    ap.add_argument("--roles", nargs="*", default=roles)
    ap.add_argument("--workers", type=int, default=1,
                    help="Parallel jobs. Match this to actual GPU capacity; 1 is safest.")
    args=ap.parse_args()
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futures=[ex.submit(run, r) for r in args.roles]
        ok=True
        for f in as_completed(futures):
            role, rc=f.result()
            print(f"{role}: {'PASS' if rc==0 else 'FAIL'}")
            ok &= (rc==0)
    raise SystemExit(0 if ok else 1)
