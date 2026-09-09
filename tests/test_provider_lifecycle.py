from __future__ import annotations

from core.credentials import CredentialManager
from core.provider_lifecycle import ProviderLifecycleTester
from models.provider_lifecycle import LifecycleStatus
from models.workflow import WorkflowPlan, WorkflowStep


def workflow(provider: str = "n8n") -> WorkflowPlan:
    return WorkflowPlan(
        name="Lifecycle Test",
        provider=provider,
        steps=[
            WorkflowStep(id="trigger", type="trigger", app="webhook", action="receive_request"),
            WorkflowStep(id="action", type="action", app="gmail", action="send_email", depends_on=["trigger"]),
        ],
    )


def test_lifecycle_is_blocked_without_explicit_opt_in(monkeypatch):
    monkeypatch.delenv("PROVIDER_LIFECYCLE_LIVE", raising=False)
    tester = ProviderLifecycleTester(CredentialManager(environ={"N8N_API_KEY": "test-key", "N8N_BASE_URL": "https://example.test"}))
    result = tester.create_and_cleanup(workflow())
    assert result.status == LifecycleStatus.BLOCKED
    assert result.dry_run is True
    assert result.resource_id is None


def test_lifecycle_readiness_requires_credentials_and_opt_in(monkeypatch):
    monkeypatch.setenv("PROVIDER_LIFECYCLE_LIVE", "1")
    tester = ProviderLifecycleTester(CredentialManager(environ={"N8N_API_KEY": "test-key", "N8N_BASE_URL": "https://example.test"}))
    readiness = tester.validate(workflow())
    assert readiness["credential_configured"] is True
    assert readiness["live_opt_in"] is True
    assert readiness["ready"] is True


def test_lifecycle_unknown_provider_is_blocked(monkeypatch):
    monkeypatch.setenv("PROVIDER_LIFECYCLE_LIVE", "1")
    result = ProviderLifecycleTester().create_and_cleanup(workflow("generic"))
    assert result.status == LifecycleStatus.BLOCKED
