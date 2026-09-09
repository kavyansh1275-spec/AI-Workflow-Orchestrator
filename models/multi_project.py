from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field


class ProjectWorkflow(BaseModel):
    workflow_id: str
    name: str
    request: str
    provider: str
    workflow: dict[str, Any]
    depends_on: list[str] = Field(default_factory=list)
    shared_inputs: list[str] = Field(default_factory=list)
    shared_outputs: list[str] = Field(default_factory=list)
    status: str = "planned"


class MultiWorkflowProject(BaseModel):
    project_id: str
    request: str
    workflows: list[ProjectWorkflow] = Field(default_factory=list)
    dependencies: list[dict[str, Any]] = Field(default_factory=list)
    shared_data: dict[str, Any] = Field(default_factory=dict)
    monitoring: dict[str, Any] = Field(default_factory=dict)
    recovery: dict[str, Any] = Field(default_factory=dict)
    status: str = "planned"

    def summary(self) -> dict[str, Any]:
        return {
            "project_id": self.project_id,
            "workflow_count": len(self.workflows),
            "dependency_count": len(self.dependencies),
            "providers": sorted({item.provider for item in self.workflows}),
            "status": self.status,
        }
