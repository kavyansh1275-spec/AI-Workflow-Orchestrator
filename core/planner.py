from __future__ import annotations

import re

from models.workflow import WorkflowPlan, WorkflowStep


class Planner:
    """Convert common natural-language automation requests into a V1 plan.

    V1 intentionally uses deterministic rules rather than an external LLM so the
    foundation is testable without API keys. An AI planner can replace this class later.
    """

    def plan(self, request: str) -> WorkflowPlan:
        request = request.strip()
        if not request:
            raise ValueError("request cannot be empty")

        lowered = request.lower()
        steps: list[WorkflowStep] = []

        if any(word in lowered for word in ("form", "forms", "form submission")):
            steps.append(
                WorkflowStep(
                    id="step_1",
                    type="trigger",
                    app="forms",
                    action="receive_submission",
                )
            )
        elif any(word in lowered for word in ("webhook", "http request")):
            steps.append(
                WorkflowStep(
                    id="step_1",
                    type="trigger",
                    app="webhook",
                    action="receive_request",
                )
            )
        elif "schedule" in lowered or "scheduled" in lowered:
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

        if any(word in lowered for word in ("ai", "analyze", "analyse", "summarize", "classify")):
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

        if any(word in lowered for word in ("gmail", "email", "e-mail", "mail")):
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
        elif "slack" in lowered:
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

        if "spreadsheet" in lowered or "google sheets" in lowered or "sheets" in lowered:
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
