"""Launch independent LoRA/QLoRA training jobs for the RoboLab model suite.

Requires a suitable GPU environment and a real pretrained base model in each
training/configs/*.json file. No pretend-training or fake checkpoints are made.
"""
from __future__ import annotations
import argparse
import json
import subprocess
import sys
from pathlib import Path

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--role', default='all')
    ap.add_argument('--config-dir', default='training/configs')
    args = ap.parse_args()
    configs = sorted(Path(args.config_dir).glob('*.json'))
    if args.role != 'all':
        configs = [Path(args.config_dir) / f'{args.role}.json']
    for cfg in configs:
        if not cfg.exists():
            raise SystemExit(f'Missing config: {cfg}')
        data = json.loads(cfg.read_text(encoding='utf-8'))
        base_model = data['base_model']
        if base_model.startswith('SET_'):
            raise SystemExit(f'Set a real pretrained base_model in {cfg} before training.')
        cmd = [
            sys.executable, 'training/train_lora.py',
            '--base-model', base_model,
            '--data', data['dataset'],
            '--output', data['output_dir'],
            '--epochs', str(data.get('epochs', 3)),
            '--lr', str(data.get('learning_rate', 2e-4)),
            '--max-length', str(data.get('max_seq_length', 8192)),
        ]
        print('Launching:', ' '.join(cmd))
        rc = subprocess.call(cmd)
        if rc != 0:
            return rc
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
