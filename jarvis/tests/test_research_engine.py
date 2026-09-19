import unittest

from jarvis.research_engine import ResearchEngine


class TestResearchEngine(unittest.TestCase):
    def test_rejects_non_http_urls(self):
        with self.assertRaises(ValueError):
            ResearchEngine().fetch("file:///etc/passwd")


if __name__ == "__main__":
    unittest.main()
