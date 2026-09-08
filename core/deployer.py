from __future__ import annotations

from typing import Any

from core.providers import ProviderRegistry
from models.workflow import WorkflowPlan


class Deployer:
    """V2 deployment facade with dry-run safety."""

    def __init__(self, registry: ProviderRegistry | None = None) -> None:
        self.registry = registry or ProviderRegistry()

    def deploy(self, workflow: WorkflowPlan, dry_run: bool = True) -> dict[str, Any]:
        if workflow.provider == "generic":
            return {
                "provider": "generic",
                "status": "planned",
                "dry_run": dry_run,
                "message": "No provider selected; workflow remains provider-independent.",
            }

        integration = self.registry.get(workflow.provider)
        if dry_run:
            return {
                "provider": workflow.provider,
                "status": "dry_run",
                "dry_run": True,
                "message": f"Validated {workflow.provider} deployment without external API calls.",
                "workflow": workflow.model_dump(),
            }

        return integration.deploy(workflow)
