from __future__ import annotations

import os
import tempfile
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient


class AuthTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        with patch.dict(os.environ, {"AUTH_DB_PATH": os.path.join(self.temp_dir.name, "auth.db")}, clear=False):
            from core.auth_store import AuthStore
            from ui import app as app_module
            app_module.store = AuthStore()
            self.app_module = app_module
            self.client = TestClient(app_module.app)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_register_and_login(self) -> None:
        response = self.client.post("/api/auth/register", json={"username": "kav", "password": "test-password-123"})
        self.assertEqual(response.status_code, 201)
        token = self.client.post(
            "/api/auth/token",
            data={"username": "kav", "password": "test-password-123"},
        )
        self.assertEqual(token.status_code, 200)
        self.assertEqual(token.json()["token_type"], "bearer")

    def test_protected_route_requires_auth(self) -> None:
        response = self.client.get("/api/workflows")
        self.assertEqual(response.status_code, 401)

    def test_user_workflows_are_isolated(self) -> None:
        for username in ("alpha", "bravo"):
            self.client.post("/api/auth/register", json={"username": username, "password": "test-password-123"})

        alpha_token = self.client.post("/api/auth/token", data={"username": "alpha", "password": "test-password-123"}).json()["access_token"]
        bravo_token = self.client.post("/api/auth/token", data={"username": "bravo", "password": "test-password-123"}).json()["access_token"]

        result = self.client.post(
            "/api/run",
            headers={"Authorization": f"Bearer {alpha_token}"},
            json={"request": "When a form is submitted, send an email notification", "environment": "staging"},
        )
        self.assertEqual(result.status_code, 200)

        alpha = self.client.get("/api/workflows", headers={"Authorization": f"Bearer {alpha_token}"})
        bravo = self.client.get("/api/workflows", headers={"Authorization": f"Bearer {bravo_token}"})
        self.assertEqual(len(alpha.json()), 1)
        self.assertEqual(bravo.json(), [])


if __name__ == "__main__":
    unittest.main()
