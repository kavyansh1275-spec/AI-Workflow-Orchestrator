import tempfile
import unittest
from pathlib import Path

from core.v10 import V10Engine


class RunExporterTests(unittest.TestCase):
    def test_completed_run_can_be_exported(self) -> None:
        engine = V10Engine()
        run = engine.run("Receive a webhook and send an email")

        with tempfile.TemporaryDirectory() as directory:
            path = engine.export(run, directory)
            self.assertTrue(Path(path).exists())
            self.assertEqual(Path(path).suffix, ".json")
            self.assertIn(run.run_id, Path(path).name)
            self.assertIn('"status": "completed"', Path(path).read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
