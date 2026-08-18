# API Reference

This document summarizes the main API endpoints exposed by the UDP 2.0 Living Risk Engine.

## Request flow diagram

```mermaid
flowchart LR
    classDef client fill:#4C6EF5,color:#fff,stroke:#364FC7,stroke-width:1px;
    classDef endpoint fill:#7048E8,color:#fff,stroke:#5F3DC4,stroke-width:1px;
    classDef core fill:#12B886,color:#fff,stroke:#087F5B,stroke-width:1px;

    Client([Client / X-Trace-ID]):::client --> Health[GET /health]:::endpoint
    Client --> Ingest[POST /api/v1/signal/ingest]:::endpoint
    Client --> Onboard[POST /api/v1/onboarding/prefill]:::endpoint
    Client --> Coverage[POST /api/v1/coverage/recommend]:::endpoint
    Client --> TwinState[GET /api/v1/twin/state/{location_id}]:::endpoint
    Client --> Actions[GET /api/v1/actions/active]:::endpoint

    Health --> Tooling{{UDP2Tooling}}:::core
    Ingest --> Tooling
    Onboard --> Tooling
    Coverage --> Tooling
    TwinState --> Tooling
    Actions --> Tooling
```

## Health endpoint

### GET /health

Returns the service health status and current trace identifier.

Example:

```bash
curl http://localhost:8080/health
```

## Ingest signal

### POST /api/v1/signal/ingest

Accepts a signal payload, updates risk state, and returns the evaluation result.

Example payload:

```json
{
  "location_id": "LOC-001",
  "signal_type": "storm",
  "source_system_code": "OWM",
  "telemetry": {
    "wind_mph": 90,
    "hail_inches": 0.7
  }
}
```

## Prefill onboarding

### POST /api/v1/onboarding/prefill

Creates customer and policy context for a location and masks personally identifiable details in the response.

Example payload:

```json
{
  "location_id": "LOC-001",
  "first_name": "Taylor",
  "last_name": "Rivera",
  "email": "taylor.rivera@example.com"
}
```

## Coverage recommendation

### POST /api/v1/coverage/recommend

Returns context-aware coverage recommendations based on the digital twin state.

Example payload:

```json
{
  "location_id": "LOC-001"
}
```

## Twin state

### GET /api/v1/twin/state/{location_id}

Returns the active digital twin state for a location.

## Active actions

### GET /api/v1/actions/active

Returns current actions that are active for the system.

## Trace behavior

All endpoints support propagation of the `X-Trace-ID` header for correlation and observability.

## Related docs

- [../README.md](../README.md)
- [../DEPLOYMENT_GUIDE.md](../DEPLOYMENT_GUIDE.md)
- [udp-architecture.md](udp-architecture.md)
- [ai-overview.md](ai-overview.md)
