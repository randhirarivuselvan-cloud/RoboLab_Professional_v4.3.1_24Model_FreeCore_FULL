from __future__ import annotations

import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ai.local_models.registry import MODEL_SPECS
from ai.local_models.runtime import LocalModelRuntime, write_checkpoint


def test_suite_has_exactly_48_local_roles():
    assert len(MODEL_SPECS) == 48
    assert len(set(MODEL_SPECS)) == 48


def test_untrained_model_does_not_fall_back_to_network():
    with tempfile.TemporaryDirectory() as directory:
        status = LocalModelRuntime(directory).status("architect")
        assert status["state"] == "NOT_IMPLEMENTED"
        assert status["code"] == "MODEL_NOT_TRAINED"


def test_checkpoint_is_actually_trained_and_served_locally():
    with tempfile.TemporaryDirectory() as directory:
        write_checkpoint("power", directory)
        runtime = LocalModelRuntime(directory)
        status = runtime.status("power")
        assert status["state"] == "TRAINED_LOCAL"
        response = runtime.generate("power", "Calculate battery current and power budget.")
        assert response["state"] == "COMPLETED"
        assert response["mode"] == "local_trained_retrieval"
        assert response["network_used"] is False
