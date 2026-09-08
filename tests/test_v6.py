import unittest

from core.orchestrator import Orchestrator
from core.runtime import WorkflowRuntime
from models.workflow import WorkflowPlan, WorkflowStep


class V6RuntimeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.orchestrator = Orchestrator()
        self.runtime = WorkflowRuntime()

    def test_v6_dry_run_executes_in_dependency_order(self) -> None:
        workflow = self.orchestrator.build(
            "Receive a webhook, analyze it with AI, and send the result to Gmail"
        )

        result = self.runtime.run(workflow)

        self.assertEqual(result.status, "completed")
        self.assertTrue(result.dry_run)
        self.assertEqual([step.step_id for step in result.steps], ["step_1", "step_2", "step_3"])
        self.assertTrue(all(step.status == "completed" for step in result.steps))

    def test_v6_condition_can_skip_step(self) -> None:
        workflow = WorkflowPlan(
            name="conditional",
            request="test",
            description="test",
            steps=[
                WorkflowStep(id="step_1", type="trigger", app="webhook", action="receive_request"),
                WorkflowStep(
                    id="step_2",
                    type="action",
                    app="gmail",
                    action="send_email",
                    depends_on=["step_1"],
                    condition="score is low",
                ),
            ],
        )

        result = self.runtime.run(workflow)

        self.assertEqual(result.steps[0].status, "completed")
        self.assertEqual(result.steps[1].status, "skipped")
        self.assertEqual(result.status, "completed")

    def test_v6_rejects_unsafe_live_execution(self) -> None:
        workflow = self.orchestrator.build("Receive a webhook and send an email")

        with self.assertRaises(ValueError):
            self.runtime.run(workflow, dry_run=False)

    def test_v6_orchestrator_execute(self) -> None:
        result = self.orchestrator.execute("Receive a webhook and send an email")

        self.assertEqual(result["status"], "completed")
        self.assertTrue(result["dry_run"])
        self.assertEqual(len(result["steps"]), 2)
        self.assertEqual(result["steps"][0]["status"], "completed")


if __name__ == "__main__":
    unittest.main()
