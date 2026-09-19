from __future__ import annotations

import re

from models.intent import WorkflowIntent


class WorkflowIntelligence:
    """Deterministic V3 request understanding layer.

    V3 stays offline and credential-free while extracting provider, trigger,
    actions, and simple conditional language into a normalized intent.
    """

    PROVIDERS = ("n8n", "make", "zapier", "generic")

    def analyze(self, request: str) -> WorkflowIntent:
        request = request.strip()
        if not request:
            raise ValueError("request cannot be empty")

        lowered = request.lower()
        provider = self._provider(lowered)
        trigger = self._trigger(lowered)
        actions = self._actions(lowered)
        conditions = self._conditions(lowered)

        confidence = 0.65
        if trigger != "manual":
            confidence += 0.15
        if actions:
            confidence += 0.15
        if provider != "generic":
            confidence += 0.05

        return WorkflowIntent(
            request=request,
            provider=provider,
            trigger=trigger,
            actions=actions,
            conditions=conditions,
            confidence=min(confidence, 1.0),
        )

    def _provider(self, text: str) -> str:
        if re.search(r"\bn8n\b", text):
            return "n8n"
        if re.search(r"\bmake(?:\.com)?\b", text):
            return "make"
        if re.search(r"\bzapier\b", text):
            return "zapier"
        return "generic"

    def _trigger(self, text: str) -> str:
        if re.search(r"\b(form|forms|form submission|form response)\b", text):
            return "forms.receive_submission"
        if re.search(r"\b(webhook|http request|api request)\b", text):
            return "webhook.receive_request"
        if re.search(r"\b(schedule|scheduled|every day|every week|daily|weekly)\b", text):
            return "scheduler.run_on_schedule"
        if re.search(r"\b(new email|incoming email|email arrives)\b", text):
            return "gmail.receive_email"
        if re.search(r"\b(new row|row added)\b", text):
            return "google_sheets.row_added"
        return "manual.start"

    def _actions(self, text: str) -> list[str]:
        matches: list[tuple[int, str]] = []
        patterns = {
            "ai.analyze": r"\b(ai|analyze|analyse|summarize|summarise|classify|extract)\b",
            "gmail.send_email": r"\b(gmail|email|e-mail|mail)\b",
            "slack.send_message": r"\bslack\b",
            "google_sheets.append_row": r"\b(google sheets|spreadsheet|sheets)\b",
            "notion.create_page": r"\bnotion\b",
            "discord.send_message": r"\bdiscord\b",
        }
        for action, pattern in patterns.items():
            match = re.search(pattern, text)
            if match:
                matches.append((match.start(), action))

        # Trigger phrases such as "email arrives" must not become send actions.
        if self._trigger(text) == "gmail.receive_email":
            matches = [(pos, action) for pos, action in matches if action != "gmail.send_email"]

        return [action for _, action in sorted(matches)]

    def _conditions(self, text: str) -> list[str]:
        conditions: list[str] = []
        patterns = (
            r"if\s+(.+?)(?=\s+then\b|\s+send\b|\s+and\s+then\b|$)",
            r"only\s+if\s+(.+?)(?=\s+then\b|\s+send\b|\s+and\s+then\b|$)",
        )
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                condition = match.group(1).strip(" .,")
                if condition and condition not in conditions:
                    conditions.append(condition)
        return conditions
