# UDP 2.0 Living Risk Engine

The UDP 2.0 Living Risk Engine is an insurance digital twin reference application designed for proactive, telemetry-driven risk prevention. It combines an API-first backend, orchestration logic, AI-assisted risk evaluation, and cloud deployment assets for local, Azure, and GCP environments.

## Overview

This repository models a modern insurance workflow in which telemetry, underwriting context, risk scoring, and policy recommendations are assembled into a single operational loop. The system supports:

- Telemetry ingestion and location-based risk assessment
- Policy onboarding and prefill workflows
- Context-aware coverage recommendations
- Risk-state tracking for a digital twin
- Active loss-prevention actions
- Traceable AI assurance and audit logging

## Core capabilities

- Real-time twin state management for insured properties or infrastructure
- Event-driven signal processing for weather, IoT, or exposure changes
- Policy-aware coverage recommendations
- Active action detection and preventive recommendations
- X-Trace-ID propagation for observability and auditability
- Local-first development with portable deployment scripts for Azure and GCP

## Repository map

```text
udp2-living-risk-engine/
├── app/                          # FastAPI app and HTTP endpoints
├── agents/                       # orchestration and risk-processing logic
├── data_layer/                   # domain schemas and data models
├── deployment/                   # Docker and cloud deployment assets
├── mcp_tools/                    # tool gateway, trace helpers, and business logic
├── tests/                        # project tests
├── README.md                     # project overview and navigation
├── DEPLOYMENT_GUIDE.md           # broader deployment and architecture guide
├── requirements.txt              # Python dependencies
├── docker-compose.yml            # root Docker Compose file (legacy/local helper)
├── deployment/Dockerfile         # container image definition
├── deployment/deploy_azure.sh    # Azure deployment script
├── deployment/deploy_gcp.sh      # GCP Cloud Run deployment script
└── docs/                         # deep-dive documentation
```

## Quick start

### 1) Install dependencies

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2) Run locally

```bash
uvicorn app.main:app --reload --port 8080
```

### 3) Check health

```bash
curl http://localhost:8080/health
```

## API surface

The application exposes the following endpoints:

- `POST /api/v1/signal/ingest`
- `POST /api/v1/onboarding/prefill`
- `POST /api/v1/coverage/recommend`
- `GET /api/v1/twin/state/{location_id}`
- `GET /api/v1/actions/active`
- `GET /health`

All requests can carry the `X-Trace-ID` header for correlation across operations.

## Local deployment

For containerized local execution use the deployment compose file:

```bash
docker compose -f deployment/docker-compose.yml up --build
```

See:

- [docs/local-deployment.md](docs/local-deployment.md)
- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

## Azure deployment

The repo includes Azure deployment automation for Container Apps.

```bash
bash deployment/deploy_azure.sh
```

See:

- [docs/azure-deployment.md](docs/azure-deployment.md)

## GCP deployment

The repo includes GCP deployment automation for Cloud Run.

```bash
bash deployment/deploy_gcp.sh
```

See:

- [docs/gcp-deployment.md](docs/gcp-deployment.md)

## Architecture references

The system is built around an insurance digital-twin architecture with policy-aware orchestration and AI-assisted risk decisions.

See:

- [docs/udp-architecture.md](docs/udp-architecture.md)
- [docs/ai-overview.md](docs/ai-overview.md)
- [docs/api-reference.md](docs/api-reference.md)

## Testing

Run the project tests with:

```bash
pytest -q
```

The current suite validates the core application behaviors and API contract.

## Documentation index

- [docs/local-deployment.md](docs/local-deployment.md)
- [docs/azure-deployment.md](docs/azure-deployment.md)
- [docs/gcp-deployment.md](docs/gcp-deployment.md)
- [docs/udp-architecture.md](docs/udp-architecture.md)
- [docs/ai-overview.md](docs/ai-overview.md)
- [docs/api-reference.md](docs/api-reference.md)
- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

## Notes

This repository is intended as a reference implementation and can be adapted for local experiments, cloud deployment testing, or enterprise prototype scenarios. The codebase is structured to keep the application simple and deployable while still reflecting realistic insurance and risk-monitoring workflows.
