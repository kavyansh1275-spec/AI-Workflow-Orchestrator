from __future__ import annotations

from core.deployer import Deployer
from core.executor import Executor
from core.planner import Planner
from core.provider_selector import ProviderSelector
from models.workflow import WorkflowPlan


class Orchestrator:
    """V2 application service: request -> plan -> provider -> validation."""

    def __init__(
        self,
        planner: Planner | None = None,
        executor: Executor | None = None,
        provider_selector: ProviderSelector | None = None,
        deployer: Deployer | None = None,
    ) -> None:
        self.planner = planner or Planner()
        self.executor = executor or Executor()
        self.provider_selector = provider_selector or ProviderSelector()
        self.deployer = deployer or Deployer()

    def build(self, request: str) -> WorkflowPlan:
        workflow = self.planner.plan(request)
        workflow = self.provider_selector.apply(workflow)
        self.validate(workflow)
        return workflow

    def validate(self, workflow: WorkflowPlan) -> None:
        if not workflow.steps:
            raise ValueError("workflow must contain at least one step")
        if workflow.steps[0].type != "trigger":
            raise ValueError("workflow must start with a trigger")

        ids = [step.id for step in workflow.steps]
        if len(ids) != len(set(ids)):
            raise ValueError("workflow step IDs must be unique")

    def simulate(self, request: str) -> list[str]:
        workflow = self.build(request)
        return self.executor.run(workflow)

    def deploy(self, request: str, dry_run: bool = True) -> dict:
        workflow = self.build(request)
        return self.deployer.deploy(workflow, dry_run=dry_run)
