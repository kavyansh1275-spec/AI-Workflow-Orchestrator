from __future__ import annotations

from typing import Any

from integrations.base import Integration
from models.workflow import WorkflowPlan


class ZapierIntegration(Integration):
    name = "zapier"

    def deploy(self, workflow: WorkflowPlan) -> dict[str, Any]:
        return {
            "provider": self.name,
            "status": "not_implemented",
            "message": "Real Zapier deployment is planned for a later version.",
            "workflow": workflow.model_dump(),
        }
