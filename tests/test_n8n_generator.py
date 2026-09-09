import unittest

from core.generator import WorkflowGenerator
from models.workflow import WorkflowPlan, WorkflowStep


class N8nGeneratorTests(unittest.TestCase):
    def test_common_apps_map_to_native_n8n_nodes(self) -> None:
        apps = [
            ("webhook", "n8n-nodes-base.webhook"),
            ("schedule", "n8n-nodes-base.scheduleTrigger"),
            ("form", "n8n-nodes-base.formTrigger"),
            ("gmail", "n8n-nodes-base.gmail"),
            ("slack", "n8n-nodes-base.slack"),
            ("discord", "n8n-nodes-base.discord"),
            ("notion", "n8n-nodes-base.notion"),
            ("google_sheets", "n8n-nodes-base.googleSheets"),
            ("airtable", "n8n-nodes-base.airtable"),
            ("telegram", "n8n-nodes-base.telegram"),
            ("http", "n8n-nodes-base.httpRequest"),
            ("ai", "@n8n/n8n-nodes-langchain.openAi"),
        ]
        for app, expected in apps:
            with self.subTest(app=app):
                workflow = WorkflowPlan(
                    name=f"{app}-test",
                    request=f"run {app}",
                    description="test",
                    provider="n8n",
                    steps=[WorkflowStep(id="step_1", type="action", app=app, action="run")],
                )
                artifact = WorkflowGenerator().generate(workflow)
                self.assertEqual(artifact["nodes"][0]["type"], expected)
                self.assertEqual(artifact["nodes"][0]["typeVersion"], 1)

    def test_unknown_apps_keep_fallback_mapping(self) -> None:
        workflow = WorkflowPlan(
            name="custom-test",
            request="run custom",
            description="test",
            provider="n8n",
            steps=[WorkflowStep(id="step_1", type="action", app="customapp", action="run")],
        )
        artifact = WorkflowGenerator().generate(workflow)
        self.assertEqual(artifact["nodes"][0]["type"], "n8n-nodes-base.customapp")


if __name__ == "__main__":
    unittest.main()
