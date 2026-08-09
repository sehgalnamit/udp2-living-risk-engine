from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert response.headers["X-Trace-ID"] == body["trace_id"]


def test_onboarding_prefill_masks_pii() -> None:
    payload = {
        "location_id": f"LOC-{uuid4()}",
        "first_name": "Taylor",
        "last_name": "Rivera",
        "email": "taylor.rivera@example.com",
    }
    response = client.post("/api/v1/onboarding/prefill", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["customer"]["first_name"].endswith("***")
    assert body["customer"]["last_name"].endswith("***")
    assert body["customer"]["email"].startswith("t***@")


def test_signal_ingestion_triggers_guardian_and_twin_state() -> None:
    location_id = f"LOC-{uuid4()}"
    prefill = client.post(
        "/api/v1/onboarding/prefill",
        json={
            "location_id": location_id,
            "first_name": "Jordan",
            "last_name": "Lee",
            "email": "jordan.lee@example.com",
        },
    )
    assert prefill.status_code == 200
    ingest = client.post(
        "/api/v1/signal/ingest",
        headers={"X-Trace-ID": str(uuid4())},
        json={
            "location_id": location_id,
            "signal_type": "openweather",
            "source_system_code": "OWM",
            "telemetry": {"wind_mph": 92, "hail_inches": 0.8},
        },
    )
    assert ingest.status_code == 200
    result = ingest.json()["result"]
    assert result["twin_state_and_score"]["risk_score"] >= 0.5
    assert result["guardian_action_check"]["triggered"] is True
    assert ingest.headers["X-Trace-ID"] == ingest.json()["trace_id"]

    state = client.get(f"/api/v1/twin/state/{location_id}")
    assert state.status_code == 200
    states = state.json()["states"]
    assert states
    assert states[0]["location_id"] == location_id

    actions = client.get("/api/v1/actions/active")
    assert actions.status_code == 200
    active_actions = actions.json()["actions"]
    assert len(active_actions) >= 1


def test_coverage_recommendation_endpoint() -> None:
    location_id = f"LOC-{uuid4()}"
    prefill = client.post(
        "/api/v1/onboarding/prefill",
        json={
            "location_id": location_id,
            "first_name": "Avery",
            "last_name": "Stone",
            "email": "avery.stone@example.com",
        },
    )
    assert prefill.status_code == 200
    ingest = client.post(
        "/api/v1/signal/ingest",
        json={
            "location_id": location_id,
            "signal_type": "iot_valve",
            "source_system_code": "IOT",
            "telemetry": {"line_pressure": 140, "leak_probability": 0.22},
        },
    )
    assert ingest.status_code == 200
    recommend = client.post("/api/v1/coverage/recommend", json={"location_id": location_id})
    assert recommend.status_code == 200
    body = recommend.json()
    assert "recommendations" in body

