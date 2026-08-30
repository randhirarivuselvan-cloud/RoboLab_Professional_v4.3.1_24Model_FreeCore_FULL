"""Compatibility export for the local-only 48-model registry."""
from ai.local_models.registry import MODEL_SPECS, ModelSpec, model_for, public_registry

__all__ = ["MODEL_SPECS", "ModelSpec", "model_for", "public_registry"]
