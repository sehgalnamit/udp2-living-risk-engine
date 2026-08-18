# UDP 2.0 Architecture Overview

This document describes the architecture model used by the UDP 2.0 Living Risk Engine.

## Design intent

The project is intended to represent an insurance digital twin that continuously assesses exposure, monitors risk, and can generate preventive actions before a loss event escalates.

## System diagram

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'fontSize': '24px'}, 'flowchart': {'useMaxWidth': false, 'nodeSpacing': 70, 'rankSpacing': 90}}}%%
flowchart LR
    classDef input fill:#1971C2,color:#fff,stroke:#1864AB,stroke-width:2px;
    classDef api fill:#7048E8,color:#fff,stroke:#5F3DC4,stroke-width:2px;
    classDef core fill:#12B886,color:#fff,stroke:#087F5B,stroke-width:2px;
    classDef logic fill:#0CA678,color:#fff,stroke:#087F5B,stroke-width:2px;
    classDef data fill:#F59F00,color:#fff,stroke:#E67700,stroke-width:2px;
    classDef audit fill:#E64980,color:#fff,stroke:#C2255C,stroke-width:2px;

    A[Policy + Customer\nContext]:::input --> B[[FastAPI API]]:::api
    C[Telemetry / Weather /\nHazard Signals]:::input --> B
    B --> D{{LivingRiskOrchestrator}}:::core

    subgraph Engine["Orchestrated Logic"]
        direction TB
        E[Digital Twin\nState Engine]:::logic
        F[Guardian Action\nLogic]:::logic
        G[Parametric Trigger\nLogic]:::logic
        H[AI Assurance\nLogging]:::logic
    end

    D --> E
    D --> F
    D --> G
    D --> H

    E --> I[(DuckDB\nRuntime State)]:::data
    F --> J([Action / Recommendation\nOutput]):::core
    G --> J
    H --> K[/Audit Trail &\nTraceability/]:::audit
```

## Core architecture layers

### 1. API layer

The FastAPI application serves the operational surface for onboarding, ingestion, coverage, and state queries.

Key responsibilities:

- accept incoming telemetry or policy context
- route requests through the orchestration layer
- propagate trace IDs
- return structured, auditable responses

### 2. Orchestration layer

The orchestrator sits above the data and tool layers and coordinates the execution path for incoming signals.

Typical flow:

1. ingest location and signal metadata
2. update the digital twin state
3. compute live risk score
4. trigger guardian action if threshold is breached
5. evaluate parametric payout logic
6. recommend contextual coverage
7. log assurance metadata

### 3. Tooling and MCP layer

The tool layer centralizes business logic for:

- customer context and policy data
- event-based twin refresh
- risk computation
- coverage recommendation
- guardrail and assurance logging

This creates a clean boundary between application endpoints and core business rules.

### 4. Data layer

The project uses in-memory DuckDB-backed tables to model risk and policy state during runtime. This enables fast local development and testability without a full cloud data stack.

## Digital twin model

The system models a living risk state for a location or asset using data such as:

- policy details
- twin status
- risk object metadata
- events and telemetry
- scoring outputs
- preventive actions

## Observability model

Each request can carry an `X-Trace-ID` to provide request-level correlation. This makes it easier to trace signal ingestion, policy actions, and AI assurance logs.

## Related docs

- [../README.md](../README.md)
- [../DEPLOYMENT_GUIDE.md](../DEPLOYMENT_GUIDE.md)
- [ai-overview.md](ai-overview.md)
- [api-reference.md](api-reference.md)
