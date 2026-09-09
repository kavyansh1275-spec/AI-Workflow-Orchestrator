import json
import unittest
from core.credentials import CredentialManager
from integrations.make import MakeIntegration
from integrations.make_client import MakeClient
from models.workflow import WorkflowPlan, WorkflowStep


class FakeResponse:
    def __init__(self, payload): self.payload = payload
    def __enter__(self): return self
    def __exit__(self, *args): return None
    def read(self): return json.dumps(self.payload).encode()


class MakeTests(unittest.TestCase):
    def setUp(self):
        self.workflow = WorkflowPlan(
            name="make-live-test", request="Receive webhook and send email",
            description="Test workflow", provider="make",
            steps=[
                WorkflowStep(id="step_1", type="trigger", app="webhook", action="receive_request", config={"path": "incoming"}),
                WorkflowStep(id="step_2", type="action", app="gmail", action="send_email", depends_on=["step_1"], config={"to": "test@example.com"}),
            ],
        )

    def test_missing_credentials_block_deployment(self):
        with self.assertRaises(RuntimeError):
            MakeIntegration(CredentialManager({})).deploy(self.workflow)

    def test_client_auth_and_create_endpoint(self):
        seen = {}
        def opener(request, timeout):
            seen.update(url=request.full_url, method=request.method, auth=request.get_header("Authorization"), body=request.data)
            return FakeResponse({"scenario": {"id": 123, "name": "demo", "isActive": False}})
        client = MakeClient("https://eu1.make.com", "secret", 42, opener=opener)
        result = client.create_scenario("{}", '{"type":"on-demand"}', "demo")
        self.assertEqual(result["scenario"]["id"], 123)
        self.assertEqual(seen["url"], "https://eu1.make.com/api/v2/scenarios")
        self.assertEqual(seen["method"], "POST")
        self.assertEqual(seen["auth"], "Token secret")
        self.assertEqual(json.loads(seen["body"])["teamId"], 42)

    def test_blueprint_is_serialized(self):
        integration = MakeIntegration(CredentialManager({"MAKE_API_TOKEN": "secret", "MAKE_BASE_URL": "https://eu1.make.com"}))
        with unittest.mock.patch.dict("os.environ", {"MAKE_TEAM_ID": "42"}):
            blueprint = integration._blueprint(self.workflow)
        payload = json.loads(blueprint)
        self.assertEqual(len(payload["subflows"]), 1)
        self.assertEqual(len(payload["subflows"][0]["flow"]), 2)

    def test_deploy_returns_scenario(self):
        credentials = CredentialManager({"MAKE_API_TOKEN": "secret", "MAKE_BASE_URL": "https://eu1.make.com"})
        with unittest.mock.patch.dict("os.environ", {"MAKE_TEAM_ID": "42"}), unittest.mock.patch("integrations.make.MakeClient.create_scenario") as create:
            create.return_value = {"scenario": {"id": 456, "name": "make-live-test", "isActive": False}}
            result = MakeIntegration(credentials).deploy(self.workflow)
        self.assertEqual(result["status"], "created")
        self.assertEqual(result["scenario_id"], 456)


if __name__ == "__main__": unittest.main()
