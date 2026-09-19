import unittest
from jarvis.business_forecast_engine import BusinessForecastEngine
class TestBusinessForecastEngine(unittest.TestCase):
    def test_forecast(self):
        r=BusinessForecastEngine().moving_average([10,20,30],2,2)
        self.assertEqual(r.values,(25.0,27.5))
if __name__=="__main__": unittest.main()
