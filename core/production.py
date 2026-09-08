from __future__ import annotations

import hashlib
import json
from uuid import uuid4

from core.generator import WorkflowGenerator
from core.integration_manager import IntegrationManager
from models.deployment import (
    DeploymentEnvironment,
    DeploymentPlan,
    DeploymentRecord,
    DeploymentStatus,
)
from models.workflow import WorkflowPlan


class ProductionDeployer:
    """V8 release manager with safe local deployment simulation.

    Real provider API deployment is intentionally disabled until credentials and
    provider adapters are added in a later version.
    """

    def __init__(
        self,
        generator: WorkflowGenerator | None = None,
        integration_manager: IntegrationManager | None = None,
    ) -> None:
        self.generator = generator or WorkflowGenerator()
        self.integration_manager = integration_manager or IntegrationManager()
        self._history: dict[str, DeploymentRecord] = {}

    def prepare(
        self,
        workflow: WorkflowPlan,
        environment: str = "staging",
        dry_run: bool = True,
    ) -> DeploymentPlan:
        target = self._environment(environment)
        self.integration_manager.validate_workflow(workflow)
        artifact = self.generator.generate(workflow)
        artifact_sha256 = hashlib.sha256(
            json.dumps(artifact, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        return DeploymentPlan(
            release_id=f"rel-{uuid4().hex[:12]}",
            workflow_name=workflow.name,
            provider=workflow.provider,
            environment=target,
            dry_run=dry_run,
            artifact_sha256=artifact_sha256,
            artifact=artifact,
        )

    def deploy(
        self,
        workflow: WorkflowPlan,
        environment: str = "staging",
        dry_run: bool = True,
    ) -> DeploymentRecord:
        plan = self.prepare(workflow, environment, dry_run)
        if not dry_run:
            raise RuntimeError(
                "live production deployment is disabled in V8; use dry_run=True until provider credentials and adapters are configured"
            )

        record = DeploymentRecord(
            release_id=plan.release_id,
            workflow_name=plan.workflow_name,
            provider=plan.provider,
            environment=plan.environment,
            status=DeploymentStatus.PLANNED,
            dry_run=True,
            artifact_sha256=plan.artifact_sha256,
            message=f"Release prepared for {plan.environment.value}; no external API call was made.",
        )
        self._history[record.release_id] = record
        return record

    def rollback(self, release_id: str) -> DeploymentRecord:
        record = self._history.get(release_id)
        if record is None:
            raise KeyError(f"unknown release: {release_id}")
        if record.status == DeploymentStatus.ROLLED_BACK:
            return record

        rolled_back = record.model_copy(
            update={
                "status": DeploymentStatus.ROLLED_BACK,
                "message": f"Release {release_id} rolled back locally; no external API call was made.",
            }
        )
        self._history[release_id] = rolled_back
        return rolled_back

    def history(self) -> list[DeploymentRecord]:
        return list(self._history.values())

    def health(self, release_id: str) -> dict[str, object]:
        record = self._history.get(release_id)
        if record is None:
            raise KeyError(f"unknown release: {release_id}")
        return {
            "release_id": release_id,
            "environment": record.environment.value,
            "healthy": record.status != DeploymentStatus.ROLLED_BACK,
            "status": record.status.value,
            "dry_run": record.dry_run,
        }

    @staticmethod
    def _environment(value: str) -> DeploymentEnvironment:
        try:
            return DeploymentEnvironment(value.strip().lower())
        except ValueError as exc:
            allowed = ", ".join(item.value for item in DeploymentEnvironment)
            raise ValueError(f"unsupported deployment environment: {value}; expected one of: {allowed}") from exc
