import unittest
from jarvis.business_intelligence_pipeline_v2 import BusinessIntelligencePipelineV2
class TestBusinessIntelligencePipelineV2(unittest.TestCase):
    def test_full_pipeline(self):
        r=BusinessIntelligencePipelineV2().analyze(100,120,10,100,20,10,2,
            [{"revenue":10},{"revenue":11},{"revenue":9},{"revenue":100}],[30,20,10],2)
        self.assertEqual(r.kpis.profit,-20); self.assertTrue(r.forecast); self.assertTrue(r.insights); self.assertEqual(r.decisions[0].priority,"high")
if __name__=="__main__": unittest.main()
