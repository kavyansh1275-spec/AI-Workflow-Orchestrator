from dataclasses import dataclass
from .config import Config
from .memory import Memory
from .planner import Planner
from .router import SkillRouter

@dataclass
class JarvisBrain:
    config: Config
    def __post_init__(self):
        self.memory = Memory()
        self.router = SkillRouter()
        self.planner = Planner(self.router)

    def handle(self, request: str) -> str:
        skills = self.router.route(request)
        plan = self.planner.build(request, skills, self.config.max_steps)
        self.memory.remember(request, skills)
        lines = [f"Intent: {plan.intent}", f"Skills: {', '.join(skills) or 'general'}", "Plan:"]
        lines.extend(f"{i}. {step}" for i, step in enumerate(plan.steps, 1))
        if self.config.dry_run:
            lines.append("Mode: dry-run (execution tools are not enabled yet).")
        return "\n".join(lines)
