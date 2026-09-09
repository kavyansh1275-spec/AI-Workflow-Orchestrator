from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class LiveDeploymentStatus(str, Enum):
    BLOCKED = "blocked"
    CREATED = "created"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


class LiveDeploymentResult(BaseModel):
    deployment_id: str = Field(default_factory=lambda: f"live-{uuid4().hex[:12]}")
    provider: str
    status: LiveDeploymentStatus
    dry_run: bool = False
    resource_id: str | None = None
    resource_name: str | None = None
    active: bool = False
    message: str
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: datetime | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
