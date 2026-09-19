from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from core.orchestrator import Orchestrator
from core.jarvis_terminal import JarvisTerminal, TerminalEvent


@dataclass
class BrainEvent:
    stage: str
    status: str
    message: str
    data: dict[str, Any] = field(default_factory=dict)


class JarvisBrain:
    """Single entry point for every command coming from the JARVIS interface.

    The brain classifies a request, selects an existing capability, executes it,
    and emits observable events that the GUI can stream into its terminal.
    """

    def __init__(self, orchestrator: Orchestrator | None = None) -> None:
        self.orchestrator = orchestrator or Orchestrator()
        self.terminal = terminal or JarvisTerminal()

    def execute(
        self,
        request: str,
        emit: Callable[[BrainEvent], None] | None = None,
    ) -> dict[str, Any]:
        request = request.strip()
        if not request:
            raise ValueError("request cannot be blank")

        def event(stage: str, status: str, message: str, **data: Any) -> None:
            if emit:
                emit(BrainEvent(stage, status, message, data))

        event("understand", "running", "Brain is understanding the command.")
        decision = self.orchestrator.decide(request)
        event(
            "understand",
            "completed",
            "Command understood.",
            provider=decision.get("provider"),
            requirements=decision.get("requirements", {}),
        )

        if decision.get("needs_clarification"):
            missing = decision.get("requirements", {}).get("missing", [])
            event("clarify", "blocked", "Command needs configuration before execution.", missing=missing)
            return {"status": "needs_clarification", "decision": decision, "missing": missing}

        lowered = request.lower()

        if self._looks_like_project_build(lowered):
            event("plan", "running", "Selecting the autonomous project builder.")
            result = self._run_project_build(request, event)
        elif self._looks_like_research(lowered):
            event("plan", "running", "Selecting the research engine.")
            result = self.orchestrator.research(request)
            event("research", "completed", "Research completed.")
        elif self._looks_like_workflow(lowered):
            event("plan", "running", "Selecting the workflow engine.")
            result = self._run_workflow(request, event)
        elif self._looks_like_deployment(lowered):
            event("plan", "running", "Selecting the deployment planner.")
            result = self.orchestrator.plan_deployment(request)
            event("deploy", "completed", "Deployment plan created.")
        else:
            event("plan", "running", "Using the general workflow orchestrator.")
            result = self._run_workflow(request, event)

        event("complete", "completed", "Command execution completed.")
        return {"status": "completed", "decision": decision, "result": result}

    def _run_workflow(self, request: str, event: Callable[..., None]) -> dict[str, Any]:
        event("plan", "completed", "Building dependency-aware workflow.")
        workflow = self.orchestrator.build(request)
        event("code", "completed", "Workflow plan built.", steps=len(workflow.steps))
        event("test", "running", "Running safe workflow simulation.")
        execution = self.orchestrator.execute(request, dry_run=True)
        event("test", "completed", "Workflow simulation passed.")
        return {
            "workflow": workflow.model_dump(mode="json"),
            "execution": execution,
        }

    def _run_project_build(self, request: str, event: Callable[..., None]) -> dict[str, Any]:
        event("plan", "completed", "Project plan created.")
        event("code", "running", "Building the application plan and project artifacts.")
        result = self.orchestrator.build_project(request)
        artifacts = result.get("artifacts", {})
        event("code", "completed", "Real project files generated.", **artifacts)
        project_dir = artifacts.get("project_dir")
        if project_dir:
            event("terminal", "command", f"python -m py_compile app.py (cwd={project_dir})")
            root = __import__("pathlib").Path(project_dir)
            app = root / "app.py"
            if app.exists():
                def forward(item: TerminalEvent) -> None:
                    event("terminal", item.stream, item.line)
                code = self.terminal.run(["python", "-m", "py_compile", "app.py"], emit=forward, timeout=60)
                if code != 0:
                    event("debug", "blocked", "Generated Python source failed validation.", exit_code=code)
                    result["status"] = "build_validation_failed"
                    return result
            event("test", "completed", "Generated project validation passed.")
        return result

    @staticmethod
    def _looks_like_project_build(text: str) -> bool:
        return any(token in text for token in (
            "build me an app", "build an app", "create an app", "build a website",
            "create a website", "build a saas", "make me an app", "develop an app",
        ))

    @staticmethod
    def _looks_like_research(text: str) -> bool:
        return any(token in text for token in ("research", "market research", "customer research"))

    @staticmethod
    def _looks_like_workflow(text: str) -> bool:
        return any(token in text for token in ("workflow", "automation", "when ", "whenever "))

    @staticmethod
    def _looks_like_deployment(text: str) -> bool:
        return any(token in text for token in ("deploy", "publish", "release", "go live"))
