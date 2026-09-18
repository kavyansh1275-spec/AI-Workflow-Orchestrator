import unittest
from jarvis.automation_integration import AutomationIntegration
class TestAutomationIntegration(unittest.TestCase):
    def test_end_to_end(self):
        a=AutomationIntegration(); a.register("email",lambda x:"email" in x,"notify",lambda x:"ok"); a.route("email",[("notify","")])
        r=a.handle("email received"); self.assertEqual(r.successful_actions,1)
if __name__=="__main__": unittest.main()
