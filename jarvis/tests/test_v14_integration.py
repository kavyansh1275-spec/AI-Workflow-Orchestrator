import unittest
from jarvis.v14_integration import V14Integration
from jarvis.router import SkillRouter
from jarvis.planner import Planner
class TestV14Integration(unittest.TestCase):
    def test_version(self):
        v=V14Integration(SkillRouter(),Planner(SkillRouter()))
        self.assertEqual(v.VERSION,"14.0.0")
if __name__=="__main__": unittest.main()
