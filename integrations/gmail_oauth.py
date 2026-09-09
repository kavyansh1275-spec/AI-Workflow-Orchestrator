from __future__ import annotations

import os
from typing import Any
from urllib.parse import urlencode


GMAIL_SEND_SCOPE = "https://www.googleapis.com/auth/gmail.send"
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"


class GmailOAuth:
    """Small OAuth helper for connecting a user's Gmail account.

    Secrets/tokens are intentionally not persisted by this class. A production
    deployment should store encrypted refresh tokens in its connection store.
    """

    def __init__(self, client_id: str | None = None, client_secret: str | None = None, redirect_uri: str | None = None) -> None:
        self.client_id = client_id or os.getenv("GOOGLE_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("GOOGLE_CLIENT_SECRET")
        self.redirect_uri = redirect_uri or os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/api/connections/gmail/callback")

    def authorization_url(self, state: str) -> str:
        if not self.client_id:
            raise RuntimeError("Missing GOOGLE_CLIENT_ID")
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": GMAIL_SEND_SCOPE,
            "access_type": "offline",
            "prompt": "consent",
            "state": state,
        }
        return f"{GOOGLE_AUTH_URL}?{urlencode(params)}"

    def token_request(self, code: str) -> dict[str, Any]:
        if not self.client_id or not self.client_secret:
            raise RuntimeError("Missing GOOGLE_CLIENT_ID or GOOGLE_CLIENT_SECRET")
        return {
            "code": code,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_uri,
            "grant_type": "authorization_code",
        }
