from __future__ import annotations

import hashlib
import re
from typing import Any

from core.orchestrator import Orchestrator
from models.multi_project import MultiWorkflowProject, ProjectWorkflow


class AutonomousMultiProjectBuilder:
    """Break one large automation goal into dependent, safe workflow units."""

    _SEPARATORS = re.compile(r"\s+(?:then|after that|next|finally)\s+|\s*;\s*|(?<=[.!?])\s+")

    def __init__(self, orchestrator: Orchestrator | None = None) -> None:
        self.orchestrator = orchestrator or Orchestrator()

    def _stages(self, request: str) -> list[str]:
        parts = [part.strip(" ,") for part in self._SEPARATORS.split(request) if part.strip(" ,")]
        if len(parts) <= 1:
            return [request]

        stages: list[str] = [parts[0]]
        # Downstream workflows need an explicit trigger so the existing planner
        # can build a valid workflow instead of falling back to manual.start.
        trigger_prefix = self._trigger_prefix(parts[0])
        for part in parts[1:]:
            stages.append(f"{trigger_prefix}, {part}")
        return stages[:6]

    @staticmethod
    def _trigger_prefix(first_stage: str) -> str:
        text = first_stage.lower()
        if re.search(r"\b(form|forms|form submission|form response)\b", text):
            return "When a form submission is received"
        if re.search(r"\b(webhook|http request|api request)\b", text):
            return "When a webhook is received"
        if re.search(r"\b(schedule|scheduled|every day|every week|daily|weekly)\b", text):
            return "When the scheduled event runs"
        if re.search(r"\b(new email|incoming email|email arrives)\b", text):
            return "When an incoming email arrives"
        if re.search(r"\b(new row|row added)\b", text):
            return "When a new spreadsheet row is added"
        return "When the previous workflow completes"

    @staticmethod
    def _shared_data(workflows: list[ProjectWorkflow]) -> dict[str, Any]:
        return {
            "contract": "workflow-project-v14",
            "handoff": {
                item.workflow_id: {
                    "outputs": item.shared_outputs,
                    "inputs": item.shared_inputs,
                }
                for item in workflows
            },
            "state_store": "project_shared_state",
        }

    def build(self, request: str, environment: str = "staging") -> MultiWorkflowProject:
        request = request.strip()
        if not request:
            raise ValueError("multi-workflow project request cannot be blank")

        stages = self._stages(request)
        workflows: list[ProjectWorkflow] = []
        dependencies: list[dict[str, Any]] = []

        for index, stage in enumerate(stages, start=1):
            workflow = self.orchestrator.build(stage)
            workflow_id = f"wf-{index:02d}-{hashlib.sha256(stage.encode()).hexdigest()[:8]}"
            depends_on = [workflows[-1].workflow_id] if workflows else []
            shared_inputs = ["previous_workflow_output"] if depends_on else []
            shared_outputs = [f"{workflow_id}.result"]
            workflows.append(
                ProjectWorkflow(
                    workflow_id=workflow_id,
                    name=workflow.name,
                    request=stage,
                    provider=workflow.provider,
                    workflow=workflow.model_dump(mode="json"),
                    depends_on=depends_on,
                    shared_inputs=shared_inputs,
                    shared_outputs=shared_outputs,
                    status="ready_for_simulation",
                )
            )
            if depends_on:
                dependencies.append(
                    {
                        "from": depends_on[0],
                        "to": workflow_id,
                        "type": "data_handoff",
                        "condition": "upstream_completed",
                    }
                )

        project_id = f"multi-{hashlib.sha256(request.encode()).hexdigest()[:12]}"
        monitoring = {
            "enabled": True,
            "mode": "safe_observation",
            "scope": "project_and_workflow",
            "health_checks": ["workflow_status", "dependency_state", "handoff_integrity"],
            "failure_threshold": 3,
        }
        recovery = {
            "enabled": True,
            "strategy": "retry_failed_workflow_then_pause_dependents",
            "max_retries": 2,
            "rollback": "delegate_to_existing_release_or_live_rollback",
            "live_mutation": False,
        }
        return MultiWorkflowProject(
            project_id=project_id,
            request=request,
            workflows=workflows,
            dependencies=dependencies,
            shared_data=self._shared_data(workflows),
            monitoring=monitoring,
            recovery=recovery,
            status="ready_for_review",
        )
