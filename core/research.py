from __future__ import annotations

import hashlib
import re
from typing import Any

from core.orchestrator import Orchestrator
from models.research import AutomationResearchResult, ResearchFinding


class AutonomousResearchEngine:
    """Turn a business problem into an actionable automation research brief."""

    def __init__(self, orchestrator: Orchestrator | None = None) -> None:
        self.orchestrator = orchestrator or Orchestrator()

    @staticmethod
    def _id(request: str) -> str:
        return f"research-{hashlib.sha256(request.encode()).hexdigest()[:12]}"

    @staticmethod
    def _sentences(request: str) -> list[str]:
        return [part.strip(" ,") for part in re.split(r"\s+(?:and then|then|after that|next|finally)\s+|[.!?]+", request) if part.strip(" ,")]

    @staticmethod
    def _requirements(request: str, integrations: dict[str, Any]) -> list[str]:
        requirements = [
            "A clear trigger must start the automation.",
            "Each business action must have a supported integration or HTTP/API fallback.",
            "Data must be passed between dependent steps without exposing credentials.",
            "The workflow must be testable in safe simulation before live deployment.",
            "Failures must be observable and recoverable without uncontrolled live mutation.",
        ]
        if integrations.get("required_integrations"):
            requirements.append("All identified required integrations must be configured before live execution.")
        return requirements

    @staticmethod
    def _risks(integrations: dict[str, Any], provider: str) -> list[dict[str, Any]]:
        risks = [
            {"risk": "Missing credentials", "severity": "high", "mitigation": "Use credential readiness checks before deployment."},
            {"risk": "Provider-specific action mismatch", "severity": "medium", "mitigation": "Validate generated native actions before release."},
            {"risk": "Downstream failure propagation", "severity": "medium", "mitigation": "Pause dependents and retry failed stages."},
        ]
        if provider == "generic":
            risks.append({"risk": "Provider capability uncertainty", "severity": "medium", "mitigation": "Require provider selection review before deployment."})
        if integrations.get("missing_integrations"):
            risks.append({"risk": "Missing integrations", "severity": "high", "mitigation": "Resolve integration gaps before live execution."})
        return risks

    def research(self, request: str) -> AutomationResearchResult:
        request = request.strip()
        if not request:
            raise ValueError("research request cannot be blank")

        integration_data = self.orchestrator.integration_intelligence(request)
        decision = self.orchestrator.decide(request)
        provider = str(decision.get("provider", "generic"))
        sentences = self._sentences(request)
        problem = sentences[0] if sentences else request
        goal = sentences[-1] if len(sentences) > 1 else f"Automate: {request}"
        requirements = self._requirements(request, integration_data)
        required_integrations = integration_data.get("required_integrations", [])
        missing = integration_data.get("missing_integrations", [])

        provider_options = [
            {"provider": provider, "confidence": decision.get("confidence", 0.0), "reason": decision.get("provider_reason", "Primary provider selected by orchestrator.")},
        ]
        if provider != "n8n":
            provider_options.append({"provider": "n8n", "confidence": 0.5, "reason": "Alternative for flexible multi-step orchestration."})
        if provider != "make":
            provider_options.append({"provider": "make", "confidence": 0.5, "reason": "Alternative for visual SaaS integrations."})
        if provider != "zapier":
            provider_options.append({"provider": "zapier", "confidence": 0.5, "reason": "Alternative for common app-to-app automations."})

        findings = [
            ResearchFinding(category="problem", finding=problem, confidence=0.85, evidence=sentences[:3]),
            ResearchFinding(category="goal", finding=goal, confidence=0.8, evidence=[request]),
            ResearchFinding(category="integrations", finding=f"Identified {len(required_integrations)} required integration(s).", confidence=0.9, evidence=[str(item) for item in required_integrations]),
            ResearchFinding(category="provider", finding=f"Primary provider: {provider}.", confidence=float(decision.get("confidence", 0.0) or 0.0), evidence=[str(decision.get("provider_reason", ""))]),
        ]

        gaps = [str(item) for item in missing]
        readiness = "ready_for_design" if not gaps else "blocked_by_integration_gaps"
        acceptance = [
            "Every required integration is mapped to a supported workflow step.",
            "The workflow starts with a valid trigger and preserves step dependencies.",
            "Safe simulation passes for every generated workflow.",
            "Deployment remains blocked until credentials and explicit authorization are present.",
        ]
        return AutomationResearchResult(
            research_id=self._id(request),
            request=request,
            problem=problem,
            goal=goal,
            requirements=requirements,
            integrations=[{"name": str(item), "required": True} for item in required_integrations],
            provider_options=provider_options,
            risks=self._risks(integration_data, provider),
            acceptance_criteria=acceptance,
            findings=findings,
            gaps=gaps,
            readiness=readiness,
        )
