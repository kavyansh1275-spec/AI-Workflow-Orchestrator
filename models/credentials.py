from __future__ import annotations

from enum import Enum
from pydantic import BaseModel, Field, SecretStr


class CredentialStatus(str, Enum):
    CONFIGURED = "configured"
    MISSING = "missing"
    INVALID = "invalid"


class ProviderCredential(BaseModel):
    """Non-persistent credential configuration for an external provider."""

    provider: str
    api_key: SecretStr | None = None
    base_url: str | None = None
    status: CredentialStatus = CredentialStatus.MISSING
    metadata: dict[str, str] = Field(default_factory=dict)

    def masked(self) -> dict[str, str | None]:
        value = self.api_key.get_secret_value() if self.api_key else ""
        masked = f"{value[:4]}...{value[-4:]}" if len(value) >= 8 else ("***" if value else None)
        return {
            "provider": self.provider,
            "api_key": masked,
            "base_url": self.base_url,
            "status": self.status.value,
        }
