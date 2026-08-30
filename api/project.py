import re


def _budget(text: str):
    match = re.search(r"(?:under|below|within|max(?:imum)?\s*(?:budget|cost)?\s*)\s*[₹rs.]*\s*([0-9][0-9,]*)", text.lower())
    if match:
        return int(match.group(1).replace(',', ''))
    return None


def analyze_idea(description):
    text = description.strip()
    words = text.lower()
    budget = _budget(text)
    is_robot = any(x in words for x in ["robot", "rover", "vehicle"])
    is_fire = any(x in words for x in ["firefighting", "fire fighting", "firefighter", "flame", "fire"])
    is_arduino = "arduino" in words or "uno" in words

    sensors = []
    actuators = []
    systems = []
    requirements = []
    constraints = []

    if is_fire:
        sensors += [
            "Flame/IR detection sensor for a supervised educational prototype",
            "Front obstacle-distance sensor",
        ]
        actuators += ["Two-wheel DC gearmotor drive via a rated motor driver"]
        systems += ["Mobile robotics platform", "Fire-target detection subsystem", "Supervised suppression/demo subsystem"]
        requirements += [
            "Detect a target consistently before activating the demo action",
            "Stop the drive system on obstacle or fault conditions",
            "Use a non-hazardous test target/simulation during development",
        ]
        constraints += ["Do not treat the design as fire-service equipment", "Validate all real-world tests under appropriate adult supervision"]

    if is_arduino:
        systems.append("Arduino Uno control platform")
        requirements.append("Stay within Arduino Uno GPIO, ADC, PWM, memory and power limits")

    if any(x in words for x in ["camera", "vision"]):
        sensors.append("Camera / vision system")
    if any(x in words for x in ["ultrasonic", "distance"]):
        sensors.append("Ultrasonic distance sensor")
    if any(x in words for x in ["imu", "gyro", "accelerometer"]):
        sensors.append("IMU")
    if any(x in words for x in ["motor", "wheel", "drive"]):
        actuators.append("Motor/drive system")
    if "servo" in words:
        actuators.append("Servo actuator")
    if is_robot:
        systems.append("Mobile robotics platform")
    if any(x in words for x in ["iot", "wifi", "bluetooth", "cloud"]):
        systems.append("Connectivity/IoT")

    # Deduplicate while preserving order.
    sensors = list(dict.fromkeys(sensors))
    actuators = list(dict.fromkeys(actuators))
    systems = list(dict.fromkeys(systems))

    if not sensors:
        sensors.append("Select sensors from the Component Lab")
    if not actuators:
        actuators.append("Select actuators from the Component Lab")
    if not systems:
        systems.append("Define the mechanical/electronic architecture")

    if budget is not None:
        constraints.append(f"Target budget: ₹{budget}")

    controller = "Arduino Uno" if is_arduino else "Choose a controller based on compute, I/O, power and connectivity needs."
    power = "Estimate voltage, current, peak load and battery/runtime requirements; motors must not be powered from MCU GPIO pins."

    next_steps = [
        "Convert the idea into measurable requirements and acceptance tests.",
        "Choose candidate components within the stated constraints/budget.",
        "Generate and review the electrical connection/pin plan.",
        "Generate a board-specific software starter and test cases.",
        "Run simulation or bench validation before physical tests.",
        "Review the project with the independent verification stages.",
    ]

    return {
        "concept": text,
        "status": "Concept analyzed — structured engineering baseline generated.",
        "architecture": {
            "sensing": sensors,
            "actuation": actuators,
            "systems": systems,
            "controller": controller,
            "power": power,
        },
        "requirements": requirements,
        "constraints": constraints,
        "budget_inr": budget,
        "next_steps": next_steps,
        "confidence": "Deterministic engineering baseline; verify specifications, competition rules and physical behavior before deployment.",
    }
