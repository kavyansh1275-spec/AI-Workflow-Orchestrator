import unittest
from jarvis.system_orchestrator import SystemOrchestrator
from jarvis.router import SkillRouter
from jarvis.planner import Planner
class TestSystemOrchestrator(unittest.TestCase):
    def test_system(self):
        s=SystemOrchestrator(SkillRouter(),Planner(SkillRouter())); s.register("x",lambda a:"ok")
        r=s.run("research AI",[("x","")])
        self.assertTrue(r.success); self.assertTrue(r.status.ready)
if __name__=="__main__": unittest.main()
