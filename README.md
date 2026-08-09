# UDP 2.0 Living Risk Engine

Insurance Digital Twin reference application for proactive, telemetry-driven risk prevention.

## Run locally

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8080
```

## API endpoints

- `POST /api/v1/signal/ingest`
- `POST /api/v1/onboarding/prefill`
- `POST /api/v1/coverage/recommend`
- `GET /api/v1/twin/state/{location_id}`
- `GET /api/v1/actions/active`
- `GET /health`

All endpoints propagate `X-Trace-ID`.

## Deploy

- Local docker compose: `deployment/docker-compose.yml`
- GCP Cloud Run script: `deployment/deploy_gcp.sh`
- Azure Container Apps script: `deployment/deploy_azure.sh`
