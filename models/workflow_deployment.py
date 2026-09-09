from __future__ import annotations
from typing import Any
from pydantic import BaseModel, Field

class WorkflowDeploymentResult(BaseModel):
    deployment_id: str
    request: str
    provider: str
    artifact: dict[str, Any] = Field(default_factory=dict)
    readiness: dict[str, Any] = Field(default_factory=dict)
    deployment: dict[str, Any] = Field(default_factory=dict)
    status: str = "ready"
