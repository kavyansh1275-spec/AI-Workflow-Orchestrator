from .system_orchestrator import SystemOrchestrator
class V14Integration:
    VERSION="14.0.0"
    def __init__(self,router,planner,max_steps=12):
        self.system=SystemOrchestrator(router,planner,max_steps)
    def register(self,name,handler): self.system.register(name,handler)
    def run(self,request,actions=()):
        return self.system.run(request,actions)
