import unittest
from jarvis.workflow_engine import Workflow,WorkflowEngine
class TestWorkflowEngine(unittest.TestCase):
    def test_workflow(self):
        e=WorkflowEngine(); e.register("a",lambda x:"ok"); e.register("b",lambda x:x.upper())
        r=e.run(Workflow("demo",(("a",""),("b","done"))))
        self.assertTrue(r.success); self.assertEqual(r.runs[1].result,"DONE")
if __name__=="__main__": unittest.main()
