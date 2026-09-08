from __future__ import annotations

from integrations.base import Integration
from integrations.make import MakeIntegration
from integrations.n8n import N8nIntegration
from integrations.zapier import ZapierIntegration


class ProviderRegistry:
    """Central registry for V2 provider adapters."""

    def __init__(self) -> None:
        self._providers: dict[str, Integration] = {
            "n8n": N8nIntegration(),
            "make": MakeIntegration(),
            "zapier": ZapierIntegration(),
        }

    def get(self, provider: str) -> Integration:
        if provider == "generic":
            raise ValueError("generic workflows do not have a deploy provider")
        try:
            return self._providers[provider]
        except KeyError as exc:
            raise ValueError(f"unsupported provider: {provider}") from exc

    def names(self) -> list[str]:
        return sorted(self._providers)
