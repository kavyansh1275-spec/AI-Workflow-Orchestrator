import tempfile
import unittest
from pathlib import Path

from jarvis.brain import JarvisBrain
from jarvis.config import Config


class TestBrain(unittest.TestCase):
    def test_brain_uses_local_provider(self):
        with tempfile.TemporaryDirectory() as tmp:
            config = Config(
                model="local-router",
                provider="local",
                dry_run=True,
                max_steps=6,
                memory_path=str(Path(tmp) / "memory.db"),
            )
            result = JarvisBrain(config).handle("build a Python automation tool")
        self.assertIn("AI: local/local-router", result)
        self.assertIn("Response:", result)
        self.assertIn("Python automation tool", result)


if __name__ == "__main__":
    unittest.main()
