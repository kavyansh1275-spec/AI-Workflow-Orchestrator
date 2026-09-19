import os
import unittest
from unittest.mock import patch

from jarvis.ai_provider import AIProviderManager, LocalProvider


class TestAIProvider(unittest.TestCase):
    def test_local_provider_is_dependency_free(self):
        result = LocalProvider().generate("build a website")
        self.assertEqual(result.provider, "local")
        self.assertIn("build a website", result.text)

    def test_unknown_provider_falls_back(self):
        result = AIProviderManager("unknown").generate("test task")
        self.assertTrue(result.used_fallback)
        self.assertEqual(result.provider, "local")

    def test_gemini_without_key_falls_back(self):
        with patch.dict(os.environ, {}, clear=True):
            result = AIProviderManager("gemini").generate("test task")
        self.assertTrue(result.used_fallback)
        self.assertEqual(result.provider, "local")


if __name__ == "__main__":
    unittest.main()
