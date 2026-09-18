from .skills.registry import SkillRegistry

class SkillRouter:
    def __init__(self):
        self.registry = SkillRegistry()
    def route(self, request: str) -> list[str]:
        text = request.lower()
        scores = {name: sum(1 for kw in skill.keywords if kw in text) for name, skill in self.registry.skills.items()}
        selected = [name for name, score in scores.items() if score > 0]
        return selected[:8]
