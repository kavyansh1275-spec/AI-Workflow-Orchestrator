from __future__ import annotations

import hashlib
from core.orchestrator import Orchestrator
from models.deployment_plan import DeploymentPlan


class AutonomousDeploymentPlanner:
    """Prepare a deployment plan without mutating external providers."""
    def __init__(self, orchestrator: Orchestrator | None = None) -> None:
        self.orchestrator = orchestrator or Orchestrator()

    def plan(self, request: str, environment: str = "staging") -> DeploymentPlan:
        request = request.strip()
        if not request:
            raise ValueError("deployment request cannot be blank")
        decision = self.orchestrator.decide(request)
        validation = self.orchestrator.validate_solution(request)
        provider = str(decision.get("provider", "generic"))
        ready = bool(validation.get("passed"))
        return DeploymentPlan(
            deployment_id=f"plan-{hashlib.sha256(request.encode()).hexdigest()[:12]}",
            environment=environment,
            provider=provider,
            preflight=[{"name": "quality_gates", "passed": ready}, {"name": "credentials", "passed": False, "reason": "Runtime credentials must be checked at deployment time"}],
            authorization={"required": True, "explicit_live_confirmation": True},
            rollback={"required": True, "strategy": "provider_rollback"},
            status="ready_for_authorization" if ready else "blocked_by_validation",
        )
