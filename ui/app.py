from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, WebSocket, WebSocketDisconnect, status
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, Field

from core.auth import create_access_token, current_username, hash_password, verify_password
from core.auth_store import AuthStore
from core.orchestrator import Orchestrator
from core.v10 import V10Engine


ROOT = Path(__file__).resolve().parent
orchestrator = Orchestrator()
engine = V10Engine(orchestrator=orchestrator)
store = AuthStore()
app = FastAPI(
    title="AI Workflow Orchestrator",
    version="14.0.0",
    description="Authenticated multi-user control center with V14 autonomous multi-workflow project planning.",
)


class RequestBody(BaseModel):
    request: str = Field(min_length=1, max_length=4000)
    environment: str = "staging"
    live: bool = False


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "ui": "14.0.0", "mode": "safe"}


@app.post("/api/auth/register")
def register(form: OAuth2PasswordRequestForm = Depends()) -> dict[str, str]:
    try:
        store.create_user(form.username, hash_password(form.password))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"message": "registered"}


@app.post("/api/auth/login")
def login(form: OAuth2PasswordRequestForm = Depends()) -> dict[str, str]:
    user = store.get_user(form.username)
    if not user or not verify_password(form.password, user["password_hash"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid credentials")
    return {"access_token": create_access_token(form.username), "token_type": "bearer"}


@app.get("/api/auth/me")
def me(username: str = Depends(current_username)) -> dict[str, str]:
    return {"username": username}


@app.post("/api/run")
def run(body: RequestBody, username: str = Depends(current_username)) -> dict[str, Any]:
    result = engine.run(body.request, environment=body.environment, dry_run=True).model_dump(mode="json")
    store.save_workflow(username, body.request, body.environment, json.dumps(result), datetime.now(timezone.utc).isoformat())
    return result


@app.post("/api/project")
def project(body: RequestBody, username: str = Depends(current_username)) -> dict[str, Any]:
    try:
        payload = orchestrator.build_project(body.request, environment=body.environment)
        store.save_workflow(username, body.request, body.environment, json.dumps(payload), datetime.now(timezone.utc).isoformat())
        return payload
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/multi-project")
def multi_project(body: RequestBody, username: str = Depends(current_username)) -> dict[str, Any]:
    try:
        payload = orchestrator.build_multi_project(body.request, environment=body.environment)
        store.save_workflow(username, body.request, body.environment, json.dumps(payload), datetime.now(timezone.utc).isoformat())
        return payload
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/api/integration-intelligence")
def integration_intelligence(request: str, _: str = Depends(current_username)) -> dict[str, Any]:
    try:
        return orchestrator.integration_intelligence(request)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/api/live-deployment-readiness")
def live_deployment_readiness(request: str, _: str = Depends(current_username)) -> dict[str, Any]:
    try:
        return orchestrator.live_deployment_readiness(request)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/deploy/live")
def deploy_live(body: RequestBody, _: str = Depends(current_username)) -> dict[str, Any]:
    try:
        return orchestrator.live_deploy(body.request, live=body.live)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/deploy/rollback/{deployment_id}")
def rollback_live(deployment_id: str, _: str = Depends(current_username)) -> dict[str, Any]:
    try:
        return orchestrator.live_rollback(deployment_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.websocket("/ws/events")
async def events(websocket: WebSocket) -> None:
    await websocket.accept()
    try:
        payload = await websocket.receive_json()
        request = str(payload.get("request", "")).strip()
        environment = str(payload.get("environment", "staging"))
        if not request:
            await websocket.send_json({"type": "error", "detail": "request is required"})
            return
        await websocket.send_json({"type": "run_started", "request": request})
        run = engine.run(request, environment=environment, dry_run=True)
        for event in run.events:
            await websocket.send_json({"type": "event", "event": event.model_dump(mode="json")})
        await websocket.send_json({"type": "run_completed", "result": run.model_dump(mode="json")})
    except WebSocketDisconnect:
        return
    except Exception as exc:
        await websocket.send_json({"type": "error", "detail": str(exc)})
    finally:
        try:
            await websocket.close()
        except Exception:
            pass


@app.get("/")
def root() -> FileResponse:
    return FileResponse(ROOT / "index.html")
