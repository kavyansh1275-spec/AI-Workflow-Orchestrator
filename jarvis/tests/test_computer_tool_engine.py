import tempfile
import unittest
from pathlib import Path
from jarvis.computer_tool_engine import ComputerToolEngine

class TestComputerToolEngine(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "hello.txt").write_text("hello", encoding="utf-8")
        self.engine = ComputerToolEngine(self.root, dry_run=True)

    def tearDown(self):
        self.tmp.cleanup()

    def test_list_and_read(self):
        self.assertIn("hello.txt", self.engine.list_files().output)
        self.assertEqual(self.engine.read_file("hello.txt").output, "hello")

    def test_path_escape_blocked(self):
        with self.assertRaises(ValueError):
            self.engine.read_file("../outside.txt")

    def test_write_dry_run(self):
        result = self.engine.write_file("new.txt", "data")
        self.assertTrue(result.ok)
        self.assertFalse((self.root / "new.txt").exists())

    def test_command_allowlist(self):
        self.assertFalse(self.engine.run_command("del hello.txt").ok)
        self.assertTrue(self.engine.run_command("python --version").ok)

    def test_app_allowlist(self):
        self.assertTrue(self.engine.launch_app("notepad.exe").ok)
        self.assertFalse(self.engine.launch_app("unknown.exe").ok)

if __name__ == "__main__":
    unittest.main()
