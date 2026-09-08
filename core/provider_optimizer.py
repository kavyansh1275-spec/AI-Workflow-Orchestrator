from __future__ import annotations

from models.intent import WorkflowIntent


class ProviderOptimizer:
    """V5 provider decision policy with explicit-user preference precedence."""

    def choose(self, request: str, intent: WorkflowIntent) -> tuple[str, str]:
        explicit = intent.provider
        if explicit != "generic":
            return explicit, "explicit_user_preference"

        if intent.conditions or len(intent.actions) >= 3:
            return "n8n", "complexity"
        if len(intent.actions) == 2:
            return "make", "multi_step"
        if len(intent.actions) == 1:
            # Keep V2's provider-neutral fallback for simple form workflows,
            # while allowing a webhook-based simple automation to use Zapier.
            if intent.trigger == "webhook.receive_request":
                return "zapier", "simple_webhook_automation"
            return "generic", "simple_provider_neutral_automation"
        return "generic", "insufficient_workflow_detail"
