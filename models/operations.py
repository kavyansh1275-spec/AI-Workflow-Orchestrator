from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class OperationStatus(str, Enum):
    PLANNED = "planned"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    RETRYING = "retrying"
    FAILED = "failed"
    RECOVERED = "recovered"
    BLOCKED = "blocked"


class FailureClass(str, Enum):
    NONE = "none"
    RETRYABLE = "retryable"
    CONFIGURATION = "configuration"
    AUTHENTICATION = "authentication"
    RATE_LIMIT = "rate_limit"
    PERMANENT = "permanent"
    UNKNOWN = "unknown"


class OperationAttempt(BaseModel):
    attempt_id: str = Field(default_factory=lambda: str(uuid4()))
    attempt_number: int = Field(ge=1)
    status: OperationStatus
    failure_class: FailureClass = FailureClass.NONE
    message: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = Field(default_factory=dict)


class OperationReport(BaseModel):
    operation_id: str = Field(default_factory=lambda: str(uuid4()))
    workflow_name: str
    provider: str
    status: OperationStatus
    failure_class: FailureClass = FailureClass.NONE
    attempts: list[OperationAttempt] = Field(default_factory=list)
    recovery_action: str | None = None
    message: str
    dry_run: bool = True
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: datetime | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
