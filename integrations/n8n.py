from __future__ import annotations

from typing import Any

from integrations.base import Integration
from models.workflow import WorkflowPlan


class N8nIntegration(Integration):
    name = "n8n"

    def deploy(self, workflow: WorkflowPlan) -> dict[str, Any]:
        return {
            "provider": self.name,
            "status": "not_implemented",
            "message": "Real n8n deployment is planned for a later version.",
            "workflow": workflow.model_dump(),
        }
