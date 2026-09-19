from __future__ import annotations
from dataclasses import dataclass
from typing import Callable

@dataclass(frozen=True)
class BusinessTask:
    role: str
    objective: str

class BusinessIntelligenceAgent:
    """Bounded specialist roles for business analysis."""
    ROLES=("analyst","sales_analyst","finance_analyst","risk_analyst","reporter")
    def __init__(self,max_tasks=5): self.max_tasks=max(1,max_tasks); self.handlers:dict[str,Callable[[str],str]]={}
    def register(self,role,handler):
        if role not in self.ROLES: raise ValueError(f"Unknown business role: {role}")
        self.handlers[role]=handler
    def plan(self,objective):
        return tuple(BusinessTask(r,objective) for r in self.ROLES[:self.max_tasks]) if objective.strip() else ()
    def execute(self,objective):
        return tuple((t.role,self.handlers[t.role](t.objective) if t.role in self.handlers else "planned") for t in self.plan(objective))
