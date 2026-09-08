from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class GeneratedWorkflow(BaseModel):
    """Portable V4 workflow artifact ready for export or later deployment."""

    provider: str
    format: str
    name: str
    artifact: dict[str, Any] = Field(default_factory=dict)
    dry_run: bool = True
