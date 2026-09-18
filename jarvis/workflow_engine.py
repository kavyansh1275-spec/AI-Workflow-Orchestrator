from __future__ import annotations
from dataclasses import dataclass
from .automation_engine import AutomationEngine, AutomationRun

@dataclass(frozen=True)
class Workflow:
    name: str
    tasks: tuple[tuple[str,str], ...]

@dataclass(frozen=True)
class WorkflowResult:
    name: str
    runs: tuple[AutomationRun,...]
    success: bool

class WorkflowEngine:
    """Sequential workflow runner using only explicitly registered automation handlers."""
    def __init__(self,max_tasks=12): self.automation=AutomationEngine(max_tasks)
    def register(self,name,handler): self.automation.register(name,handler)
    def run(self,workflow: Workflow) -> WorkflowResult:
        runs=self.automation.execute(list(workflow.tasks))
        return WorkflowResult(workflow.name,runs, bool(runs) and all(r.success for r in runs))
