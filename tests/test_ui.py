from __future__ import annotations

import unittest

from ui.app import app


class UiStructureTests(unittest.TestCase):
    def test_fastapi_app_exists(self) -> None:
        paths = {route.path for route in app.routes}
        for path in (
            "/",
            "/api/health",
            "/api/analyze",
            "/api/run",
            "/api/operate",
            "/api/operations",
            "/api/releases",
            "/api/provider-tests",
        ):
            self.assertIn(path, paths)

    def test_ui_is_safe_dry_run_only(self) -> None:
        paths = {route.path for route in app.routes}
        self.assertNotIn("/api/deploy", paths)
        self.assertNotIn("/api/lifecycle", paths)


if __name__ == "__main__":
    unittest.main()
