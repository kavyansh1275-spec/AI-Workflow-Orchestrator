from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field


class DeploymentPlan(BaseModel):
    deployment_id: str
    environment: str
    provider: str
    preflight: list[dict[str, Any]] = Field(default_factory=list)
    authorization: dict[str, Any] = Field(default_factory=dict)
    rollback: dict[str, Any] = Field(default_factory=dict)
    status: str = "blocked"
