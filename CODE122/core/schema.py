from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any
import json, uuid

@dataclass
class Component:
    id: str
    name: str
    kind: str
    voltage_min: float | None = None
    voltage_max: float | None = None
    current_ma: float | None = None
    pins: list[str] = field(default_factory=list)

@dataclass
class Connection:
    source_component: str
    source_pin: str
    target_component: str
    target_pin: str

@dataclass
class EngineeringProject:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "Untitled RoboLab Project"
    requirements: list[str] = field(default_factory=list)
    components: list[Component] = field(default_factory=list)
    connections: list[Connection] = field(default_factory=list)
    firmware: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "EngineeringProject":
        return cls(
            id=value.get("id", str(uuid.uuid4())),
            name=value.get("name", "Untitled RoboLab Project"),
            requirements=list(value.get("requirements", [])),
            components=[Component(**c) for c in value.get("components", [])],
            connections=[Connection(**c) for c in value.get("connections", [])],
            firmware=value.get("firmware", ""),
            metadata=dict(value.get("metadata", {})),
        )

    def json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)
