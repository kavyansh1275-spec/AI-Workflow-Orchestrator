from __future__ import annotations
import hashlib
from typing import Any
from models.workflow_deployment import WorkflowDeploymentResult

class AutonomousWorkflowDeployment:
    """Turns a compiled workflow into a deployment-ready or explicitly authorized live deployment."""
    def __init__(self, orchestrator: Any):
        self.orchestrator = orchestrator

    def prepare(self, request: str, environment: str = "staging", live: bool = False) -> WorkflowDeploymentResult:
        request = request.strip()
        if not request:
            raise ValueError("workflow deployment request cannot be blank")
        plan = self.orchestrator.build(request)
        artifact = self.orchestrator.generator.generate(plan)
        readiness = self.orchestrator.live_deployment_readiness(request)
        deployment = self.orchestrator.live_deploy(request, live=live) if live else {"status": "dry_run", "environment": environment, "authorized": False}
        status = "deployed" if live and deployment.get("status") not in {"blocked", "failed"} else "ready_for_authorization" if readiness.get("ready") else "blocked"
        return WorkflowDeploymentResult(deployment_id=f"deploy-{hashlib.sha256(request.encode()).hexdigest()[:12]}", request=request, provider=plan.provider, artifact=artifact, readiness=readiness, deployment=deployment, status=status)
