import unittest
from jarvis.automation_state import AutomationState
class TestAutomationState(unittest.TestCase):
    def test_state(self):
        s=AutomationState(); s.record("a",False); self.assertTrue(s.can_retry("a")); s.record("a",True); self.assertFalse(s.can_retry("a"))
if __name__=="__main__": unittest.main()
