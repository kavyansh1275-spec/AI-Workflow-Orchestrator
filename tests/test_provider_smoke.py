from __future__ import annotations

from core.credentials import CredentialManager
from core.provider_smoke import ProviderSmokeTester
from models.provider_testing import ProviderTestStatus


def test_all_providers_skip_without_credentials() -> None:
    manager = CredentialManager(environ={})
    results = ProviderSmokeTester(manager).run_all()
    assert set(results) == {"n8n", "make", "zapier"}
    assert all(item["status"] == ProviderTestStatus.SKIPPED.value for item in results.values())


def test_unknown_provider_is_rejected() -> None:
    tester = ProviderSmokeTester(CredentialManager(environ={}))
    try:
        tester.run("unknown")
    except ValueError as exc:
        assert "unsupported provider" in str(exc)
    else:
        raise AssertionError("unknown provider should be rejected")
