from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class WorkflowIntent(BaseModel):
    """V3 normalized understanding of a natural-language workflow request."""

    request: str
    provider: str = "generic"
    trigger: str
    actions: list[str] = Field(default_factory=list)
    conditions: list[str] = Field(default_factory=list)
    confidence: float = 1.0

    @field_validator("request", "trigger", "provider")
    @classmethod
    def must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("intent fields cannot be blank")
        return value.strip()

    @field_validator("confidence")
    @classmethod
    def valid_confidence(cls, value: float) -> float:
        if not 0.0 <= value <= 1.0:
            raise ValueError("confidence must be between 0 and 1")
        return value
