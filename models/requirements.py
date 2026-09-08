from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class WorkflowRequirements(BaseModel):
    """Requirements inferred from a user's automation request."""

    inputs: list[str] = Field(default_factory=list)
    outputs: list[str] = Field(default_factory=list)
    apps: list[str] = Field(default_factory=list)
    data: list[str] = Field(default_factory=list)
    conditions: list[str] = Field(default_factory=list)
    missing: list[str] = Field(default_factory=list)
    confidence: float = 0.0

    @field_validator("confidence")
    @classmethod
    def valid_confidence(cls, value: float) -> float:
        if not 0.0 <= value <= 1.0:
            raise ValueError("confidence must be between 0 and 1")
        return value
