from __future__ import annotations

from pydantic import BaseModel, Field


class IntegrationRecommendation(BaseModel):
    app: str
    action: str
    score: float = Field(ge=0.0, le=1.0)
    reason: str
    required_fields: list[str] = Field(default_factory=list)


class IntegrationAnalysis(BaseModel):
    recommendations: list[IntegrationRecommendation] = Field(default_factory=list)
    recommended_apps: list[str] = Field(default_factory=list)
    recommended_actions: list[str] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list)
    ready: bool = False
