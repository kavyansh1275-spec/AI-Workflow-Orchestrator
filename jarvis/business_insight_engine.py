from __future__ import annotations
from dataclasses import dataclass
from .business_intelligence_engine import KPIReport, SalesFunnelReport, Anomaly
from .business_forecast_engine import Forecast

@dataclass(frozen=True)
class BusinessInsight:
    area: str
    signal: str
    evidence: str
    action: str
    priority: str

class BusinessInsightEngine:
    """Turns measured business signals into transparent, non-prescriptive insights."""
    def analyze(self,kpi: KPIReport, funnel: SalesFunnelReport | None = None,
                anomalies: tuple[Anomaly,...] = (), forecast: Forecast | None = None) -> tuple[BusinessInsight,...]:
        out=[]
        if kpi.profit < 0:
            out.append(BusinessInsight("finance","negative profit",f"Profit is {kpi.profit:.2f}","Review major cost drivers and pricing assumptions","high"))
        elif kpi.margin < .10:
            out.append(BusinessInsight("finance","low margin",f"Margin is {kpi.margin:.1%}","Review costs, pricing and product mix","medium"))
        if funnel and funnel.conversion_rate < .05:
            out.append(BusinessInsight("sales","low conversion",f"Lead-to-customer conversion is {funnel.conversion_rate:.1%}","Inspect qualification, follow-up and offer friction","medium"))
        for anomaly in anomalies:
            out.append(BusinessInsight("risk","anomaly detected",f"{anomaly.field}={anomaly.value:.2f} vs baseline {anomaly.baseline:.2f}","Verify the underlying record before acting","high" if anomaly.severity=="high" else "medium"))
        if forecast and forecast.values and forecast.values[-1] < forecast.values[0]:
            out.append(BusinessInsight("forecast","declining baseline forecast",f"Forecast moves from {forecast.values[0]:.2f} to {forecast.values[-1]:.2f}","Review recent trend drivers and assumptions","medium"))
        return tuple(out)
