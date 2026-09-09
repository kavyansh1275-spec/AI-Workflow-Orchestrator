from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from core.orchestrator import Orchestrator
from core.v10 import V10Engine


ROOT = Path(__file__).resolve().parent
orchestrator = Orchestrator()
engine = V10Engine(orchestrator=orchestrator)
app = FastAPI(
    title="AI Workflow Orchestrator",
    version="8.2.0",
    description="Safe web control center for the workflow orchestration engine.",
)


class RequestBody(BaseModel):
    request: str = Field(min_length=1, max_length=4000)
    environment: str = "staging"


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    return FileResponse(ROOT / "static" / "index.html")


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "mode": "safe-dry-run", "ui": "8.2.0"}


@app.get("/api/credentials")
def credentials() -> dict[str, dict[str, str | None]]:
    return orchestrator.credential_status()


@app.get("/api/providers")
def providers() -> dict[str, list[str]]:
    return orchestrator.list_integrations()


@app.get("/api/integrations")
def integrations() -> dict[str, list[str]]:
    return orchestrator.list_integrations()


@app.get("/api/operations")
def operations() -> list[dict[str, Any]]:
    return orchestrator.operation_history()


@app.get("/api/releases")
def releases() -> list[dict[str, Any]]:
    return orchestrator.deployment_history()


@app.get("/api/provider-tests")
def provider_tests() -> dict[str, dict[str, Any]]:
    return orchestrator.provider_smoke_tests()


@app.post("/api/analyze")
def analyze(body: RequestBody) -> dict[str, Any]:
    try:
        workflow = orchestrator.build(body.request)
        return {
            "analysis": orchestrator.analyze(body.request),
            "decision": orchestrator.decide(body.request),
            "workflow": workflow.model_dump(mode="json"),
            "integrations": orchestrator.inspect_integrations(body.request),
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/run")
def run(body: RequestBody) -> dict[str, Any]:
    try:
        result = engine.run(body.request, environment=body.environment, dry_run=True)
        return result.model_dump(mode="json")
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/operate")
def operate(body: RequestBody) -> dict[str, Any]:
    try:
        return orchestrator.operate(body.request, dry_run=True)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.websocket("/ws/events")
async def event_stream(websocket: WebSocket) -> None:
    """Stream a completed safe V10 run as ordered UI events.

    The engine itself remains synchronous and deterministic. The websocket gives the
    browser a live event channel without exposing provider mutations or credentials.
    """
    await websocket.accept()
    try:
        payload = await websocket.receive_json()
        body = RequestBody.model_validate(payload)
        result = engine.run(body.request, environment=body.environment, dry_run=True)
        await websocket.send_json({"type": "run_started", "status": result.status})
        for event in result.events:
            await websocket.send_json({"type": "event", "event": event.model_dump(mode="json")})
        await websocket.send_json({"type": "run_completed", "result": result.model_dump(mode="json")})
    except WebSocketDisconnect:
        return
    except Exception as exc:
        await websocket.send_json({"type": "error", "message": str(exc)})
    finally:
        await websocket.close()
