import unittest
from jarvis.orchestrator import Orchestrator
from jarvis.router import SkillRouter
from jarvis.planner import Planner
class TestOrchestrator(unittest.TestCase):
    def test_prepare(self):
        r=Orchestrator(SkillRouter(),Planner(SkillRouter())).prepare("build a website")
        self.assertTrue(r.verified); self.assertTrue(r.plan.steps)
if __name__=="__main__": unittest.main()
