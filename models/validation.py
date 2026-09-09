from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field


class ValidationResult(BaseModel):
    validation_id: str
    passed: bool
    score: float
    checks: list[dict[str, Any]] = Field(default_factory=list)
    failures: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    status: str = "passed"
