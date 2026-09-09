from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from core.orchestrator import Orchestrator


ROOT = Path(__file__).resolve().parent
orchestrator = Orchestrator()
app = FastAPI(title="AI Workflow Orchestrator", version="8.0.0", description="Safe web interface for the workflow orchestration engine.")


class RequestBody(BaseModel):
    request: str = Field(min_length=1, max_length=4000)
    environment: str = "staging"


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    return FileResponse(ROOT / "static" / "index.html")


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "mode": "safe-dry-run"}


@app.get("/api/credentials")
def credentials() -> dict[str, dict[str, str | None]]:
    return orchestrator.credential_status()


@app.get("/api/providers")
def providers() -> dict[str, list[str]]:
    return orchestrator.list_integrations()


@app.post("/api/analyze")
def analyze(body: RequestBody) -> dict[str, Any]:
    try:
        return {
            "analysis": orchestrator.analyze(body.request),
            "decision": orchestrator.decide(body.request),
            "workflow": orchestrator.build(body.request).model_dump(mode="json"),
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/run")
def run(body: RequestBody) -> dict[str, Any]:
    try:
        # The UI intentionally exposes only the safe V10 dry-run pipeline.
        from core.v10 import V10Engine

        result = V10Engine(orchestrator=orchestrator).run(
            body.request,
            environment=body.environment,
            dry_run=True,
        )
        return result.model_dump(mode="json")
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/api/integrations")
def integrations() -> dict[str, list[str]]:
    return orchestrator.list_integrations()
