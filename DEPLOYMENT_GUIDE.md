# UDP 2.0 Living Risk Engine Deployment Guide

This repository contains the UDP 2.0 Living Risk Engine reference application for telemetry-driven insurance risk prevention.

## Project overview

The app exposes a FastAPI service that supports:

- `POST /api/v1/signal/ingest`
- `POST /api/v1/onboarding/prefill`
- `POST /api/v1/coverage/recommend`
- `GET /api/v1/twin/state/{location_id}`
- `GET /api/v1/actions/active`
- `GET /health`

The app propagates the `X-Trace-ID` header on all requests.

## Repository structure

- `app/` — FastAPI application entry point and routes
- `agents/` — orchestration and risk logic
- `data_layer/` — data models and telemetry schema
- `deployment/` — Docker and cloud deployment assets
- `mcp_tools/` — external tool integrations and trace helpers
- `tests/` — test coverage
- `requirements.txt` — Python dependencies

## Local development

1. Create and activate a Python environment:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Start the API locally:

```bash
uvicorn app.main:app --reload --port 8080
```

4. Validate with health check:

```bash
curl http://localhost:8080/health
```

## Docker local deployment

The project includes a container definition in `deployment/docker-compose.yml` and `deployment/Dockerfile`.

Run:

```bash
docker compose -f deployment/docker-compose.yml up --build
```

The service listens on:

```text
http://localhost:8080
```

## Azure deployment

Use the script in `deployment/deploy_azure.sh`.

Prerequisites:

- Azure CLI installed and logged in
- Docker installed
- an Azure subscription

Run:

```bash
bash deployment/deploy_azure.sh
```

This script:

- creates a resource group
- provisions an Azure Container Registry
- builds the local image
- pushes the image to ACR
- creates a Container App environment and deploys the app

## GCP deployment

Use the script in `deployment/deploy_gcp.sh`.

Prerequisites:

- `gcloud` installed and authenticated
- a GCP project configured
- Docker installed

Run:

```bash
bash deployment/deploy_gcp.sh
```

This script:

- builds the container image
- pushes it to Google Container Registry
- deploys it to Cloud Run on port 8080

## Recommended verification checks

After deployment, validate:

```bash
curl http://localhost:8080/health
curl -X POST http://localhost:8080/api/v1/signal/ingest \
  -H "Content-Type: application/json" \
  -H "X-Trace-ID: test-trace-123" \
  -d '{
    "location_id": "loc-001",
    "signal_type": "storm",
    "source_system_code": "weather",
    "telemetry": {"wind_speed_kph": 85, "rain_mm": 20}
  }'
```

## Notes

- The repo is designed for a local-first developer workflow and cloud deployment scripts.
- The deployment scripts assume the app is started on port 8080.
- All tracing is intentionally passed through `X-Trace-ID` to maintain correlation across requests and downstream actions.
