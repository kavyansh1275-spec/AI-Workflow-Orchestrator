import unittest

from jarvis.web_dev_engine import WebDevelopmentEngine


class TestWebDevelopmentEngine(unittest.TestCase):
    def test_build_and_validate_landing_page(self):
        engine = WebDevelopmentEngine()
        project = engine.build_landing_page("My App", "Hello <world>")
        self.assertEqual(engine.validate_html(project.html), [])
        self.assertIn("&lt;world&gt;", project.html)


if __name__ == "__main__":
    unittest.main()
