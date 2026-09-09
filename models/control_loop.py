from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field


class ControlLoopResult(BaseModel):
    loop_id: str
    status: str
    stages: list[dict[str, Any]] = Field(default_factory=list)
    health: dict[str, Any] = Field(default_factory=dict)
    recovery: dict[str, Any] = Field(default_factory=dict)
    next_action: str = "review"
