from __future__ import annotations

import hashlib
from typing import Any

from core.orchestrator import Orchestrator
from models.project import ProjectPlan


class AutonomousProjectBuilder:
    """Turns one natural-language business goal into a complete safe project run."""

    def __init__(self, orchestrator: Orchestrator | None = None) -> None:
        self.orchestrator = orchestrator or Orchestrator()

    def build(self, request: str, environment: str = "staging") -> ProjectPlan:
        request = request.strip()
        if not request:
            raise ValueError("project request cannot be blank")

        workflow = self.orchestrator.build(request)
        analysis = self.orchestrator.analyze(request)
        integrations = self.orchestrator.inspect_integrations(request)
        artifact = self.orchestrator.generate(request)
        simulation = self.orchestrator.simulate(request)
        release = self.orchestrator.release(request, environment=environment, dry_run=True)
        execution = self.orchestrator.execute(request, dry_run=True)
        supervision = self.orchestrator.supervise(request, execution=execution)

        digest = hashlib.sha256(request.encode("utf-8")).hexdigest()[:12]
        readiness = {
            "safe_to_simulate": True,
            "live_deployment": False,
            "credentials": self.orchestrator.credential_status(),
            "provider": workflow.provider,
            "environment": environment,
            "missing_integrations": [
                item for item in integrations if item.get("status") not in {"available", "supported"}
            ],
        }
        return ProjectPlan(
            project_id=f"project-{digest}",
            name=workflow.name,
            request=request,
            provider=workflow.provider,
            confidence=workflow.intent_confidence,
            workflow=workflow.model_dump(mode="json"),
            integrations=integrations,
            artifact=artifact,
            simulation=simulation,
            release=release,
            supervision=supervision,
            readiness=readiness,
            status="ready_for_review",
        )
