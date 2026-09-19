import unittest
from jarvis.trigger_engine import TriggerEngine
class TestTriggerEngine(unittest.TestCase):
    def test_match(self):
        e=TriggerEngine(); e.register("email",lambda x:"email" in x.lower())
        self.assertEqual(e.match("New EMAIL received"),("email",))
if __name__=="__main__": unittest.main()
