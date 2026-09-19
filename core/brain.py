from __future__ import annotations

import re
from typing import Any

from core.intelligence import WorkflowIntelligence
from models.intent import WorkflowIntent
from models.requirements import WorkflowRequirements


class WorkflowBrain:
    """V5 decision layer built around a deterministic, provider-neutral fallback."""

    def __init__(self, intelligence: WorkflowIntelligence | None = None) -> None:
        self.intelligence = intelligence or WorkflowIntelligence()

    def understand(self, request: str) -> WorkflowIntent:
        return self.intelligence.analyze(request)

    @staticmethod
    def _is_order_request(text: str) -> bool:
        return re.search(r"\b(new order|new purchase|order arrives|purchase arrives)\b", text) is not None

    def requirements(self, request: str) -> WorkflowRequirements:
        intent = self.understand(request)
        text = request.lower()
        inputs: list[str] = []
        outputs: list[str] = []
        data: list[str] = []
        missing: list[str] = []

        if intent.trigger != "manual.start":
            inputs.append(intent.trigger)
        if intent.actions:
            outputs.extend(intent.actions)

        for label, pattern in (
            ("form data", r"\b(form|submission|response)\b"),
            ("webhook payload", r"\b(webhook|http request|api request|payload)\b"),
            ("email content", r"\b(email|mail|message)\b"),
            ("record data", r"\b(row|spreadsheet|sheet|database|record)\b"),
        ):
            if re.search(pattern, text) and label not in data:
                data.append(label)

        if self._is_order_request(text):
            data.extend(item for item in ("customer details", "order details") if item not in data)

            if intent.trigger == "manual.start":
                missing.append("order source")
            if "google sheets" in text or "spreadsheet" in text or "sheets" in text:
                missing.append("Google Sheets destination")
            if "business owner" in text or "owner" in text:
                missing.append("business owner email")
            if "database" in text:
                missing.append("order database")
            if "relevant team" in text or "notify the team" in text or "notify team" in text:
                missing.append("team notification channel")
            if "follow-up" in text or "follow up" in text:
                missing.append("follow-up task destination")
        else:
            if intent.trigger == "manual.start":
                missing.append("trigger source")
            if "gmail.send_email" in intent.actions:
                missing.append("email recipient")
            if "slack.send_message" in intent.actions or "discord.send_message" in intent.actions:
                missing.append("destination channel")
            if "notion.create_page" in intent.actions:
                missing.append("Notion destination")

        confidence = min(1.0, intent.confidence + (0.05 if data else 0.0))
        return WorkflowRequirements(
            inputs=inputs,
            outputs=outputs,
            apps=sorted({step.split(".", 1)[0] for step in [intent.trigger, *intent.actions]}),
            data=data,
            conditions=intent.conditions,
            missing=missing,
            confidence=confidence,
        )

    def decide(self, request: str) -> dict[str, Any]:
        intent = self.understand(request)
        requirements = self.requirements(request)
        return {
            "intent": intent.model_dump(),
            "requirements": requirements.model_dump(),
            "provider": intent.provider,
            "needs_clarification": bool(requirements.missing),
        }
