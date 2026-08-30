from dataclasses import dataclass

SPECIALISTS = [
    "builder", "code", "circuit", "embedded", "robotics", "electronics", "mechanics", "cad",
    "physics", "chemistry", "materials", "control", "kinematics", "navigation", "computer_vision",
    "sensors", "motors", "power", "pcb", "communication", "iot", "simulation", "testing", "debugging",
    "firmware", "algorithms", "python", "cpp", "micropython", "arduino", "esp32", "stm32",
    "raspberry_pi", "linux", "math", "optimization", "signal_processing", "automation", "manufacturing",
    "safety", "documentation", "bom", "requirements", "architecture", "verification", "repair", "planner"
]

@dataclass(frozen=True)
class ModelStatus:
    role: str
    state: str = "UNTRAINED"
    checkpoint: str | None = None

REGISTRY = {role: ModelStatus(role) for role in SPECIALISTS}

assert len(REGISTRY) == 48

def status() -> list[dict]:
    return [vars(x) for x in REGISTRY.values()]
