from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any

from core.credentials import CredentialManager
from core.generator import WorkflowGenerator
from integrations.make import MakeIntegration
from integrations.n8n import N8nIntegration
from integrations.zapier import ZapierIntegration
from models.provider_lifecycle import LifecycleAction, LifecycleStatus, ProviderLifecycleTest
from models.workflow import WorkflowPlan


class ProviderLifecycleTester:
    """Opt-in live provider lifecycle tester.

    The live path is deliberately disabled unless PROVIDER_LIFECYCLE_LIVE=1 is
    present in the runtime environment. A successful create test immediately
    cleans up the created resource, so test resources are not intentionally
    left behind. Credentials are read only from the environment.
    """

    def __init__(
        self,
        credentials: CredentialManager | None = None,
        generator: WorkflowGenerator | None = None,
    ) -> None:
        self.credentials = credentials or CredentialManager()
        self.generator = generator or WorkflowGenerator()

    @staticmethod
    def _live_allowed() -> bool:
        return os.getenv("PROVIDER_LIFECYCLE_LIVE", "0").strip().lower() in {"1", "true", "yes"}

    def create_and_cleanup(self, workflow: WorkflowPlan) -> ProviderLifecycleTest:
        provider = workflow.provider.strip().lower()
        started = datetime.now(timezone.utc)
        if provider not in {"n8n", "make", "zapier"}:
            return ProviderLifecycleTest(
                provider=provider,
                action=LifecycleAction.CREATE,
                status=LifecycleStatus.BLOCKED,
                dry_run=True,
                message="Lifecycle testing is supported only for n8n, Make, and Zapier.",
                started_at=started,
                completed_at=datetime.now(timezone.utc),
            )
        if not self._live_allowed():
            return ProviderLifecycleTest(
                provider=provider,
                action=LifecycleAction.CREATE,
                status=LifecycleStatus.BLOCKED,
                dry_run=True,
                message="Live lifecycle testing is disabled. Set PROVIDER_LIFECYCLE_LIVE=1 explicitly to opt in.",
                started_at=started,
                completed_at=datetime.now(timezone.utc),
            )
        try:
            self.credentials.require(provider)
            if provider == "n8n":
                result = N8nIntegration(self.credentials, self.generator).deploy(workflow)
                resource_id = str(result.get("workflow_id") or "") or None
                if not resource_id:
                    raise RuntimeError("n8n create response did not contain a workflow ID")
                N8nIntegration(self.credentials, self.generator).delete(resource_id)
            elif provider == "make":
                result = MakeIntegration(self.credentials, self.generator).deploy(workflow)
                resource_id = str(result.get("scenario_id") or "") or None
                if not resource_id:
                    raise RuntimeError("Make create response did not contain a scenario ID")
                MakeIntegration(self.credentials, self.generator).delete(int(resource_id))
            else:
                result = ZapierIntegration(self.credentials, self.generator).deploy(workflow)
                resource_id = str(result.get("zap_id") or "") or None
                if not resource_id:
                    raise RuntimeError("Zapier create response did not contain a Zap ID")
                ZapierIntegration(self.credentials, self.generator).delete_zap(resource_id)
            return ProviderLifecycleTest(
                provider=provider,
                action=LifecycleAction.CREATE,
                status=LifecycleStatus.PASSED,
                dry_run=False,
                resource_id=resource_id,
                message="Live create-and-cleanup lifecycle test passed; the temporary resource was deleted.",
                started_at=started,
                completed_at=datetime.now(timezone.utc),
                metadata={"cleanup": "completed"},
            )
        except Exception as exc:
            return ProviderLifecycleTest(
                provider=provider,
                action=LifecycleAction.CREATE,
                status=LifecycleStatus.FAILED,
                dry_run=False,
                message=f"Live lifecycle test failed: {exc}",
                started_at=started,
                completed_at=datetime.now(timezone.utc),
                metadata={"error_type": type(exc).__name__},
            )

    def validate(self, workflow: WorkflowPlan) -> dict[str, Any]:
        provider = workflow.provider.strip().lower()
        credential = self.credentials.get(provider) if provider in {"n8n", "make", "zapier"} else None
        return {
            "provider": provider,
            "credential_configured": bool(credential and credential.api_key),
            "live_opt_in": self._live_allowed(),
            "ready": bool(credential and credential.api_key and self._live_allowed()),
        }
