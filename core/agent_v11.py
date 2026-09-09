from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class WorkflowStep:
    id: str
    app: str
    action: str
    role: str
    depends_on: list[str]


@dataclass(frozen=True)
class AgentPlan:
    goal: str
    provider: str
    confidence: float
    steps: list[WorkflowStep]
    missing_integrations: list[str]
    notes: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "goal": self.goal,
            "provider": self.provider,
            "confidence": self.confidence,
            "steps": [asdict(step) for step in self.steps],
            "missing_integrations": self.missing_integrations,
            "notes": self.notes,
        }


class WorkflowAgentV11:
    """Goal-to-workflow agent foundation for real provider adapters."""

    APP_PATTERNS = {
        "google forms": ("Google Forms", "receive submission", "trigger"),
        "form": ("Forms", "receive submission", "trigger"),
        "crm": ("CRM", "create or update contact", "action"),
        "notion": ("Notion", "create page", "action"),
        "clickup": ("ClickUp", "create task or document", "action"),
        "gmail": ("Gmail", "send email", "action"),
        "email": ("Email", "send email", "action"),
        "slack": ("Slack", "send message", "action"),
        "report": ("AI", "generate report", "transform"),
        "summar": ("AI", "summarize input", "transform"),
        "analy": ("AI", "analyze input", "transform"),
    }

    def build(self, request: str, preferred_provider: str | None = None) -> AgentPlan:
        text = request.strip()
        if not text:
            raise ValueError("Automation request cannot be blank")
        lower = text.lower()
        steps: list[WorkflowStep] = []
        missing: list[str] = []
        seen: set[str] = set()

        for key, (app, action, role) in self.APP_PATTERNS.items():
            if key in lower and app not in seen:
                step_id = f"step_{len(steps) + 1}"
                depends = [steps[-1].id] if steps else []
                steps.append(WorkflowStep(step_id, app, action, role, depends))
                seen.add(app)

        if any(w in lower for w in ("add", "save", "store", "create", "update")) and "CRM" not in seen:
            missing.append("CRM target")
        if any(w in lower for w in ("email", "mail", "follow-up", "follow up")) and "Email" not in seen and "Gmail" not in seen:
            missing.append("email provider")
        if any(w in lower for w in ("report", "summar", "analyz", "analyse")) and "AI" not in seen:
            steps.append(WorkflowStep(f"step_{len(steps)+1}", "AI", "analyze input", "transform", [steps[-1].id] if steps else []))
            seen.add("AI")

        if not steps:
            raise ValueError("No actionable workflow stages were detected")

        provider = preferred_provider or self._choose_provider(lower)
        confidence = min(0.95, 0.55 + 0.07 * len(steps) - 0.08 * len(missing))
        notes = ["V11 never stores credentials inside workflow plans."]
        if provider == "n8n":
            notes.append("n8n selected as the default provider because this repository already has an API client.")
        if missing:
            notes.append("Missing integrations must be configured before live deployment.")
        return AgentPlan(text, provider, round(max(confidence, 0.1), 2), steps, missing, notes)

    @staticmethod
    def _choose_provider(text: str) -> str:
        scores = {"n8n": 0, "make": 0, "zapier": 0}
        for provider in scores:
            if provider in text:
                scores[provider] += 3
        return max(scores, key=lambda name: (scores[name], name == "n8n"))

    @staticmethod
    def n8n_artifact(plan: AgentPlan) -> dict[str, Any]:
        nodes = []
        for index, step in enumerate(plan.steps):
            nodes.append({
                "id": step.id,
                "name": f"{step.app}: {step.action}",
                "type": "automation-agent.placeholder",
                "position": [index * 260, 0],
                "parameters": {"app": step.app, "action": step.action, "role": step.role},
            })
        connections = {}
        for index, step in enumerate(plan.steps[:-1]):
            connections[step.id] = {"main": [[{"node": plan.steps[index + 1].id, "type": "main", "index": 0}]]}
        return {
            "name": "AI Agent - Generated Workflow",
            "active": False,
            "settings": {},
            "nodes": nodes,
            "connections": connections,
            "meta": {"agent_version": "V11", "provider": "n8n", "confidence": plan.confidence},
        }
