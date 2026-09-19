from __future__ import annotations
from dataclasses import dataclass
from .orchestration_pipeline import OrchestrationPipeline
from .execution_coordinator import ExecutionCoordinator
from .system_status import SystemStatus

@dataclass(frozen=True)
class SystemOrchestrationResult:
    success: bool
    orchestration: object
    execution: object
    status: SystemStatus

class SystemOrchestrator:
    """Top-level bounded coordinator for JARVIS subsystems."""
    def __init__(self, router, planner, max_steps=12):
        self.pipeline=OrchestrationPipeline(router,planner,max_steps)
        self.coordinator=ExecutionCoordinator(self.pipeline.orchestrator,max_steps)

    def register(self,name,handler):
        self.coordinator.register(name,handler)

    def run(self,request,actions=()):
        orchestration=self.pipeline.run(request)
        execution=self.coordinator.execute(request,actions)
        status=SystemStatus(True,True,True,True,execution.success and orchestration.success)
        return SystemOrchestrationResult(execution.success and orchestration.success,orchestration,execution,status)
