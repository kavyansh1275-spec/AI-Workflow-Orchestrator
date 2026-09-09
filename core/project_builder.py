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

        integration_intelligence = self.orchestrator.integration_intelligence(request)
        workflow = self.orchestrator.build(request)
        analysis = self.orchestrator.analyze(request)
        integrations = self.orchestrator.inspect_integrations(request)
        artifact = self.orchestrator.generate(request)
        simulation = self.orchestrator.simulate(request)
        release = self.orchestrator.release(request, environment=environment, dry_run=True)
        execution = self.orchestrator.execute(request, dry_run=True)
        supervision = self.orchestrator.supervise(request, execution=execution)

        digest = hashlib.sha256(request.encode("utf-8")).hexdigest()[:12]
        gaps = list(integration_intelligence.get("gaps", []))
        readiness = {
            "safe_to_simulate": True,
            "live_deployment": False,
            "credentials": self.orchestrator.credential_status(),
            "provider": workflow.provider,
            "environment": environment,
            "integration_intelligence_ready": bool(integration_intelligence.get("ready")),
            "integration_gaps": gaps,
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
            integration_intelligence=integration_intelligence,
            integrations=integrations,
            artifact=artifact,
            simulation=simulation,
            release=release,
            supervision=supervision,
            readiness=readiness,
            status="ready_for_review" if not gaps else "needs_integration_review",
        )
