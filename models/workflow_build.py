from __future__ import annotations
from typing import Any
from pydantic import BaseModel, Field

class WorkflowBuildResult(BaseModel):
    build_id: str
    request: str
    provider: str
    workflow: dict[str, Any] = Field(default_factory=dict)
    artifacts: list[dict[str, Any]] = Field(default_factory=list)
    checks: list[dict[str, Any]] = Field(default_factory=list)
    status: str = "built"
