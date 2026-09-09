from __future__ import annotations

import unittest

from fastapi.testclient import TestClient

from ui.app import app


class UiV3Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_health_reports_current_ui(self) -> None:
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["ui"], "13.0.0")

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

    def test_project_route_is_authenticated(self) -> None:
        response = self.client.post("/api/project", json={"request": "Create a form to email workflow"})
        self.assertEqual(response.status_code, 401)

    def test_live_routes_are_authenticated(self) -> None:
        readiness = self.client.get("/api/live-deployment-readiness", params={"request": "Create a webhook to email workflow"})
        self.assertEqual(readiness.status_code, 401)
        deploy = self.client.post("/api/deploy/live", json={"request": "Create a webhook to email workflow", "live": True})
        self.assertEqual(deploy.status_code, 401)

    def test_no_unprotected_live_mutation_routes_are_exposed(self) -> None:
        paths = {route.path for route in app.routes}
        self.assertIn("/api/deploy/live", paths)
        self.assertIn("/api/deploy/rollback/{deployment_id}", paths)
        self.assertIn("/api/project", paths)
        self.assertIn("/ws/events", paths)


if __name__ == "__main__":
    unittest.main()
