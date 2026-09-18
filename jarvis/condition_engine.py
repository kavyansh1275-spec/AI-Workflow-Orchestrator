from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Any

@dataclass(frozen=True)
class Condition:
    name: str
    predicate: Callable[[Any], bool]

class ConditionEngine:
    def evaluate(self,condition: Condition,value: Any) -> bool:
        try: return bool(condition.predicate(value))
        except Exception: return False
    def branch(self,conditions: tuple[Condition,...],value: Any) -> str:
        for condition in conditions:
            if self.evaluate(condition,value): return condition.name
        return "default"
