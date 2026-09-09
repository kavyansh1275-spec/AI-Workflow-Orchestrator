from __future__ import annotations

import unittest

from core.multi_project import AutonomousMultiProjectBuilder


class TestAutonomousMultiProjectBuilder(unittest.TestCase):
    def test_builds_dependent_workflows(self) -> None:
        project = AutonomousMultiProjectBuilder().build(
            "Receive a webhook and analyze it with AI, then email the result, then notify Slack."
        )
        self.assertTrue(project.project_id.startswith("multi-"))
        self.assertGreaterEqual(len(project.workflows), 2)
        self.assertEqual(len(project.dependencies), len(project.workflows) - 1)
        self.assertEqual(project.workflows[1].depends_on, [project.workflows[0].workflow_id])
        self.assertTrue(project.shared_data["handoff"])
        self.assertTrue(project.monitoring["enabled"])
        self.assertTrue(project.recovery["enabled"])
        self.assertFalse(project.recovery["live_mutation"])
        self.assertEqual(project.status, "ready_for_review")

    def test_single_goal_still_produces_one_workflow(self) -> None:
        project = AutonomousMultiProjectBuilder().build(
            "Create an automation that receives a webhook and sends an email."
        )
        self.assertEqual(len(project.workflows), 1)
        self.assertEqual(project.dependencies, [])

    def test_blank_request_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            AutonomousMultiProjectBuilder().build("   ")


if __name__ == "__main__":
    unittest.main()
