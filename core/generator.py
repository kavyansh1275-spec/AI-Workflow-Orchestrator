from __future__ import annotations

from typing import Any

from models.workflow import WorkflowPlan


class WorkflowGenerator:
    """Generate provider-specific workflow artifacts.

    Provider artifacts stay credential-free. Live adapters are responsible for
    authentication and deployment; this layer only translates the workflow
    model into provider-native structure.
    """

    SUPPORTED_PROVIDERS = {"n8n", "make", "zapier", "generic"}

    _N8N_NODE_TYPES = {
        "webhook": "n8n-nodes-base.webhook",
        "schedule": "n8n-nodes-base.scheduleTrigger",
        "form": "n8n-nodes-base.formTrigger",
        "gmail": "n8n-nodes-base.gmail",
        "slack": "n8n-nodes-base.slack",
        "discord": "n8n-nodes-base.discord",
        "notion": "n8n-nodes-base.notion",
        "google_sheets": "n8n-nodes-base.googleSheets",
        "airtable": "n8n-nodes-base.airtable",
        "telegram": "n8n-nodes-base.telegram",
        "http": "n8n-nodes-base.httpRequest",
        "ai": "@n8n/n8n-nodes-langchain.openAi",
    }

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
                    "typeVersion": self._n8n_type_version(step),
                    "position": [index * 240, 0],
                    "parameters": step.config,
                }
            )

        connections: dict[str, list[str]] = {}
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

    @classmethod
    def _n8n_type(cls, step: Any) -> str:
        if step.app in cls._N8N_NODE_TYPES:
            return cls._N8N_NODE_TYPES[step.app]
        return f"n8n-nodes-base.{step.app}"

    @classmethod
    def _n8n_type_version(cls, step: Any) -> int:
        # Keep the default conservative. Provider-specific version negotiation
        # can be added later without changing the workflow model.
        return 1
