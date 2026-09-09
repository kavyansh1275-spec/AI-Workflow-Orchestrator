from __future__ import annotations

import unittest
from unittest.mock import MagicMock

from core.research import AutonomousResearchEngine


class TestAutonomousResearchEngine(unittest.TestCase):
    def test_research_builds_actionable_brief(self) -> None:
        orchestrator = MagicMock()
        orchestrator.integration_intelligence.return_value = {
            "required_integrations": ["webhook", "email"],
            "missing_integrations": [],
        }
        orchestrator.decide.return_value = {
            "provider": "n8n",
            "confidence": 0.9,
            "provider_reason": "Best fit for multi-step automation.",
        }

        result = AutonomousResearchEngine(orchestrator).research(
            "Receive a webhook and analyze it with AI, then email the result."
        )

        self.assertTrue(result.research_id.startswith("research-"))
        self.assertEqual(result.readiness, "ready_for_design")
        self.assertGreaterEqual(len(result.requirements), 5)
        self.assertEqual(len(result.integrations), 2)
        self.assertEqual(result.provider_options[0]["provider"], "n8n")
        self.assertTrue(result.acceptance_criteria)
        self.assertTrue(result.risks)

    def test_missing_integrations_block_readiness(self) -> None:
        orchestrator = MagicMock()
        orchestrator.integration_intelligence.return_value = {
            "required_integrations": ["crm"],
            "missing_integrations": ["crm"],
        }
        orchestrator.decide.return_value = {"provider": "make", "confidence": 0.7}

        result = AutonomousResearchEngine(orchestrator).research("Capture leads in the CRM.")

        self.assertEqual(result.readiness, "blocked_by_integration_gaps")
        self.assertEqual(result.gaps, ["crm"])

    def test_blank_request_rejected(self) -> None:
        with self.assertRaises(ValueError):
            AutonomousResearchEngine(MagicMock()).research("   ")


if __name__ == "__main__":
    unittest.main()
