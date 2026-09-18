import unittest
from jarvis.business_intelligence_engine import BusinessIntelligenceEngine

class TestBusinessIntelligenceEngine(unittest.TestCase):
    def setUp(self): self.e=BusinessIntelligenceEngine()
    def test_kpis(self):
        r=self.e.kpis(10000,6500,50)
        self.assertEqual(r.profit,3500); self.assertAlmostEqual(r.margin,.35); self.assertEqual(r.average_order_value,200)
    def test_funnel(self):
        r=self.e.sales_funnel(100,40,20,10)
        self.assertAlmostEqual(r.qualification_rate,.4); self.assertAlmostEqual(r.conversion_rate,.1)
    def test_anomaly(self):
        r=self.e.detect_anomalies([{"revenue":10},{"revenue":11},{"revenue":9},{"revenue":100}],"revenue",2)
        self.assertTrue(r)
    def test_growth_and_summary(self):
        self.assertAlmostEqual(self.e.growth_rate(100,120),.2)
        self.assertIn("Profit:",self.e.executive_summary(self.e.kpis(100,60,2)))
    def test_invalid_funnel(self):
        with self.assertRaises(ValueError): self.e.sales_funnel(10,20,1,1)

if __name__=="__main__": unittest.main()
