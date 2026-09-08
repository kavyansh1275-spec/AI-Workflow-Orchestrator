import unittest

from core.autonomy import AutonomousManager
from models.autonomy import AutonomyAction, WorkflowHealth, WorkflowState
from models.workflow import WorkflowPlan, WorkflowStep


class V9AutonomyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.workflow = WorkflowPlan(
            name="autonomous-test",
            request="Receive a webhook and send an email",
            description="V9 test workflow",
            steps=[
                WorkflowStep(id="step_1", type="trigger", app="webhook", action="receive_request"),
                WorkflowStep(id="step_2", type="action", app="gmail", action="send_email", depends_on=["step_1"]),
            ],
        )
        self.manager = AutonomousManager()

    def test_healthy_workflow_is_monitored(self) -> None:
        report = self.manager.supervise(self.workflow)
        self.assertTrue(report.state.health.healthy)
        self.assertEqual(report.decision.action, AutonomyAction.MONITOR)

    def test_failure_requests_retry(self) -> None:
        report = self.manager.supervise(
            self.workflow,
            execution={"status": "failed", "failed_steps": ["step_2"]},
        )
        self.assertFalse(report.state.health.healthy)
        self.assertEqual(report.decision.action, AutonomyAction.RETRY)

    def test_repeated_failures_trigger_rollback(self) -> None:
        state = WorkflowState(
            workflow_name=self.workflow.name,
            health=WorkflowHealth(healthy=False, score=0.25, reasons=["failure"]),
            consecutive_failures=2,
        )
        report = self.manager.supervise(
            self.workflow,
            execution={"status": "failed", "failed_steps": ["step_2"]},
            previous_state=state,
        )
        self.assertEqual(report.state.consecutive_failures, 3)
        self.assertEqual(report.decision.action, AutonomyAction.ROLLBACK)

    def test_decisions_are_dry_run_by_default(self) -> None:
        report = self.manager.supervise(self.workflow)
        self.assertTrue(report.dry_run)
        self.assertIsNotNone(report.decision.decision_id)


if __name__ == "__main__":
    unittest.main()
