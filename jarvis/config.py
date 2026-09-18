from dataclasses import dataclass
import os

@dataclass(frozen=True)
class Config:
    model: str
    dry_run: bool
    max_steps: int


def load_config() -> Config:
    return Config(
        model=os.getenv("JARVIS_MODEL", "gemini"),
        dry_run=os.getenv("JARVIS_DRY_RUN", "true").lower() != "false",
        max_steps=int(os.getenv("JARVIS_MAX_STEPS", "12")),
    )
