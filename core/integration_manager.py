from __future__ import annotations

from core.integration_intelligence import IntegrationIntelligence
from integrations.catalog import IntegrationCatalog
from models.workflow import WorkflowPlan


class IntegrationManager:
    """V7 capability validation plus V12 natural-language integration intelligence."""

    def __init__(
        self,
        catalog: IntegrationCatalog | None = None,
        intelligence: IntegrationIntelligence | None = None,
    ) -> None:
        self.catalog = catalog or IntegrationCatalog()
        self.intelligence = intelligence or IntegrationIntelligence(self.catalog)

    def validate_workflow(self, workflow: WorkflowPlan) -> None:
        for step in workflow.steps:
            spec = self.catalog.require(step.app, step.action)
            missing = [field for field in spec.required_fields if field not in step.config]
            missing = [field for field in missing if not str(step.config.get(field, "")).startswith("configure_")]
            if missing:
                raise ValueError(
                    f"integration {step.app}.{step.action} is missing required config: {missing}"
                )

    def inspect(self, workflow: WorkflowPlan) -> list[dict[str, object]]:
        self.validate_workflow(workflow)
        result: list[dict[str, object]] = []
        for step in workflow.steps:
            spec = self.catalog.require(step.app, step.action)
            result.append(
                {
                    "step_id": step.id,
                    "app": spec.app,
                    "action": spec.action,
                    "category": spec.category,
                    "ready": True,
                    "required_fields": list(spec.required_fields),
                }
            )
        return result

    def analyze_request(self, request: str) -> dict[str, object]:
        return self.intelligence.analyze(request)

    def capabilities(self) -> dict[str, list[str]]:
        result: dict[str, list[str]] = {}
        for capability in self.catalog.list_capabilities():
            app, action = capability.split(".", 1)
            result.setdefault(app, []).append(action)
        return result
