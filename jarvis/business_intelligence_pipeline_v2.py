from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable, Mapping
from .business_data_engine import BusinessDataEngine
from .business_decision_engine import BusinessDecisionEngine, DecisionItem
from .business_forecast_engine import BusinessForecastEngine, Forecast
from .business_insight_engine import BusinessInsight, BusinessInsightEngine
from .business_intelligence_engine import BusinessIntelligenceEngine, KPIReport, SalesFunnelReport

@dataclass(frozen=True)
class FullBusinessReport:
    kpis: KPIReport
    funnel: SalesFunnelReport | None
    forecast: Forecast | None
    insights: tuple[BusinessInsight,...]
    decisions: tuple[DecisionItem,...]

class BusinessIntelligencePipelineV2:
    """Complete V11 analysis pipeline: normalize, measure, forecast, explain, prioritize."""
    def __init__(self):
        self.data=BusinessDataEngine()
        self.bi=BusinessIntelligenceEngine()
        self.forecaster=BusinessForecastEngine()
        self.insights=BusinessInsightEngine()
        self.decisions=BusinessDecisionEngine()

    def analyze(self,revenue,costs,orders=0,leads=None,qualified=None,opportunities=None,customers=None,
                records:Iterable[Mapping[str,object]]=(), trend_values:Iterable[float]=(), forecast_horizon=3):
        normalized=self.data.normalize(records)
        kpi=self.bi.kpis(revenue,costs,orders)
        funnel=None
        vals=(leads,qualified,opportunities,customers)
        if any(v is not None for v in vals):
            if not all(v is not None for v in vals): raise ValueError("All funnel counts are required together")
            funnel=self.bi.sales_funnel(leads,qualified,opportunities,customers)
        revenue_rows=[r for r in normalized if "revenue" in r]
        anomalies=self.bi.detect_anomalies(revenue_rows,"revenue")
        series=[float(v) for v in trend_values]
        forecast=self.forecaster.moving_average(series,forecast_horizon) if series else None
        insights=self.insights.analyze(kpi,funnel,anomalies,forecast)
        return FullBusinessReport(kpi,funnel,forecast,insights,self.decisions.prioritize(insights))
