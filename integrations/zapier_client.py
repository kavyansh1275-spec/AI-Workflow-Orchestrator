from __future__ import annotations

import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class ZapierApiError(RuntimeError):
    """Raised when the Zapier API rejects or cannot complete a request."""


class ZapierClient:
    """Small dependency-free client for Zapier's Powered by Zapier API."""

    def __init__(self, base_url: str, token: str, timeout: float = 30.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.timeout = timeout
        if not self.base_url:
            raise ValueError("Zapier base URL cannot be blank")
        if not self.token:
            raise ValueError("Zapier token cannot be blank")
        if timeout <= 0:
            raise ValueError("timeout must be positive")

    def _request(
        self,
        method: str,
        path: str,
        payload: dict[str, Any] | None = None,
        query: str = "",
    ) -> dict[str, Any]:
        url = f"{self.base_url}/{path.lstrip('/')}"
        if query:
            url = f"{url}?{query}"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        body = json.dumps(payload).encode("utf-8") if payload is not None else None
        request = Request(url, data=body, headers=headers, method=method.upper())
        try:
            with urlopen(request, timeout=self.timeout) as response:
                raw = response.read().decode("utf-8")
                return json.loads(raw) if raw else {}
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise ZapierApiError(f"Zapier API error {exc.code}: {detail}") from exc
        except URLError as exc:
            raise ZapierApiError(f"Zapier API connection error: {exc.reason}") from exc

    def list_zaps(self, limit: int = 100, offset: int = 0) -> dict[str, Any]:
        if limit <= 0 or offset < 0:
            raise ValueError("limit must be positive and offset cannot be negative")
        return self._request("GET", "/v2/zaps", query=f"limit={limit}&offset={offset}")

    def get_zap(self, zap_id: str) -> dict[str, Any]:
        return self._request("GET", f"/v2/zaps/{zap_id}")

    def create_zap(self, title: str, steps: list[dict[str, Any]], enabled: bool = False) -> dict[str, Any]:
        if not title.strip():
            raise ValueError("Zap title cannot be blank")
        if not steps:
            raise ValueError("Zap must contain at least one step")
        return self._request(
            "POST",
            "/v2/zaps",
            {"data": {"title": title, "steps": steps, "enabled": enabled}},
        )

    def delete_zap(self, zap_id: str) -> dict[str, Any]:
        return self._request("DELETE", f"/v2/zaps/{zap_id}")
