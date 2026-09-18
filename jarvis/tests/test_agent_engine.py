import unittest
from jarvis.agent_engine import AgentEngine, Tool

class TestAgentEngine(unittest.TestCase):
    def setUp(self):
        self.agent = AgentEngine(max_steps=2)
        self.agent.register_tool(Tool("echo", "Returns input", lambda x: x))

    def test_plan(self):
        self.assertEqual(len(self.agent.plan("test task")), 5)

    def test_execute_and_verify(self):
        result = self.agent.execute("hello", [("echo", "one"), ("echo", "two")])
        self.assertTrue(result.success)
        self.assertEqual(len(result.steps), 2)

    def test_unknown_tool(self):
        result = self.agent.execute("hello", [("missing", "x")])
        self.assertFalse(result.success)
        self.assertEqual(result.stopped_reason, "unregistered_tool")

    def test_step_limit(self):
        result = self.agent.execute("hello", [("echo", "1"), ("echo", "2"), ("echo", "3")])
        self.assertFalse(result.success)
        self.assertEqual(result.stopped_reason, "step_limit")

if __name__ == "__main__":
    unittest.main()
