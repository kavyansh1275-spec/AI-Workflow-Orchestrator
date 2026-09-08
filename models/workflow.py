from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, field_validator


class WorkflowStep(BaseModel):
    """One provider-independent workflow operation."""

    id: str
    type: str
    app: str
    action: str
    config: dict[str, Any] = Field(default_factory=dict)
    depends_on: list[str] = Field(default_factory=list)
    condition: str | None = None

    @field_validator("id", "type", "app", "action")
    @classmethod
    def must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("workflow step fields cannot be blank")
        return value.strip()


class WorkflowPlan(BaseModel):
    """Structured representation produced by the V3 planner."""

    name: str
    request: str
    description: str
    steps: list[WorkflowStep] = Field(default_factory=list)
    provider: str = "generic"
    intent_confidence: float = 1.0

    @field_validator("name", "request", "description", "provider")
    @classmethod
    def must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("workflow metadata cannot be blank")
        return value.strip()

    @field_validator("intent_confidence")
    @classmethod
    def valid_confidence(cls, value: float) -> float:
        if not 0.0 <= value <= 1.0:
            raise ValueError("intent_confidence must be between 0 and 1")
        return value

    def to_pretty_json(self) -> str:
        return self.model_dump_json(indent=2)
