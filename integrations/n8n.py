from __future__ import annotations

from typing import Any

from core.credentials import CredentialManager
from core.generator import WorkflowGenerator
from integrations.base import Integration
from integrations.n8n_client import N8nClient
from models.workflow import WorkflowPlan


class N8nIntegration(Integration):
    """Live n8n adapter backed by the n8n Public REST API."""

    name = "n8n"

    def __init__(self, credentials: CredentialManager | None = None, generator: WorkflowGenerator | None = None) -> None:
        self.credentials = credentials or CredentialManager()
        self.generator = generator or WorkflowGenerator()

    def _client(self) -> N8nClient:
        credential = self.credentials.require(self.name)
        base_url = credential.base_url
        if not base_url:
            raise RuntimeError("Missing N8N_BASE_URL. Set it to your n8n instance URL.")
        return N8nClient(base_url=base_url, api_key=credential.api_key.get_secret_value())

    def _payload(self, workflow: WorkflowPlan) -> dict[str, Any]:
        artifact = self.generator.generate(workflow)
        nodes = []
        names = {step.id: f"{step.app}: {step.action}" for step in workflow.steps}
        for index, step in enumerate(workflow.steps):
            nodes.append(
                {
                    "id": step.id,
                    "name": names[step.id],
                    "type": artifact["nodes"][index]["type"],
                    "typeVersion": 1,
                    "position": [index * 260, 0],
                    "parameters": step.config,
                }
            )

        connections: dict[str, dict[str, list[list[dict[str, Any]]]]] = {}
        for step in workflow.steps:
            for dependency in step.depends_on:
                source_name = names[dependency]
                connections.setdefault(source_name, {}).setdefault("main", [[]])
                connections[source_name]["main"][0].append(
                    {"node": names[step.id], "type": "main", "index": 0}
                )

        return {
            "name": workflow.name[:128],
            "nodes": nodes,
            "connections": connections,
            "settings": {"executionOrder": "v1"},
        }

    def deploy(self, workflow: WorkflowPlan) -> dict[str, Any]:
        client = self._client()
        created = client.create_workflow(self._payload(workflow))
        return {
            "provider": self.name,
            "status": "created",
            "dry_run": False,
            "workflow_id": created.get("id"),
            "name": created.get("name", workflow.name),
            "active": created.get("active", False),
            "response": created,
        }

    def list_workflows(self, limit: int = 100) -> dict[str, Any]:
        return self._client().list_workflows(limit=limit)

    def get_workflow(self, workflow_id: str) -> dict[str, Any]:
        return self._client().get_workflow(workflow_id)

    def activate(self, workflow_id: str) -> dict[str, Any]:
        return self._client().activate_workflow(workflow_id)

    def deactivate(self, workflow_id: str) -> dict[str, Any]:
        return self._client().deactivate_workflow(workflow_id)

    def delete(self, workflow_id: str) -> dict[str, Any]:
        return self._client().delete_workflow(workflow_id)
