import tempfile
import unittest
from pathlib import Path
from webdev.engine import WebDeveloper

class WebDeveloperTests(unittest.TestCase):
    def test_slug(self):
        self.assertEqual(WebDeveloper.slug("Hello World 2026"),"hello-world-2026")
    def test_generate_validate(self):
        with tempfile.TemporaryDirectory() as d:
            e=WebDeveloper(d); p=Path(d)/"demo"; p.mkdir()
            self.assertGreaterEqual(e.generate("Build a gym website",p)["files"],4)
            self.assertGreaterEqual(e.validate_files(p)["file_count"],4)
    def test_no_test_command(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d); (p/"index.html").write_text("<title>x</title>")
            self.assertTrue(WebDeveloper(d).run_tests(p)["passed"])

if __name__=="__main__": unittest.main()
