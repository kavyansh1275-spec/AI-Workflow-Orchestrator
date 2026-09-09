from __future__ import annotations

import os
import json
from typing import Any

from core.credentials import CredentialManager
from core.generator import WorkflowGenerator
from integrations.base import Integration
from integrations.make_client import MakeClient
from models.workflow import WorkflowPlan


class MakeIntegration(Integration):
    """Live Make scenario adapter backed by the Make API v2."""

    name = "make"

    def __init__(self, credentials: CredentialManager | None = None, generator: WorkflowGenerator | None = None) -> None:
        self.credentials = credentials or CredentialManager()
        self.generator = generator or WorkflowGenerator()

    def _client(self) -> MakeClient:
        credential = self.credentials.require(self.name)
        base_url = credential.base_url or "https://eu1.make.com"
        team_id = os.getenv("MAKE_TEAM_ID")
        if not team_id:
            raise RuntimeError("Missing MAKE_TEAM_ID. Set it to the Make team ID used for the scenario.")
        try:
            parsed_team_id = int(team_id)
        except ValueError as exc:
            raise RuntimeError("MAKE_TEAM_ID must be an integer") from exc
        return MakeClient(base_url, credential.api_key.get_secret_value(), parsed_team_id)

    def _blueprint(self, workflow: WorkflowPlan) -> str:
        artifact = self.generator.generate(workflow)
        modules = []
        for module in artifact["modules"]:
            modules.append({
                "id": module["id"],
                "module": f"{module['app']}.{module['action']}",
                "version": 1,
                "parameters": module["parameters"],
                "mapper": {},
            })
        return json.dumps({"subflows": [{"flow": modules}]}, separators=(",", ":"))

    def deploy(self, workflow: WorkflowPlan) -> dict[str, Any]:
        client = self._client()
        result = client.create_scenario(
            blueprint=self._blueprint(workflow),
            scheduling=json.dumps({"type": "on-demand"}),
            name=workflow.name[:120],
        )
        scenario = result.get("scenario", result)
        return {
            "provider": self.name,
            "status": "created",
            "dry_run": False,
            "scenario_id": scenario.get("id") if isinstance(scenario, dict) else None,
            "name": scenario.get("name", workflow.name) if isinstance(scenario, dict) else workflow.name,
            "active": scenario.get("isActive", False) if isinstance(scenario, dict) else False,
            "response": result,
        }

    def list_scenarios(self, limit: int = 100, offset: int = 0) -> dict[str, Any]:
        return self._client().list_scenarios(limit=limit, offset=offset)

    def get_scenario(self, scenario_id: int) -> dict[str, Any]:
        return self._client().get_scenario(scenario_id)

    def update(self, scenario_id: int, payload: dict[str, Any], confirmed: bool = False) -> dict[str, Any]:
        return self._client().update_scenario(scenario_id, payload, confirmed=confirmed)

    def activate(self, scenario_id: int) -> dict[str, Any]:
        return self._client().activate_scenario(scenario_id)

    def deactivate(self, scenario_id: int) -> dict[str, Any]:
        return self._client().deactivate_scenario(scenario_id)

    def run(self, scenario_id: int, data: dict[str, Any] | None = None, responsive: bool = False) -> dict[str, Any]:
        return self._client().run_scenario(scenario_id, data=data, responsive=responsive)

    def delete(self, scenario_id: int) -> dict[str, Any]:
        return self._client().delete_scenario(scenario_id)
