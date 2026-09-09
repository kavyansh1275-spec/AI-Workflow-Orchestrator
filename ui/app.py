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
ROOT=Path(__file__).resolve().parent; orchestrator=Orchestrator(); engine=V10Engine(orchestrator=orchestrator); store=AuthStore()
app=FastAPI(title="AI Workflow Orchestrator",version="20.0.0",description="Authenticated autonomous automation control center with V20 closed-loop intelligence.")
class RequestBody(BaseModel):
    request:str=Field(min_length=1,max_length=4000); environment:str="staging"; live:bool=False
class RegisterBody(BaseModel):
    username:str=Field(min_length=3,max_length=64,pattern=r"^[A-Za-z0-9_.-]+$"); password:str=Field(min_length=8,max_length=128)
@app.get("/",include_in_schema=False)
def index(): return FileResponse(ROOT/"static"/"index.html")
@app.get("/api/health")
def health(): return {"status":"ok","mode":"authenticated-safe-v20","ui":"20.0.0"}
@app.post("/api/auth/register",status_code=status.HTTP_201_CREATED)
def register(body:RegisterBody):
    if not store.create_user(body.username,hash_password(body.password),datetime.now(timezone.utc).isoformat()): raise HTTPException(409,"Username already exists")
    return {"username":body.username,"status":"created"}
@app.post("/api/auth/token")
def token(form:OAuth2PasswordRequestForm=Depends()):
    user=store.get_user(form.username)
    if not user or bool(user["disabled"]) or not verify_password(form.password,str(user["hashed_password"])): raise HTTPException(401,"Incorrect username or password",headers={"WWW-Authenticate":"Bearer"})
    return {"access_token":create_access_token(form.username),"token_type":"bearer"}
@app.get("/api/auth/me")
def me(username:str=Depends(current_username)): return {"username":username}
@app.get("/api/credentials")
def credentials(_:str=Depends(current_username)): return orchestrator.credential_status()
@app.get("/api/providers")
def providers(_:str=Depends(current_username)): return orchestrator.list_integrations()
@app.get("/api/integrations")
def integrations(_:str=Depends(current_username)): return orchestrator.list_integrations()
@app.get("/api/integration-intelligence")
def integration_intelligence(request:str,_:str=Depends(current_username)): return orchestrator.integration_intelligence(request)
@app.get("/api/research")
def research(request:str,_:str=Depends(current_username)): return orchestrator.research(request)
@app.get("/api/solution")
def solution(request:str,_:str=Depends(current_username)): return orchestrator.design_solution(request)
@app.get("/api/validation")
def validation(request:str,_:str=Depends(current_username)): return orchestrator.validate_solution(request)
@app.get("/api/deployment-plan")
def deployment_plan(request:str,environment:str="staging",_:str=Depends(current_username)): return orchestrator.plan_deployment(request,environment=environment)
@app.get("/api/control-loop")
def control_loop(request:str,environment:str="staging",_:str=Depends(current_username)): return orchestrator.control_loop(request,environment=environment)
@app.get("/api/live-deployment-readiness")
def live_deployment_readiness(request:str,_:str=Depends(current_username)): return orchestrator.live_deployment_readiness(request)
@app.get("/api/operations")
def operations(_:str=Depends(current_username)): return orchestrator.operation_history()
@app.get("/api/releases")
def releases(_:str=Depends(current_username)): return orchestrator.deployment_history()
@app.get("/api/provider-tests")
def provider_tests(_:str=Depends(current_username)): return orchestrator.provider_smoke_tests()
@app.get("/api/workflows")
def workflows(username:str=Depends(current_username)): return store.list_workflows(username)
@app.post("/api/analyze")
def analyze(body:RequestBody,_:str=Depends(current_username)):
    workflow=orchestrator.build(body.request); return {"analysis":orchestrator.analyze(body.request),"decision":orchestrator.decide(body.request),"integration_intelligence":orchestrator.integration_intelligence(body.request),"workflow":workflow.model_dump(mode="json"),"integrations":orchestrator.inspect_integrations(body.request)}
@app.post("/api/project")
def project(body:RequestBody,username:str=Depends(current_username)):
    payload=orchestrator.build_project(body.request,environment=body.environment); store.save_workflow(username,body.request,body.environment,json.dumps(payload),datetime.now(timezone.utc).isoformat()); return payload
@app.post("/api/multi-project")
def multi_project(body:RequestBody,username:str=Depends(current_username)):
    payload=orchestrator.build_multi_project(body.request,environment=body.environment); store.save_workflow(username,body.request,body.environment,json.dumps(payload),datetime.now(timezone.utc).isoformat()); return payload
@app.post("/api/agent")
def agent(body:RequestBody,_:str=Depends(current_username)): return orchestrator.run_agent(body.request,environment=body.environment,authorize_live=body.live)
@app.post("/api/deploy/live")
def deploy_live(body:RequestBody,_:str=Depends(current_username)): return orchestrator.live_deploy(body.request,live=body.live)
@app.post("/api/deploy/rollback/{deployment_id}")
def rollback_live(deployment_id:str,_:str=Depends(current_username)): return orchestrator.live_rollback(deployment_id)
@app.post("/api/run")
def run(body:RequestBody,username:str=Depends(current_username)):
    result=engine.run(body.request,environment=body.environment,dry_run=True); payload=result.model_dump(mode="json"); store.save_workflow(username,body.request,body.environment,json.dumps(payload),datetime.now(timezone.utc).isoformat()); return payload
@app.post("/api/operate")
def operate(body:RequestBody,_:str=Depends(current_username)): return orchestrator.operate(body.request,dry_run=True)
@app.websocket("/ws/events")
async def event_stream(websocket:WebSocket):
    await websocket.accept()
    try:
        body=RequestBody.model_validate(await websocket.receive_json()); result=engine.run(body.request,environment=body.environment,dry_run=True); await websocket.send_json({"type":"run_started","status":result.status})
        for event in result.events: await websocket.send_json({"type":"event","event":event.model_dump(mode="json")})
        await websocket.send_json({"type":"run_completed","result":result.model_dump(mode="json")})
    except WebSocketDisconnect: return
    except Exception as exc: await websocket.send_json({"type":"error","message":str(exc)})
    finally: await websocket.close()
