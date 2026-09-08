import unittest

from core.orchestrator import Orchestrator


class OrchestratorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.orchestrator = Orchestrator()

    def test_form_ai_email_request(self) -> None:
        workflow = self.orchestrator.build(
            "Receive a form submission, analyze it with AI, and send the result to Gmail"
        )

        self.assertEqual(workflow.steps[0].type, "trigger")
        self.assertEqual(workflow.steps[0].app, "forms")
        self.assertEqual(workflow.steps[1].app, "ai")
        self.assertEqual(workflow.steps[2].app, "gmail")

    def test_webhook_slack_request(self) -> None:
        workflow = self.orchestrator.build("Receive a webhook and send a Slack message")

        self.assertEqual(workflow.steps[0].app, "webhook")
        self.assertEqual(workflow.steps[1].app, "slack")

    def test_sheets_request(self) -> None:
        workflow = self.orchestrator.build("When a form arrives, append it to Google Sheets")

        self.assertEqual(workflow.steps[-1].app, "google_sheets")
        self.assertEqual(workflow.steps[-1].action, "append_row")

    def test_empty_request_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self.orchestrator.build("   ")

    def test_simulation_returns_ordered_trace(self) -> None:
        trace = self.orchestrator.simulate("Receive a webhook and email the result")

        self.assertEqual(len(trace), 2)
        self.assertIn("step_1", trace[0])
        self.assertIn("webhook.receive_request", trace[0])
        self.assertIn("gmail.send_email", trace[1])


if __name__ == "__main__":
    unittest.main()
