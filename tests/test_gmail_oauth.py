from __future__ import annotations

import unittest
from unittest.mock import patch

from core.gmail_connections import GmailConnectionManager
from integrations.gmail_oauth import GmailOAuth, GMAIL_SEND_SCOPE


class GmailOAuthTests(unittest.TestCase):
    def test_authorization_url_uses_send_scope(self) -> None:
        oauth = GmailOAuth("client", "secret", "http://localhost/callback")
        url = oauth.authorization_url("state123")
        self.assertIn("client_id=client", url)
        self.assertIn("state=state123", url)
        self.assertIn("gmail.send", url)

    def test_missing_client_id_is_rejected(self) -> None:
        oauth = GmailOAuth(None, "secret")
        with patch.dict("os.environ", {}, clear=True):
            with self.assertRaises(RuntimeError):
                oauth.authorization_url("state")

    def test_connection_state_and_metadata(self) -> None:
        oauth = GmailOAuth("client", "secret", "http://localhost/callback")
        manager = GmailConnectionManager(oauth)
        url = manager.begin("client-gmail")
        self.assertIn("accounts.google.com", url)
        connection = manager.complete("client-gmail", "client@example.com")
        self.assertEqual(connection["status"], "connected")
        self.assertEqual(connection["scopes"], [GMAIL_SEND_SCOPE])
        self.assertFalse(connection["token_stored"])

    def test_state_is_one_time(self) -> None:
        oauth = GmailOAuth("client", "secret")
        manager = GmailConnectionManager(oauth)
        url = manager.begin("client-gmail")
        state = url.split("state=", 1)[1]
        self.assertTrue(manager.consume_state(state))
        self.assertFalse(manager.consume_state(state))


if __name__ == "__main__":
    unittest.main()
