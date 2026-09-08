from __future__ import annotations

import re

from core.intelligence import WorkflowIntelligence
from models.workflow import WorkflowPlan, WorkflowStep


class Planner:
    """Convert normalized V3 intent into a dependency-aware workflow plan."""

    def __init__(self, intelligence: WorkflowIntelligence | None = None) -> None:
        self.intelligence = intelligence or WorkflowIntelligence()

    def plan(self, request: str) -> WorkflowPlan:
        intent = self.intelligence.analyze(request)
        steps: list[WorkflowStep] = [
            WorkflowStep(
                id="step_1",
                type="trigger",
                app=intent.trigger.split(".", 1)[0],
                action=intent.trigger.split(".", 1)[1],
            )
        ]

        for index, action in enumerate(intent.actions, start=2):
            app, operation = action.split(".", 1)
            config = {"input": "previous_step.output"}
            if action == "gmail.send_email":
                config = {"to": "configure_recipient", "body": "previous_step.output"}
            elif action == "slack.send_message":
                config = {"channel": "configure_channel", "message": "previous_step.output"}
            elif action == "google_sheets.append_row":
                config = {"values": "previous_step.output"}
            elif action == "notion.create_page":
                config = {"title": "configure_title", "content": "previous_step.output"}
            elif action == "discord.send_message":
                config = {"channel": "configure_channel", "message": "previous_step.output"}

            condition = intent.conditions[0] if intent.conditions else None
            steps.append(
                WorkflowStep(
                    id=f"step_{index}",
                    type="action",
                    app=app,
                    action=operation,
                    config=config,
                    depends_on=[steps[-1].id],
                    condition=condition,
                )
            )

        name_words = re.sub(r"[^a-zA-Z0-9 ]", " ", request).split()[:6]
        name = " ".join(name_words).title() or "Untitled Workflow"

        return WorkflowPlan(
            name=name,
            request=request,
            description=f"V3 workflow plan generated from: {request}",
            steps=steps,
            provider=intent.provider,
            intent_confidence=intent.confidence,
        )
