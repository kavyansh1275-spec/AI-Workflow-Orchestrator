import unittest

from jarvis.programming_engine import ProgrammingEngine


class TestProgrammingEngine(unittest.TestCase):
    def setUp(self):
        self.engine = ProgrammingEngine()

    def test_valid_python(self):
        result = self.engine.analyze_python(
            "import os\nclass App: pass\ndef run(): return 1\n"
        )
        self.assertTrue(result.valid)
        self.assertIn("os", result.imports)
        self.assertIn("App", result.classes)
        self.assertIn("run", result.functions)

    def test_invalid_python(self):
        result = self.engine.analyze_python("def broken(:\n    pass")
        self.assertFalse(result.valid)
        self.assertTrue(result.errors)


if __name__ == "__main__":
    unittest.main()
