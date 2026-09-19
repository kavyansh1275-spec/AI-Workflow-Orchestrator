from dataclasses import dataclass
from .debug_engine import DebugEngine

@dataclass(frozen=True)
class SelfDebugResult:
    attempts: int
    fixed: bool
    debug: object = None

class SelfDebugger:
    def __init__(self, max_attempts=3):
        self.max_attempts = max(1, max_attempts)
        self.debugger = DebugEngine()

    def run_check(self, check):
        last = None
        for attempt in range(1, self.max_attempts + 1):
            try:
                if check():
                    return SelfDebugResult(attempt, True)
            except Exception as exc:
                last = self.debugger.propose_fix(self.debugger.diagnose(exc))
        return SelfDebugResult(self.max_attempts, False, last)
