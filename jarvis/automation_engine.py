from __future__ import annotations
from dataclasses import dataclass
from typing import Callable

@dataclass(frozen=True)
class AutomationTask:
    name: str
    action: str
    enabled: bool = True

@dataclass(frozen=True)
class AutomationRun:
    task: str
    success: bool
    result: str

class AutomationEngine:
    """Bounded, allowlisted automation engine with explicit task registration."""
    def __init__(self, max_tasks: int = 12):
        self.max_tasks=max(1,max_tasks)
        self.handlers: dict[str,Callable[[str],str]]={}

    def register(self,name: str,handler: Callable[[str],str]) -> None:
        key=name.strip()
        if not key: raise ValueError("Task name is required")
        self.handlers[key]=handler

    def plan(self, tasks: list[AutomationTask]) -> tuple[AutomationTask,...]:
        return tuple(tasks[:self.max_tasks])

    def run(self, task: AutomationTask, argument: str = "") -> AutomationRun:
        if not task.enabled: return AutomationRun(task.name,False,"Task disabled")
        handler=self.handlers.get(task.name)
        if handler is None: return AutomationRun(task.name,False,"Task not registered")
        try: return AutomationRun(task.name,True,str(handler(argument)))
        except Exception as exc: return AutomationRun(task.name,False,f"Task error: {type(exc).__name__}")

    def execute(self,tasks: list[tuple[str,str]]) -> tuple[AutomationRun,...]:
        runs=[]
        for name,argument in tasks[:self.max_tasks]:
            runs.append(self.run(AutomationTask(name,name),argument))
        return tuple(runs)
