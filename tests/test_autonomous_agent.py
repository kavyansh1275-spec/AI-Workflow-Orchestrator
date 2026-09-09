from __future__ import annotations

import unittest
from unittest.mock import MagicMock

from core.autonomous_agent import AutonomousAutomationAgent


class TestAutonomousAutomationAgent(unittest.TestCase):
    def test_safe_agent_completes_planning_pipeline(self) -> None:
        orchestrator = MagicMock()
        orchestrator.integration_intelligence.return_value = {"required_integrations": ["webhook", "email"]}
        orchestrator.decide.return_value = {"provider": "n8n", "confidence": 0.9}
        orchestrator.build_multi_project.return_value = {
            "project_id": "multi-test",
            "workflows": [{"workflow_id": "wf-01", "request": "Receive a webhook and send an email."}],
        }
        orchestrator.simulate.return_value = ["trigger: simulated", "email: simulated"]

        result = AutonomousAutomationAgent(orchestrator).plan("Receive a webhook and send an email.")

        self.assertEqual(result.status, "ready_for_review")
        self.assertEqual(result.next_action, "review")
        self.assertTrue(result.authorization_required)
        self.assertTrue(result.testing["passed"])
        self.assertEqual(len(result.stages), 7)
        self.assertEqual(result.deployment["status"], "blocked")
        orchestrator.simulate.assert_called_once()

    def test_live_authorization_never_bypasses_provider_gate(self) -> None:
        orchestrator = MagicMock()
        orchestrator.integration_intelligence.return_value = {}
        orchestrator.decide.return_value = {"provider": "n8n"}
        orchestrator.build_multi_project.return_value = {
            "project_id": "multi-test",
            "workflows": [{"workflow_id": "wf-01", "request": "Receive a webhook and send an email."}],
        }
        orchestrator.simulate.return_value = ["ok"]

        result = AutonomousAutomationAgent(orchestrator).plan("Receive a webhook and send an email.", authorize_live=True)

        self.assertEqual(result.deployment["status"], "ready")
        self.assertTrue(result.deployment["authorized"])
        self.assertEqual(result.next_action, "deploy_with_explicit_live_confirmation")

    def test_blank_request_rejected(self) -> None:
        with self.assertRaises(ValueError):
            AutonomousAutomationAgent(MagicMock()).plan("   ")


if __name__ == "__main__":
    unittest.main()
