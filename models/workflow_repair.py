from __future__ import annotations
from typing import Any
from pydantic import BaseModel, Field

class WorkflowRepairResult(BaseModel):
    repair_id: str
    request: str
    attempts: int
    tests: list[dict[str, Any]] = Field(default_factory=list)
    repairs: list[dict[str, Any]] = Field(default_factory=list)
    final_artifact: dict[str, Any] = Field(default_factory=dict)
    passed: bool = False
    status: str = "blocked"
