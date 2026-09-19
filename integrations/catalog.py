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
    IntegrationSpec("manual", "start", "trigger", description="Start a workflow manually from a user request."),
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
