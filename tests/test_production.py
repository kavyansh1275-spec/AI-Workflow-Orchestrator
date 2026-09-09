from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class ProductionPackagingTests(unittest.TestCase):
    def test_dockerfile_exists_and_uses_safe_server_command(self) -> None:
        dockerfile = (ROOT / "Dockerfile").read_text(encoding="utf-8")
        self.assertIn("FROM python:3.12-slim", dockerfile)
        self.assertIn('"uvicorn", "ui.app:app"', dockerfile)
        self.assertIn('"--host", "0.0.0.0"', dockerfile)
        self.assertIn('"--port", "8000"', dockerfile)

    def test_dockerignore_excludes_secrets_and_local_state(self) -> None:
        ignore = (ROOT / ".dockerignore").read_text(encoding="utf-8")
        for entry in (".env", ".env.*", "*.db", "__pycache__"):
            self.assertIn(entry, ignore)

    def test_compose_requires_jwt_secret_from_environment(self) -> None:
        compose = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")
        self.assertIn("JWT_SECRET: ${JWT_SECRET}", compose)
        self.assertIn("restart: unless-stopped", compose)


if __name__ == "__main__":
    unittest.main()
