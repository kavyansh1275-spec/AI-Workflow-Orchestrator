import unittest
from jarvis.business_intelligence_pipeline import BusinessIntelligencePipeline
class TestBusinessIntelligencePipeline(unittest.TestCase):
    def test_analyze(self):
        r=BusinessIntelligencePipeline().analyze(10000,6000,40,100,50,20,10,[{"revenue":10},{"revenue":11},{"revenue":9},{"revenue":100}]); self.assertEqual(r.kpis.profit,4000); self.assertIsNotNone(r.funnel)
    def test_partial_funnel(self):
        with self.assertRaises(ValueError): BusinessIntelligencePipeline().analyze(1,1,1,leads=10)
if __name__=="__main__": unittest.main()
