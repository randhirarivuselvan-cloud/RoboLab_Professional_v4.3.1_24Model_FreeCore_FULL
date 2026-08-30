from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any

class AIProvider(ABC):
    name = "base"

    @abstractmethod
    def available(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def generate(self, system: str, prompt: str, model: str | None = None) -> dict[str, Any]:
        raise NotImplementedError
