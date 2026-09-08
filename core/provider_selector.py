from __future__ import annotations

import re

from models.workflow import WorkflowPlan


class ProviderSelector:
    """Choose a provider from explicit user hints, with a safe generic fallback."""

    PROVIDERS = ("n8n", "make", "zapier", "generic")

    _EXPLICIT_PATTERNS = {
        "n8n": (r"\bn8n\b",),
        "make": (r"\bmake(?:\.com)?\b",),
        "zapier": (r"\bzapier\b",),
    }

    def select(self, request: str) -> str:
        lowered = request.lower()
        for provider in ("n8n", "make", "zapier"):
            if any(re.search(pattern, lowered) for pattern in self._EXPLICIT_PATTERNS[provider]):
                return provider
        return "generic"

    def apply(self, workflow: WorkflowPlan) -> WorkflowPlan:
        provider = self.select(workflow.request)
        return workflow.model_copy(update={"provider": provider})
