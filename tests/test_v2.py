import unittest

from core.orchestrator import Orchestrator
from core.provider_selector import ProviderSelector


class V2ProviderTests(unittest.TestCase):
    def setUp(self) -> None:
        self.orchestrator = Orchestrator()

    def test_explicit_n8n_provider(self) -> None:
        workflow = self.orchestrator.build("Create an n8n workflow that receives a webhook and sends an email")
        self.assertEqual(workflow.provider, "n8n")

    def test_explicit_make_provider(self) -> None:
        workflow = self.orchestrator.build("Build this in Make.com: receive a form and send an email")
        self.assertEqual(workflow.provider, "make")

    def test_explicit_zapier_provider(self) -> None:
        workflow = self.orchestrator.build("Build this in Zapier: receive a form and send an email")
        self.assertEqual(workflow.provider, "zapier")

    def test_generic_fallback(self) -> None:
        workflow = self.orchestrator.build("Receive a form and send an email")
        self.assertEqual(workflow.provider, "generic")

    def test_dry_run_deployment_is_safe(self) -> None:
        result = self.orchestrator.deploy("Build this in n8n: receive a webhook and send an email")
        self.assertEqual(result["status"], "dry_run")
        self.assertTrue(result["dry_run"])
        self.assertEqual(result["provider"], "n8n")

    def test_provider_selector_is_case_insensitive(self) -> None:
        selector = ProviderSelector()
        self.assertEqual(selector.select("USE ZAPIER FOR THIS"), "zapier")


if __name__ == "__main__":
    unittest.main()
