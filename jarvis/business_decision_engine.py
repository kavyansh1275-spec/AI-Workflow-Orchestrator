from __future__ import annotations
from dataclasses import dataclass
from .business_insight_engine import BusinessInsight

@dataclass(frozen=True)
class DecisionItem:
    priority: str
    area: str
    action: str
    rationale: str

class BusinessDecisionEngine:
    """Orders operational follow-ups by urgency without claiming certainty."""
    ORDER={"high":0,"medium":1,"low":2}
    def prioritize(self, insights: tuple[BusinessInsight,...]) -> tuple[DecisionItem,...]:
        items=[DecisionItem(i.priority,i.area,i.action,i.evidence) for i in insights]
        return tuple(sorted(items,key=lambda x:(self.ORDER.get(x.priority,9),x.area)))
