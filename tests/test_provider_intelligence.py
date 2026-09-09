from __future__ import annotations

import unittest

from core.provider_intelligence import ProviderIntelligence


class ProviderIntelligenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.intelligence = ProviderIntelligence()

    def test_known_n8n_mapping(self) -> None:
        mapping = self.intelligence.map_step("n8n", "gmail", "send_email")
        self.assertEqual(mapping.native, "n8n-nodes-base.gmail")
        self.assertGreater(mapping.confidence, 0.0)

    def test_known_make_mapping(self) -> None:
        mapping = self.intelligence.map_step("make", "slack", "send_message")
        self.assertEqual(mapping.native, "slack.createMessage")

    def test_known_zapier_mapping(self) -> None:
        mapping = self.intelligence.map_step("zapier", "webhook", "receive_request")
        self.assertEqual(mapping.native, "webhooks.catch_hook")

    def test_unknown_mapping_is_explicit(self) -> None:
        mapping = self.intelligence.map_step("zapier", "unknown", "thing")
        self.assertEqual(mapping.confidence, 0.0)
        self.assertEqual(mapping.native, "")

    def test_validate_reports_unknown_steps(self) -> None:
        unsupported = self.intelligence.validate(
            "zapier",
            [
                {"app": "gmail", "action": "send_email"},
                {"app": "unknown", "action": "thing"},
            ],
        )
        self.assertEqual(unsupported, ["unknown.thing"])

    def test_enrich_adds_native_metadata(self) -> None:
        result = self.intelligence.enrich(
            "n8n",
            [{"id": "step-1", "app": "slack", "action": "send_message"}],
        )
        self.assertEqual(result[0]["provider_native"], "n8n-nodes-base.slack")
        self.assertGreater(result[0]["mapping_confidence"], 0.0)


if __name__ == "__main__":
    unittest.main()
