from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Config:
    model: str
    provider: str
    dry_run: bool
    max_steps: int
    memory_path: str


def load_config() -> Config:
    return Config(
        model=os.getenv("JARVIS_MODEL", "gemini-3.6-flash"),
        provider=os.getenv("JARVIS_PROVIDER", "gemini"),
        dry_run=os.getenv("JARVIS_DRY_RUN", "true").lower() != "false",
        max_steps=max(1, int(os.getenv("JARVIS_MAX_STEPS", "12"))),
        memory_path=os.getenv("JARVIS_MEMORY_PATH", "jarvis_memory.db"),
    )
