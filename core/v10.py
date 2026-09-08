from __future__ import annotations

from typing import Any

from core.orchestrator import Orchestrator
from models.v10 import GateStatus, PipelineEvent, QualityGate, V10Run, V10Stage


class V10Engine:
    """Unified, deterministic end-to-end orchestration facade.

    V10 composes the capabilities built in V1-V9. External provider calls remain
    disabled unless a future credential-aware adapter is explicitly introduced.
    """

    def __init__(self, orchestrator: Orchestrator | None = None) -> None:
        self.orchestrator = orchestrator or Orchestrator()

    def _event(self, stage: V10Stage, status: str, message: str, **metadata: Any) -> PipelineEvent:
        return PipelineEvent(stage=stage, status=status, message=message, metadata=metadata)

    def run(self, request: str, environment: str = "staging", dry_run: bool = True) -> V10Run:
        request = request.strip()
        if not request:
            raise ValueError("request cannot be blank")
        if not dry_run:
            raise ValueError("V10 live execution is blocked until credential-aware provider adapters are implemented")

        events: list[PipelineEvent] = []
        gates: list[QualityGate] = []

        events.append(self._event(V10Stage.UNDERSTAND, "completed", "Request understood by the V5 decision engine."))
        decision = self.orchestrator.decide(request)
        events.append(self._event(V10Stage.DECIDE, "completed", "Provider and workflow strategy selected.", provider=decision.get("provider")))

        workflow = self.orchestrator.build(request)
        events.append(self._event(V10Stage.PLAN, "completed", "Provider-independent workflow plan created.", steps=len(workflow.steps)))

        self.orchestrator.validate(workflow)
        integrations = self.orchestrator.inspect_integrations(request)
        gates.append(QualityGate(name="workflow-structure", status=GateStatus.PASSED, message="Workflow structure and dependencies are valid."))
        gates.append(QualityGate(name="integrations", status=GateStatus.PASSED, message=f"All {len(integrations)} workflow capabilities are supported."))
        events.append(self._event(V10Stage.VALIDATE, "completed", "All V10 quality gates passed.", gate_count=len(gates)))

        generated = self.orchestrator.generate(request)
        events.append(self._event(V10Stage.GENERATE, "completed", "Provider-specific artifact generated in dry-run mode."))

        execution = self.orchestrator.execute(request, dry_run=True)
        events.append(self._event(V10Stage.EXECUTE, "completed", "Local runtime simulation completed safely."))

        release = self.orchestrator.release(request, environment=environment, dry_run=True)
        events.append(self._event(V10Stage.RELEASE, "completed", "Release plan created without external deployment."))

        supervision = self.orchestrator.supervise(request, execution=execution)
        events.append(self._event(V10Stage.SUPERVISE, "completed", "Autonomous health supervision completed."))

        confidence = float(decision.get("confidence", workflow.intent_confidence))
        return V10Run(
            request=request,
            status="completed",
            provider=workflow.provider,
            confidence=max(0.0, min(1.0, confidence)),
            dry_run=True,
            gates=gates,
            events=events,
            result={
                "decision": decision,
                "workflow": workflow.model_dump(),
                "integrations": integrations,
                "generated": generated,
                "execution": execution,
                "release": release,
                "supervision": supervision,
            },
        )
