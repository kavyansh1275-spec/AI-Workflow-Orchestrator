from __future__ import annotations

from typing import Any

from core.credentials import CredentialManager
from core.generator import WorkflowGenerator
from integrations.base import Integration
from integrations.zapier_client import ZapierClient
from models.workflow import WorkflowPlan


class ZapierIntegration(Integration):
    """Live Zapier adapter using the Powered by Zapier v2 API."""

    name = "zapier"

    def __init__(
        self,
        credentials: CredentialManager | None = None,
        generator: WorkflowGenerator | None = None,
    ) -> None:
        self.credentials = credentials or CredentialManager()
        self.generator = generator or WorkflowGenerator()

    def _client(self) -> ZapierClient:
        credential = self.credentials.require(self.name)
        base_url = credential.base_url or "https://api.zapier.com"
        return ZapierClient(base_url=base_url, token=credential.api_key.get_secret_value())

    @staticmethod
    def _steps(workflow: WorkflowPlan) -> list[dict[str, Any]]:
        """Convert workflow steps to Zapier API steps.

        A real Zapier action identifier is required in each step's config as
        `zapier_action`. Authentication IDs are optional because some apps,
        such as webhook actions, do not require authentication.
        """
        steps: list[dict[str, Any]] = []
        for step in workflow.steps:
            action = step.config.get("zapier_action")
            if not action:
                raise RuntimeError(
                    f"Zapier action mapping missing for step '{step.id}'. "
                    f"Add config['zapier_action'] before live deployment."
                )
            item: dict[str, Any] = {
                "action": action,
                "inputs": step.config.get("zapier_inputs", {}),
                "authentication": step.config.get("zapier_authentication"),
            }
            alias = step.config.get("zapier_alias")
            if alias:
                item["alias"] = alias
            steps.append(item)
        return steps

    def artifact(self, workflow: WorkflowPlan) -> dict[str, Any]:
        artifact = self.generator.generate(workflow)
        artifact["steps"] = self._steps(workflow)
        return artifact

    def deploy(self, workflow: WorkflowPlan) -> dict[str, Any]:
        client = self._client()
        steps = self._steps(workflow)
        response = client.create_zap(workflow.name, steps, enabled=False)
        data = response.get("data", response)
        return {
            "provider": self.name,
            "status": "created",
            "dry_run": False,
            "zap_id": data.get("id"),
            "title": data.get("title", workflow.name),
            "enabled": data.get("is_enabled", False),
            "workflow": workflow.model_dump(),
            "response": response,
        }

    def list_zaps(self, limit: int = 100, offset: int = 0) -> dict[str, Any]:
        return self._client().list_zaps(limit=limit, offset=offset)

    def get_zap(self, zap_id: str) -> dict[str, Any]:
        return self._client().get_zap(zap_id)

    def delete_zap(self, zap_id: str) -> dict[str, Any]:
        return self._client().delete_zap(zap_id)
