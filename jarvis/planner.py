from dataclasses import dataclass
from .router import SkillRouter

@dataclass
class Plan:
    intent: str
    steps: list[str]

class Planner:
    def __init__(self, router: SkillRouter):
        self.router = router
    def build(self, request: str, skills: list[str], max_steps: int) -> Plan:
        steps = [f"Activate {s} skill" for s in skills]
        steps += ["Execute required tools", "Verify output", "Record useful result in memory"]
        return Plan(intent=request, steps=steps[:max_steps])
