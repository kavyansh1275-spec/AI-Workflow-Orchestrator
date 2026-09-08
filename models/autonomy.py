from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class AutonomyAction(str, Enum):
    MONITOR = "monitor"
    RETRY = "retry"
    ROLLBACK = "rollback"
    PAUSE = "pause"
    RESUME = "resume"
    NOOP = "noop"


class WorkflowHealth(BaseModel):
    healthy: bool
    score: float = Field(ge=0.0, le=1.0)
    reasons: list[str] = Field(default_factory=list)


class AutonomousDecision(BaseModel):
    decision_id: str = Field(default_factory=lambda: str(uuid4()))
    action: AutonomyAction
    reason: str
    confidence: float = Field(ge=0.0, le=1.0)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = Field(default_factory=dict)


class WorkflowState(BaseModel):
    workflow_name: str
    status: str = "active"
    health: WorkflowHealth
    consecutive_failures: int = 0
    retry_count: int = 0
    version: str = "initial"
    last_decision_id: str | None = None


class AutonomyReport(BaseModel):
    workflow: str
    state: WorkflowState
    decision: AutonomousDecision
    dry_run: bool = True
