import unittest
from jarvis.router import SkillRouter
from jarvis.planner import Planner

class TestCore(unittest.TestCase):
    def setUp(self):
        self.router = SkillRouter()
    def test_programming_route(self):
        self.assertIn("programming", self.router.route("debug my Python code"))
    def test_web_route(self):
        self.assertIn("web_development", self.router.route("build a React website"))
    def test_business_route(self):
        self.assertIn("marketing", self.router.route("create a marketing campaign"))
    def test_all_skills_registered(self):
        self.assertGreaterEqual(len(self.router.registry.list()), 31)
    def test_planner(self):
        plan = Planner(self.router).build("make a website", ["web_development"], 5)
        self.assertTrue(plan.steps)

if __name__ == "__main__":
    unittest.main()
