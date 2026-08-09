from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Header, HTTPException, Response
from pydantic import BaseModel, Field

from agents.orchestrator import LivingRiskOrchestrator
from mcp_tools.tools import UDP2Tooling, ensure_trace_id

app = FastAPI(title="UDP 2.0 Living Risk Engine", version="2.0.0")
tooling = UDP2Tooling()
orchestrator = LivingRiskOrchestrator(tooling)


class SignalIngestRequest(BaseModel):
    location_id: str
    signal_type: str
    source_system_code: str | None = None
    telemetry: dict[str, Any] = Field(default_factory=dict)


class OnboardingPrefillRequest(BaseModel):
    location_id: str
    first_name: str
    last_name: str
    email: str


class CoverageRecommendRequest(BaseModel):
    location_id: str


@app.post("/api/v1/signal/ingest")
def ingest_signal(
    payload: SignalIngestRequest,
    response: Response,
    x_trace_id: str | None = Header(default=None, alias="X-Trace-ID"),
) -> dict[str, Any]:
    trace_id = ensure_trace_id(x_trace_id)
    try:
        result = orchestrator.execute_signal_dag(payload.model_dump(), trace_id=trace_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    response.headers["X-Trace-ID"] = trace_id
    return {"trace_id": trace_id, "result": result}


@app.post("/api/v1/onboarding/prefill")
def prefill_onboarding(
    payload: OnboardingPrefillRequest,
    response: Response,
    x_trace_id: str | None = Header(default=None, alias="X-Trace-ID"),
) -> dict[str, Any]:
    trace_id = ensure_trace_id(x_trace_id)
    result = tooling.prefill_property_twin(
        location_id=payload.location_id,
        first_name=payload.first_name,
        last_name=payload.last_name,
        email=payload.email,
        trace_id=trace_id,
    )
    response.headers["X-Trace-ID"] = trace_id
    return result


@app.post("/api/v1/coverage/recommend")
def recommend_coverage(
    payload: CoverageRecommendRequest,
    response: Response,
    x_trace_id: str | None = Header(default=None, alias="X-Trace-ID"),
) -> dict[str, Any]:
    trace_id = ensure_trace_id(x_trace_id)
    result = tooling.recommend_contextual_coverage(payload.location_id, trace_id=trace_id)
    response.headers["X-Trace-ID"] = trace_id
    return result


@app.get("/api/v1/twin/state/{location_id}")
def get_twin_state(location_id: str, response: Response, x_trace_id: str | None = Header(default=None, alias="X-Trace-ID")) -> dict[str, Any]:
    trace_id = ensure_trace_id(x_trace_id)
    response.headers["X-Trace-ID"] = trace_id
    return {"trace_id": trace_id, "states": tooling.get_twin_state(location_id)}


@app.get("/api/v1/actions/active")
def get_active_actions(response: Response, x_trace_id: str | None = Header(default=None, alias="X-Trace-ID")) -> dict[str, Any]:
    trace_id = ensure_trace_id(x_trace_id)
    response.headers["X-Trace-ID"] = trace_id
    return {"trace_id": trace_id, "actions": tooling.get_active_actions()}


@app.get("/health")
def health(response: Response, x_trace_id: str | None = Header(default=None, alias="X-Trace-ID")) -> dict[str, Any]:
    trace_id = ensure_trace_id(x_trace_id)
    status = tooling.health()
    status["trace_id"] = trace_id
    response.headers["X-Trace-ID"] = trace_id
    return status

