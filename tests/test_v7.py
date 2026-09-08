import unittest

from core.integration_manager import IntegrationManager
from core.orchestrator import Orchestrator
from models.workflow import WorkflowPlan, WorkflowStep


class V7IntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.orchestrator = Orchestrator()
        self.manager = IntegrationManager()

    def test_v7_catalog_contains_core_apps(self) -> None:
        capabilities = self.manager.capabilities()

        for app in ("gmail", "slack", "discord", "notion", "google_sheets", "airtable", "telegram"):
            self.assertIn(app, capabilities)

    def test_v7_build_validates_supported_workflow(self) -> None:
        workflow = self.orchestrator.build(
            "Receive a webhook, analyze it with AI, email the result, and post it to Slack"
        )

        inspection = self.orchestrator.integration_manager.inspect(workflow)

        self.assertEqual(len(inspection), len(workflow.steps))
        self.assertTrue(all(item["ready"] for item in inspection))

    def test_v7_rejects_unsupported_capability(self) -> None:
        workflow = WorkflowPlan(
            name="unsupported",
            request="test",
            description="test",
            steps=[
                WorkflowStep(
                    id="step_1",
                    type="trigger",
                    app="unknown_app",
                    action="receive",
                )
            ],
        )

        with self.assertRaises(ValueError):
            self.manager.validate_workflow(workflow)

    def test_v7_allows_configuration_placeholders(self) -> None:
        workflow = WorkflowPlan(
            name="placeholder",
            request="test",
            description="test",
            steps=[
                WorkflowStep(id="step_1", type="trigger", app="webhook", action="receive_request"),
                WorkflowStep(
                    id="step_2",
                    type="action",
                    app="gmail",
                    action="send_email",
                    config={"to": "configure_recipient", "body": "previous_step.output"},
                    depends_on=["step_1"],
                ),
            ],
        )

        self.manager.validate_workflow(workflow)

    def test_v7_inspect_integrations(self) -> None:
        inspection = self.orchestrator.inspect_integrations(
            "Receive a webhook and send the result to Gmail"
        )

        self.assertEqual(inspection[0]["app"], "webhook")
        self.assertEqual(inspection[-1]["app"], "gmail")
        self.assertTrue(inspection[-1]["ready"])


if __name__ == "__main__":
    unittest.main()
