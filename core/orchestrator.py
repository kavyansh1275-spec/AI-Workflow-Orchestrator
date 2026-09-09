from __future__ import annotations

from core.autonomy import AutonomousManager
from core.brain import WorkflowBrain
from core.credentials import CredentialManager
from core.deployer import Deployer
from core.executor import Executor
from core.generator import WorkflowGenerator
from core.integration_manager import IntegrationManager
from core.live_deployment import LiveDeploymentManager
from core.operations import AutonomousOperations
from core.planner import Planner
from core.production import ProductionDeployer
from core.provider_lifecycle import ProviderLifecycleTester
from core.provider_optimizer import ProviderOptimizer
from core.provider_selector import ProviderSelector
from core.provider_smoke import ProviderSmokeTester
from core.runtime import WorkflowRuntime
from models.autonomy import WorkflowState
from models.workflow import WorkflowPlan


class Orchestrator:
    """V21 application service for solution-to-workflow compilation."""
    def __init__(self, planner=None, executor=None, provider_selector=None, deployer=None, generator=None, brain=None, provider_optimizer=None, runtime=None, integration_manager=None, production_deployer=None, autonomy_manager=None, credential_manager=None, operations=None, smoke_tester=None, lifecycle_tester=None, live_deployer=None) -> None:
        self.planner=planner or Planner(); self.executor=executor or Executor(); self.provider_selector=provider_selector or ProviderSelector(); self.deployer=deployer or Deployer(); self.generator=generator or WorkflowGenerator(); self.brain=brain or WorkflowBrain(self.planner.intelligence); self.provider_optimizer=provider_optimizer or ProviderOptimizer(); self.runtime=runtime or WorkflowRuntime(); self.integration_manager=integration_manager or IntegrationManager(); self.production_deployer=production_deployer or ProductionDeployer(self.generator,self.integration_manager); self.autonomy_manager=autonomy_manager or AutonomousManager(); self.credential_manager=credential_manager or CredentialManager(); self.operations=operations or AutonomousOperations(); self.smoke_tester=smoke_tester or ProviderSmokeTester(self.credential_manager); self.lifecycle_tester=lifecycle_tester or ProviderLifecycleTester(self.credential_manager,self.generator); self.live_deployer=live_deployer or LiveDeploymentManager(self.credential_manager,self.generator)
    def build(self, request):
        workflow=self.planner.plan(request); intent=self.brain.understand(request); provider,_=self.provider_optimizer.choose(request,intent); workflow=self.provider_selector.apply(workflow) if provider=="generic" else workflow.model_copy(update={"provider":provider}); self.validate(workflow); self.integration_manager.validate_workflow(workflow); return workflow
    def build_project(self, request, environment="staging"):
        from core.project_builder import AutonomousProjectBuilder; return AutonomousProjectBuilder(self).build(request,environment=environment).model_dump(mode="json")
    def build_multi_project(self, request, environment="staging"):
        from core.multi_project import AutonomousMultiProjectBuilder; return AutonomousMultiProjectBuilder(self).build(request,environment=environment).model_dump(mode="json")
    def run_agent(self, request, environment="staging", authorize_live=False):
        from core.autonomous_agent import AutonomousAutomationAgent; return AutonomousAutomationAgent(self).plan(request,environment=environment,authorize_live=authorize_live).model_dump(mode="json")
    def research(self, request):
        from core.research import AutonomousResearchEngine; return AutonomousResearchEngine(self).research(request).model_dump(mode="json")
    def design_solution(self, request):
        from core.solution_designer import AutonomousSolutionDesigner; return AutonomousSolutionDesigner(self).design(request).model_dump(mode="json")
    def validate_solution(self, request):
        from core.validator import AutonomousValidator; return AutonomousValidator(self).validate(request).model_dump(mode="json")
    def plan_deployment(self, request, environment="staging"):
        from core.deployment_planner import AutonomousDeploymentPlanner; return AutonomousDeploymentPlanner(self).plan(request,environment=environment).model_dump(mode="json")
    def control_loop(self, request, environment="staging"):
        from core.control_loop import AutonomousControlLoop; return AutonomousControlLoop(self).run(request,environment=environment).model_dump(mode="json")
    def build_workflow(self, request):
        from core.workflow_builder import AutonomousWorkflowBuilder; return AutonomousWorkflowBuilder(self).build(request).model_dump(mode="json")
    def integration_intelligence(self, request): return self.integration_manager.analyze_request(request)
    def validate(self, workflow: WorkflowPlan):
        if not workflow.steps: raise ValueError("workflow must contain at least one step")
        if workflow.steps[0].type != "trigger": raise ValueError("workflow must start with a trigger")
        ids=[s.id for s in workflow.steps]
        if len(ids)!=len(set(ids)): raise ValueError("workflow step IDs must be unique")
        known=set(ids)
        for step in workflow.steps:
            missing=set(step.depends_on)-known
            if missing: raise ValueError(f"workflow step {step.id} has unknown dependencies: {sorted(missing)}")
            if step.id in step.depends_on: raise ValueError(f"workflow step {step.id} cannot depend on itself")
    def analyze(self,request): return self.brain.understand(request).model_dump()
    def decide(self,request):
        decision=self.brain.decide(request); provider,reason=self.provider_optimizer.choose(request,self.brain.understand(request)); decision["provider"]=provider; decision["provider_reason"]=reason; return decision
    def inspect_integrations(self,request): return self.integration_manager.inspect(self.build(request))
    def list_integrations(self): return self.integration_manager.capabilities()
    def credential_status(self): return self.credential_manager.status()
    def provider_smoke_test(self,provider): return self.smoke_tester.run(provider).model_dump(mode="json")
    def provider_smoke_tests(self): return self.smoke_tester.run_all()
    def provider_lifecycle_test(self,request): return self.lifecycle_tester.create_and_cleanup(self.build(request)).model_dump(mode="json")
    def provider_lifecycle_readiness(self,request): return self.lifecycle_tester.validate(self.build(request))
    def live_deploy(self,request,live=False): return self.live_deployer.deploy(self.build(request),live=live).model_dump(mode="json")
    def live_deployment_readiness(self,request): return self.live_deployer.readiness(self.build(request))
    def live_rollback(self,deployment_id): return self.live_deployer.rollback(deployment_id).model_dump(mode="json")
    def simulate(self,request): return self.executor.run(self.build(request))
    def generate(self,request):
        workflow=self.build(request); return {"provider":workflow.provider,"name":workflow.name,"artifact":self.generator.generate(workflow),"dry_run":True}
    def execute(self,request,dry_run=True): return self.runtime.run(self.build(request),dry_run=dry_run).model_dump()
    def operate(self,request,dry_run=True): return self.operations.run(self.build(request),dry_run=dry_run).model_dump()
    def operation_history(self): return [r.model_dump() for r in self.operations.history()]
    def operation(self,operation_id): return self.operations.get(operation_id).model_dump()
    def classify_failure(self,error): return self.operations.classify_failure(error).value
    def deploy(self,request,dry_run=True): return self.deployer.deploy(self.build(request),dry_run=dry_run)
    def release(self,request,environment="staging",dry_run=True): return self.production_deployer.deploy(self.build(request),environment=environment,dry_run=dry_run).model_dump()
    def deployment_history(self): return [r.model_dump() for r in self.production_deployer.history()]
    def rollback(self,release_id): return self.production_deployer.rollback(release_id).model_dump()
    def deployment_health(self,release_id): return self.production_deployer.health(release_id)
    def supervise(self,request,execution=None,previous_state: WorkflowState|None=None): return self.autonomy_manager.supervise(self.build(request),execution=execution,previous_state=previous_state).model_dump()
