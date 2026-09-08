from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field, field_validator


class DeploymentEnvironment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class DeploymentStatus(str, Enum):
    PLANNED = "planned"
    DEPLOYED = "deployed"
    ROLLED_BACK = "rolled_back"


class DeploymentPlan(BaseModel):
    """Credential-free release plan produced by the V8 production layer."""

    release_id: str
    workflow_name: str
    provider: str
    environment: DeploymentEnvironment
    dry_run: bool = True
    artifact_sha256: str
    artifact: dict = Field(default_factory=dict)

    @field_validator("release_id", "workflow_name", "provider", "artifact_sha256")
    @classmethod
    def must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("deployment fields cannot be blank")
        return value.strip()


class DeploymentRecord(BaseModel):
    """Serializable deployment history entry."""

    release_id: str
    workflow_name: str
    provider: str
    environment: DeploymentEnvironment
    status: DeploymentStatus
    dry_run: bool
    artifact_sha256: str
    message: str
