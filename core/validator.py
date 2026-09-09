from __future__ import annotations

import hashlib
from typing import Any

from core.orchestrator import Orchestrator
from models.validation import ValidationResult


class AutonomousValidator:
    """Run deterministic quality gates across the planned automation."""

    def __init__(self, orchestrator: Orchestrator | None = None) -> None:
        self.orchestrator = orchestrator or Orchestrator()

    def validate(self, request: str) -> ValidationResult:
        request = request.strip()
        if not request:
            raise ValueError("validation request cannot be blank")
        solution = self.orchestrator.design_solution(request)
        checks: list[dict[str, Any]] = []
        failures: list[str] = []
        checks.append({"name": "solution_architecture", "passed": bool(solution.get("architecture"))})
        checks.append({"name": "workflow_count", "passed": bool(solution.get("workflows"))})
        checks.append({"name": "integration_mapping", "passed": all("name" in item for item in solution.get("integrations", []))})
        for check in checks:
            if not check["passed"]:
                failures.append(str(check["name"]))
        simulation_passed = False
        try:
            simulation = self.orchestrator.simulate(request)
            simulation_passed = bool(simulation)
        except Exception as exc:
            failures.append(f"simulation: {exc}")
        checks.append({"name": "safe_simulation", "passed": simulation_passed})
        score = round(sum(1 for item in checks if item["passed"]) / len(checks), 2)
        passed = not failures and score >= 0.75
        return ValidationResult(
            validation_id=f"validation-{hashlib.sha256(request.encode()).hexdigest()[:12]}",
            passed=passed,
            score=score,
            checks=checks,
            failures=failures,
            warnings=[] if passed else ["Resolve failed quality gates before live deployment."],
            status="passed" if passed else "blocked",
        )
