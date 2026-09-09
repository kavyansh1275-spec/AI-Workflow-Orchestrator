from __future__ import annotations

import hashlib
from typing import Any

from core.orchestrator import Orchestrator
from models.autonomous_agent import AgentStage, AutonomousAgentResult


class AutonomousAutomationAgent:
    """V15 safe autonomous agent: research, design, build, test, authorize, monitor, recover."""

    def __init__(self, orchestrator: Orchestrator | None = None) -> None:
        self.orchestrator = orchestrator or Orchestrator()

    @staticmethod
    def _id(request: str) -> str:
        return f"agent-{hashlib.sha256(request.encode()).hexdigest()[:12]}"

    def plan(self, request: str, environment: str = "staging", authorize_live: bool = False) -> AutonomousAgentResult:
        request = request.strip()
        if not request:
            raise ValueError("autonomous agent request cannot be blank")

        stages: list[AgentStage] = []
        research = self.orchestrator.integration_intelligence(request)
        stages.append(AgentStage(name="research", status="completed", output=research, message="Integration and capability research completed."))

        design = self.orchestrator.decide(request)
        stages.append(AgentStage(name="design", status="completed", output=design, message="Provider and workflow strategy selected."))

        project = self.orchestrator.build_multi_project(request, environment=environment)
        stages.append(AgentStage(name="build", status="completed", output=project, message="Workflow project constructed."))

        tests: dict[str, Any] = {"workflow_count": len(project.get("workflows", [])), "results": []}
        for item in project.get("workflows", []):
            stage_request = str(item.get("request", request))
            try:
                simulation = self.orchestrator.simulate(stage_request)
                tests["results"].append({"workflow_id": item.get("workflow_id"), "status": "passed", "simulation": simulation})
            except Exception as exc:
                tests["results"].append({"workflow_id": item.get("workflow_id"), "status": "failed", "error": str(exc)})
        tests["passed"] = all(result["status"] == "passed" for result in tests["results"])
        stages.append(AgentStage(name="test", status="completed" if tests["passed"] else "failed", output=tests, message="Safe simulations completed."))

        deployment: dict[str, Any]
        if authorize_live and tests["passed"] and len(project.get("workflows", [])) == 1:
            deployment = {"status": "ready", "authorized": True, "note": "Single-workflow live deployment can be requested through the existing safety-gated deployment API."}
            next_action = "deploy_with_explicit_live_confirmation"
        else:
            deployment = {"status": "blocked", "authorized": False, "reason": "Live deployment requires explicit authorization and passes through existing provider safety gates."}
            next_action = "review"
        stages.append(AgentStage(name="deploy", status=deployment["status"], output=deployment, message=deployment["reason"] if deployment["status"] == "blocked" else deployment["note"]))

        monitoring = {
            "enabled": True,
            "mode": "safe_observation",
            "scope": "project_and_workflow",
            "checks": ["workflow_health", "dependency_state", "provider_health", "execution_failures"],
        }
        recovery = {
            "enabled": True,
            "strategy": "classify_failure_then_retry_then_pause_dependents",
            "max_retries": 2,
            "rollback": "use_existing_release_or_live_rollback",
            "automatic_live_mutation": False,
        }
        stages.append(AgentStage(name="monitor", status="ready", output=monitoring, message="Project monitoring plan prepared."))
        stages.append(AgentStage(name="recover", status="ready", output=recovery, message="Failure recovery plan prepared."))

        status = "ready_for_review" if tests["passed"] else "blocked_by_tests"
        return AutonomousAgentResult(
            agent_id=self._id(request),
            request=request,
            status=status,
            authorization_required=not authorize_live,
            stages=stages,
            project=project,
            research=research,
            design=design,
            testing=tests,
            deployment=deployment,
            monitoring=monitoring,
            recovery=recovery,
            next_action=next_action,
        )
