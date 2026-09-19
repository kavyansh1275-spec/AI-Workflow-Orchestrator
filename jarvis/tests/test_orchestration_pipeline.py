import unittest
from jarvis.orchestration_pipeline import OrchestrationPipeline
from jarvis.router import SkillRouter
from jarvis.planner import Planner
class TestOrchestrationPipeline(unittest.TestCase):
    def test_pipeline(self):
        r=OrchestrationPipeline(SkillRouter(),Planner(SkillRouter())).run("research AI")
        self.assertTrue(r.success); self.assertFalse(r.recovery_attempted)
if __name__=="__main__": unittest.main()
