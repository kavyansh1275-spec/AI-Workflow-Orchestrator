import unittest

from core.credentials import CredentialManager
from models.credentials import CredentialStatus


class CredentialManagerTests(unittest.TestCase):
    def test_missing_credentials_are_reported_without_secrets(self) -> None:
        manager = CredentialManager({})
        status = manager.status()

        self.assertEqual(status["n8n"]["status"], CredentialStatus.MISSING.value)
        self.assertIsNone(status["n8n"]["api_key"])

    def test_credentials_are_loaded_from_environment(self) -> None:
        manager = CredentialManager(
            {
                "N8N_API_KEY": "n8n-test-secret-1234",
                "N8N_BASE_URL": "https://example.invalid",
            }
        )
        credential = manager.get("n8n")

        self.assertEqual(credential.status, CredentialStatus.CONFIGURED)
        self.assertEqual(credential.base_url, "https://example.invalid")
        self.assertEqual(credential.masked()["api_key"], "n8n-...1234")

    def test_require_fails_with_actionable_message_when_missing(self) -> None:
        manager = CredentialManager({})

        with self.assertRaisesRegex(RuntimeError, "MAKE_API_TOKEN"):
            manager.require("make")

    def test_unknown_provider_is_rejected(self) -> None:
        manager = CredentialManager({})

        with self.assertRaisesRegex(ValueError, "unsupported credential provider"):
            manager.get("unknown")


if __name__ == "__main__":
    unittest.main()
