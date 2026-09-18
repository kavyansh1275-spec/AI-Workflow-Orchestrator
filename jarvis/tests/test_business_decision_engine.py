import unittest
from jarvis.business_decision_engine import BusinessDecisionEngine
from jarvis.business_insight_engine import BusinessInsight
class TestBusinessDecisionEngine(unittest.TestCase):
    def test_priority(self):
        x=(BusinessInsight("sales","x","e","a","medium"),BusinessInsight("finance","x","e","b","high"))
        r=BusinessDecisionEngine().prioritize(x)
        self.assertEqual(r[0].priority,"high")
if __name__=="__main__": unittest.main()
