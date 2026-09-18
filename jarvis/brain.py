from dataclasses import dataclass

from .ai_provider import AIProviderManager
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
        self.ai = AIProviderManager(self.config.provider, self.config.model)

    def _build_prompt(self, request: str, skills: list[str]) -> str:
        skill_text = ", ".join(skills) or "general reasoning"
        return (
            "You are JARVIS, a modular AI assistant. "
            "Answer the user's task clearly and safely. "
            f"Activated skills: {skill_text}. "
            f"User task: {request}"
        )

    def handle(self, request: str) -> str:
        skills = self.router.route(request)
        plan = self.planner.build(request, skills, self.config.max_steps)
        self.memory.remember(request, skills)

        response = self.ai.generate(self._build_prompt(request, skills))

        lines = [
            f"Intent: {plan.intent}",
            f"Skills: {', '.join(skills) or 'general'}",
            f"AI: {response.provider}/{response.model}",
            "Plan:",
        ]
        lines.extend(f"{i}. {step}" for i, step in enumerate(plan.steps, 1))
        lines.append("Response:")
        lines.append(response.text)
        if response.used_fallback:
            lines.append("Note: configured AI provider was unavailable; local fallback was used.")
        if self.config.dry_run:
            lines.append("Mode: dry-run (execution tools are not enabled yet).")
        return "
".join(lines)
