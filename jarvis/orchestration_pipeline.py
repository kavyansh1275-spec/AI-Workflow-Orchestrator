from __future__ import annotations
from dataclasses import dataclass
from .orchestrator import Orchestrator, OrchestrationResult
from .self_debugger import SelfDebugger

@dataclass(frozen=True)
class PipelineResult:
    orchestration: OrchestrationResult
    success: bool
    recovery_attempted: bool

class OrchestrationPipeline:
    """Top-level bounded pipeline: plan, verify and recover planning failures."""
    def __init__(self, router, planner, max_steps=12):
        self.orchestrator=Orchestrator(router,planner,max_steps)
        self.debugger=SelfDebugger(2)

    def run(self,request):
        result=self.orchestrator.prepare(request)
        if result.verified:
            return PipelineResult(result,True,False)
        recovery=self.debugger.run_check(lambda: self.orchestrator.prepare(request).verified)
        return PipelineResult(result,recovery.fixed,recovery.attempts>1)
