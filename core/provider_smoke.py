from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any

from core.credentials import CredentialManager
from integrations.make_client import MakeClient
from integrations.n8n_client import N8nClient
from integrations.zapier_client import ZapierClient
from models.provider_testing import ProviderSmokeTest, ProviderTestStatus


class ProviderSmokeTester:
    """Opt-in, read-only provider connectivity tests.

    These tests never create, modify, activate, execute, or delete a workflow.
    They only verify that configured credentials can reach a provider's read API.
    """

    def __init__(self, credentials: CredentialManager | None = None) -> None:
        self.credentials = credentials or CredentialManager()

    def run(self, provider: str, timeout: float = 10.0) -> ProviderSmokeTest:
        provider = provider.strip().lower()
        if provider not in {"n8n", "make", "zapier"}:
            raise ValueError(f"unsupported provider: {provider}")

        started = datetime.now(timezone.utc)
        credential = self.credentials.get(provider)
        if not credential.api_key:
            return ProviderSmokeTest(
                provider=provider,
                status=ProviderTestStatus.SKIPPED,
                message="No provider credential is configured; no external request was made.",
                completed_at=datetime.now(timezone.utc),
                metadata={"credential_status": credential.status.value},
            )

        try:
            if provider == "n8n":
                base_url = credential.base_url or os.getenv("N8N_BASE_URL")
                if not base_url:
                    raise RuntimeError("N8N_BASE_URL is required for the n8n smoke test")
                client = N8nClient(base_url=base_url, api_key=credential.api_key.get_secret_value(), timeout=timeout)
                client.list_workflows(limit=1)
                checks = ["credentials", "base_url", "GET /api/v1/workflows"]
            elif provider == "make":
                base_url = credential.base_url or os.getenv("MAKE_BASE_URL") or "https://eu1.make.com"
                team_id = int(os.getenv("MAKE_TEAM_ID", "0"))
                if team_id <= 0:
                    raise RuntimeError("MAKE_TEAM_ID must be set to a positive team ID for the Make smoke test")
                client = MakeClient(base_url=base_url, api_token=credential.api_key.get_secret_value(), team_id=team_id, timeout=timeout)
                client.list_scenarios(limit=1)
                checks = ["credentials", "base_url", "team_id", "GET /api/v2/scenarios"]
            else:
                base_url = credential.base_url or os.getenv("ZAPIER_BASE_URL") or "https://api.zapier.com"
                client = ZapierClient(base_url=base_url, token=credential.api_key.get_secret_value(), timeout=timeout)
                client.list_zaps(limit=1)
                checks = ["credentials", "base_url", "GET /v2/zaps"]

            return ProviderSmokeTest(
                provider=provider,
                status=ProviderTestStatus.PASSED,
                dry_run=False,
                checks=checks,
                message="Read-only provider connectivity test passed; no workflow mutation was performed.",
                started_at=started,
                completed_at=datetime.now(timezone.utc),
            )
        except Exception as exc:
            return ProviderSmokeTest(
                provider=provider,
                status=ProviderTestStatus.FAILED,
                dry_run=False,
                message=f"Read-only provider connectivity test failed: {exc}",
                started_at=started,
                completed_at=datetime.now(timezone.utc),
                metadata={"error_type": type(exc).__name__},
            )

    def run_all(self) -> dict[str, dict[str, Any]]:
        return {provider: self.run(provider).model_dump(mode="json") for provider in ("n8n", "make", "zapier")}
