import unittest
from jarvis.business_intelligence_agent import BusinessIntelligenceAgent
class TestBusinessIntelligenceAgent(unittest.TestCase):
    def test_plan_and_handler(self):
        a=BusinessIntelligenceAgent(max_tasks=2); a.register("analyst",lambda x:"ok")
        self.assertEqual(a.execute("analyze")[0],("analyst","ok"))
        self.assertEqual(len(a.plan("analyze")),2)
    def test_bad_role(self):
        with self.assertRaises(ValueError): BusinessIntelligenceAgent().register("unknown",lambda x:x)
if __name__=="__main__": unittest.main()
