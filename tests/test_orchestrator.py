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
        self.assertEqual(workflow.steps[1].depends_on, ["step_1"])
        self.assertEqual(workflow.steps[2].depends_on, ["step_2"])
        self.assertGreaterEqual(workflow.intent_confidence, 0.8)

    def test_webhook_slack_request(self) -> None:
        workflow = self.orchestrator.build("Receive a webhook and send a Slack message")

        self.assertEqual(workflow.steps[0].app, "webhook")
        self.assertEqual(workflow.steps[1].app, "slack")

    def test_sheets_request(self) -> None:
        workflow = self.orchestrator.build("When a form arrives, append it to Google Sheets")

        self.assertEqual(workflow.steps[-1].app, "google_sheets")
        self.assertEqual(workflow.steps[-1].action, "append_row")

    def test_v3_multi_action_request(self) -> None:
        workflow = self.orchestrator.build(
            "In n8n, receive a webhook, analyze it with AI, send an email, then post to Slack"
        )

        self.assertEqual(workflow.provider, "n8n")
        self.assertEqual(
            [(step.app, step.action) for step in workflow.steps],
            [
                ("webhook", "receive_request"),
                ("ai", "analyze"),
                ("gmail", "send_email"),
                ("slack", "send_message"),
            ],
        )

    def test_v3_condition_is_attached_to_actions(self) -> None:
        workflow = self.orchestrator.build(
            "Receive a form, if the score is high then send an email"
        )

        self.assertTrue(workflow.steps[-1].condition)
        self.assertIn("score is high", workflow.steps[-1].condition)

    def test_v3_analysis(self) -> None:
        intent = self.orchestrator.analyze(
            "Build this in Make: receive a webhook, analyze with AI, and send to Gmail"
        )

        self.assertEqual(intent["provider"], "make")
        self.assertEqual(intent["trigger"], "webhook.receive_request")
        self.assertEqual(intent["actions"], ["ai.analyze", "gmail.send_email"])
        self.assertGreaterEqual(intent["confidence"], 0.8)

    def test_v4_n8n_generation(self) -> None:
        result = self.orchestrator.generate(
            "Build this in n8n: receive a webhook, analyze it with AI, and send the result to Gmail"
        )

        self.assertEqual(result["provider"], "n8n")
        self.assertTrue(result["dry_run"])
        artifact = result["artifact"]
        self.assertEqual(artifact["format"], "n8n")
        self.assertEqual(len(artifact["nodes"]), 3)
        self.assertIn("step_1", artifact["connections"])

    def test_v4_make_generation(self) -> None:
        result = self.orchestrator.generate(
            "Build this in Make: receive a webhook and send the result to Gmail"
        )

        self.assertEqual(result["provider"], "make")
        self.assertEqual(result["artifact"]["format"], "make")
        self.assertEqual(len(result["artifact"]["modules"]), 2)
        self.assertEqual(result["artifact"]["modules"][1]["depends_on"], [1])

    def test_v4_zapier_generation(self) -> None:
        result = self.orchestrator.generate(
            "Build this in Zapier: receive a webhook, analyze with AI, and email the result"
        )

        self.assertEqual(result["provider"], "zapier")
        self.assertEqual(result["artifact"]["format"], "zapier")
        self.assertEqual([step["order"] for step in result["artifact"]["steps"]], [1, 2, 3])

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
