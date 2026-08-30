"""Scalable, from-scratch Transformer configuration for RoboLab CODE122.

No pretrained weights or hosted model APIs are used by this module.
The configuration supports small development runs and larger training runs.
"""
from dataclasses import dataclass, asdict
import json
from pathlib import Path

@dataclass(frozen=True)
class ModelConfig:
    name: str
    vocab_size: int = 32768
    context_length: int = 2048
    layers: int = 12
    d_model: int = 768
    heads: int = 12
    ff_mult: int = 4
    dropout: float = 0.0
    rope_theta: float = 10000.0
    tie_embeddings: bool = True

    @property
    def parameters_estimate(self) -> int:
        # Approximate dense decoder-only Transformer parameter count.
        emb = self.vocab_size * self.d_model * (1 if self.tie_embeddings else 2)
        block = self.layers * (4 * self.d_model * self.d_model + 2 * self.d_model * (self.ff_mult * self.d_model))
        return emb + block + self.d_model

    def validate(self) -> None:
        if self.d_model % self.heads:
            raise ValueError("d_model must be divisible by heads")
        if self.context_length < 128:
            raise ValueError("context_length is too small")
        if self.layers < 1 or self.d_model < 128:
            raise ValueError("invalid model dimensions")


def make_specialist_config(name: str, tier: str = "research") -> ModelConfig:
    tiers = {
        "mobile": dict(layers=6, d_model=384, heads=6, context_length=1024),
        "dev": dict(layers=12, d_model=768, heads=12, context_length=2048),
        "research": dict(layers=24, d_model=1536, heads=24, context_length=4096),
        "scale": dict(layers=32, d_model=2560, heads=32, context_length=8192),
    }
    if tier not in tiers:
        raise ValueError(f"unknown tier: {tier}")
    cfg = ModelConfig(name=name, **tiers[tier])
    cfg.validate()
    return cfg


def write_registry(names: list[str], path: str, tier: str = "research") -> None:
    configs = [asdict(make_specialist_config(n, tier)) | {"parameters_estimate": make_specialist_config(n, tier).parameters_estimate} for n in names]
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(configs, indent=2), encoding="utf-8")
