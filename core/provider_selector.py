from __future__ import annotations

from models.workflow import WorkflowPlan


class ProviderSelector:
    """Choose a provider from explicit user hints, with a safe generic fallback."""

    PROVIDERS = ("n8n", "make", "zapier", "generic")

    def select(self, request: str) -> str:
        lowered = request.lower()
        if "n8n" in lowered:
            return "n8n"
        if "make.com" in lowered or "make com" in lowered or "make" in lowered:
            return "make"
        if "zapier" in lowered:
            return "zapier"
        return "generic"

    def apply(self, workflow: WorkflowPlan) -> WorkflowPlan:
        provider = self.select(workflow.request)
        return workflow.model_copy(update={"provider": provider})
