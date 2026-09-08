from __future__ import annotations

from models.workflow import WorkflowPlan


class Executor:
    """Safe V1 simulator for validating workflow execution order.

    It does not call external services. It produces an execution trace that can
    later be handed to real provider adapters.
    """

    def run(self, workflow: WorkflowPlan) -> list[str]:
        if not workflow.steps:
            raise ValueError("workflow must contain at least one step")

        trace: list[str] = []
        for step in workflow.steps:
            trace.append(f"{step.id}: {step.type} -> {step.app}.{step.action}")
        return trace
