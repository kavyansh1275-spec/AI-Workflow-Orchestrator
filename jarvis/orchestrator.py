from __future__ import annotations
from dataclasses import dataclass
from .planner import Planner, Plan
from .router import SkillRouter
from .verification_engine import VerificationEngine

@dataclass(frozen=True)
class OrchestrationResult:
    request: str
    skills: tuple[str,...]
    plan: Plan
    verified: bool

class Orchestrator:
    """Coordinates routing, planning and bounded verification."""
    def __init__(self, router: SkillRouter, planner: Planner, max_steps: int = 12):
        self.router=router
        self.planner=planner
        self.max_steps=max(1,max_steps)
        self.verifier=VerificationEngine()

    def prepare(self, request: str) -> OrchestrationResult:
        skills=tuple(self.router.route(request)[:8])
        plan=self.planner.build(request,list(skills),self.max_steps)
        self.verifier.checks.clear()
        self.verifier.register("plan_has_steps",lambda: bool(plan.steps))
        passed=all(r.passed for r in self.verifier.verify())
        return OrchestrationResult(request,skills,plan,passed)
