from __future__ import annotations

import os
from collections.abc import Mapping

from models.credentials import CredentialStatus, ProviderCredential


class CredentialManager:
    """Load provider credentials from environment variables without persisting secrets."""

    ENV_KEYS = {
        "n8n": "N8N_API_KEY",
        "make": "MAKE_API_TOKEN",
        "zapier": "ZAPIER_API_TOKEN",
    }

    BASE_URL_KEYS = {
        "n8n": "N8N_BASE_URL",
        "make": "MAKE_BASE_URL",
        "zapier": "ZAPIER_BASE_URL",
    }

    def __init__(self, environ: Mapping[str, str] | None = None) -> None:
        self._environ = dict(environ) if environ is not None else dict(os.environ)
        self._credentials: dict[str, ProviderCredential] = {}

    def load(self, provider: str) -> ProviderCredential:
        provider = provider.strip().lower()
        if provider not in self.ENV_KEYS:
            raise ValueError(f"unsupported credential provider: {provider}")

        key_name = self.ENV_KEYS[provider]
        base_url = self._environ.get(self.BASE_URL_KEYS[provider]) or None
        api_key = self._environ.get(key_name) or None
        status = CredentialStatus.CONFIGURED if api_key else CredentialStatus.MISSING

        credential = ProviderCredential(
            provider=provider,
            api_key=api_key,
            base_url=base_url,
            status=status,
        )
        self._credentials[provider] = credential
        return credential

    def load_all(self) -> dict[str, ProviderCredential]:
        return {provider: self.load(provider) for provider in self.ENV_KEYS}

    def get(self, provider: str) -> ProviderCredential:
        provider = provider.strip().lower()
        if provider not in self._credentials:
            return self.load(provider)
        return self._credentials[provider]

    def is_configured(self, provider: str) -> bool:
        return self.get(provider).status == CredentialStatus.CONFIGURED

    def require(self, provider: str) -> ProviderCredential:
        credential = self.get(provider)
        if credential.status != CredentialStatus.CONFIGURED:
            env_name = self.ENV_KEYS[provider.strip().lower()]
            raise RuntimeError(
                f"Missing credentials for {provider}. Set {env_name} in the runtime environment."
            )
        return credential

    def status(self) -> dict[str, dict[str, str | None]]:
        return {provider: self.get(provider).masked() for provider in self.ENV_KEYS}
