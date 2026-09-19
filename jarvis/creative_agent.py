from __future__ import annotations
from dataclasses import dataclass
from typing import Callable

@dataclass(frozen=True)
class CreativeAgentTask:
    role: str
    objective: str

class CreativeAgent:
    """Bounded creative specialist coordinator."""
    ROLES=("director","storyboarder","asset_designer","animator","editor","verifier")
    def __init__(self,max_tasks=6):
        self.max_tasks=max(1,max_tasks)
        self.handlers:dict[str,Callable[[str],str]]={}
    def register(self,role,handler):
        if role not in self.ROLES: raise ValueError(f"Unknown creative role: {role}")
        self.handlers[role]=handler
    def plan(self,objective):
        if not objective.strip(): return ()
        return tuple(CreativeAgentTask(r,objective) for r in self.ROLES[:self.max_tasks])
    def execute(self,objective):
        results=[]
        for task in self.plan(objective):
            handler=self.handlers.get(task.role)
            results.append((task.role, handler(task.objective) if handler else "planned"))
        return tuple(results)
