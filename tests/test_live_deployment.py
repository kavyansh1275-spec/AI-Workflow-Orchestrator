from __future__ import annotations

import unittest

from core.credentials import CredentialManager
from core.live_deployment import LiveDeploymentManager
from models.live_deployment import LiveDeploymentStatus
from models.workflow import WorkflowPlan, WorkflowStep


def workflow(provider: str = "n8n") -> WorkflowPlan:
    return WorkflowPlan(
        request="V13 live deployment safety test",
        description="Test a provider deployment safety gate.",
        name="V13 Live Deployment Test",
        provider=provider,
        steps=[
            WorkflowStep(id="trigger", type="trigger", app="webhook", action="receive_request"),
            WorkflowStep(
                id="email",
                type="action",
                app="gmail",
                action="send_email",
                config={"to": "configure_to", "body": "configure_body"},
                depends_on=["trigger"],
            ),
        ],
    )


class TestLiveDeploymentManager(unittest.TestCase):
    def test_live_deployment_requires_explicit_enablement(self) -> None:
        manager = LiveDeploymentManager(
            CredentialManager(environ={"N8N_API_KEY": "test-key", "N8N_BASE_URL": "https://example.test"})
        )
        result = manager.deploy(workflow(), live=True)
        self.assertEqual(result.status, LiveDeploymentStatus.BLOCKED)
        self.assertIsNone(result.resource_id)

    def test_non_live_request_is_always_blocked(self) -> None:
        manager = LiveDeploymentManager()
        result = manager.deploy(workflow(), live=False)
        self.assertEqual(result.status, LiveDeploymentStatus.BLOCKED)

    def test_unsupported_provider_is_blocked(self) -> None:
        manager = LiveDeploymentManager()
        result = manager.deploy(workflow("generic"), live=True)
        self.assertEqual(result.status, LiveDeploymentStatus.BLOCKED)

    def test_make_readiness_reports_team_requirement(self) -> None:
        manager = LiveDeploymentManager(
            CredentialManager(environ={"MAKE_API_TOKEN": "test-token", "MAKE_BASE_URL": "https://example.test"})
        )
        readiness = manager.readiness(workflow("make"))
        self.assertTrue(readiness["credential_configured"])
        self.assertFalse(readiness["team_id_configured"])


if __name__ == "__main__":
    unittest.main()
