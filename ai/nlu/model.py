from __future__ import annotations
import base64, hashlib, json, math, re, struct, zlib
from pathlib import Path

_MODEL_PATH = Path(__file__).with_name("model.json")


def _unpack(spec: dict[str, object], count: int) -> list[float]:
    raw = zlib.decompress(base64.b64decode(str(spec["data"])))
    vals = struct.unpack("<" + "e" * count, raw)
    scale = float(spec["scale"])
    return [float(v) * scale for v in vals]


_DATA = json.loads(_MODEL_PATH.read_text(encoding="utf-8"))
_LABELS: list[str] = _DATA["labels"]
_D = int(_DATA["feature_dim"])
_H = int(_DATA["hidden_dim"])
_W1 = _unpack(_DATA["W1"], _D * _H)
_B1 = _unpack(_DATA["b1"], _H)
_W2 = _unpack(_DATA["W2"], _H * len(_LABELS))
_B2 = _unpack(_DATA["b2"], len(_LABELS))
_THRESHOLD = float(_DATA.get("threshold", 0.24))


def _hash_feature(gram: str) -> int:
    digest = hashlib.sha256(gram.encode("utf-8")).digest()
    return int.from_bytes(digest[:4], "little") % _D


def _features(text: str) -> list[float]:
    clean = re.sub(r"\s+", " ", text.lower().strip())
    x = [0.0] * _D
    padded = " " + clean + " "
    for n in (2, 3, 4):
        for i in range(max(0, len(padded) - n + 1)):
            gram = padded[i : i + n]
            x[_hash_feature(gram)] += 1.0
    for word in re.findall(r"[a-z0-9][a-z0-9\-\.]*", clean):
        x[_hash_feature("w:" + word)] += 2.0
    norm = math.sqrt(sum(v * v for v in x)) or 1.0
    return [v / norm for v in x]


def _sigmoid(v: float) -> float:
    if v >= 0:
        e = math.exp(-min(v, 50.0))
        return 1.0 / (1.0 + e)
    e = math.exp(max(v, -50.0))
    return e / (1.0 + e)


def _neural_scores(text: str) -> list[float]:
    x = _features(text)
    hidden = []
    for j in range(_H):
        total = _B1[j]
        for i, xv in enumerate(x):
            total += xv * _W1[i * _H + j]
        hidden.append(max(0.0, total))
    out = []
    width = len(_LABELS)
    for k in range(width):
        total = _B2[k]
        for j, hv in enumerate(hidden):
            total += hv * _W2[j * width + k]
        out.append(_sigmoid(total))
    return out


def _alias_boost(text: str, label: str) -> float:
    # Exact aliases provide a small safety boost for rare part numbers/names.
    t = text.lower()
    aliases = {
        "arduino uno": ["arduino uno", "uno r3", "uno"],
        "ultrasonic sensor": ["ultrasonic", "hc-sr04", "distance sensor"],
        "ir sensor": ["infrared", "ir sensor", "ir obstacle"],
        "line sensor": ["line sensor", "line follower", "ir array"],
        "flame sensor": ["flame sensor", "fire detector", "flame detector"],
        "smoke gas sensor": ["smoke sensor", "gas sensor", "mq2", "mq-2"],
        "dc motor": ["dc motor", "gear motor", "geared motor", "motor"],
        "servo motor": ["servo", "sg90", "mg996r"],
        "pump": ["pump", "water pump", "mini pump"],
        "camera": ["camera", "vision", "webcam"],
        "imu": ["imu", "gyroscope", "accelerometer", "mpu6050"],
        "battery": ["battery", "battery pack", "rechargeable battery"],
        "lipo battery": ["lipo", "li-po", "lithium polymer"],
        "li-ion battery": ["li-ion", "lithium ion", "18650"],
        "l298n": ["l298n", "l298", "h bridge"],
        "tb6612": ["tb6612", "tb6612fng"],
        "pca9685": ["pca9685"],
        "wifi module": ["wifi", "wi-fi"],
        "bluetooth module": ["bluetooth", "hc-05", "hc05", "hc-06"],
    }
    return 0.45 if any(a in t for a in aliases.get(label, [])) else 0.0


def recognize_components(text: str, top_k: int = 12, threshold: float | None = None) -> list[dict[str, object]]:
    if not text or not text.strip():
        return []
    scores = _neural_scores(text)
    use_threshold = _THRESHOLD if threshold is None else threshold
    ranked = sorted(range(len(_LABELS)), key=lambda i: scores[i] + _alias_boost(text, _LABELS[i]), reverse=True)
    results: list[dict[str, object]] = []
    for i in ranked[: max(top_k, 1)]:
        score = min(0.99, scores[i] + _alias_boost(text, _LABELS[i]))
        if score >= use_threshold:
            results.append({"component": _LABELS[i], "confidence": round(score, 3), "model": "robolab-nlu-0.1"})
    return results
