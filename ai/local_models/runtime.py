from __future__ import annotations

import hashlib
import json
import math
import re
from collections import Counter
from pathlib import Path
from typing import Iterable

from .registry import MODEL_SPECS, ModelSpec, checkpoint_path

TOKEN_RE = re.compile(r"[a-z0-9_+#.-]+")


def tokenize(text: str) -> list[str]:
    return TOKEN_RE.findall(text.lower())


def bootstrap_examples(spec: ModelSpec) -> list[dict[str, str]]:
    terms = ", ".join(spec.seed_terms)
    return [
        {
            "prompt": f"Create a {spec.role} review for a robotics project.",
            "response": f"{spec.role}: identify known facts, missing {terms} evidence, measurable checks, risks, and a reversible next action.",
        },
        {
            "prompt": f"What must be validated before accepting a {spec.key} result?",
            "response": f"{spec.role}: separate evidence from assumptions; record inputs, constraints, test method, result, and unresolved risk.",
        },
        {
            "prompt": f"Find the highest-risk issue in this engineering design.",
            "response": f"{spec.role}: prioritize safety, interface compatibility, ratings, and independently reproducible validation before deployment.",
        },
        {
            "prompt": f"Prepare a handoff for the {spec.key} subsystem.",
            "response": f"{spec.role}: include configuration, interfaces, limits, test evidence, rollback path, and owner for unresolved items.",
        },
    ]


def _vector(tokens: Iterable[str], idf: dict[str, float]) -> dict[str, float]:
    counts = Counter(tokens)
    return {token: count * idf.get(token, 0.0) for token, count in counts.items() if token in idf}


def _norm(vector: dict[str, float]) -> float:
    return math.sqrt(sum(value * value for value in vector.values()))


def train_model(spec: ModelSpec, examples: list[dict[str, str]]) -> dict:
    if len(examples) < 2:
        raise ValueError("At least two examples are required for local training.")
    documents = [tokenize(row["prompt"]) for row in examples]
    doc_count = len(documents)
    frequency = Counter(token for document in documents for token in set(document))
    idf = {token: math.log((1 + doc_count) / (1 + seen)) + 1 for token, seen in frequency.items()}
    serialized_examples = []
    for row, document in zip(examples, documents, strict=True):
        vector = _vector(document, idf)
        serialized_examples.append({
            "prompt": row["prompt"],
            "response": row["response"],
            "vector": vector,
            "norm": _norm(vector),
        })
    source_digest = hashlib.sha256(json.dumps(examples, sort_keys=True).encode("utf-8")).hexdigest()
    return {
        "format": "robolab-local-retrieval-v1",
        "training": "from_scratch_local_bootstrap",
        "role": spec.key,
        "model_id": spec.model_id,
        "examples": len(examples),
        "idf": idf,
        "documents": serialized_examples,
        "training_data_sha256": source_digest,
        "network_used": False,
    }


def write_checkpoint(role: str, output_root: str | Path) -> Path:
    spec = MODEL_SPECS[role]
    checkpoint = train_model(spec, bootstrap_examples(spec))
    output = checkpoint_path(role, output_root)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(checkpoint, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return output


class LocalModelRuntime:
    """Loads only RoboLab's local trained checkpoints; it has no HTTP or vendor dependency."""

    def __init__(self, root: str | Path | None = None):
        self.root = root

    def status(self, role: str) -> dict:
        if role not in MODEL_SPECS:
            return {"state": "NOT_IMPLEMENTED", "code": "UNKNOWN_ROLE", "role": role}
        path = checkpoint_path(role, self.root)
        if not path.is_file():
            return {
                "state": "NOT_IMPLEMENTED",
                "code": "MODEL_NOT_TRAINED",
                "role": role,
                "model": MODEL_SPECS[role].model_id,
                "message": "Local model checkpoint is absent. Run the from-scratch trainer; no remote fallback exists.",
            }
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            if payload.get("role") != role or payload.get("format") != "robolab-local-retrieval-v1":
                raise ValueError("checkpoint identity mismatch")
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            return {"state": "FAILED", "code": "INVALID_CHECKPOINT", "role": role, "message": str(exc)}
        return {"state": "TRAINED_LOCAL", "role": role, "model": payload["model_id"], "examples": payload["examples"], "network_used": False}

    def generate(self, role: str, prompt: str) -> dict:
        status = self.status(role)
        if status["state"] != "TRAINED_LOCAL":
            return status
        payload = json.loads(checkpoint_path(role, self.root).read_text(encoding="utf-8"))
        query = _vector(tokenize(prompt), payload["idf"])
        query_norm = _norm(query)
        best = None
        best_score = -1.0
        for row in payload["documents"]:
            dot = sum(value * row["vector"].get(token, 0.0) for token, value in query.items())
            score = dot / (query_norm * row["norm"]) if query_norm and row["norm"] else 0.0
            if score > best_score:
                best, best_score = row, score
        return {
            "state": "COMPLETED",
            "mode": "local_trained_retrieval",
            "model": payload["model_id"],
            "role": role,
            "response": best["response"] if best else "No trained local response is available.",
            "similarity": round(best_score, 6),
            "limitations": ["This is a small local statistical retrieval model, not a generative frontier language model."],
            "network_used": False,
        }
