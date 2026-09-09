from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field


class SolutionBlueprint(BaseModel):
    solution_id: str
    request: str
    architecture: list[dict[str, Any]] = Field(default_factory=list)
    workflows: list[dict[str, Any]] = Field(default_factory=list)
    integrations: list[dict[str, Any]] = Field(default_factory=list)
    data_contracts: list[dict[str, Any]] = Field(default_factory=list)
    validation: list[str] = Field(default_factory=list)
    risks: list[dict[str, Any]] = Field(default_factory=list)
    status: str = "designed"

    def summary(self) -> dict[str, Any]:
        return {"solution_id": self.solution_id, "status": self.status, "workflows": len(self.workflows), "integrations": len(self.integrations)}
