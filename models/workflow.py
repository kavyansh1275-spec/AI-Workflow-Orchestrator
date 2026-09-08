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

    @field_validator("id", "type", "app", "action")
    @classmethod
    def must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("workflow step fields cannot be blank")
        return value.strip()


class WorkflowPlan(BaseModel):
    """Structured representation produced by the V1 planner."""

    name: str
    request: str
    description: str
    steps: list[WorkflowStep] = Field(default_factory=list)
    provider: str = "generic"

    @field_validator("name", "request", "description", "provider")
    @classmethod
    def must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("workflow metadata cannot be blank")
        return value.strip()

    def to_pretty_json(self) -> str:
        return self.model_dump_json(indent=2)
