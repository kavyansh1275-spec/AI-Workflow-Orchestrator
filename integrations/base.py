from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from models.workflow import WorkflowPlan


class Integration(ABC):
    """Contract for future n8n, Make, Zapier, and other providers."""

    name: str

    @abstractmethod
    def deploy(self, workflow: WorkflowPlan) -> dict[str, Any]:
        """Deploy a workflow and return provider metadata."""
        raise NotImplementedError
