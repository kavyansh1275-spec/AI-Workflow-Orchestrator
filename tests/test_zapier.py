from __future__ import annotations

import os
import unittest
from unittest.mock import patch

from core.credentials import CredentialManager
from integrations.zapier import ZapierIntegration
from integrations.zapier_client import ZapierClient
from models.workflow import WorkflowPlan, WorkflowStep


class FakeResponse:
    def __init__(self, payload: dict):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        import json
        return json.dumps(self.payload).encode("utf-8")


class ZapierTests(unittest.TestCase):
    def workflow(self) -> WorkflowPlan:
        return WorkflowPlan(
            name="Test Zap",
            request="Send a webhook payload to a Zapier action",
            description="test",
            provider="zapier",
            steps=[
                WorkflowStep(
                    id="step_1",
                    type="action",
                    app="webhook",
                    action="receive_request",
                    config={
                        "zapier_action": "core:test-action",
                        "zapier_inputs": {"url": "https://example.test"},
                    },
                )
            ],
        )

    def test_missing_credentials_block_deployment(self):
        integration = ZapierIntegration(CredentialManager(environ={}))
        with self.assertRaisesRegex(RuntimeError, "ZAPIER_API_TOKEN"):
            integration.deploy(self.workflow())

    @patch.dict(os.environ, {"ZAPIER_API_TOKEN": "test-token"}, clear=False)
    @patch("integrations.zapier_client.urlopen")
    def test_client_uses_bearer_auth_and_create_endpoint(self, mock_urlopen):
        mock_urlopen.return_value = FakeResponse({"data": {"id": "zap-123", "title": "Test Zap"}})
        client = ZapierClient("https://api.zapier.com", "test-token")
        response = client.create_zap(
            "Test Zap",
            [{"action": "core:test-action", "inputs": {}, "authentication": None}],
            enabled=False,
        )
        request = mock_urlopen.call_args.args[0]
        self.assertEqual(request.full_url, "https://api.zapier.com/v2/zaps")
        self.assertEqual(request.get_header("Authorization"), "Bearer test-token")
        self.assertEqual(response["data"]["id"], "zap-123")

    def test_action_mapping_is_required(self):
        workflow = self.workflow()
        workflow.steps[0].config.pop("zapier_action")
        with self.assertRaisesRegex(RuntimeError, "zapier_action"):
            ZapierIntegration(CredentialManager(environ={"ZAPIER_API_TOKEN": "x"})).artifact(workflow)

    @patch("integrations.zapier.ZapierClient.create_zap")
    def test_deploy_returns_created_zap(self, mock_create):
        mock_create.return_value = {"data": {"id": "zap-456", "title": "Test Zap", "is_enabled": False}}
        integration = ZapierIntegration(CredentialManager(environ={"ZAPIER_API_TOKEN": "x"}))
        result = integration.deploy(self.workflow())
        self.assertEqual(result["status"], "created")
        self.assertEqual(result["zap_id"], "zap-456")
        self.assertFalse(result["enabled"])


if __name__ == "__main__":
    unittest.main()
