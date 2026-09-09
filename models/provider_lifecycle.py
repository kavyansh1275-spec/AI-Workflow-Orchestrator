from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class LifecycleAction(str, Enum):
    VALIDATE = "validate"
    CREATE = "create"
    RUN = "run"
    STOP = "stop"
    DELETE = "delete"
    NONE = "none"


class LifecycleStatus(str, Enum):
    BLOCKED = "blocked"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"


class ProviderLifecycleTest(BaseModel):
    test_id: str = Field(default_factory=lambda: f"lifecycle-{uuid4().hex[:12]}")
    provider: str
    action: LifecycleAction
    status: LifecycleStatus
    dry_run: bool = True
    message: str
    resource_id: str | None = None
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: datetime | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
