import unittest
from jarvis.agent_engine import AgentEngine, Tool
from jarvis.memory import Memory

class TestAgentEngine(unittest.TestCase):
    def setUp(self):
        self.memory = Memory()
        self.agent = AgentEngine(max_steps=2, memory=self.memory)
        self.agent.register_tool(Tool("echo", "Returns input", lambda x: x))

    def test_plan_without_memory(self):
        self.assertEqual(len(self.agent.plan("test task")), 5)

    def test_memory_aware_plan(self):
        self.memory.remember("build website", ["web_development"], "project", persist=False)
        plan = self.agent.plan("build website")
        self.assertIn("apply relevant memory context", plan)

    def test_execute_and_remember(self):
        result = self.agent.execute("hello", [("echo", "one"), ("echo", "two")])
        self.assertTrue(result.success)
        self.assertEqual(len(self.memory.recent()), 1)

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
