from __future__ import annotations
import unittest
from unittest.mock import MagicMock
from core.workflow_builder import AutonomousWorkflowBuilder
from core.workflow_deployment import AutonomousWorkflowDeployment
from core.workflow_repair import AutonomousWorkflowRepair
from core.final_workflow import FinalWorkflowPipeline

class TestV21V24(unittest.TestCase):
    def mock_orchestrator(self):
        o=MagicMock()
        o.design_solution.return_value={"workflows":[{"name":"Lead Intake","provider":"n8n","trigger":"webhook","actions":[{"app":"google_sheets","action":"create_row"}],"depends_on":[]}]}
        o.decide.return_value={"provider":"n8n"}
        o.build.return_value=MagicMock(provider="n8n")
        o.generator.generate.return_value={"format":"n8n","nodes":[]}
        o.live_deployment_readiness.return_value={"ready":True}
        o.live_deploy.return_value={"status":"deployed"}
        o.build_workflow.return_value={"status":"built","provider":"n8n","workflow":{"format":"n8n","nodes":[]}}
        o.validate_solution.return_value={"passed":True,"status":"passed"}
        o.simulate.return_value=["ok"]
        o.test_and_repair.return_value={"passed":True,"status":"passed","attempts":1,"final_artifact":{"format":"n8n"}}
        o.deploy_workflow.return_value={"status":"ready_for_authorization"}
        return o

    def test_v21_builds_workflow(self):
        result=AutonomousWorkflowBuilder(self.mock_orchestrator()).build("Receive leads")
        self.assertEqual(result.status,"built")
        self.assertEqual(result.provider,"n8n")

    def test_v22_stays_safe_without_live_flag(self):
        result=AutonomousWorkflowDeployment(self.mock_orchestrator()).prepare("Receive leads")
        self.assertEqual(result.status,"ready_for_authorization")
        self.assertFalse(result.deployment["authorized"])

    def test_v23_tests_and_repairs(self):
        result=AutonomousWorkflowRepair(self.mock_orchestrator()).run("Receive leads")
        self.assertTrue(result.passed)
        self.assertEqual(result.attempts,1)

    def test_v24_final_pipeline(self):
        result=FinalWorkflowPipeline(self.mock_orchestrator()).run("Receive leads")
        self.assertTrue(result.passed)
        self.assertEqual(result.status,"complete")
        self.assertEqual(len(result.stages),3)

if __name__ == "__main__":
    unittest.main()
