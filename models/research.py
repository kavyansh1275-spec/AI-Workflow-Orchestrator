from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field


class ResearchFinding(BaseModel):
    category: str
    finding: str
    confidence: float = 0.0
    evidence: list[str] = Field(default_factory=list)


class AutomationResearchResult(BaseModel):
    research_id: str
    request: str
    problem: str
    goal: str
    requirements: list[str] = Field(default_factory=list)
    integrations: list[dict[str, Any]] = Field(default_factory=list)
    provider_options: list[dict[str, Any]] = Field(default_factory=list)
    risks: list[dict[str, Any]] = Field(default_factory=list)
    acceptance_criteria: list[str] = Field(default_factory=list)
    findings: list[ResearchFinding] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list)
    readiness: str = "review"

    def summary(self) -> dict[str, Any]:
        return {
            "research_id": self.research_id,
            "readiness": self.readiness,
            "requirements": len(self.requirements),
            "integrations": len(self.integrations),
            "provider_options": len(self.provider_options),
            "risks": len(self.risks),
            "gaps": len(self.gaps),
        }
