from __future__ import annotations
import hashlib
from typing import Any
from models.final_workflow import FinalWorkflowResult

class FinalWorkflowPipeline:
    """V24 end-to-end solution-to-final-workflow pipeline."""
    def __init__(self, orchestrator: Any):
        self.orchestrator = orchestrator

    def run(self, request: str, environment: str = "staging", live: bool = False) -> FinalWorkflowResult:
        request = request.strip()
        if not request:
            raise ValueError("final workflow request cannot be blank")
        build = self.orchestrator.build_workflow(request)
        repair = self.orchestrator.test_and_repair(request)
        deployment = self.orchestrator.deploy_workflow(request, environment=environment, live=live)
        passed = bool(repair.get("passed")) and bool(build.get("status") == "built")
        stages = [
            {"stage": "compile", "status": build.get("status", "blocked")},
            {"stage": "test_and_repair", "status": repair.get("status", "blocked"), "attempts": repair.get("attempts", 0)},
            {"stage": "deployment", "status": deployment.get("status", "blocked")},
        ]
        return FinalWorkflowResult(pipeline_id=f"final-{hashlib.sha256(request.encode()).hexdigest()[:12]}", request=request, stages=stages, provider=build.get("provider", "generic"), artifact=repair.get("final_artifact") or build.get("workflow", {}), deployment=deployment, passed=passed, status="complete" if passed else "blocked")
