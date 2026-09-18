import unittest
from jarvis.condition_engine import Condition,ConditionEngine
class TestConditionEngine(unittest.TestCase):
    def test_branch(self):
        e=ConditionEngine()
        c=(Condition("high",lambda x:x>10),Condition("low",lambda x:x<=10))
        self.assertEqual(e.branch(c,20),"high"); self.assertEqual(e.branch(c,5),"low")
if __name__=="__main__": unittest.main()
