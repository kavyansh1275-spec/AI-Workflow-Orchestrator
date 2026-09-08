from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class IntegrationSpec:
    """Credential-free description of an application capability."""

    app: str
    action: str
    category: str
    required_fields: tuple[str, ...] = ()
    description: str = ""


# V7 expands the supported application surface without making live API calls.
_INTEGRATIONS: tuple[IntegrationSpec, ...] = (
    IntegrationSpec("webhook", "receive_request", "trigger", description="Receive an inbound webhook request."),
    IntegrationSpec("forms", "receive_submission", "trigger", description="Receive a form submission."),
    IntegrationSpec("form", "receive_submission", "trigger", description="Receive a form submission."),
    IntegrationSpec("schedule", "run", "trigger", description="Start a workflow on a schedule."),
    IntegrationSpec("gmail", "send_email", "communication", ("to", "body"), "Send an email."),
    IntegrationSpec("gmail", "search_email", "communication", ("query",), "Search email messages."),
    IntegrationSpec("slack", "send_message", "communication", ("channel", "message"), "Send a Slack message."),
    IntegrationSpec("discord", "send_message", "communication", ("channel", "message"), "Send a Discord message."),
    IntegrationSpec("notion", "create_page", "productivity", ("title", "content"), "Create a Notion page."),
    IntegrationSpec("google_sheets", "append_row", "data", ("values",), "Append a row to Google Sheets."),
    IntegrationSpec("google_sheets", "find_rows", "data", ("query",), "Find matching spreadsheet rows."),
    IntegrationSpec("airtable", "create_record", "data", ("fields",), "Create an Airtable record."),
    IntegrationSpec("airtable", "find_records", "data", ("query",), "Find Airtable records."),
    IntegrationSpec("telegram", "send_message", "communication", ("chat_id", "message"), "Send a Telegram message."),
    IntegrationSpec("http", "request", "utility", ("url", "method"), "Make a generic HTTP request."),
    IntegrationSpec("ai", "analyze", "ai", description="Analyze or transform workflow data with an AI step."),
)


class IntegrationCatalog:
    """Read-only registry of supported V7 application capabilities."""

    def __init__(self, specs: tuple[IntegrationSpec, ...] = _INTEGRATIONS) -> None:
        self._specs = {(spec.app, spec.action): spec for spec in specs}

    def resolve(self, app: str, action: str) -> IntegrationSpec | None:
        return self._specs.get((app.strip().lower(), action.strip().lower()))

    def require(self, app: str, action: str) -> IntegrationSpec:
        spec = self.resolve(app, action)
        if spec is None:
            raise ValueError(f"unsupported integration capability: {app}.{action}")
        return spec

    def list_apps(self) -> list[str]:
        return sorted({spec.app for spec in self._specs.values()})

    def list_capabilities(self) -> list[str]:
        return sorted(f"{spec.app}.{spec.action}" for spec in self._specs.values())

    def describe(self, app: str | None = None) -> list[dict[str, object]]:
        specs = self._specs.values() if app is None else (s for s in self._specs.values() if s.app == app.lower())
        return [
            {
                "app": spec.app,
                "action": spec.action,
                "category": spec.category,
                "required_fields": list(spec.required_fields),
                "description": spec.description,
            }
            for spec in sorted(specs, key=lambda item: (item.app, item.action))
        ]
