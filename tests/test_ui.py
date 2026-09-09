from __future__ import annotations

import unittest

from ui.app import app


class UiStructureTests(unittest.TestCase):
    def test_fastapi_app_exists(self) -> None:
        paths = {route.path for route in app.routes}
        self.assertIn("/", paths)
        self.assertIn("/api/health", paths)
        self.assertIn("/api/analyze", paths)
        self.assertIn("/api/run", paths)

    def test_ui_is_safe_dry_run_only(self) -> None:
        paths = {route.path for route in app.routes}
        self.assertNotIn("/api/deploy", paths)
        self.assertNotIn("/api/lifecycle", paths)


if __name__ == "__main__":
    unittest.main()
