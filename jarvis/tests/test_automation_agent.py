import unittest
from jarvis.automation_agent import AutomationAgent
class TestAutomationAgent(unittest.TestCase):
    def test_agent(self):
        a=AutomationAgent(); a.register("executor",lambda x:"done")
        self.assertEqual(a.execute("run")[1],("executor","done"))
if __name__=="__main__": unittest.main()
