import unittest
from jarvis.business_insight_engine import BusinessInsightEngine
from jarvis.business_intelligence_engine import BusinessIntelligenceEngine
from jarvis.business_forecast_engine import BusinessForecastEngine
class TestBusinessInsightEngine(unittest.TestCase):
    def test_insights(self):
        e=BusinessIntelligenceEngine(); k=e.kpis(100,95,2)
        f=e.sales_funnel(100,40,10,2)
        forecast=BusinessForecastEngine().moving_average([30,20,10],2,2)
        r=BusinessInsightEngine().analyze(k,f,(),forecast)
        self.assertTrue(any(x.area=="finance" for x in r))
        self.assertTrue(any(x.area=="sales" for x in r))
if __name__=="__main__": unittest.main()
