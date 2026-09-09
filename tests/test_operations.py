import unittest

from core.operations import AutonomousOperations
from models.operations import FailureClass, OperationStatus
from models.workflow import WorkflowPlan, WorkflowStep


class AutonomousOperationsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = AutonomousOperations(max_retries=2)
        self.workflow = WorkflowPlan(
            name="operation_test",
            request="Receive a webhook and send an email",
            description="operations test",
            provider="n8n",
            steps=[
                WorkflowStep(id="step_1", type="trigger", app="webhook", action="receive_request"),
                WorkflowStep(id="step_2", type="action", app="gmail", action="send_email", depends_on=["step_1"]),
            ],
        )

    def test_dry_run_succeeds(self) -> None:
        report = self.engine.run(self.workflow)
        self.assertEqual(report.status, OperationStatus.SUCCEEDED)
        self.assertEqual(len(report.attempts), 1)

    def test_failure_classification(self) -> None:
        self.assertEqual(self.engine.classify_failure("HTTP 503 timeout"), FailureClass.RETRYABLE)
        self.assertEqual(self.engine.classify_failure("HTTP 429 rate limit"), FailureClass.RATE_LIMIT)
        self.assertEqual(self.engine.classify_failure("401 unauthorized api key"), FailureClass.AUTHENTICATION)
        self.assertEqual(self.engine.classify_failure("missing required recipient"), FailureClass.CONFIGURATION)

    def test_retry_then_success(self) -> None:
        calls = {"count": 0}

        def flaky() -> None:
            calls["count"] += 1
            if calls["count"] < 2:
                raise RuntimeError("temporary connection timeout")

        report = self.engine.run(self.workflow, operation=flaky, dry_run=False)
        self.assertEqual(report.status, OperationStatus.SUCCEEDED)
        self.assertEqual(len(report.attempts), 2)
        self.assertEqual(report.attempts[0].failure_class, FailureClass.RETRYABLE)

    def test_permanent_failure_stops(self) -> None:
        def broken() -> None:
            raise RuntimeError("missing required configuration")

        report = self.engine.run(self.workflow, operation=broken, dry_run=False)
        self.assertEqual(report.status, OperationStatus.FAILED)
        self.assertEqual(report.failure_class, FailureClass.CONFIGURATION)
        self.assertEqual(report.recovery_action, "rollback_or_manual_review")
        self.assertEqual(len(report.attempts), 1)

    def test_history(self) -> None:
        report = self.engine.run(self.workflow)
        self.assertEqual(self.engine.get(report.operation_id).operation_id, report.operation_id)
        self.assertEqual(len(self.engine.history()), 1)


if __name__ == "__main__":
    unittest.main()
