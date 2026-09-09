from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any

from core.credentials import CredentialManager
from core.generator import WorkflowGenerator
from integrations.make import MakeIntegration
from integrations.n8n import N8nIntegration
from integrations.zapier import ZapierIntegration
from models.live_deployment import LiveDeploymentResult, LiveDeploymentStatus
from models.workflow import WorkflowPlan


class LiveDeploymentManager:
    """V13 credential-aware provider deployment with explicit safety gates.

    Resources are created disabled/inactive by provider adapters. Live deployment
    is blocked unless LIVE_DEPLOYMENT_ENABLED is explicitly enabled and the
    caller requests live mode. Credentials are never stored by this manager.
    """

    def __init__(
        self,
        credentials: CredentialManager | None = None,
        generator: WorkflowGenerator | None = None,
    ) -> None:
        self.credentials = credentials or CredentialManager()
        self.generator = generator or WorkflowGenerator()
        self._created: dict[str, tuple[str, str]] = {}

    @staticmethod
    def enabled() -> bool:
        return os.getenv("LIVE_DEPLOYMENT_ENABLED", "0").strip().lower() in {"1", "true", "yes"}

    def deploy(self, workflow: WorkflowPlan, live: bool = False) -> LiveDeploymentResult:
        started = datetime.now(timezone.utc)
        provider = workflow.provider.strip().lower()
        if not live:
            return self._blocked(provider, "Live deployment was not requested.", started)
        if not self.enabled():
            return self._blocked(
                provider,
                "Live deployment is disabled. Set LIVE_DEPLOYMENT_ENABLED=1 explicitly to opt in.",
                started,
            )
        if provider not in {"n8n", "make", "zapier"}:
            return self._blocked(provider, "Live deployment supports n8n, Make, and Zapier only.", started)

        try:
            self.credentials.require(provider)
            if provider == "n8n":
                result = N8nIntegration(self.credentials, self.generator).deploy(workflow)
                resource_id = str(result.get("workflow_id") or "") or None
                resource_name = result.get("name", workflow.name)
            elif provider == "make":
                result = MakeIntegration(self.credentials, self.generator).deploy(workflow)
                resource_id = str(result.get("scenario_id") or "") or None
                resource_name = result.get("name", workflow.name)
            else:
                result = ZapierIntegration(self.credentials, self.generator).deploy(workflow)
                resource_id = str(result.get("zap_id") or "") or None
                resource_name = result.get("title", workflow.name)

            if not resource_id:
                raise RuntimeError(f"{provider} deployment did not return a resource ID")

            deployment_id = f"live-{resource_id}"
            self._created[deployment_id] = (provider, resource_id)
            return LiveDeploymentResult(
                deployment_id=deployment_id,
                provider=provider,
                status=LiveDeploymentStatus.CREATED,
                resource_id=resource_id,
                resource_name=str(resource_name),
                active=False,
                message="Live resource created successfully and left inactive.",
                started_at=started,
                completed_at=datetime.now(timezone.utc),
                metadata={"activation": "not_requested"},
            )
        except Exception as exc:
            return LiveDeploymentResult(
                provider=provider,
                status=LiveDeploymentStatus.FAILED,
                message=f"Live deployment failed: {exc}",
                started_at=started,
                completed_at=datetime.now(timezone.utc),
                metadata={"error_type": type(exc).__name__},
            )

    def rollback(self, deployment_id: str) -> LiveDeploymentResult:
        target = self._created.get(deployment_id)
        if target is None:
            raise KeyError(f"unknown live deployment: {deployment_id}")
        provider, resource_id = target
        try:
            if provider == "n8n":
                N8nIntegration(self.credentials, self.generator).delete(resource_id)
            elif provider == "make":
                MakeIntegration(self.credentials, self.generator).delete(int(resource_id))
            else:
                ZapierIntegration(self.credentials, self.generator).delete_zap(resource_id)
            del self._created[deployment_id]
            return LiveDeploymentResult(
                deployment_id=deployment_id,
                provider=provider,
                status=LiveDeploymentStatus.ROLLED_BACK,
                resource_id=resource_id,
                message="Live resource deleted successfully during rollback.",
                completed_at=datetime.now(timezone.utc),
            )
        except Exception as exc:
            return LiveDeploymentResult(
                deployment_id=deployment_id,
                provider=provider,
                status=LiveDeploymentStatus.FAILED,
                resource_id=resource_id,
                message=f"Rollback failed: {exc}",
                completed_at=datetime.now(timezone.utc),
                metadata={"error_type": type(exc).__name__},
            )

    def readiness(self, workflow: WorkflowPlan) -> dict[str, Any]:
        provider = workflow.provider.strip().lower()
        credential = self.credentials.get(provider) if provider in {"n8n", "make", "zapier"} else None
        extra = {}
        if provider == "make":
            extra["team_id_configured"] = bool(os.getenv("MAKE_TEAM_ID"))
        return {
            "provider": provider,
            "supported": provider in {"n8n", "make", "zapier"},
            "credential_configured": bool(credential and credential.api_key),
            "live_enabled": self.enabled(),
            "ready": bool(credential and credential.api_key and self.enabled()) and provider in {"n8n", "make", "zapier"},
            **extra,
        }

    @staticmethod
    def _blocked(provider: str, message: str, started: datetime) -> LiveDeploymentResult:
        return LiveDeploymentResult(
            provider=provider,
            status=LiveDeploymentStatus.BLOCKED,
            message=message,
            started_at=started,
            completed_at=datetime.now(timezone.utc),
        )
