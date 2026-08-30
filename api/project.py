def analyze_idea(description):
    text = description.strip()
    words = text.lower()
    sensors = []
    actuators = []
    systems = []
    if any(x in words for x in ["camera", "vision"]): sensors.append("Camera / vision system")
    if any(x in words for x in ["ultrasonic", "distance"]): sensors.append("Distance sensor")
    if any(x in words for x in ["imu", "gyro", "accelerometer"]): sensors.append("IMU")
    if any(x in words for x in ["motor", "wheel", "drive"]): actuators.append("Motor/drive system")
    if "servo" in words: actuators.append("Servo actuator")
    if any(x in words for x in ["robot", "rover", "vehicle"]): systems.append("Mobile robotics platform")
    if any(x in words for x in ["iot", "wifi", "bluetooth", "cloud"]): systems.append("Connectivity/IoT")
    if not sensors: sensors.append("Select sensors from the Component Lab")
    if not actuators: actuators.append("Select actuators from the Component Lab")
    if not systems: systems.append("Define the mechanical/electronic architecture")
    return {
        "concept": text,
        "novelty_mode": True,
        "status": "Concept captured — engineering analysis required.",
        "architecture": {
            "sensing": sensors,
            "actuation": actuators,
            "systems": systems,
            "controller": "Choose a controller based on compute, I/O, power and connectivity needs.",
            "power": "Estimate voltage, current, peak load and battery/runtime requirements."
        },
        "next_steps": [
            "Define measurable requirements and constraints.",
            "Choose candidate components.",
            "Create the circuit and mechanical concept.",
            "Generate a software starter.",
            "Simulate/test assumptions where possible.",
            "Prototype and iterate."
        ],
        "confidence": "Concept-level only; physical feasibility must be validated."
    }
