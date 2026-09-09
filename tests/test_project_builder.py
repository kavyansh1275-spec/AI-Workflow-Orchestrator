import unittest

from core.project_builder import AutonomousProjectBuilder


class TestAutonomousProjectBuilder(unittest.TestCase):
    def test_builds_complete_safe_project(self) -> None:
        project = AutonomousProjectBuilder().build(
            "Create an automation that receives a webhook, analyzes it with AI, emails the result, and posts it to Slack."
        )
        self.assertTrue(project.project_id.startswith("project-"))
        self.assertTrue(project.workflow["steps"])
        self.assertIn(project.provider, {"n8n", "make", "zapier", "generic"})
        self.assertTrue(project.artifact)
        self.assertTrue(project.simulation)
        self.assertEqual(project.status, "ready_for_review")
        self.assertTrue(project.readiness["safe_to_simulate"])
        self.assertFalse(project.readiness["live_deployment"])

    def test_blank_request_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            AutonomousProjectBuilder().build("   ")


if __name__ == "__main__":
    unittest.main()
