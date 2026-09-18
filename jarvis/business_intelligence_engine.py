from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable, Mapping

@dataclass(frozen=True)
class KPIReport:
    revenue: float
    costs: float
    profit: float
    margin: float
    orders: int
    average_order_value: float

@dataclass(frozen=True)
class SalesFunnelReport:
    leads: int
    qualified: int
    opportunities: int
    customers: int
    qualification_rate: float
    conversion_rate: float

@dataclass(frozen=True)
class Anomaly:
    field: str
    value: float
    baseline: float
    deviation: float
    severity: str

class BusinessIntelligenceEngine:
    """Dependency-free business analytics, KPI, funnel and anomaly engine."""

    def kpis(self, revenue: float, costs: float, orders: int = 0) -> KPIReport:
        revenue, costs = float(revenue), float(costs)
        if revenue < 0 or costs < 0 or orders < 0:
            raise ValueError("revenue, costs and orders must be non-negative")
        profit = revenue - costs
        margin = profit / revenue if revenue else 0.0
        aov = revenue / orders if orders else 0.0
        return KPIReport(revenue, costs, profit, margin, orders, aov)

    def sales_funnel(self, leads: int, qualified: int, opportunities: int, customers: int) -> SalesFunnelReport:
        values=(leads,qualified,opportunities,customers)
        if any(not isinstance(v,int) or v < 0 for v in values): raise ValueError("funnel counts must be non-negative integers")
        if not leads >= qualified >= opportunities >= customers:
            raise ValueError("funnel counts must decrease from leads to customers")
        return SalesFunnelReport(leads,qualified,opportunities,customers,
            qualified/leads if leads else 0.0, customers/leads if leads else 0.0)

    def detect_anomalies(self, records: Iterable[Mapping[str, float]], field: str, threshold: float = 2.0) -> tuple[Anomaly, ...]:
        rows=list(records)
        if not rows: return ()
        if threshold <= 0: raise ValueError("threshold must be positive")
        values=[float(r[field]) for r in rows if field in r]
        if len(values) < 2: return ()
        mean=sum(values)/len(values)
        variance=sum((x-mean)**2 for x in values)/len(values)
        std=variance**0.5
        if std == 0: return ()
        result=[]
        for value in values:
            deviation=abs(value-mean)/std
            if deviation >= threshold:
                result.append(Anomaly(field,value,mean,deviation,"high" if deviation >= threshold*1.5 else "medium"))
        return tuple(result)

    @staticmethod
    def growth_rate(previous: float, current: float) -> float:
        previous,current=float(previous),float(current)
        if previous == 0: return 0.0 if current == 0 else float("inf")
        return (current-previous)/abs(previous)

    @staticmethod
    def executive_summary(kpi: KPIReport, funnel: SalesFunnelReport | None = None) -> str:
        lines=[f"Revenue: {kpi.revenue:.2f}",f"Costs: {kpi.costs:.2f}",
               f"Profit: {kpi.profit:.2f}",f"Margin: {kpi.margin:.1%}",
               f"Orders: {kpi.orders}",f"Average order value: {kpi.average_order_value:.2f}"]
        if funnel: lines += [f"Leads: {funnel.leads}",f"Customer conversion: {funnel.conversion_rate:.1%}"]
        return "\n".join(lines)
