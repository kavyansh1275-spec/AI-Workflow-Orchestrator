import unittest

from jarvis.brain import JarvisBrain
from jarvis.config import Config


class TestBrain(unittest.TestCase):
    def test_brain_uses_local_provider(self):
        config = Config(
            model="local-router",
            provider="local",
            dry_run=True,
            max_steps=6,
        )
        result = JarvisBrain(config).handle("build a Python automation tool")
        self.assertIn("AI: local/local-router", result)
        self.assertIn("Response:", result)
        self.assertIn("Python automation tool", result)


if __name__ == "__main__":
    unittest.main()
