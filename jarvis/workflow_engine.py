from __future__ import annotations
from dataclasses import dataclass
from .automation_engine import AutomationEngine, AutomationTask, AutomationRun
from .automation_state import AutomationState

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
    """Sequential workflow runner with bounded execution and failure state."""
    def __init__(self,max_tasks=12):
        self.automation=AutomationEngine(max_tasks); self.state=AutomationState()
    def register(self,name,handler): self.automation.register(name,handler)
    def run(self,workflow: Workflow) -> WorkflowResult:
        runs=[]
        for name,argument in workflow.tasks[:self.automation.max_tasks]:
            run=self.automation.run(AutomationTask(name,name),argument)
            runs.append(run); self.state.record(name,run.success)
            if not run.success: break
        return WorkflowResult(workflow.name,tuple(runs),bool(runs) and all(r.success for r in runs))
