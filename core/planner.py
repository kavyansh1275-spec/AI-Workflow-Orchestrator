from __future__ import annotations

import re

from core.intelligence import WorkflowIntelligence
from models.workflow import WorkflowPlan, WorkflowStep


class Planner:
    """Convert normalized V3 intent into a dependency-aware workflow plan."""

    def __init__(self, intelligence: WorkflowIntelligence | None = None) -> None:
        self.intelligence = intelligence or WorkflowIntelligence()

    @staticmethod
    def _is_order_webhook_request(request: str) -> bool:
        text = request.lower()
        return (
            re.search(r"\b(new order|new purchase|order arrives|purchase arrives)\b", text) is not None
            and re.search(r"\b(webhook|http request|api request)\b", text) is not None
        )

    def _plan_order_webhook_workflow(self, request: str, provider: str, confidence: float) -> WorkflowPlan:
        """Expand an order webhook request into explicit structured operations."""
        steps = [
            WorkflowStep(id="step_1", type="trigger", app="webhook", action="receive_request"),
            WorkflowStep(
                id="step_2", type="action", app="ai", action="analyze",
                config={
                    "input": "step_1.output",
                    "extract": ["customer_name", "customer_email", "order_id", "products", "total_amount"],
                },
                depends_on=["step_1"],
            ),
            WorkflowStep(
                id="step_3", type="action", app="google_sheets", action="append_row",
                config={"values": {
                    "customer_name": "step_2.output.customer_name",
                    "customer_email": "step_2.output.customer_email",
                    "order_id": "step_2.output.order_id",
                    "products": "step_2.output.products",
                    "total_amount": "step_2.output.total_amount",
                }},
                depends_on=["step_2"],
            ),
            WorkflowStep(
                id="step_4", type="action", app="gmail", action="send_email",
                config={
                    "to": "step_2.output.customer_email",
                    "body": {
                        "template": "order_confirmation",
                        "customer_name": "step_2.output.customer_name",
                        "order_id": "step_2.output.order_id",
                        "products": "step_2.output.products",
                        "total_amount": "step_2.output.total_amount",
                    },
                },
                depends_on=["step_2"],
            ),
            WorkflowStep(
                id="step_5", type="action", app="gmail", action="send_email",
                config={
                    "to": "configure_business_owner_email",
                    "body": {
                        "template": "new_order_alert",
                        "customer_name": "step_2.output.customer_name",
                        "order_id": "step_2.output.order_id",
                        "total_amount": "step_2.output.total_amount",
                    },
                },
                depends_on=["step_2"],
            ),
            WorkflowStep(
                id="step_6", type="action", app="gmail", action="send_email",
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
            ),
            WorkflowStep(
                id="step_7", type="action", app="orders", action="mark_processed",
                config={"order_id": "step_2.output.order_id"},
                depends_on=["step_3", "step_4", "step_5", "step_6"],
            ),
        ]
        name_words = re.sub(r"[^a-zA-Z0-9 ]", " ", request).split()[:6]
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
        if self._is_order_webhook_request(request):
            return self._plan_order_webhook_workflow(request, intent.provider, intent.confidence)

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
