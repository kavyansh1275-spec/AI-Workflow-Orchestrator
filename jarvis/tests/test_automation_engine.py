import unittest
from jarvis.automation_engine import AutomationEngine, AutomationTask
class TestAutomationEngine(unittest.TestCase):
    def test_register_and_run(self):
        e=AutomationEngine(); e.register("greet",lambda x:f"Hello {x}")
        r=e.run(AutomationTask("greet","greet"),"Kav")
        self.assertTrue(r.success); self.assertEqual(r.result,"Hello Kav")
    def test_disabled(self):
        r=AutomationEngine().run(AutomationTask("x","x",False))
        self.assertFalse(r.success)
    def test_missing(self):
        r=AutomationEngine().run(AutomationTask("x","x"))
        self.assertFalse(r.success)
    def test_bound(self):
        e=AutomationEngine(2); self.assertEqual(len(e.plan([AutomationTask("a","a")]*3)),2)
if __name__=="__main__": unittest.main()
