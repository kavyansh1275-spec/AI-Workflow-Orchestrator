from __future__ import annotations
from dataclasses import dataclass
from typing import Callable
from .automation_engine import AutomationEngine

@dataclass(frozen=True)
class AutomationTaskPlan:
    role: str
    objective: str

class AutomationAgent:
    ROLES=("planner","executor","verifier")
    def __init__(self,max_tasks=3):
        self.max_tasks=max(1,max_tasks); self.handlers:dict[str,Callable[[str],str]]={}
    def register(self,role,handler):
        if role not in self.ROLES: raise ValueError(f"Unknown automation role: {role}")
        self.handlers[role]=handler
    def plan(self,objective):
        return tuple(AutomationTaskPlan(r,objective) for r in self.ROLES[:self.max_tasks]) if objective.strip() else ()
    def execute(self,objective):
        return tuple((p.role,self.handlers[p.role](p.objective) if p.role in self.handlers else "planned") for p in self.plan(objective))
