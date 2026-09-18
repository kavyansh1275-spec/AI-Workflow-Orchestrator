from __future__ import annotations
from dataclasses import dataclass
from .trigger_engine import TriggerEngine
from .automation_engine import AutomationEngine,AutomationRun

@dataclass(frozen=True)
class EventResult:
    event: str
    triggers: tuple[str,...]
    runs: tuple[AutomationRun,...]

class EventAutomationEngine:
    def __init__(self,max_tasks=12):
        self.triggers=TriggerEngine(); self.automation=AutomationEngine(max_tasks)
        self.routes:dict[str,tuple[tuple[str,str],...]]={}
    def register_trigger(self,name,predicate): self.triggers.register(name,predicate)
    def register_action(self,name,handler): self.automation.register(name,handler)
    def route(self,trigger_name,tasks): self.routes[trigger_name]=tuple(tasks)
    def handle(self,event: str) -> EventResult:
        matched=self.triggers.match(event); runs=[]
        for trigger in matched:
            runs.extend(self.automation.execute(list(self.routes.get(trigger,()))))
        return EventResult(event,matched,tuple(runs))
