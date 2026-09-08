from __future__ import annotations

from typing import Any

from models.autonomy import (
    AutonomyAction,
    AutonomyReport,
    AutonomousDecision,
    WorkflowHealth,
    WorkflowState,
)
from models.workflow import WorkflowPlan


class AutonomousManager:
    """V9 deterministic workflow supervisor; safe by default and dry-run only."""

    def assess_health(self, workflow: WorkflowPlan, execution: dict[str, Any] | None = None) -> WorkflowHealth:
        if execution is None:
            return WorkflowHealth(healthy=True, score=1.0, reasons=["No execution failure reported."])

        status = str(execution.get("status", "unknown"))
        if status in {"completed", "success", "dry_run"}:
            return WorkflowHealth(healthy=True, score=1.0, reasons=["Latest execution completed successfully."])

        failed = execution.get("failed_steps", [])
        return WorkflowHealth(
            healthy=False,
            score=0.25,
            reasons=[f"Latest execution status is {status}.", f"Failed steps: {len(failed)}."],
        )

    def decide(self, workflow: WorkflowPlan, state: WorkflowState) -> AutonomousDecision:
        if state.status == "paused":
            return AutonomousDecision(action=AutonomyAction.PAUSE, reason="Workflow is already paused.", confidence=1.0)
        if not state.health.healthy:
            if state.consecutive_failures >= 3:
                return AutonomousDecision(
                    action=AutonomyAction.ROLLBACK,
                    reason="Repeated failures reached the rollback threshold.",
                    confidence=0.95,
                )
            return AutonomousDecision(
                action=AutonomyAction.RETRY,
                reason="The latest execution failed and the retry threshold has not been reached.",
                confidence=0.9,
            )
        return AutonomousDecision(
            action=AutonomyAction.MONITOR,
            reason="Workflow health is normal; continue monitoring.",
            confidence=0.99,
        )

    def supervise(
        self,
        workflow: WorkflowPlan,
        execution: dict[str, Any] | None = None,
        previous_state: WorkflowState | None = None,
        dry_run: bool = True,
    ) -> AutonomyReport:
        health = self.assess_health(workflow, execution)
        previous = previous_state or WorkflowState(workflow_name=workflow.name, health=health)
        failures = previous.consecutive_failures + (0 if health.healthy else 1)
        state = previous.model_copy(update={"health": health, "consecutive_failures": failures})
        decision = self.decide(workflow, state)
        state = state.model_copy(update={"last_decision_id": decision.decision_id})
        return AutonomyReport(workflow=workflow.name, state=state, decision=decision, dry_run=dry_run)
