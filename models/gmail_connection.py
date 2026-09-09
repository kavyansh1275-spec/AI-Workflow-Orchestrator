from __future__ import annotations

from pydantic import BaseModel, Field


class GmailConnection(BaseModel):
    """Non-secret representation of a user's Gmail OAuth connection."""

    connection_id: str
    email: str | None = None
    provider: str = "gmail"
    scopes: list[str] = Field(default_factory=list)
    status: str = "disconnected"
    token_stored: bool = False
