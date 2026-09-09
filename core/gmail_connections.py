from __future__ import annotations

import secrets
from typing import Any

from integrations.gmail_oauth import GmailOAuth


class GmailConnectionManager:
    """Manage OAuth connection metadata without persisting secrets in source control."""

    def __init__(self, oauth: GmailOAuth | None = None) -> None:
        self.oauth = oauth or GmailOAuth()
        self._states: set[str] = set()
        self._connections: dict[str, dict[str, Any]] = {}

    def begin(self, connection_id: str) -> str:
        state = secrets.token_urlsafe(32)
        self._states.add(state)
        self._connections[connection_id] = {
            "connection_id": connection_id,
            "provider": "gmail",
            "status": "pending",
            "scopes": ["https://www.googleapis.com/auth/gmail.send"],
            "token_stored": False,
        }
        return self.oauth.authorization_url(state)

    def consume_state(self, state: str) -> bool:
        if state not in self._states:
            return False
        self._states.remove(state)
        return True

    def complete(self, connection_id: str, email: str | None = None) -> dict[str, Any]:
        connection = self._connections.setdefault(connection_id, {"connection_id": connection_id, "provider": "gmail"})
        connection.update({"email": email, "status": "connected", "scopes": ["https://www.googleapis.com/auth/gmail.send"]})
        return dict(connection)

    def get(self, connection_id: str) -> dict[str, Any] | None:
        connection = self._connections.get(connection_id)
        return dict(connection) if connection else None
