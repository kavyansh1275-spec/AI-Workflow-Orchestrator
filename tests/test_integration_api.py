from __future__ import annotations

import unittest

from fastapi.testclient import TestClient

from ui.app import app


class IntegrationApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        username = "v12_api_user"
        password = "integration-test-password"
        self.client.post("/api/auth/register", json={"username": username, "password": password})
        token = self.client.post(
            "/api/auth/token",
            data={"username": username, "password": password},
        ).json()["access_token"]
        self.headers = {"Authorization": f"Bearer {token}"}

    def test_integration_intelligence_endpoint(self) -> None:
        response = self.client.get(
            "/api/integration-intelligence",
            params={"request": "When a form is submitted, analyze it with AI, save it to Google Sheets, and email the result."},
            headers=self.headers,
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("forms", payload["recommended_apps"])
        self.assertIn("ai", payload["recommended_apps"])
        self.assertIn("google_sheets", payload["recommended_apps"])
        self.assertIn("gmail", payload["recommended_apps"])

    def test_endpoint_requires_authentication(self) -> None:
        response = self.client.get(
            "/api/integration-intelligence",
            params={"request": "Send an email"},
        )
        self.assertEqual(response.status_code, 401)


if __name__ == "__main__":
    unittest.main()
