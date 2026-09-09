from __future__ import annotations
import hashlib
from typing import Any
from models.workflow_repair import WorkflowRepairResult

class AutonomousWorkflowRepair:
    """Builds, tests and safely retries a workflow without mutating live providers."""
    def __init__(self, orchestrator: Any):
        self.orchestrator = orchestrator

    def run(self, request: str, max_attempts: int = 3) -> WorkflowRepairResult:
        request = request.strip()
        if not request:
            raise ValueError("workflow repair request cannot be blank")
        max_attempts = max(1, min(int(max_attempts), 5))
        tests: list[dict[str, Any]] = []
        repairs: list[dict[str, Any]] = []
        artifact: dict[str, Any] = {}
        passed = False
        for attempt in range(1, max_attempts + 1):
            try:
                built = self.orchestrator.build_workflow(request)
                artifact = built.get("workflow", {})
                validation = self.orchestrator.validate_solution(request)
                simulation = self.orchestrator.simulate(request)
                ok = bool(built.get("status") == "built" and validation.get("passed") and simulation)
                tests.append({"attempt": attempt, "validation": validation.get("status"), "simulation": bool(simulation), "passed": ok})
                if ok:
                    passed = True
                    break
                repairs.append({"attempt": attempt, "action": "recompile_and_revalidate", "safe": True})
            except Exception as exc:
                tests.append({"attempt": attempt, "passed": False, "error": str(exc)})
                repairs.append({"attempt": attempt, "action": "rebuild_after_failure", "safe": True, "error": str(exc)})
        return WorkflowRepairResult(repair_id=f"repair-{hashlib.sha256(request.encode()).hexdigest()[:12]}", request=request, attempts=len(tests), tests=tests, repairs=repairs, final_artifact=artifact, passed=passed, status="passed" if passed else "blocked")
