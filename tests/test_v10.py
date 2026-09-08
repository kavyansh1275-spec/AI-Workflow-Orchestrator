import unittest

from core.v10 import V10Engine
from models.v10 import GateStatus, V10Stage


class V10EngineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = V10Engine()
        self.request = "Create an automation that receives a webhook, analyzes it with AI, emails the result, and posts it to Slack."

    def test_end_to_end_pipeline_completes(self) -> None:
        run = self.engine.run(self.request)
        self.assertEqual(run.status, "completed")
        self.assertTrue(run.dry_run)
        self.assertIsNotNone(run.provider)
        self.assertGreaterEqual(run.confidence, 0.0)
        self.assertTrue(all(g.status == GateStatus.PASSED for g in run.gates))

    def test_all_v10_stages_are_recorded(self) -> None:
        run = self.engine.run(self.request)
        stages = [event.stage for event in run.events]
        self.assertEqual(stages, list(V10Stage))

    def test_pipeline_contains_previous_version_outputs(self) -> None:
        run = self.engine.run(self.request)
        for key in ("decision", "workflow", "integrations", "generated", "execution", "release", "supervision"):
            self.assertIn(key, run.result)

    def test_live_execution_is_blocked(self) -> None:
        with self.assertRaises(ValueError):
            self.engine.run(self.request, dry_run=False)

    def test_blank_request_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self.engine.run("   ")


if __name__ == "__main__":
    unittest.main()
