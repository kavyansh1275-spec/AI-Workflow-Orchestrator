from __future__ import annotations
from dataclasses import dataclass, field

@dataclass
class AutomationState:
    completed: list[str] = field(default_factory=list)
    failed: list[str] = field(default_factory=list)

    def record(self,name: str,success: bool) -> None:
        (self.completed if success else self.failed).append(name)

    def can_retry(self,name: str) -> bool:
        return name in self.failed and name not in self.completed
