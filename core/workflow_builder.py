from __future__ import annotations
import hashlib
from typing import Any
from models.workflow_build import WorkflowBuildResult

class AutonomousWorkflowBuilder:
    """Compiles an approved solution/request into a provider-shaped workflow."""
    def __init__(self, orchestrator: Any):
        self.orchestrator = orchestrator

    def build(self, request: str) -> WorkflowBuildResult:
        request = request.strip()
        if not request:
            raise ValueError("workflow build request cannot be blank")
        solution = self.orchestrator.design_solution(request)
        provider = str(self.orchestrator.decide(request).get("provider", "generic"))
        workflows = solution.get("workflows", []) if isinstance(solution, dict) else []
        if not workflows:
            project = self.orchestrator.build_multi_project(request)
            workflows = project.get("workflows", []) if isinstance(project, dict) else []
        generated = []
        for item in workflows:
            generated.append({"name": item.get("name", "Workflow"), "provider": item.get("provider", provider), "trigger": item.get("trigger", "manual"), "actions": item.get("actions", []), "depends_on": item.get("depends_on", [])})
        artifact = {"provider": provider, "workflows": generated, "source": "solution_blueprint"}
        checks = [
            {"name": "solution_available", "passed": bool(solution)},
            {"name": "workflow_generated", "passed": bool(generated)},
            {"name": "provider_selected", "passed": provider != ""},
        ]
        return WorkflowBuildResult(build_id=f"build-{hashlib.sha256(request.encode()).hexdigest()[:12]}", request=request, provider=provider, workflow=artifact, artifacts=[artifact], checks=checks, status="built" if all(c["passed"] for c in checks) else "blocked")
