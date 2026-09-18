from dataclasses import dataclass, field

@dataclass(frozen=True)
class Skill:
    name: str
    description: str
    keywords: tuple[str, ...] = field(default_factory=tuple)
    capabilities: tuple[str, ...] = field(default_factory=tuple)
    def plan(self, task: str) -> str:
        return f"Use {self.name} to work on: {task}"
