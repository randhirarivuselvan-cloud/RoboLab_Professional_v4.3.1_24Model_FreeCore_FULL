from __future__ import annotations
import re
from typing import Any
from .component_catalog import COMPONENT_CATALOG


def _budget(text: str) -> int | None:
    patterns = [
        r"(?:under|below|within|less than|max(?:imum)?(?:\s+budget|\s+cost)?)\s*(?:₹|rs\.?|inr|\$|usd)?\s*([0-9][0-9,]*)",
        r"(?:₹|rs\.?|inr|\$|usd)\s*([0-9][0-9,]*)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text.lower())
        if match:
            return int(match.group(1).replace(",", ""))
    return None


def _norm(text: str) -> str:
    return re.sub(r"[^a-z0-9+#.\-]+", " ", text.lower()).strip()


def recognize_components(text: str) -> list[dict[str, Any]]:
    normalized = _norm(text)
    found: list[dict[str, Any]] = []
    for canonical, (category, aliases) in COMPONENT_CATALOG.items():
        for alias in aliases:
            if _norm(alias) in normalized:
                found.append({"name": canonical, "category": category, "matched_alias": alias})
                break

    # Preserve explicit quantities even when the exact component is not in the catalog.
    quantity_pattern = re.compile(r"\b(\d+)\s+([a-z][a-z0-9+#.\- ]{1,45})")
    for qty, noun in quantity_pattern.findall(normalized):
        noun = noun.strip()
        if not noun or any(noun in item["name"].lower() or item["name"].lower() in noun for item in found):
            continue
        found.append({"name": noun, "category": "user-specified", "quantity": int(qty), "matched_alias": noun})

    unique: dict[str, dict[str, Any]] = {}
    for item in found:
        unique[item["name"]] = item
    return list(unique.values())


def _controller(found: list[dict[str, Any]], text: str) -> str:
    for item in found:
        if item["category"] == "controller":
            return item["name"]
    if "arduino" in text.lower():
        return "Arduino-family controller (exact board to confirm)"
    return "Controller to be selected from compute, I/O, timing, power and connectivity requirements"


def analyze_idea(description: str):
    text = description.strip()
    words = _norm(text)
    budget = _budget(text)
    recognized = recognize_components(text)
    sensors = [x["name"] for x in recognized if x["category"] == "sensor"]
    actuators = [x["name"] for x in recognized if x["category"] in {"actuator", "driver"}]
    systems: list[str] = []
    requirements: list[str] = []
    constraints: list[str] = []

    # Natural-language goals.
    if any(x in words for x in ["robot", "rover", "vehicle", "bot", "drone"]):
        systems.append("robotics platform")
    if any(x in words for x in ["autonomous", "autonomously", "self driving", "self-driving"]):
        systems.append("autonomous behavior")
    if any(x in words for x in ["firefighting", "fire fighting", "firefighter", "flame", "fire"]):
        systems.extend(["fire/environment sensing", "supervised suppression/demo subsystem"])
        if not sensors or not any("flame" in s.lower() or "smoke" in s.lower() for s in sensors):
            sensors.append("Flame/IR detection sensor")
        requirements.extend([
            "Use a clearly defined and supervised test procedure",
            "Define a stop/fault state before enabling actuators",
            "Use a non-hazardous demonstration target during development",
        ])
    if any(x in words for x in ["line follower", "line following", "line tracking"]):
        systems.append("line-following control")
        if not sensors:
            sensors.append("Line sensor array")
    if any(x in words for x in ["camera", "vision", "image"]):
        systems.append("vision/perception")
    if any(x in words for x in ["wifi", "wi-fi", "bluetooth", "cloud", "iot", "lora"]):
        systems.append("connectivity/telemetry")
    if any(x in words for x in ["arm", "gripper", "pick and place"]):
        systems.append("manipulator")
    if any(x in words for x in ["wheel", "motor", "drive"]):
        systems.append("motion/drive")
        if not actuators:
            actuators.append("DC motor drive via a rated motor driver")

    systems = list(dict.fromkeys(systems)) or ["general embedded/robotics system"]
    sensors = list(dict.fromkeys(sensors)) or ["No explicit sensor identified — propose candidates from the task/environment"]
    actuators = list(dict.fromkeys(actuators)) or ["No explicit actuator identified — propose candidates from the task/motion requirements"]

    if budget is not None:
        constraints.append(f"Target budget: ₹{budget:,}; verify current local prices and availability")
    if "arduino" in words or "uno" in words:
        systems.append("Arduino-compatible control platform")
        requirements.append("Stay within the selected Arduino board's GPIO, ADC, PWM, memory and power constraints")
    if not requirements:
        requirements.append("Convert the natural-language goal into measurable acceptance criteria before final design")
    if not constraints:
        constraints.append("Verify exact component ratings, interfaces, environmental limits and competition rules")

    return {
        "concept": text,
        "status": "Concept analyzed — natural-language engineering baseline generated.",
        "recognized_components": recognized,
        "budget_inr": budget,
        "architecture": {
            "sensing": sensors,
            "actuation": actuators,
            "systems": systems,
            "controller": _controller(recognized, text),
            "power": "Build a voltage/current/peak-load/runtime budget from the selected hardware; never drive motors directly from MCU GPIO pins.",
        },
        "requirements": requirements,
        "constraints": constraints,
        "next_steps": [
            "Extract measurable requirements and acceptance tests.",
            "Resolve recognized parts to exact components or preserve the user's custom part names.",
            "Generate a checkable circuit and pin map from the chosen components.",
            "Generate board-specific firmware tied to that circuit.",
            "Run independent verification and compilation checks.",
            "Prototype and validate on real hardware before competition or field use.",
        ],
        "confidence": "Natural-language baseline; exact specifications require authoritative datasheets and physical validation.",
    }
