from __future__ import annotations

from core.executor import Executor
from core.planner import Planner
from models.workflow import WorkflowPlan


class Orchestrator:
    """V1 application service: request -> plan -> validation -> execution trace."""

    def __init__(self, planner: Planner | None = None, executor: Executor | None = None) -> None:
        self.planner = planner or Planner()
        self.executor = executor or Executor()

    def build(self, request: str) -> WorkflowPlan:
        workflow = self.planner.plan(request)
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
