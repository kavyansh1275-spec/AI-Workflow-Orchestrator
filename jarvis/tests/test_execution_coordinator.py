import unittest
from jarvis.execution_coordinator import ExecutionCoordinator
from jarvis.orchestrator import Orchestrator
from jarvis.router import SkillRouter
from jarvis.planner import Planner
class TestExecutionCoordinator(unittest.TestCase):
    def test_execute(self):
        r=Orchestrator(SkillRouter(),Planner(SkillRouter()))
        c=ExecutionCoordinator(r); c.register("x",lambda a:"ok")
        result=c.execute("build a website",[("x","")])
        self.assertTrue(result.success); self.assertEqual(result.runs[0].result,"ok")
if __name__=="__main__": unittest.main()
