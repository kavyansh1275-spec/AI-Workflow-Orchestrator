from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class SystemStatus:
    core: bool
    memory: bool
    automation: bool
    verification: bool
    orchestration: bool

    @property
    def ready(self): return all((self.core,self.memory,self.automation,self.verification,self.orchestration))

    def summary(self):
        return "JARVIS: READY" if self.ready else "JARVIS: PARTIAL"
