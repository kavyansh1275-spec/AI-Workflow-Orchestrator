from __future__ import annotations

import unittest

from core.integration_intelligence import IntegrationIntelligence


class IntegrationIntelligenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.intelligence = IntegrationIntelligence()

    def test_form_email_and_ai_are_detected(self) -> None:
        result = self.intelligence.analyze(
            "When a form is submitted, analyze the data with AI and send an email notification."
        )
        apps = result["recommended_apps"]
        self.assertIn("forms", apps)
        self.assertIn("ai", apps)
        self.assertIn("gmail", apps)

    def test_sheets_and_slack_are_detected(self) -> None:
        result = self.intelligence.analyze(
            "Save the result to Google Sheets and notify the team in Slack."
        )
        self.assertIn("google_sheets", result["recommended_apps"])
        self.assertIn("slack", result["recommended_apps"])

    def test_unknown_meeting_transcription_is_reported_as_gap(self) -> None:
        result = self.intelligence.analyze(
            "Transcribe a meeting and summarize the transcript."
        )
        self.assertTrue(any("transcription" in gap for gap in result["gaps"]))

    def test_empty_request_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self.intelligence.analyze("   ")


if __name__ == "__main__":
    unittest.main()
