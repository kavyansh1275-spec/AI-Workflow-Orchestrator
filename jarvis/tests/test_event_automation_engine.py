import unittest
from jarvis.event_automation_engine import EventAutomationEngine
class TestEventAutomationEngine(unittest.TestCase):
    def test_event_flow(self):
        e=EventAutomationEngine(); e.register_trigger("email",lambda x:"email" in x.lower())
        e.register_action("notify",lambda x:"sent"); e.route("email",[("notify","")])
        r=e.handle("Email arrived"); self.assertEqual(r.triggers,("email",)); self.assertTrue(r.runs[0].success)
if __name__=="__main__": unittest.main()
