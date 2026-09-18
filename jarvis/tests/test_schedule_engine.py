import unittest
from jarvis.schedule_engine import ScheduleEngine,ScheduledTask
class TestScheduleEngine(unittest.TestCase):
    def test_schedule(self):
        e=ScheduleEngine()
        tasks=[ScheduledTask("later","2026-01-02T10:00:00","b"),ScheduledTask("now","2026-01-01T10:00:00","a")]
        self.assertEqual(e.sort(tasks)[0].name,"now")
        self.assertFalse(e.validate(ScheduledTask("","bad","")))
if __name__=="__main__": unittest.main()
