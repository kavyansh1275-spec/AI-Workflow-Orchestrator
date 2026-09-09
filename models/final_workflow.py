from __future__ import annotations
from typing import Any
from pydantic import BaseModel, Field

class FinalWorkflowResult(BaseModel):
    pipeline_id: str
    request: str
    stages: list[dict[str, Any]] = Field(default_factory=list)
    provider: str = "generic"
    artifact: dict[str, Any] = Field(default_factory=dict)
    deployment: dict[str, Any] = Field(default_factory=dict)
    passed: bool = False
    status: str = "blocked"
