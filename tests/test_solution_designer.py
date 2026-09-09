from __future__ import annotations

import unittest
from unittest.mock import MagicMock

from core.solution_designer import AutonomousSolutionDesigner


class TestSolutionDesigner(unittest.TestCase):
    def test_design_builds_architecture(self) -> None:
        orchestrator = MagicMock()
        orchestrator.research.return_value = MagicMock(integrations=[{"name": "webhook"}], risks=[] , gaps=[])
        orchestrator.build_multi_project.return_value = {"workflows": [{"workflow_id": "wf-01", "provider": "n8n", "name": "Receive", "depends_on": [], "shared_inputs": [], "shared_outputs": ["wf-01.result"]}]}
        result = AutonomousSolutionDesigner(orchestrator).design("Receive a webhook")
        self.assertEqual(result.status, "ready_for_validation")
        self.assertEqual(len(result.architecture), 1)
        self.assertEqual(result.data_contracts[0]["outputs"], ["wf-01.result"])

    def test_blank_request_rejected(self) -> None:
        with self.assertRaises(ValueError):
            AutonomousSolutionDesigner(MagicMock()).design(" ")


if __name__ == "__main__":
    unittest.main()
