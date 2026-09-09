import json
import unittest
from unittest.mock import patch

from core.credentials import CredentialManager
from integrations.n8n import N8nIntegration
from integrations.n8n_client import N8nClient
from models.workflow import WorkflowPlan, WorkflowStep


class FakeResponse:
    def __init__(self, payload: dict) -> None:
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return None

    def read(self):
        return json.dumps(self.payload).encode("utf-8")


class N8nTests(unittest.TestCase):
    def setUp(self) -> None:
        self.workflow = WorkflowPlan(
            name="n8n-live-test",
            request="Receive a webhook and send an email",
            description="Test workflow",
            provider="n8n",
            steps=[
                WorkflowStep(
                    id="step_1",
                    type="trigger",
                    app="webhook",
                    action="receive_request",
                    config={"path": "incoming"},
                ),
                WorkflowStep(
                    id="step_2",
                    type="action",
                    app="gmail",
                    action="send_email",
                    depends_on=["step_1"],
                    config={"to": "test@example.com"},
                ),
            ],
        )

    def test_missing_credentials_block_live_deployment(self) -> None:
        integration = N8nIntegration(CredentialManager({}))
        with self.assertRaises(RuntimeError):
            integration.deploy(self.workflow)

    def test_client_sends_n8n_api_key(self) -> None:
        seen = {}

        def opener(request, timeout):
            seen["url"] = request.full_url
            seen["method"] = request.method
            seen["key"] = request.get_header("X-n8n-api-key")
            return FakeResponse({"id": "wf_123", "name": "demo", "active": False})

        client = N8nClient("https://n8n.example.com", "secret-key", opener=opener)
        result = client.create_workflow({"name": "demo", "nodes": [], "connections": {}})
        self.assertEqual(result["id"], "wf_123")
        self.assertEqual(seen["url"], "https://n8n.example.com/api/v1/workflows")
        self.assertEqual(seen["method"], "POST")
        self.assertEqual(seen["key"], "secret-key")

    def test_client_quotes_workflow_id(self) -> None:
        seen = {}

        def opener(request, timeout):
            seen["url"] = request.full_url
            return FakeResponse({"id": "wf"})

        client = N8nClient("https://n8n.example.com", "secret-key", opener=opener)
        client.get_workflow("wf/with spaces")
        self.assertEqual(seen["url"], "https://n8n.example.com/api/v1/workflows/wf%2Fwith%20spaces")

    def test_update_uses_put(self) -> None:
        seen = {}

        def opener(request, timeout):
            seen["method"] = request.method
            return FakeResponse({"id": "wf_123"})

        client = N8nClient("https://n8n.example.com", "secret-key", opener=opener)
        client.update_workflow("wf_123", {"name": "updated"})
        self.assertEqual(seen["method"], "PUT")

    def test_payload_uses_n8n_connection_shape(self) -> None:
        credentials = CredentialManager({"N8N_API_KEY": "secret", "N8N_BASE_URL": "https://n8n.example.com"})
        integration = N8nIntegration(credentials)
        payload = integration._payload(self.workflow)
        self.assertEqual(payload["name"], "n8n-live-test")
        self.assertNotIn("active", payload)
        self.assertEqual(payload["connections"]["webhook: receive_request"]["main"][0][0]["node"], "gmail: send_email")

    @patch("integrations.n8n.N8nClient.create_workflow")
    def test_deploy_returns_created_workflow(self, create_workflow) -> None:
        create_workflow.return_value = {"id": "wf_456", "name": "n8n-live-test", "active": False}
        credentials = CredentialManager({"N8N_API_KEY": "secret", "N8N_BASE_URL": "https://n8n.example.com"})
        result = N8nIntegration(credentials).deploy(self.workflow)
        self.assertEqual(result["status"], "created")
        self.assertEqual(result["workflow_id"], "wf_456")
        create_workflow.assert_called_once()


if __name__ == "__main__":
    unittest.main()
