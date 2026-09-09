from __future__ import annotations

import json
from collections.abc import Callable, Mapping
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


class N8nApiError(RuntimeError):
    """Raised when the n8n Public API rejects a request."""


class N8nClient:
    """Small dependency-free client for the n8n Public REST API."""

    def __init__(self, base_url: str, api_key: str, opener: Callable[..., Any] | None = None, timeout: float = 20.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.opener = opener or urlopen
        self.timeout = timeout
        if not self.base_url:
            raise ValueError("n8n base URL cannot be blank")
        if not self.api_key:
            raise ValueError("n8n API key cannot be blank")
        if timeout <= 0:
            raise ValueError("timeout must be greater than zero")

    @staticmethod
    def _id(value: str) -> str:
        value = str(value).strip()
        if not value:
            raise ValueError("workflow_id cannot be blank")
        return quote(value, safe="")

    def _request(self, method: str, path: str, payload: Mapping[str, Any] | None = None) -> dict[str, Any]:
        body = json.dumps(payload).encode("utf-8") if payload is not None else None
        request = Request(
            f"{self.base_url}{path}",
            data=body,
            method=method,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "X-N8N-API-KEY": self.api_key,
            },
        )
        try:
            with self.opener(request, timeout=self.timeout) as response:
                raw = response.read().decode("utf-8")
                return json.loads(raw) if raw else {}
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise N8nApiError(f"n8n API returned HTTP {exc.code}: {detail[:500]}") from exc
        except URLError as exc:
            raise N8nApiError(f"Could not reach n8n: {exc.reason}") from exc
        except json.JSONDecodeError as exc:
            raise N8nApiError("n8n returned an invalid JSON response") from exc

    def list_workflows(self, limit: int = 100) -> dict[str, Any]:
        if not 1 <= limit <= 250:
            raise ValueError("limit must be between 1 and 250")
        return self._request("GET", f"/api/v1/workflows?limit={limit}")

    def get_workflow(self, workflow_id: str) -> dict[str, Any]:
        return self._request("GET", f"/api/v1/workflows/{self._id(workflow_id)}")

    def create_workflow(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        return self._request("POST", "/api/v1/workflows", payload)

    def update_workflow(self, workflow_id: str, payload: Mapping[str, Any]) -> dict[str, Any]:
        return self._request("PUT", f"/api/v1/workflows/{self._id(workflow_id)}", payload)

    def delete_workflow(self, workflow_id: str) -> dict[str, Any]:
        return self._request("DELETE", f"/api/v1/workflows/{self._id(workflow_id)}")

    def activate_workflow(self, workflow_id: str) -> dict[str, Any]:
        return self._request("POST", f"/api/v1/workflows/{self._id(workflow_id)}/activate")

    def deactivate_workflow(self, workflow_id: str) -> dict[str, Any]:
        return self._request("POST", f"/api/v1/workflows/{self._id(workflow_id)}/deactivate")
