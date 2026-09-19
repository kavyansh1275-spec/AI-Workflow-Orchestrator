import unittest
from jarvis.multi_agent_engine import MultiAgentCoordinator

class TestMultiAgentCoordinator(unittest.TestCase):
    def test_delegate(self):
        c = MultiAgentCoordinator()
        messages = c.delegate("build project")
        self.assertEqual([m.receiver for m in messages], ["planner","builder","verifier"])

    def test_handlers(self):
        c = MultiAgentCoordinator()
        c.register_handler("planner", lambda goal: "plan ready")
        result = c.run("test")
        self.assertEqual(result[0].content, "plan ready")

    def test_unknown_role(self):
        c = MultiAgentCoordinator()
        with self.assertRaises(ValueError):
            c.register_handler("unknown", lambda x: x)

if __name__ == "__main__":
    unittest.main()
