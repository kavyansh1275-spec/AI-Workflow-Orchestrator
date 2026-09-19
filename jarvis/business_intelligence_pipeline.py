from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable, Mapping
from .business_intelligence_engine import BusinessIntelligenceEngine, KPIReport, SalesFunnelReport, Anomaly

@dataclass(frozen=True)
class BusinessReport:
    kpis: KPIReport
    funnel: SalesFunnelReport | None
    anomalies: tuple[Anomaly, ...]
    summary: str

class BusinessIntelligencePipeline:
    """High-level V11 pipeline for turning business records into a bounded report."""
    def __init__(self): self.engine=BusinessIntelligenceEngine()
    def analyze(self,revenue,costs,orders=0,leads=None,qualified=None,opportunities=None,customers=None,records:Iterable[Mapping[str,float]]=(),field="revenue"):
        kpis=self.engine.kpis(revenue,costs,orders)
        funnel=None
        funnel_values=(leads,qualified,opportunities,customers)
        if any(v is not None for v in funnel_values):
            if not all(v is not None for v in funnel_values): raise ValueError("All funnel counts are required together")
            funnel=self.engine.sales_funnel(leads,qualified,opportunities,customers)
        anomalies=self.engine.detect_anomalies(records,field)
        return BusinessReport(kpis,funnel,anomalies,self.engine.executive_summary(kpis,funnel))
