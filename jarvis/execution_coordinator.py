from __future__ import annotations
from dataclasses import dataclass
from .orchestrator import Orchestrator, OrchestrationResult
from .automation_engine import AutomationEngine, AutomationRun

@dataclass(frozen=True)
class CoordinationResult:
    orchestration: OrchestrationResult
    runs: tuple[AutomationRun,...]
    success: bool

class ExecutionCoordinator:
    """Connects orchestration plans to explicitly registered bounded actions."""
    def __init__(self, orchestrator: Orchestrator, max_steps=12):
        self.orchestrator=orchestrator
        self.automation=AutomationEngine(max_steps)

    def register(self,name,handler):
        self.automation.register(name,handler)

    def execute(self,request,actions=()):
        orchestration=self.orchestrator.prepare(request)
        runs=self.automation.execute(list(actions)[:self.automation.max_tasks])
        success=orchestration.verified and (not actions or all(r.success for r in runs))
        return CoordinationResult(orchestration,tuple(runs),success)
