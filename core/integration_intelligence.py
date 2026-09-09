from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any

from integrations.catalog import IntegrationCatalog, IntegrationSpec


@dataclass(frozen=True)
class IntegrationCandidate:
    app: str
    action: str
    score: float
    reason: str
    required_fields: tuple[str, ...]

    def model_dump(self) -> dict[str, Any]:
        return {
            "app": self.app,
            "action": self.action,
            "score": round(self.score, 3),
            "reason": self.reason,
            "required_fields": list(self.required_fields),
        }


class IntegrationIntelligence:
    """Maps natural-language business requirements to catalog capabilities.

    This layer is deterministic and credential-free: it recommends capabilities but
    never calls a provider or exposes secrets. It is intentionally conservative so
    unknown requirements become explicit gaps instead of silently becoming actions.
    """

    _ALIASES = {
        "email": {"gmail"},
        "mail": {"gmail"},
        "spreadsheet": {"google_sheets"},
        "sheets": {"google_sheets"},
        "database": {"airtable"},
        "project manager": {"notion"},
        "chat": {"slack", "discord", "telegram"},
        "notification": {"slack", "discord", "telegram", "gmail"},
        "webhook": {"webhook"},
        "form": {"forms", "form"},
        "ai": {"ai"},
    }

    _ACTION_HINTS = {
        "send": {"send_email", "send_message"},
        "email": {"send_email", "search_email"},
        "notify": {"send_email", "send_message"},
        "append": {"append_row"},
        "save": {"create_record", "create_page", "append_row"},
        "create": {"create_record", "create_page"},
        "find": {"find_records", "find_rows", "search_email"},
        "search": {"find_records", "find_rows", "search_email"},
        "analyze": {"analyze"},
        "summarize": {"analyze"},
        "extract": {"analyze"},
        "request": {"request"},
        "submit": {"receive_submission"},
        "schedule": {"run"},
    }

    def __init__(self, catalog: IntegrationCatalog | None = None) -> None:
        self.catalog = catalog or IntegrationCatalog()

    @staticmethod
    def _tokens(text: str) -> set[str]:
        return set(re.findall(r"[a-z0-9_]+", text.lower()))

    def _score(self, text: str, spec: IntegrationSpec) -> tuple[float, str]:
        tokens = self._tokens(text)
        score = 0.0
        reasons: list[str] = []
        if spec.app in tokens:
            score += 0.65
            reasons.append(f"explicit app: {spec.app}")
        for alias, apps in self._ALIASES.items():
            if alias in text.lower() and spec.app in apps:
                score += 0.45
                reasons.append(f"matches concept: {alias}")
        for hint, actions in self._ACTION_HINTS.items():
            if hint in tokens and spec.action in actions:
                score += 0.25
                reasons.append(f"matches action intent: {hint}")
        if spec.category in tokens:
            score += 0.1
        return min(score, 1.0), "; ".join(dict.fromkeys(reasons)) or "catalog capability match"

    def recommend(self, request: str, limit: int = 12) -> list[IntegrationCandidate]:
        if not request.strip():
            raise ValueError("integration intelligence requires a non-empty request")
        candidates: list[IntegrationCandidate] = []
        for spec in self.catalog._specs.values():
            score, reason = self._score(request, spec)
            if score > 0:
                candidates.append(IntegrationCandidate(spec.app, spec.action, score, reason, spec.required_fields))
        return sorted(candidates, key=lambda item: (-item.score, item.app, item.action))[:limit]

    def analyze(self, request: str) -> dict[str, Any]:
        recommendations = self.recommend(request)
        apps: list[str] = []
        actions: list[str] = []
        for candidate in recommendations:
            if candidate.app not in apps:
                apps.append(candidate.app)
            if candidate.action not in actions:
                actions.append(candidate.action)
        gaps: list[str] = []
        lowered = request.lower()
        if any(word in lowered for word in ("crm", "customer relationship")) and "airtable" not in apps:
            gaps.append("crm integration is not explicitly represented in the current catalog")
        if "transcript" in lowered or "meeting notes" in lowered:
            gaps.append("meeting transcription provider is not currently represented in the catalog")
        return {
            "recommendations": [candidate.model_dump() for candidate in recommendations],
            "recommended_apps": apps,
            "recommended_actions": actions,
            "gaps": gaps,
            "ready": not gaps,
        }
