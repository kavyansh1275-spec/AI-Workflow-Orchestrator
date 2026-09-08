from __future__ import annotations

from typing import Any

from models.workflow import WorkflowPlan


class WorkflowGenerator:
    """Generate provider-specific, credential-free workflow artifacts.

    V4 converts the validated provider-independent workflow into an exportable
    representation for n8n, Make, or Zapier. It never calls an external API.
    """

    SUPPORTED_PROVIDERS = {"n8n", "make", "zapier", "generic"}

    def generate(self, workflow: WorkflowPlan) -> dict[str, Any]:
        provider = workflow.provider.lower()
        if provider not in self.SUPPORTED_PROVIDERS:
            raise ValueError(f"unsupported workflow provider: {workflow.provider}")

        if provider == "n8n":
            return self._n8n(workflow)
        if provider == "make":
            return self._make(workflow)
        if provider == "zapier":
            return self._zapier(workflow)
        return self._generic(workflow)

    def _n8n(self, workflow: WorkflowPlan) -> dict[str, Any]:
        nodes = []
        for index, step in enumerate(workflow.steps):
            nodes.append(
                {
                    "id": step.id,
                    "name": f"{step.app}: {step.action}",
                    "type": self._n8n_type(step),
                    "position": [index * 240, 0],
                    "parameters": step.config,
                }
            )

        connections = {}
        for step in workflow.steps:
            for dependency in step.depends_on:
                connections.setdefault(dependency, []).append(step.id)

        return {
            "format": "n8n",
            "name": workflow.name,
            "active": False,
            "nodes": nodes,
            "connections": connections,
        }

    def _make(self, workflow: WorkflowPlan) -> dict[str, Any]:
        return {
            "format": "make",
            "name": workflow.name,
            "modules": [
                {
                    "id": index + 1,
                    "app": step.app,
                    "action": step.action,
                    "parameters": step.config,
                    "depends_on": [self._step_number(workflow, item) for item in step.depends_on],
                    "condition": step.condition,
                }
                for index, step in enumerate(workflow.steps)
            ],
        }

    def _zapier(self, workflow: WorkflowPlan) -> dict[str, Any]:
        return {
            "format": "zapier",
            "name": workflow.name,
            "steps": [
                {
                    "order": index + 1,
                    "app": step.app,
                    "event": step.action,
                    "config": step.config,
                    "depends_on": step.depends_on,
                    "condition": step.condition,
                }
                for index, step in enumerate(workflow.steps)
            ],
        }

    def _generic(self, workflow: WorkflowPlan) -> dict[str, Any]:
        return {
            "format": "generic",
            "name": workflow.name,
            "steps": [step.model_dump() for step in workflow.steps],
        }

    @staticmethod
    def _step_number(workflow: WorkflowPlan, step_id: str) -> int:
        for index, step in enumerate(workflow.steps, start=1):
            if step.id == step_id:
                return index
        raise ValueError(f"unknown dependency: {step_id}")

    @staticmethod
    def _n8n_type(step: Any) -> str:
        if step.type == "trigger":
            return "n8n-nodes-base.webhook"
        if step.app == "ai":
            return "n8n-nodes-base.openAi"
        return f"n8n-nodes-base.{step.app}"
