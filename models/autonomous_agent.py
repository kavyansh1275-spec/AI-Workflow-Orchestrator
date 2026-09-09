from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field


class AgentStage(BaseModel):
    name: str
    status: str
    output: dict[str, Any] = Field(default_factory=dict)
    message: str = ""


class AutonomousAgentResult(BaseModel):
    agent_id: str
    request: str
    status: str = "planned"
    authorization_required: bool = True
    stages: list[AgentStage] = Field(default_factory=list)
    project: dict[str, Any] = Field(default_factory=dict)
    research: dict[str, Any] = Field(default_factory=dict)
    design: dict[str, Any] = Field(default_factory=dict)
    testing: dict[str, Any] = Field(default_factory=dict)
    deployment: dict[str, Any] = Field(default_factory=dict)
    monitoring: dict[str, Any] = Field(default_factory=dict)
    recovery: dict[str, Any] = Field(default_factory=dict)
    next_action: str = "review"

    def summary(self) -> dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "status": self.status,
            "stage_count": len(self.stages),
            "authorization_required": self.authorization_required,
            "next_action": self.next_action,
        }
