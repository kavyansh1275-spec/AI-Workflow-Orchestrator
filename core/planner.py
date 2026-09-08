from __future__ import annotations

import re

from models.workflow import WorkflowPlan, WorkflowStep


class Planner:
    """Convert common natural-language automation requests into a V1 plan.

    V1 intentionally uses deterministic rules rather than an external LLM so the
    foundation is testable without API keys. An AI planner can replace this class later.
    """

    @staticmethod
    def _contains_any(text: str, phrases: tuple[str, ...]) -> bool:
        """Return True when a phrase appears as a complete word/phrase."""
        return any(re.search(rf"(?<![a-z0-9]){re.escape(phrase)}(?![a-z0-9])", text) for phrase in phrases)

    def plan(self, request: str) -> WorkflowPlan:
        request = request.strip()
        if not request:
            raise ValueError("request cannot be empty")

        lowered = request.lower()
        steps: list[WorkflowStep] = []

        if self._contains_any(lowered, ("form", "forms", "form submission")):
            steps.append(
                WorkflowStep(
                    id="step_1",
                    type="trigger",
                    app="forms",
                    action="receive_submission",
                )
            )
        elif self._contains_any(lowered, ("webhook", "http request")):
            steps.append(
                WorkflowStep(
                    id="step_1",
                    type="trigger",
                    app="webhook",
                    action="receive_request",
                )
            )
        elif self._contains_any(lowered, ("schedule", "scheduled")):
            steps.append(
                WorkflowStep(
                    id="step_1",
                    type="trigger",
                    app="scheduler",
                    action="run_on_schedule",
                )
            )
        else:
            steps.append(
                WorkflowStep(
                    id="step_1",
                    type="trigger",
                    app="manual",
                    action="start",
                )
            )

        next_id = 2

        if self._contains_any(lowered, ("ai", "analyze", "analyse", "summarize", "classify")):
            steps.append(
                WorkflowStep(
                    id=f"step_{next_id}",
                    type="action",
                    app="ai",
                    action="analyze",
                    config={"input": "previous_step.output"},
                )
            )
            next_id += 1

        if self._contains_any(lowered, ("gmail", "email", "e-mail", "mail")):
            steps.append(
                WorkflowStep(
                    id=f"step_{next_id}",
                    type="action",
                    app="gmail",
                    action="send_email",
                    config={"to": "configure_recipient", "body": "previous_step.output"},
                )
            )
            next_id += 1
        elif self._contains_any(lowered, ("slack",)):
            steps.append(
                WorkflowStep(
                    id=f"step_{next_id}",
                    type="action",
                    app="slack",
                    action="send_message",
                    config={"channel": "configure_channel", "message": "previous_step.output"},
                )
            )
            next_id += 1

        if self._contains_any(lowered, ("spreadsheet", "google sheets", "sheets")):
            steps.append(
                WorkflowStep(
                    id=f"step_{next_id}",
                    type="action",
                    app="google_sheets",
                    action="append_row",
                    config={"values": "previous_step.output"},
                )
            )

        name_words = re.sub(r"[^a-zA-Z0-9 ]", " ", request).split()[:6]
        name = " ".join(name_words).title() or "Untitled Workflow"

        return WorkflowPlan(
            name=name,
            request=request,
            description=f"V1 workflow plan generated from: {request}",
            steps=steps,
        )
