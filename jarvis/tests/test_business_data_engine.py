import unittest
from jarvis.business_data_engine import BusinessDataEngine
class TestBusinessDataEngine(unittest.TestCase):
    def test_normalize_and_series(self):
        e=BusinessDataEngine(); rows=e.normalize([{"Revenue":"100"},{"revenue":200},{"revenue":"bad"}])
        self.assertEqual(e.numeric_series(rows,"revenue"),[200.0])
    def test_trend(self):
        r=BusinessDataEngine().trend(["Jan","Feb","Mar"],[10,15,12])
        self.assertEqual(r[1].change,5); self.assertEqual(r[2].change,-3)
if __name__=="__main__": unittest.main()
