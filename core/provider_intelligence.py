from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ProviderMapping:
    provider: str
    app: str
    action: str
    native: str
    confidence: float
    notes: str = ""


class ProviderIntelligence:
    """Translate provider-independent capabilities into provider-native hints.

    This layer intentionally does not invent credentials or opaque provider IDs.
    Unknown operations remain explicit so adapters can reject or request a
    provider-specific mapping rather than silently creating an invalid workflow.
    """

    _MAP: dict[str, dict[str, str]] = {
        "n8n": {
            "webhook.receive_request": "n8n-nodes-base.webhook",
            "forms.receive_submission": "n8n-nodes-base.formTrigger",
            "form.receive_submission": "n8n-nodes-base.formTrigger",
            "schedule.run": "n8n-nodes-base.scheduleTrigger",
            "gmail.send_email": "n8n-nodes-base.gmail",
            "gmail.search_email": "n8n-nodes-base.gmail",
            "slack.send_message": "n8n-nodes-base.slack",
            "discord.send_message": "n8n-nodes-base.discord",
            "notion.create_page": "n8n-nodes-base.notion",
            "google_sheets.append_row": "n8n-nodes-base.googleSheets",
            "google_sheets.find_rows": "n8n-nodes-base.googleSheets",
            "airtable.create_record": "n8n-nodes-base.airtable",
            "airtable.find_records": "n8n-nodes-base.airtable",
            "telegram.send_message": "n8n-nodes-base.telegram",
            "http.request": "n8n-nodes-base.httpRequest",
            "ai.analyze": "@n8n/n8n-nodes-langchain.openAi",
        },
        "make": {
            "webhook.receive_request": "webhooks.customWebhook",
            "forms.receive_submission": "forms.watchResponses",
            "form.receive_submission": "forms.watchResponses",
            "schedule.run": "builtin.scheduler",
            "gmail.send_email": "gmail.sendAnEmail",
            "gmail.search_email": "gmail.searchEmails",
            "slack.send_message": "slack.createMessage",
            "discord.send_message": "discord.sendMessage",
            "notion.create_page": "notion.createDataSourceItem",
            "google_sheets.append_row": "google-sheets.addRow",
            "google_sheets.find_rows": "google-sheets.searchRows",
            "airtable.create_record": "airtable.createRecord",
            "airtable.find_records": "airtable.searchRecords",
            "telegram.send_message": "telegram.sendMessage",
            "http.request": "http.makeARequest",
            "ai.analyze": "openai.createAChatCompletion",
        },
        "zapier": {
            "webhook.receive_request": "webhooks.catch_hook",
            "gmail.send_email": "gmail.send_email",
            "gmail.search_email": "gmail.search_email",
            "slack.send_message": "slack.send_channel_message",
            "discord.send_message": "discord.send_channel_message",
            "notion.create_page": "notion.create_page",
            "google_sheets.append_row": "google-sheets.create_spreadsheet_row",
            "airtable.create_record": "airtable.create_record",
            "telegram.send_message": "telegram.send_message",
            "http.request": "webhooks.custom_request",
        },
    }

    def map_step(self, provider: str, app: str, action: str) -> ProviderMapping:
        provider = provider.strip().lower()
        key = f"{app.strip().lower()}.{action.strip().lower()}"
        native = self._MAP.get(provider, {}).get(key)
        if native is None:
            return ProviderMapping(provider, app, action, "", 0.0, "No provider-native mapping registered")
        return ProviderMapping(provider, app, action, native, 0.9, "Provider-native capability mapping")

    def enrich(self, provider: str, steps: list[dict[str, Any]]) -> list[dict[str, Any]]:
        result: list[dict[str, Any]] = []
        for step in steps:
            mapping = self.map_step(provider, str(step.get("app", "")), str(step.get("action", "")))
            enriched = dict(step)
            enriched["provider_native"] = mapping.native or None
            enriched["mapping_confidence"] = mapping.confidence
            enriched["mapping_notes"] = mapping.notes
            result.append(enriched)
        return result

    def validate(self, provider: str, steps: list[dict[str, Any]]) -> list[str]:
        unsupported: list[str] = []
        for step in steps:
            mapping = self.map_step(provider, str(step.get("app", "")), str(step.get("action", "")))
            if not mapping.native:
                unsupported.append(f"{step.get('app')}.{step.get('action')}")
        return unsupported
