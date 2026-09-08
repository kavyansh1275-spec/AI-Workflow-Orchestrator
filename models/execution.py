from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class StepExecution(BaseModel):
    """Runtime result for one workflow step."""

    step_id: str
    status: str
    attempts: int = 1
    output: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None


class ExecutionResult(BaseModel):
    """Deterministic V6 execution report."""

    execution_id: str
    workflow_name: str
    status: str
    started_at: str
    finished_at: str
    dry_run: bool = True
    steps: list[StepExecution] = Field(default_factory=list)

    @classmethod
    def started(cls, execution_id: str, workflow_name: str, dry_run: bool = True) -> "ExecutionResult":
        now = datetime.now(timezone.utc).isoformat()
        return cls(
            execution_id=execution_id,
            workflow_name=workflow_name,
            status="running",
            started_at=now,
            finished_at=now,
            dry_run=dry_run,
        )
