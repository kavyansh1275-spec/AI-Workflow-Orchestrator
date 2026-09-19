from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True)
class ScheduledTask:
    name: str
    run_at: str
    action: str

class ScheduleEngine:
    """Stores validated schedules; execution remains explicit and bounded."""
    def validate(self, task: ScheduledTask) -> bool:
        try: datetime.fromisoformat(task.run_at)
        except ValueError: return False
        return bool(task.name.strip() and task.action.strip())

    def sort(self,tasks: list[ScheduledTask]) -> tuple[ScheduledTask,...]:
        valid=[t for t in tasks if self.validate(t)]
        return tuple(sorted(valid,key=lambda t:t.run_at))
