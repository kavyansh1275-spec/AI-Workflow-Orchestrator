from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class V10Stage(str, Enum):
    UNDERSTAND = "understand"
    DECIDE = "decide"
    PLAN = "plan"
    VALIDATE = "validate"
    GENERATE = "generate"
    EXECUTE = "execute"
    RELEASE = "release"
    SUPERVISE = "supervise"


class GateStatus(str, Enum):
    PASSED = "passed"
    BLOCKED = "blocked"


class PipelineEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid4()))
    stage: V10Stage
    status: str
    message: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = Field(default_factory=dict)


class QualityGate(BaseModel):
    name: str
    status: GateStatus
    message: str


class V10Run(BaseModel):
    run_id: str = Field(default_factory=lambda: str(uuid4()))
    request: str
    status: str
    provider: str | None = None
    confidence: float = Field(ge=0.0, le=1.0)
    dry_run: bool = True
    gates: list[QualityGate] = Field(default_factory=list)
    events: list[PipelineEvent] = Field(default_factory=list)
    result: dict[str, Any] = Field(default_factory=dict)
