from __future__ import annotations

import re

from core.intelligence import WorkflowIntelligence
from models.workflow import WorkflowPlan, WorkflowStep


class Planner:
    """Convert normalized V3 intent into a dependency-aware workflow plan."""

    def __init__(self, intelligence: WorkflowIntelligence | None = None) -> None:
        self.intelligence = intelligence or WorkflowIntelligence()

    @staticmethod
    def _is_order_request(request: str) -> bool:
        text = request.lower()
        return re.search(r"\b(new order|new purchase|order arrives|purchase arrives)\b", text) is not None

    @staticmethod
    def _has_any(text: str, patterns: tuple[str, ...]) -> bool:
        return any(re.search(pattern, text) for pattern in patterns)

    def _plan_order_workflow(self, request: str, provider: str, confidence: float) -> WorkflowPlan:
        """Expand common order-automation requests into explicit structured operations."""
        text = request.lower()
        has_webhook = self._has_any(text, (r"\bwebhook\b", r"\bhttp request\b", r"\bapi request\b"))
        needs_sheet = self._has_any(text, (r"\bgoogle sheets\b", r"\bspreadsheet\b", r"\bsheets\b"))
        needs_processed = self._has_any(text, (r"\bmark(?:s|ed)?\b.*\bprocessed\b", r"\bprocessed\b"))
        needs_customer_status = self._has_any(text, (r"\bnew or returning\b", r"\bnew customer\b", r"\breturning customer\b"))
        needs_database = self._has_any(text, (r"\bdatabase\b", r"\brecord the order\b"))
        needs_team = self._has_any(text, (r"\brelevant team\b", r"\bnotify the team\b", r"\bnotify team\b"))
        needs_confirmation = self._has_any(text, (r"\bconfirmation\b", r"\bconfirmation email\b", r"\bpersonalized confirmation\b"))
        needs_follow_up = self._has_any(text, (r"\bfollow[- ]up task\b", r"\bfollow up task\b", r"\bfollow-up\b"))
        needs_high_value = self._has_any(text, (r"\bhigh[- ]value\b", r"\babove ₹?\s*5[, ]?000\b", r"\babove 5000\b"))

        steps: list[WorkflowStep] = [
            WorkflowStep(
                id="step_1",
                type="trigger",
                app="webhook",
                action="receive_request",
                config={} if has_webhook else {"source": "configure_order_source"},
            ),
            WorkflowStep(
                id="step_2",
                type="action",
                app="ai",
                action="analyze",
                config={
                    "input": "step_1.output",
                    "extract": [
                        "customer_name", "customer_email", "order_id", "products", "total_amount",
                    ],
                },
                depends_on=["step_1"],
            ),
        ]

        next_id = 3
        if needs_customer_status:
            steps.append(WorkflowStep(
                id=f"step_{next_id}",
                type="action",
                app="airtable",
                action="find_records",
                config={"query": "customer_email = step_2.output.customer_email"},
                depends_on=["step_2"],
            ))
            next_id += 1
            steps.append(WorkflowStep(
                id=f"step_{next_id}",
                type="action",
                app="ai",
                action="analyze",
                config={
                    "input": f"step_{next_id - 1}.output",
                    "task": "classify customer as new or returning",
                    "customer_email": "step_2.output.customer_email",
                },
                depends_on=[f"step_{next_id - 1}", "step_2"],
            ))
            next_id += 1

        if needs_sheet:
            values = {
                "customer_name": "step_2.output.customer_name",
                "customer_email": "step_2.output.customer_email",
                "order_id": "step_2.output.order_id",
                "products": "step_2.output.products",
                "total_amount": "step_2.output.total_amount",
            }
            steps.append(WorkflowStep(
                id=f"step_{next_id}",
                type="action",
                app="google_sheets",
                action="append_row",
                config={"spreadsheet": "configure_google_sheet", "values": values},
                depends_on=["step_2"],
            ))
            next_id += 1

        if needs_database:
            status_ref = f"step_{next_id - 1}.output" if needs_customer_status else "step_2.output"
            steps.append(WorkflowStep(
                id=f"step_{next_id}",
                type="action",
                app="airtable",
                action="create_record",
                config={
                    "base": "configure_order_database",
                    "fields": {
                        "customer_name": "step_2.output.customer_name",
                        "customer_email": "step_2.output.customer_email",
                        "order_id": "step_2.output.order_id",
                        "products": "step_2.output.products",
                        "total_amount": "step_2.output.total_amount",
                        "customer_status": status_ref,
                    },
                },
                depends_on=["step_2"],
            ))
            next_id += 1

        if needs_team:
            steps.append(WorkflowStep(
                id=f"step_{next_id}",
                type="action",
                app="slack",
                action="send_message",
                config={
                    "channel": "configure_team_channel",
                    "message": {
                        "template": "new_order_team_alert",
                        "order_id": "step_2.output.order_id",
                        "customer_name": "step_2.output.customer_name",
                        "total_amount": "step_2.output.total_amount",
                    },
                },
                depends_on=["step_2"],
            ))
            next_id += 1

        if needs_confirmation:
            steps.append(WorkflowStep(
                id=f"step_{next_id}",
                type="action",
                app="gmail",
                action="send_email",
                config={
                    "to": "step_2.output.customer_email",
                    "body": {
                        "template": "personalized_order_confirmation",
                        "customer_name": "step_2.output.customer_name",
                        "order_id": "step_2.output.order_id",
                        "products": "step_2.output.products",
                        "total_amount": "step_2.output.total_amount",
                    },
                },
                depends_on=["step_2"],
            ))
            next_id += 1

        if needs_high_value:
            steps.append(WorkflowStep(
                id=f"step_{next_id}",
                type="action",
                app="gmail",
                action="send_email",
                config={
                    "to": "configure_business_owner_email",
                    "body": {
                        "template": "high_value_order_alert",
                        "order_id": "step_2.output.order_id",
                        "total_amount": "step_2.output.total_amount",
                    },
                },
                depends_on=["step_2"],
                condition="step_2.output.total_amount > 5000",
            ))
            next_id += 1

        if needs_follow_up:
            steps.append(WorkflowStep(
                id=f"step_{next_id}",
                type="action",
                app="notion",
                action="create_page",
                config={
                    "title": "Follow-up: step_2.output.order_id",
                    "content": {
                        "template": "order_follow_up",
                        "order_id": "step_2.output.order_id",
                        "customer_email": "step_2.output.customer_email",
                    },
                },
                depends_on=["step_2"],
                condition="step_2.output.needs_attention == true",
            ))
            next_id += 1

        if needs_processed:
            deps = [step.id for step in steps[2:]] or ["step_2"]
            steps.append(WorkflowStep(
                id=f"step_{next_id}",
                type="action",
                app="orders",
                action="mark_processed",
                config={"order_id": "step_2.output.order_id"},
                depends_on=deps,
            ))

        name_words = re.sub(r"[^a-zA-Z0-9 ]", " ", request).split()[:8]
        name = " ".join(name_words).title() or "Untitled Workflow"
        return WorkflowPlan(
            name=name,
            request=request,
            description=f"Structured order-processing workflow generated from: {request}",
            steps=steps,
            provider=provider,
            intent_confidence=confidence,
        )

    def plan(self, request: str) -> WorkflowPlan:
        intent = self.intelligence.analyze(request)
        if self._is_order_request(request):
            return self._plan_order_workflow(request, intent.provider, intent.confidence)

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
