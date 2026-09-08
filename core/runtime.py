from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from models.execution import ExecutionResult, StepExecution
from models.workflow import WorkflowPlan, WorkflowStep


class WorkflowRuntime:
    """V6 local runtime for safe, deterministic workflow execution.

    The runtime never calls external providers. It evaluates simple conditions,
    respects step dependencies, records state, and produces an execution report.
    """

    def run(self, workflow: WorkflowPlan, dry_run: bool = True) -> ExecutionResult:
        if not dry_run:
            raise ValueError("V6 runtime only supports safe dry-run execution")

        self._validate_dependencies(workflow)
        execution = ExecutionResult.started(
            execution_id=f"exec_{uuid4().hex[:12]}",
            workflow_name=workflow.name,
            dry_run=True,
        )

        completed: set[str] = set()
        skipped: set[str] = set()

        for step in workflow.steps:
            if not set(step.depends_on).issubset(completed | skipped):
                raise ValueError(f"step {step.id} has unmet dependencies")

            if not self._condition_allows(step):
                execution.steps.append(
                    StepExecution(
                        step_id=step.id,
                        status="skipped",
                        output={"reason": "condition_not_met", "condition": step.condition},
                    )
                )
                skipped.add(step.id)
                continue

            execution.steps.append(
                StepExecution(
                    step_id=step.id,
                    status="completed",
                    output={
                        "app": step.app,
                        "action": step.action,
                        "dry_run": True,
                        "config": step.config,
                    },
                )
            )
            completed.add(step.id)

        execution.status = "completed"
        execution.finished_at = datetime.now(timezone.utc).isoformat()
        return execution

    @staticmethod
    def _validate_dependencies(workflow: WorkflowPlan) -> None:
        ids = [step.id for step in workflow.steps]
        known = set(ids)
        if len(ids) != len(known):
            raise ValueError("workflow step IDs must be unique")
        for step in workflow.steps:
            missing = set(step.depends_on) - known
            if missing:
                raise ValueError(f"step {step.id} has unknown dependencies: {sorted(missing)}")
            if step.id in step.depends_on:
                raise ValueError(f"step {step.id} cannot depend on itself")

    @staticmethod
    def _condition_allows(step: WorkflowStep) -> bool:
        if not step.condition:
            return True

        condition = step.condition.lower().strip()
        negative_markers = ("not met", "false", "failed", "low", "no ")
        positive_markers = ("true", "met", "high", "yes", "approved")

        if any(marker in condition for marker in negative_markers):
            return False
        if any(marker in condition for marker in positive_markers):
            return True
        return True
