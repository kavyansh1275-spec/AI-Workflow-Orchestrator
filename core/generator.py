from __future__ import annotations

from typing import Any

from core.provider_intelligence import ProviderIntelligence
from models.workflow import WorkflowPlan


class WorkflowGenerator:
    """Generate provider-specific workflow artifacts with native mappings."""

    SUPPORTED_PROVIDERS = {"n8n", "make", "zapier", "generic"}

    _N8N_NODE_TYPES = {
        "webhook": "n8n-nodes-base.webhook",
        "schedule": "n8n-nodes-base.scheduleTrigger",
        "form": "n8n-nodes-base.formTrigger",
        "gmail": "n8n-nodes-base.gmail",
        "slack": "n8n-nodes-base.slack",
        "discord": "n8n-nodes-base.discord",
        "notion": "n8n-nodes-base.notion",
        "google_sheets": "n8n-nodes-base.googleSheets",
        "airtable": "n8n-nodes-base.airtable",
        "telegram": "n8n-nodes-base.telegram",
        "http": "n8n-nodes-base.httpRequest",
        "ai": "@n8n/n8n-nodes-langchain.openAi",
    }

    def __init__(self, intelligence: ProviderIntelligence | None = None) -> None:
        self.intelligence = intelligence or ProviderIntelligence()

    def generate(self, workflow: WorkflowPlan) -> dict[str, Any]:
        provider = workflow.provider.lower()
        if provider not in self.SUPPORTED_PROVIDERS:
            raise ValueError(f"unsupported workflow provider: {workflow.provider}")
        if provider == "n8n":
            return self._n8n(workflow)
        if provider == "make":
            return self._make(workflow)
        if provider == "zapier":
            return self._zapier(workflow)
        return self._generic(workflow)

    def _native_steps(self, workflow: WorkflowPlan) -> list[dict[str, Any]]:
        return self.intelligence.enrich(
            workflow.provider,
            [
                {
                    "id": step.id,
                    "app": step.app,
                    "action": step.action,
                    "config": step.config,
                    "depends_on": step.depends_on,
                    "condition": step.condition,
                }
                for step in workflow.steps
            ],
        )

    def _n8n(self, workflow: WorkflowPlan) -> dict[str, Any]:
        nodes = []
        enriched = self._native_steps(workflow)
        for index, (step, native) in enumerate(zip(workflow.steps, enriched, strict=True)):
            nodes.append(
                {
                    "id": step.id,
                    "name": f"{step.app}: {step.action}",
                    "type": native["provider_native"] or self._n8n_type(step),
                    "typeVersion": self._n8n_type_version(step),
                    "position": [index * 240, 0],
                    "parameters": step.config,
                    "_mapping": {
                        "confidence": native["mapping_confidence"],
                        "notes": native["mapping_notes"],
                    },
                }
            )

        connections: dict[str, list[str]] = {}
        for step in workflow.steps:
            for dependency in step.depends_on:
                connections.setdefault(dependency, []).append(step.id)

        return {
            "format": "n8n",
            "name": workflow.name,
            "active": False,
            "nodes": nodes,
            "connections": connections,
        }

    def _make(self, workflow: WorkflowPlan) -> dict[str, Any]:
        modules = []
        for index, native in enumerate(self._native_steps(workflow), start=1):
            modules.append(
                {
                    "id": index,
                    "app": native["app"],
                    "action": native["action"],
                    "native_module": native["provider_native"],
                    "parameters": native["config"],
                    "depends_on": [self._step_number(workflow, item) for item in native["depends_on"]],
                    "condition": native["condition"],
                    "mapping_confidence": native["mapping_confidence"],
                }
            )
        return {"format": "make", "name": workflow.name, "modules": modules}

    def _zapier(self, workflow: WorkflowPlan) -> dict[str, Any]:
        steps = []
        for index, native in enumerate(self._native_steps(workflow), start=1):
            steps.append(
                {
                    "order": index,
                    "app": native["app"],
                    "event": native["action"],
                    "action_id": native["provider_native"] or None,
                    "config": native["config"],
                    "depends_on": native["depends_on"],
                    "condition": native["condition"],
                    "mapping_confidence": native["mapping_confidence"],
                }
            )
        return {"format": "zapier", "name": workflow.name, "steps": steps}

    def _generic(self, workflow: WorkflowPlan) -> dict[str, Any]:
        return {"format": "generic", "name": workflow.name, "steps": [step.model_dump() for step in workflow.steps]}

    @staticmethod
    def _step_number(workflow: WorkflowPlan, step_id: str) -> int:
        for index, step in enumerate(workflow.steps, start=1):
            if step.id == step_id:
                return index
        raise ValueError(f"unknown dependency: {step_id}")

    @classmethod
    def _n8n_type(cls, step: Any) -> str:
        return cls._N8N_NODE_TYPES.get(step.app, f"n8n-nodes-base.{step.app}")

    @staticmethod
    def _n8n_type_version(step: Any) -> int:
        return 1
