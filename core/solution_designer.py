from __future__ import annotations

import hashlib
from typing import Any

from core.orchestrator import Orchestrator
from models.solution import SolutionBlueprint


class AutonomousSolutionDesigner:
    """Convert research and project planning into a concrete automation architecture."""

    def __init__(self, orchestrator: Orchestrator | None = None) -> None:
        self.orchestrator = orchestrator or Orchestrator()

    def design(self, request: str) -> SolutionBlueprint:
        request = request.strip()
        if not request:
            raise ValueError("solution request cannot be blank")
        research = self.orchestrator.research(request)
        project = self.orchestrator.build_multi_project(request)
        workflows = project.get("workflows", [])
        architecture = []
        data_contracts = []
        for index, item in enumerate(workflows, start=1):
            architecture.append({"order": index, "workflow_id": item.get("workflow_id"), "provider": item.get("provider"), "role": item.get("name", f"Workflow {index}"), "depends_on": item.get("depends_on", [])})
            data_contracts.append({"workflow_id": item.get("workflow_id"), "inputs": item.get("shared_inputs", []), "outputs": item.get("shared_outputs", [])})
        return SolutionBlueprint(
            solution_id=f"solution-{hashlib.sha256(request.encode()).hexdigest()[:12]}",
            request=request,
            architecture=architecture,
            workflows=workflows,
            integrations=research.integrations,
            data_contracts=data_contracts,
            validation=["Trigger is defined", "Dependencies are explicit", "Integrations are mapped", "Safe simulation is required before deployment"],
            risks=research.risks,
            status="ready_for_validation" if not research.gaps else "blocked_by_research_gaps",
        )
