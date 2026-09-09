from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class ProviderTestStatus(str, Enum):
    SKIPPED = "skipped"
    PASSED = "passed"
    FAILED = "failed"
    BLOCKED = "blocked"


class ProviderSmokeTest(BaseModel):
    test_id: str = Field(default_factory=lambda: f"smoke-{uuid4().hex[:12]}")
    provider: str
    status: ProviderTestStatus
    dry_run: bool = True
    checks: list[str] = Field(default_factory=list)
    message: str
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: datetime | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
