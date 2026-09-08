import unittest

from core.orchestrator import Orchestrator
from core.production import ProductionDeployer
from models.deployment import DeploymentStatus
from models.workflow import WorkflowPlan, WorkflowStep


class V8ProductionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.orchestrator = Orchestrator()
        self.production = ProductionDeployer()

    def workflow(self) -> WorkflowPlan:
        return WorkflowPlan(
            name="release_test",
            request="Receive a webhook and send the result to Gmail",
            description="V8 release test",
            provider="generic",
            steps=[
                WorkflowStep(id="step_1", type="trigger", app="webhook", action="receive_request"),
                WorkflowStep(
                    id="step_2",
                    type="action",
                    app="gmail",
                    action="send_email",
                    config={"to": "configure_recipient", "body": "previous_step.output"},
                    depends_on=["step_1"],
                ),
            ],
        )

    def test_v8_prepare_release(self) -> None:
        plan = self.production.prepare(self.workflow(), environment="staging")

        self.assertTrue(plan.release_id.startswith("rel-"))
        self.assertEqual(plan.environment.value, "staging")
        self.assertEqual(len(plan.artifact_sha256), 64)
        self.assertTrue(plan.artifact)

    def test_v8_deploy_is_safe_dry_run(self) -> None:
        record = self.production.deploy(self.workflow(), environment="production", dry_run=True)

        self.assertEqual(record.status, DeploymentStatus.PLANNED)
        self.assertTrue(record.dry_run)
        self.assertEqual(record.environment.value, "production")

    def test_v8_live_deploy_is_explicitly_blocked(self) -> None:
        with self.assertRaises(RuntimeError):
            self.production.deploy(self.workflow(), environment="production", dry_run=False)

    def test_v8_rollback_and_health(self) -> None:
        record = self.production.deploy(self.workflow())
        rolled_back = self.production.rollback(record.release_id)
        health = self.production.health(record.release_id)

        self.assertEqual(rolled_back.status, DeploymentStatus.ROLLED_BACK)
        self.assertFalse(health["healthy"])
        self.assertEqual(health["status"], "rolled_back")

    def test_v8_orchestrator_release(self) -> None:
        result = self.orchestrator.release(
            "Create a webhook workflow that sends the result to Gmail",
            environment="staging",
            dry_run=True,
        )

        self.assertEqual(result["environment"], "staging")
        self.assertTrue(result["dry_run"])
        self.assertIn("release_id", result)

    def test_v8_rejects_unknown_environment(self) -> None:
        with self.assertRaises(ValueError):
            self.production.prepare(self.workflow(), environment="production-ish")


if __name__ == "__main__":
    unittest.main()
