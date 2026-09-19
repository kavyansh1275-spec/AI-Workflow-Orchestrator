from __future__ import annotations
from dataclasses import dataclass
from .event_automation_engine import EventAutomationEngine
@dataclass(frozen=True)
class AutomationIntegrationResult:
    event:str; matched:tuple[str,...]; successful_actions:int; failed_actions:int
class AutomationIntegration:
    def __init__(self,max_tasks=12): self.engine=EventAutomationEngine(max_tasks)
    def register(self,trigger,predicate,action,handler):
        self.engine.register_trigger(trigger,predicate); self.engine.register_action(action,handler)
    def route(self,trigger,tasks): self.engine.route(trigger,tasks)
    def handle(self,event):
        r=self.engine.handle(event)
        return AutomationIntegrationResult(event,r.triggers,sum(x.success for x in r.runs),sum(not x.success for x in r.runs))
