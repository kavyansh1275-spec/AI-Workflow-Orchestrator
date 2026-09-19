import tempfile, unittest
from pathlib import Path
from jarvis.computer_agent import create_computer_agent

class TestComputerAgent(unittest.TestCase):
    def test_tools_registered_and_bounded(self):
        with tempfile.TemporaryDirectory() as d:
            agent = create_computer_agent(d, dry_run=True, max_steps=2)
            self.assertIn("list_files", agent.list_tools())
            result = agent.execute("inspect", [("list_files","."),("read_file","x"),("list_files",".")])
            self.assertFalse(result.success)
            self.assertEqual(result.stopped_reason, "step_limit")

if __name__ == "__main__": unittest.main()
