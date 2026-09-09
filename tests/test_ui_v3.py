from __future__ import annotations
import unittest
from fastapi.testclient import TestClient
from ui.app import app
class UiV3Tests(unittest.TestCase):
    def setUp(self): self.client=TestClient(app)
    def test_health_reports_current_ui(self):
        response=self.client.get("/api/health"); self.assertEqual(response.status_code,200); self.assertEqual(response.json()["ui"],"20.0.0")
    def test_event_websocket_streams_safe_run(self):
        with self.client.websocket_connect("/ws/events") as websocket:
            websocket.send_json({"request":"When a form is submitted, send an email notification","environment":"staging"}); first=websocket.receive_json(); self.assertEqual(first["type"],"run_started")
            events=[]
            while True:
                message=websocket.receive_json()
                if message["type"]=="event": events.append(message["event"])
                elif message["type"]=="run_completed": self.assertTrue(message["result"]["dry_run"]); break
            self.assertGreaterEqual(len(events),8)
    def test_new_intelligence_routes_are_authenticated(self):
        for path in ["/api/research","/api/solution","/api/validation","/api/deployment-plan","/api/control-loop"]:
            response=self.client.get(path,params={"request":"Receive a webhook and notify Slack"}); self.assertEqual(response.status_code,401,path)
    def test_mutation_routes_are_authenticated(self):
        for path in ["/api/project","/api/multi-project","/api/agent","/api/deploy/live"]:
            response=self.client.post(path,json={"request":"Receive a webhook and notify Slack"}); self.assertEqual(response.status_code,401,path)
    def test_routes_exist(self):
        paths={route.path for route in app.routes}
        for path in ["/api/research","/api/solution","/api/validation","/api/deployment-plan","/api/control-loop","/api/agent","/ws/events"]: self.assertIn(path,paths)
if __name__=="__main__": unittest.main()
