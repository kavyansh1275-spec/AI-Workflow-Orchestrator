from __future__ import annotations

from core.autonomy import AutonomousManager
from core.brain import WorkflowBrain
from core.credentials import CredentialManager
from core.deployer import Deployer
from core.executor import Executor
from core.generator import WorkflowGenerator
from core.integration_manager import IntegrationManager
from core.operations import AutonomousOperations
from core.planner import Planner
from core.production import ProductionDeployer
from core.provider_optimizer import ProviderOptimizer
from core.provider_selector import ProviderSelector
from core.runtime import WorkflowRuntime
from models.autonomy import WorkflowState
from models.workflow import WorkflowPlan


class Orchestrator:
    """V9/V10 application service with autonomous operations management."""

    def __init__(self, planner: Planner | None = None, executor: Executor | None = None,
                 provider_selector: ProviderSelector | None = None, deployer: Deployer | None = None,
                 generator: WorkflowGenerator | None = None, brain: WorkflowBrain | None = None,
                 provider_optimizer: ProviderOptimizer | None = None, runtime: WorkflowRuntime | None = None,
                 integration_manager: IntegrationManager | None = None,
                 production_deployer: ProductionDeployer | None = None,
                 autonomy_manager: AutonomousManager | None = None,
                 credential_manager: CredentialManager | None = None,
                 operations: AutonomousOperations | None = None) -> None:
        self.planner = planner or Planner()
        self.executor = executor or Executor()
        self.provider_selector = provider_selector or ProviderSelector()
        self.deployer = deployer or Deployer()
        self.generator = generator or WorkflowGenerator()
        self.brain = brain or WorkflowBrain(self.planner.intelligence)
        self.provider_optimizer = provider_optimizer or ProviderOptimizer()
        self.runtime = runtime or WorkflowRuntime()
        self.integration_manager = integration_manager or IntegrationManager()
        self.production_deployer = production_deployer or ProductionDeployer(self.generator, self.integration_manager)
        self.autonomy_manager = autonomy_manager or AutonomousManager()
        self.credential_manager = credential_manager or CredentialManager()
        self.operations = operations or AutonomousOperations()

    def build(self, request: str) -> WorkflowPlan:
        workflow = self.planner.plan(request)
        intent = self.brain.understand(request)
        provider, _ = self.provider_optimizer.choose(request, intent)
        workflow = self.provider_selector.apply(workflow) if provider == "generic" else workflow.model_copy(update={"provider": provider})
        self.validate(workflow)
        self.integration_manager.validate_workflow(workflow)
        return workflow

    def validate(self, workflow: WorkflowPlan) -> None:
        if not workflow.steps:
            raise ValueError("workflow must contain at least one step")
        if workflow.steps[0].type != "trigger":
            raise ValueError("workflow must start with a trigger")
        ids = [step.id for step in workflow.steps]
        if len(ids) != len(set(ids)):
            raise ValueError("workflow step IDs must be unique")
        known_ids = set(ids)
        for step in workflow.steps:
            missing = set(step.depends_on) - known_ids
            if missing:
                raise ValueError(f"workflow step {step.id} has unknown dependencies: {sorted(missing)}")
            if step.id in step.depends_on:
                raise ValueError(f"workflow step {step.id} cannot depend on itself")

    def analyze(self, request: str) -> dict:
        return self.brain.understand(request).model_dump()

    def decide(self, request: str) -> dict:
        decision = self.brain.decide(request)
        provider, reason = self.provider_optimizer.choose(request, self.brain.understand(request))
        decision["provider"] = provider
        decision["provider_reason"] = reason
        return decision

    def inspect_integrations(self, request: str) -> list[dict[str, object]]:
        return self.integration_manager.inspect(self.build(request))

    def list_integrations(self) -> dict[str, list[str]]:
        return self.integration_manager.capabilities()

    def credential_status(self) -> dict[str, dict[str, str | None]]:
        return self.credential_manager.status()

    def simulate(self, request: str) -> list[str]:
        return self.executor.run(self.build(request))

    def generate(self, request: str) -> dict:
        workflow = self.build(request)
        return {"provider": workflow.provider, "name": workflow.name, "artifact": self.generator.generate(workflow), "dry_run": True}

    def execute(self, request: str, dry_run: bool = True) -> dict:
        return self.runtime.run(self.build(request), dry_run=dry_run).model_dump()

    def operate(self, request: str, dry_run: bool = True) -> dict:
        """Plan and safely operate a workflow with retry and recovery supervision."""
        return self.operations.run(self.build(request), dry_run=dry_run).model_dump()

    def operation_history(self) -> list[dict]:
        return [report.model_dump() for report in self.operations.history()]

    def operation(self, operation_id: str) -> dict:
        return self.operations.get(operation_id).model_dump()

    def classify_failure(self, error: str) -> str:
        return self.operations.classify_failure(error).value

    def deploy(self, request: str, dry_run: bool = True) -> dict:
        return self.deployer.deploy(self.build(request), dry_run=dry_run)

    def release(self, request: str, environment: str = "staging", dry_run: bool = True) -> dict:
        return self.production_deployer.deploy(self.build(request), environment=environment, dry_run=dry_run).model_dump()

    def deployment_history(self) -> list[dict]:
        return [record.model_dump() for record in self.production_deployer.history()]

    def rollback(self, release_id: str) -> dict:
        return self.production_deployer.rollback(release_id).model_dump()

    def deployment_health(self, release_id: str) -> dict[str, object]:
        return self.production_deployer.health(release_id)

    def supervise(self, request: str, execution: dict | None = None, previous_state: WorkflowState | None = None) -> dict:
        return self.autonomy_manager.supervise(self.build(request), execution=execution, previous_state=previous_state).model_dump()
