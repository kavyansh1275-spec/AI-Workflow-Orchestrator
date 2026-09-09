from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field


class ProjectPlan(BaseModel):
    """A complete automation project assembled from one natural-language goal."""

    project_id: str
    name: str
    request: str
    provider: str
    confidence: float
    workflow: dict[str, Any]
    integration_intelligence: dict[str, Any] = Field(default_factory=dict)
    integrations: list[dict[str, Any]] = Field(default_factory=list)
    artifact: dict[str, Any] = Field(default_factory=dict)
    simulation: list[str] = Field(default_factory=list)
    release: dict[str, Any] = Field(default_factory=dict)
    supervision: dict[str, Any] = Field(default_factory=dict)
    readiness: dict[str, Any] = Field(default_factory=dict)
    status: str = "planned"

    def model_summary(self) -> dict[str, Any]:
        return {
            "project_id": self.project_id,
            "name": self.name,
            "provider": self.provider,
            "confidence": self.confidence,
            "status": self.status,
            "steps": len(self.workflow.get("steps", [])),
            "integrations": len(self.integrations),
            "integration_gaps": len(self.integration_intelligence.get("gaps", [])),
        }
