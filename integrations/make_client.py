from __future__ import annotations

import json
from collections.abc import Callable, Mapping
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


class MakeApiError(RuntimeError):
    """Raised when the Make API rejects a request."""


class MakeClient:
    """Small dependency-free client for the Make API v2 scenarios endpoints."""

    def __init__(self, base_url: str, api_token: str, team_id: int, opener: Callable[..., Any] | None = None, timeout: float = 20.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_token = api_token
        self.team_id = team_id
        self.opener = opener or urlopen
        self.timeout = timeout
        if not self.base_url:
            raise ValueError("Make base URL cannot be blank")
        if not self.api_token:
            raise ValueError("Make API token cannot be blank")
        if team_id <= 0:
            raise ValueError("Make team ID must be positive")
        if timeout <= 0:
            raise ValueError("timeout must be positive")

    def _request(self, method: str, path: str, payload: Mapping[str, Any] | None = None) -> dict[str, Any]:
        body = json.dumps(payload).encode("utf-8") if payload is not None else None
        request = Request(
            f"{self.base_url}{path}",
            data=body,
            method=method,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": f"Token {self.api_token}",
            },
        )
        try:
            with self.opener(request, timeout=self.timeout) as response:
                raw = response.read().decode("utf-8")
                return json.loads(raw) if raw else {}
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise MakeApiError(f"Make API returned HTTP {exc.code}: {detail[:500]}") from exc
        except URLError as exc:
            raise MakeApiError(f"Could not reach Make: {exc.reason}") from exc
        except json.JSONDecodeError as exc:
            raise MakeApiError("Make returned an invalid JSON response") from exc

    def list_scenarios(self, limit: int = 100, offset: int = 0) -> dict[str, Any]:
        if not 1 <= limit <= 1000:
            raise ValueError("limit must be between 1 and 1000")
        if offset < 0:
            raise ValueError("offset cannot be negative")
        return self._request("GET", f"/api/v2/scenarios?teamId={self.team_id}&pg[offset]={offset}&pg[limit]={limit}")

    def get_scenario(self, scenario_id: int) -> dict[str, Any]:
        return self._request("GET", f"/api/v2/scenarios/{quote(str(scenario_id), safe='')}")

    def create_scenario(self, blueprint: str, scheduling: str, name: str, confirmed: bool = False, folder_id: int | None = None) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "blueprint": blueprint,
            "teamId": self.team_id,
            "scheduling": scheduling,
        }
        if folder_id is not None:
            payload["folderId"] = folder_id
        query = "?confirmed=true" if confirmed else ""
        result = self._request("POST", f"/api/v2/scenarios{query}", payload)
        if name and isinstance(result.get("scenario"), dict):
            scenario = result["scenario"]
            if not scenario.get("name"):
                result["scenario"] = {**scenario, "name": name}
        return result

    def update_scenario(self, scenario_id: int, payload: Mapping[str, Any], confirmed: bool = False) -> dict[str, Any]:
        query = "?confirmed=true" if confirmed else ""
        return self._request("PATCH", f"/api/v2/scenarios/{quote(str(scenario_id), safe='')}{query}", payload)

    def delete_scenario(self, scenario_id: int) -> dict[str, Any]:
        return self._request("DELETE", f"/api/v2/scenarios/{quote(str(scenario_id), safe='')}")

    def activate_scenario(self, scenario_id: int) -> dict[str, Any]:
        return self._request("POST", f"/api/v2/scenarios/{quote(str(scenario_id), safe='')}/start")

    def deactivate_scenario(self, scenario_id: int) -> dict[str, Any]:
        return self._request("POST", f"/api/v2/scenarios/{quote(str(scenario_id), safe='')}/stop")

    def run_scenario(self, scenario_id: int, data: Mapping[str, Any] | None = None, responsive: bool = False) -> dict[str, Any]:
        payload: dict[str, Any] = {"responsive": responsive}
        if data is not None:
            payload["data"] = dict(data)
        return self._request("POST", f"/api/v2/scenarios/{quote(str(scenario_id), safe='')}/run", payload)
