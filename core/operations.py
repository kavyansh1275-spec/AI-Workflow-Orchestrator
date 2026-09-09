from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Callable

from models.operations import (
    FailureClass,
    OperationAttempt,
    OperationReport,
    OperationStatus,
)
from models.workflow import WorkflowPlan


class AutonomousOperations:
    """Safe operations coordinator for retries, failure classification and recovery planning."""

    def __init__(self, max_retries: int = 2) -> None:
        if max_retries < 0:
            raise ValueError("max_retries cannot be negative")
        self.max_retries = max_retries
        self._history: dict[str, OperationReport] = {}

    def classify_failure(self, error: Exception | str) -> FailureClass:
        text = str(error).lower()
        if any(term in text for term in ("timeout", "temporarily", "connection", "503", "502", "504")):
            return FailureClass.RETRYABLE
        if any(term in text for term in ("rate limit", "429", "too many requests")):
            return FailureClass.RATE_LIMIT
        if any(term in text for term in ("unauthorized", "forbidden", "401", "403", "api key", "token")):
            return FailureClass.AUTHENTICATION
        if any(term in text for term in ("invalid", "missing", "required", "configuration")):
            return FailureClass.CONFIGURATION
        if any(term in text for term in ("not found", "unsupported", "does not exist")):
            return FailureClass.PERMANENT
        return FailureClass.UNKNOWN

    def plan(self, workflow: WorkflowPlan, dry_run: bool = True) -> OperationReport:
        report = OperationReport(
            workflow_name=workflow.name,
            provider=workflow.provider,
            status=OperationStatus.PLANNED,
            message="Operation is ready for execution and recovery supervision.",
            dry_run=dry_run,
            metadata={"step_count": len(workflow.steps), "max_retries": self.max_retries},
        )
        self._history[report.operation_id] = report
        return report

    def run(
        self,
        workflow: WorkflowPlan,
        operation: Callable[[], Any] | None = None,
        dry_run: bool = True,
    ) -> OperationReport:
        report = self.plan(workflow, dry_run=dry_run)
        attempts: list[OperationAttempt] = []
        total_attempts = self.max_retries + 1

        for number in range(1, total_attempts + 1):
            if operation is None:
                attempts.append(OperationAttempt(
                    attempt_number=number,
                    status=OperationStatus.SUCCEEDED,
                    message="Dry-run operation completed without external provider calls.",
                ))
                report = report.model_copy(update={
                    "status": OperationStatus.SUCCEEDED,
                    "attempts": attempts,
                    "message": "Autonomous dry-run operation completed successfully.",
                    "completed_at": datetime.now(timezone.utc),
                })
                self._history[report.operation_id] = report
                return report

            try:
                result = operation()
                attempts.append(OperationAttempt(
                    attempt_number=number,
                    status=OperationStatus.SUCCEEDED,
                    message="Provider operation completed successfully.",
                    metadata={"result_type": type(result).__name__},
                ))
                report = report.model_copy(update={
                    "status": OperationStatus.SUCCEEDED,
                    "attempts": attempts,
                    "message": "Operation completed successfully.",
                    "completed_at": datetime.now(timezone.utc),
                })
                self._history[report.operation_id] = report
                return report
            except Exception as exc:
                failure = self.classify_failure(exc)
                retryable = failure in {FailureClass.RETRYABLE, FailureClass.RATE_LIMIT}
                attempts.append(OperationAttempt(
                    attempt_number=number,
                    status=OperationStatus.RETRYING if retryable and number < total_attempts else OperationStatus.FAILED,
                    failure_class=failure,
                    message=str(exc),
                ))
                if not retryable or number >= total_attempts:
                    recovery = "rollback_or_manual_review" if failure != FailureClass.AUTHENTICATION else "configure_credentials"
                    report = report.model_copy(update={
                        "status": OperationStatus.FAILED,
                        "failure_class": failure,
                        "attempts": attempts,
                        "recovery_action": recovery,
                        "message": f"Operation failed after {number} attempt(s).",
                        "completed_at": datetime.now(timezone.utc),
                    })
                    self._history[report.operation_id] = report
                    return report

        raise RuntimeError("operation loop exited unexpectedly")

    def history(self) -> list[OperationReport]:
        return list(self._history.values())

    def get(self, operation_id: str) -> OperationReport:
        try:
            return self._history[operation_id]
        except KeyError as exc:
            raise KeyError(f"unknown operation: {operation_id}") from exc
