from __future__ import annotations
from dataclasses import dataclass
from typing import Callable

@dataclass(frozen=True)
class Trigger:
    name: str
    predicate: Callable[[str], bool]

class TriggerEngine:
    def __init__(self): self.triggers: dict[str,Trigger]={}
    def register(self,name,predicate):
        key=name.strip()
        if not key: raise ValueError("Trigger name is required")
        self.triggers[key]=Trigger(key,predicate)
    def match(self,event: str) -> tuple[str,...]:
        matched=[]
        for name,trigger in self.triggers.items():
            try:
                if trigger.predicate(event): matched.append(name)
            except Exception:
                continue
        return tuple(matched)
