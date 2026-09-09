from __future__ import annotations
import unittest
from unittest.mock import MagicMock
from core.solution_designer import AutonomousSolutionDesigner
from core.validator import AutonomousValidator
from core.deployment_planner import AutonomousDeploymentPlanner
from core.control_loop import AutonomousControlLoop

class TestV17V20(unittest.TestCase):
    def _mock(self):
        o=MagicMock()
        o.research.return_value={"integrations":[{"name":"webhook"}],"risks":[],"gaps":[]}
        o.build_multi_project.return_value={"workflows":[{"workflow_id":"wf-01","provider":"n8n","name":"Webhook","depends_on":[],"shared_inputs":[],"shared_outputs":["wf-01.result"]}]}
        o.simulate.return_value=["trigger simulated"]
        o.decide.return_value={"provider":"n8n","confidence":0.9}
        o.validate_solution.return_value={"passed":True,"status":"passed","gaps":[]}
        o.plan_deployment.return_value={"status":"ready_for_authorization"}
        return o
    def test_v17_solution(self): self.assertEqual(AutonomousSolutionDesigner(self._mock()).design("Receive webhook").status,"ready_for_validation")
    def test_v18_validation(self): self.assertTrue(AutonomousValidator(self._mock()).validate("Receive webhook").passed)
    def test_v19_deployment_requires_authorization(self): self.assertTrue(AutonomousDeploymentPlanner(self._mock()).plan("Receive webhook").authorization["required"])
    def test_v20_control_loop_is_safe(self):
        result=AutonomousControlLoop(self._mock()).run("Receive webhook")
        self.assertEqual(result.status,"ready_for_authorization"); self.assertFalse(result.recovery["live_mutation"])

if __name__ == "__main__": unittest.main()
