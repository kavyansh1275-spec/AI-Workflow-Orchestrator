from __future__ import annotations

import hashlib
from core.orchestrator import Orchestrator
from models.control_loop import ControlLoopResult


class AutonomousControlLoop:
    """Close the planning -> validation -> deployment-readiness -> monitoring loop safely."""
    def __init__(self, orchestrator: Orchestrator | None = None) -> None:
        self.orchestrator = orchestrator or Orchestrator()

    def run(self, request: str, environment: str = "staging") -> ControlLoopResult:
        request = request.strip()
        if not request:
            raise ValueError("control-loop request cannot be blank")
        research = self.orchestrator.research(request)
        validation = self.orchestrator.validate_solution(request)
        deployment = self.orchestrator.plan_deployment(request, environment=environment)
        stages = [
            {"stage": "research", "status": research.get("readiness", "review")},
            {"stage": "validation", "status": validation.get("status", "blocked")},
            {"stage": "deployment_readiness", "status": deployment.get("status", "blocked")},
        ]
        healthy = validation.get("passed", False) and not research.get("gaps")
        return ControlLoopResult(
            loop_id=f"loop-{hashlib.sha256(request.encode()).hexdigest()[:12]}",
            status="ready_for_authorization" if healthy else "blocked",
            stages=stages,
            health={"healthy": healthy, "mode": "safe_observation"},
            recovery={"enabled": True, "strategy": "retry_then_pause_dependents", "live_mutation": False},
            next_action="explicit_authorization" if healthy else "resolve_blockers",
        )
