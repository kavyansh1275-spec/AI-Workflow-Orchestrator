from __future__ import annotations

import unittest

from fastapi.testclient import TestClient

from ui.app import app


class UiV3Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_health_reports_ui_v3(self) -> None:
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["ui"], "8.2.0")

    def test_event_websocket_streams_safe_run(self) -> None:
        with self.client.websocket_connect("/ws/events") as websocket:
            websocket.send_json({
                "request": "When a form is submitted, send an email notification",
                "environment": "staging",
            })
            first = websocket.receive_json()
            self.assertEqual(first["type"], "run_started")
            events = []
            while True:
                message = websocket.receive_json()
                if message["type"] == "event":
                    events.append(message["event"])
                elif message["type"] == "run_completed":
                    self.assertTrue(message["result"]["dry_run"])
                    break
            self.assertGreaterEqual(len(events), 8)

    def test_no_live_mutation_routes_are_exposed(self) -> None:
        paths = {route.path for route in app.routes}
        self.assertNotIn("/api/deploy", paths)
        self.assertNotIn("/api/lifecycle", paths)
        self.assertIn("/ws/events", paths)


if __name__ == "__main__":
    unittest.main()
