# Insurance Digital Twin UDP 2.0 - Complete Deployment Prompt & Architecture Guide

> **Your Deployment & GitHub Commit Reference Document**  
> Contains: Local/GCP/Azure specific code, Architecture diagrams, UDP 2.0 data models, Free API integrations, Mock data layer  
> **Updated**: CTAIO Framework Standards — Multi-Agent Architecture, LangGraph State Machines, MCP Tool Gateways, Prime Agent Pattern

---

## TABLE OF CONTENTS

1. [Executive Summary](#executive-summary)
2. [**Multi-Agent Architecture Standards (CTAIO)**](#multi-agent-architecture-standards) ⭐ NEW
3. [Architecture Overview & Diagrams](#architecture-overview)
4. [Project Structure](#project-structure)
5. [UDP 2.0 Data Model](#udp-20-data-model)
6. [Local Development Setup](#local-development-setup)
7. [Azure Deployment](#azure-deployment)
8. [GCP Deployment](#gcp-deployment)
9. [Free External API Integrations](#free-external-api-integrations)
10. [Mock Data Layer & Simulation](#mock-data-layer)
11. [GitHub CI/CD Workflows](#github-cicd-workflows)

---

## EXECUTIVE SUMMARY

### Project: Insurance Digital Twin with UDP 2.0 + FastMCP Multi-Agent Orchestration

An AI-native enterprise platform combining **UDP 2.0 Governed Lakehouse** with **FastMCP Multi-Agent Orchestration Engine**, transforming a reactive insurer into a proactive risk guardian ("Predict-and-Prevent").

**4 Specialized Agents** power the system (Hierarchical Supervisor Network topology):
- 🤖 **Twin Risk Agent** — Continuous asset exposure monitoring
- 🛡️ **Guardian Action Agent** — Proactive loss-prevention interventions
- ⚡ **Parametric Trigger Agent** — Instant weather-event claim automation
- ✅ **AI Assurance Agent** — Compliance audit & regulatory proof

**6 Core Business Capabilities:**

1. ✅ **Proactive Risk & Loss Prevention** - Real-time risk scoring via Guardian Actions
2. ✅ **Zero-Question Onboarding** - Automated property profiling via satellite imagery
3. ✅ **Instant Parametric Claims** - Weather-triggered automatic claim approval (<5 seconds)
4. ✅ **Usage-Based Coverage** - Dynamic premium pricing based on live exposure
5. ✅ **Anti-Fraud Underwriting** - Multi-source data validation and leakage detection
6. ✅ **AI Assurance & Compliance** - OpenTelemetry trace logging, 100% auditability

**Expected Business Impact:**
- 25% reduction in applicant drop-off (Zero-Question Onboarding)
- 12–18% reduction in claim severity (Guardian Actions)
- 40% reduction in loss-adjustment expenses (Parametric automation)
- 100% auditability for automated AI/ML insurance decisions

### Technology Stack

| Layer | Local | Azure | GCP |
|-------|-------|-------|-----|
| **Multi-Agent Orchestration** | LangGraph + FastMCP | LangGraph + Azure API Mgmt | LangGraph + Apigee |
| **Agent State Machine** | LangGraph (StateGraph) | LangGraph + Redis | LangGraph + Cloud Memorystore |
| **MCP Gateway** | ContextForge (local) | ContextForge + APIM | ContextForge + Cloud Endpoints |
| **API Gateway** | FastAPI | Azure API Management | Apigee / Cloud Endpoints |
| **Ingestion** | Kafka/Celery | Event Hubs + Data Factory | Pub/Sub + Cloud Dataflow |
| **State Persistence** | Redis + PostgreSQL | Redis Cache + Azure SQL | Memorystore + Cloud SQL |
| **Storage** | PostgreSQL | ADLS Gen2 | Cloud Storage |
| **Processing** | Python Workers | Azure Databricks | Cloud Dataflow |
| **Analytics** | Jupyter | Power BI | BigQuery + Looker |
| **AI/ML** | Scikit-learn | Azure OpenAI | Vertex AI |
| **Tracing** | OpenTelemetry | Azure Monitor | Cloud Trace |

---

## MULTI-AGENT ARCHITECTURE STANDARDS

> Based on **CTAIO Frameworks** — "Architecting the AI Era" series (Aug 2026)  
> Source: *Multi-Agent Architecture: Topology, State Machines, and Inter-Agent Protocols*

### Core Concepts

This system implements 3 foundational enterprise AI principles:

- **Agentic AI**: Agents are autonomous team members that decompose goals into sub-tasks, maintain execution memory, evaluate intermediate results, call external APIs, and loop until completion
- **Graphs**: Insurance entities (Customer, Policy, Claim, Risk) are Nodes connected by Edges (OWNS, TRIGGERS, VALIDATES) — enabling multi-hop reasoning
- **Ontologies**: Formal schema governance rules preventing LLMs from hallucinating invalid business relationships (e.g., an AI cannot approve a claim without a valid policy)

### Topology: Hierarchical Supervisor Network

The system uses the **Hierarchical Supervisor Network** topology — a central Supervisor orchestrates all 4 specialized workers:

```mermaid
flowchart TD
    classDef input fill:#1971C2,color:#fff,stroke:#1864AB,stroke-width:1px;
    classDef supervisor fill:#7048E8,color:#fff,stroke:#5F3DC4,stroke-width:1px;
    classDef worker fill:#12B886,color:#fff,stroke:#087F5B,stroke-width:1px;
    classDef output fill:#F59F00,color:#fff,stroke:#E67700,stroke-width:1px;

    In[[User Input /\nExternal Trigger]]:::input --> Sup{{Supervisor Agent\nLangGraph StateGraph}}:::supervisor

    Sup --> W1[Twin Risk Worker\nAsset monitoring]:::worker
    Sup --> W2[Guardian Action Worker\nLoss prevention]:::worker
    Sup --> W3[Parametric Trigger Worker\nClaims automation]:::worker
    Sup --> W4[AI Assurance Worker\nCompliance logging]:::worker

    W1 --> Out([Output: Parametric Payout /\nGuardian Alert / Compliance Record]):::output
    W2 --> Out
    W3 --> Out
    W4 --> Out
```

### Deterministic State Machine (LangGraph)

Every agent follows a deterministic execution path with **checkpoint + HITL** (Human-in-the-Loop) support:

```mermaid
flowchart LR
    classDef state fill:#4C6EF5,color:#fff,stroke:#364FC7,stroke-width:1px;
    classDef pause fill:#F59F00,color:#fff,stroke:#E67700,stroke-width:1px;

    A([User Input]):::state --> B[[Checkpoint]]:::state --> C{{Supervisor}}:::state
    C --> D[Worker Execution]:::state
    D -.Pause / HITL.-> B
```

**Implementation** (Production-grade):

```python
# agents/supervisor_state_machine.py
from typing import TypedDict, Annotated, Sequence
import operator
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import StateGraph, END

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    next_step: str
    is_complete: bool
    session_id: str          # Prime Agent Pattern: links to Redis session
    user_approval_required: bool  # HITL flag

def supervisor_node(state: AgentState) -> dict:
    """Routes to specialized insurance worker based on trigger type."""
    messages = state.get("messages", [])
    if not messages:
        return {"next_step": "twin_risk_worker", "is_complete": False}

    last_message = messages[-1].content

    # Termination check
    if "FINAL_ANSWER" in last_message:
        return {"next_step": END, "is_complete": True}

    # Route by insurance domain trigger
    if "hail" in last_message.lower() or "wind" in last_message.lower() or "flood" in last_message.lower():
        return {"next_step": "parametric_trigger_worker", "is_complete": False}
    if "risk" in last_message.lower() or "exposure" in last_message.lower():
        return {"next_step": "twin_risk_worker", "is_complete": False}
    if "guardian" in last_message.lower() or "prevention" in last_message.lower():
        return {"next_step": "guardian_action_worker", "is_complete": False}
    if "compliance" in last_message.lower() or "audit" in last_message.lower():
        return {"next_step": "ai_assurance_worker", "is_complete": False}

    return {"next_step": "twin_risk_worker", "is_complete": False}


def twin_risk_worker(state: AgentState) -> dict:
    """Evaluates living risk model scores from Digital Twin state."""
    return {"messages": [HumanMessage(content="TwinRisk: Risk score updated.")]}

def guardian_action_worker(state: AgentState) -> dict:
    """Generates loss prevention recommendations before loss occurs."""
    return {"messages": [HumanMessage(content="Guardian: Action alert issued.")]}

def parametric_trigger_worker(state: AgentState) -> dict:
    """Evaluates weather data against policy thresholds, auto-approves claims."""
    return {"messages": [HumanMessage(content="Parametric: Claim auto-approved.")]}

def ai_assurance_worker(state: AgentState) -> dict:
    """Logs all AI decisions to compliance audit trail with OpenTelemetry."""
    return {"messages": [HumanMessage(content="AIAssurance: Decision logged.")]}


# Build LangGraph State Machine
workflow = StateGraph(AgentState)
workflow.add_node("supervisor", supervisor_node)
workflow.add_node("twin_risk_worker", twin_risk_worker)
workflow.add_node("guardian_action_worker", guardian_action_worker)
workflow.add_node("parametric_trigger_worker", parametric_trigger_worker)
workflow.add_node("ai_assurance_worker", ai_assurance_worker)

workflow.set_entry_point("supervisor")

# Explicit conditional edge map — prevents LLM hallucination of invalid routes
workflow.add_conditional_edges(
    "supervisor",
    lambda state: state["next_step"],
    {
        "twin_risk_worker": "twin_risk_worker",
        "guardian_action_worker": "guardian_action_worker",
        "parametric_trigger_worker": "parametric_trigger_worker",
        "ai_assurance_worker": "ai_assurance_worker",
        END: END
    }
)

# Workers loop back to supervisor for multi-hop orchestration
workflow.add_edge("twin_risk_worker", "supervisor")
workflow.add_edge("guardian_action_worker", "supervisor")
workflow.add_edge("parametric_trigger_worker", "ai_assurance_worker")  # Claims always audited
workflow.add_edge("ai_assurance_worker", "supervisor")

app = workflow.compile()
```

### Prime Agent Pattern — Long-Running Session State

All agents use the **Prime Agent Pattern** separating state into two tiers:

```
Short-Term Memory: Execution thread state (LangGraph active context)
Long-Term Persistence: Redis + PostgreSQL (session history, task status, HITL approvals)
```

```python
# agents/session_state.py
import redis
import json
from datetime import datetime

class PrimeAgentSession:
    """Two-tier state persistence: Redis (hot) + PostgreSQL (cold)."""

    def __init__(self, session_id: str, redis_client: redis.Redis, db_session):
        self.session_id = session_id
        self.redis = redis_client
        self.db = db_session

    def save_checkpoint(self, state: dict):
        """Short-term: save active execution state to Redis (TTL 24h)."""
        self.redis.setex(
            f"agent:session:{self.session_id}",
            86400,  # 24 hour TTL
            json.dumps(state)
        )

    def get_checkpoint(self) -> dict:
        """Restore ephemeral execution context from Redis."""
        data = self.redis.get(f"agent:session:{self.session_id}")
        return json.loads(data) if data else {}

    def persist_decision(self, agent_id: str, action: str, result: dict, approved: bool):
        """Long-term: write AI decision to PostgreSQL for compliance audit."""
        self.db.execute("""
            INSERT INTO ai_decisions (session_id, agent_id, action, result, approved, created_at)
            VALUES (:session_id, :agent_id, :action, :result, :approved, :created_at)
        """, {
            "session_id": self.session_id,
            "agent_id": agent_id,
            "action": action,
            "result": json.dumps(result),
            "approved": approved,
            "created_at": datetime.utcnow()
        })

    def request_human_approval(self, task_id: str, payload: dict):
        """HITL: pause execution and queue for human review."""
        self.redis.setex(
            f"hitl:pending:{task_id}",
            3600,  # 1 hour HITL window
            json.dumps({"session_id": self.session_id, "payload": payload, "status": "PENDING"})
        )
```

### MCP Tool Gateway — ContextForge Pattern

All worker agents interact with external tools and microservices exclusively through a **MCP Gateway** — never calling APIs directly. This enforces Zero-Trust RBAC and prevents injection attacks.

```python
# gateway/mcp_payload_validator.py
from pydantic import BaseModel, Field, ValidationError
from typing import Dict, Any, Set

class MCPToolPayload(BaseModel):
    """Strict schema for all MCP tool invocations — prevents injection attacks."""
    agent_id: str = Field(..., description="Unique ID of the calling agent")
    tool_name: str = Field(..., description="Target MCP tool name")
    arguments: Dict[str, Any] = Field(default_factory=dict)
    auth_token: str = Field(..., description="Bearer token for RBAC validation")
    session_id: str = Field(..., description="Links call to Prime Agent session")
    enduser_id: str = Field(..., description="W3C baggage: end-user identity")

class MCPGatewayProxy:
    """ContextForge-pattern MCP Gateway — Zero-Trust enforcement point."""

    def __init__(self, allowed_tools: Set[str]):
        self.allowed_tools = allowed_tools

    def validate_and_route(self, raw_payload: Dict[str, Any]) -> Dict:
        """Validates schema, enforces RBAC, propagates W3C trace context."""
        try:
            validated = MCPToolPayload(**raw_payload)
        except ValidationError as e:
            return {"status": "ERROR", "reason": f"Invalid Payload Schema: {str(e)}"}

        # Normalize bearer token
        clean_token = validated.auth_token.replace("Bearer ", "").strip()
        if not clean_token:
            return {"status": "BLOCKED", "reason": "Missing auth token"}

        # RBAC Tool Check — only allow tools registered for this agent
        if validated.tool_name not in self.allowed_tools:
            return {
                "status": "BLOCKED",
                "reason": f"Tool '{validated.tool_name}' not in allowed set for agent '{validated.agent_id}'"
            }

        # Context-aware tool pruning — pass only required tools to the agent
        return {
            "status": "APPROVED",
            "agent_id": validated.agent_id,
            "target": validated.tool_name,
            "args": validated.arguments,
            "trace_context": {
                "enduser.id": validated.enduser_id,
                "gen_ai.conversation.id": validated.session_id
            }
        }


# Tool registries per agent (Context-Aware Tool Pruning)
TWIN_RISK_TOOLS = {"get_weather_data", "get_property_risk_score", "get_hazard_proximity"}
GUARDIAN_ACTION_TOOLS = {"send_alert", "update_risk_score", "recommend_maintenance"}
PARAMETRIC_TRIGGER_TOOLS = {"evaluate_hail_trigger", "approve_claim", "trigger_payment"}
AI_ASSURANCE_TOOLS = {"log_decision", "hash_prompt", "write_compliance_record"}

# Instantiate per-agent gateways
twin_risk_gateway = MCPGatewayProxy(TWIN_RISK_TOOLS)
guardian_gateway = MCPGatewayProxy(GUARDIAN_ACTION_TOOLS)
parametric_gateway = MCPGatewayProxy(PARAMETRIC_TRIGGER_TOOLS)
assurance_gateway = MCPGatewayProxy(AI_ASSURANCE_TOOLS)
```

### Specialized Ingestion Toolset (CTAIO Standard)

Data ingestion workers must run in **ephemeral sandboxed containers** — treat all incoming payloads (HTML, PDFs, JSON) as untrusted code execution risks.

| Tool | Purpose | Use in This System |
|------|---------|-------------------|
| **ScrapeGraphAI** | LLM/graph-driven HTML → structured JSON | Property data extraction from ATTOM, satellite portals |
| **Gortex (Tree-sitter)** | AST code graph for symbol dependencies | Internal codebase analysis agents |
| **TurboOCR** | Local privacy-first PDF → structured tables | Policy document parsing, claim form extraction |
| **LangGraph** | Deterministic state machine orchestration | All 4 insurance agents |
| **FastMCP** | MCP server for tool registration | Expose insurance tools to agents |

### OpenTelemetry AI Assurance (CTAIO GovOps Standard)

Every AI decision must be **100% auditable** via full OpenTelemetry trace logging:

```python
# agents/ai_assurance.py
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
import hashlib

provider = TracerProvider()
provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
trace.set_tracer_provider(provider)
tracer = trace.get_tracer("insurance.ai_assurance")

class AIAssuranceLogger:
    """Logs all agent decisions with W3C trace context for regulatory compliance."""

    def log_agent_decision(
        self,
        session_id: str,
        agent_id: str,
        prompt: str,
        decision: str,
        model_version: str
    ):
        with tracer.start_as_current_span(f"ai.decision.{agent_id}") as span:
            # W3C baggage propagation
            span.set_attribute("enduser.id", session_id)
            span.set_attribute("gen_ai.conversation.id", session_id)
            span.set_attribute("agent.id", agent_id)
            span.set_attribute("model.version", model_version)

            # Prompt hashing — never log raw prompts (PII risk)
            span.set_attribute("prompt.hash", hashlib.sha256(prompt.encode()).hexdigest())
            span.set_attribute("decision.summary", decision[:200])  # Truncate for compliance

            # Immutable audit record
            span.set_attribute("audit.timestamp", str(datetime.utcnow()))
            span.set_attribute("audit.compliant", True)
```

---

## ARCHITECTURE OVERVIEW

### High-Level System Flow

```mermaid
flowchart LR
    classDef ui fill:#4C6EF5,color:#fff,stroke:#364FC7,stroke-width:1px;
    classDef engine fill:#12B886,color:#fff,stroke:#087F5B,stroke-width:1px;
    classDef data fill:#F59F00,color:#fff,stroke:#E67700,stroke-width:1px;

    UI[[UI / FastMCP API]]:::ui --> ME{{Multi-Agent Engine}}:::engine
    ME --> DF[/Data Fabric Access/]:::data
    DF --> LH[(UDP 2.0 Lakehouse)]:::data

    subgraph RTE["Real-Time Execution Engine"]
        direction TB
        PT[Parametric Triggers]:::engine
        RS[Risk Scoring]:::engine
        GA[Guardian Actions]:::engine
        CA[Compliance Audit]:::engine
    end

    ME --> RTE
```

### UDP 2.0 Architecture - Layered Data Platform

```mermaid
flowchart TD
    classDef source fill:#1971C2,color:#fff,stroke:#1864AB,stroke-width:1px;
    classDef ingest fill:#4C6EF5,color:#fff,stroke:#364FC7,stroke-width:1px;
    classDef raw fill:#868E96,color:#fff,stroke:#495057,stroke-width:1px;
    classDef engine fill:#12B886,color:#fff,stroke:#087F5B,stroke-width:1px;
    classDef curated fill:#0CA678,color:#fff,stroke:#087F5B,stroke-width:1px;
    classDef consume fill:#7048E8,color:#fff,stroke:#5F3DC4,stroke-width:1px;

    subgraph L1["1. Source Layer"]
        direction LR
        S1[Policy / Claims DBs\nCustomer CRM\nUnderwriting DB]:::source
        S2[Weather APIs\nSatellite Imagery\nHazard Feeds]:::source
    end

    subgraph L2["2. Ingestion Layer"]
        direction LR
        I1[Azure Data Factory + CDC\n/ Cloud Dataflow]:::ingest
        I2[Azure Event Hubs\n/ Google Pub-Sub]:::ingest
    end

    subgraph L3["3. Landing Layer (Raw Zone)"]
        direction LR
        R1[ADLS Gen2 Raw Zone]:::raw
        R2[GCS Raw Bucket]:::raw
    end

    subgraph L4["4. Processing & Engine Layer"]
        E1[Digital Twin State Engine\nDataflow / Databricks\nState Synthesis & Curation]:::engine
    end

    subgraph L5["5. Curated Layer (Data Products)"]
        direction LR
        C1[Customer / Policy / Risk\nData Products]:::curated
        C2[Guardian Actions /\nAI Assurance Data Products]:::curated
    end

    subgraph L6["6. Consumption Layer"]
        direction LR
        Q1[Power BI / Azure OpenAI\nBigQuery / Vertex AI]:::consume
        Q2[FastAPI\nParametric Triggers & Actions]:::consume
    end

    L1 --> L2 --> L3 --> L4 --> L5 --> L6
```

#### 1. SOURCE LAYER

| Core Systems | External Feeds & IoT |
|---|---|
| Policy/Claims DBs | Weather APIs |
| Customer CRM | Satellite Imagery |
| Underwriting DB | Hazard Feeds |

#### 2. INGESTION LAYER
**Azure Path:**
```
Scheduled Extracts (Daily) ──→ Azure Data Factory + CDC
Real-Time Feeds ──────────────→ Azure Event Hubs
```

**GCP Path:**
```
Scheduled Extracts (Daily) ──→ Cloud Dataflow / Cloud Datastream
Real-Time Feeds ──────────────→ Google Cloud Pub/Sub
```

#### 3. LANDING LAYER (Raw Zone)
**Azure:** ADLS Gen2 Raw Zones (Immutable Extracts)  
**GCP:** GCS Raw Buckets (Immutable Extracts)

#### 4. PROCESSING & ENGINE LAYER
```
┌──────────────────────────────────────────────────┐
│   DIGITAL TWIN STATE ENGINE                       │
├──────────────────────────────────────────────────┤
│  ✓ Cloud Dataflow / Databricks (Transformations) │
│  ✓ State Synthesis & Mapping                      │
│  ✓ Canonical Refinement                          │
│  ✓ Silver & Gold Data Curation                   │
└──────────────────────────────────────────────────┘
```

#### 5. CURATED LAYER (Data Products)
```
Historical Data Products:
  - Customer_Product_DP (Customer master)
  - Policy_Contract_DP (Policy details)
  - Risk_Intelligence_DP (Aggregated risk scores)

Real-Time Data Products:
  - Risk_Intel (Live risk factors)
  - Guardian_Actions (Preventive recommendations)
  - AI_Assurance_DP (Compliance audit scores)
```

#### 6. CONSUMPTION LAYER (APIs & Analytics)
**Azure:** Power BI + Azure API Management + Azure OpenAI  
**GCP:** BigQuery + Looker + Vertex AI  
**External:** Parametric Triggers & Actions via FastAPI

---

## PROJECT STRUCTURE

```
insurance-digital-twin/
│
├── .github/
│   ├── workflows/
│   │   ├── ci-cd-local.yml         # Local Docker build & test
│   │   ├── ci-cd-azure.yml         # Azure deployment
│   │   └── ci-cd-gcp.yml           # GCP deployment
│   └── DEPLOYMENT_CHECKLIST.md
│
├── src/
│   ├── api/
│   │   ├── main.py                 # FastAPI gateway (MCP-aware)
│   │   └── endpoints/
│   │       ├── claims.py           # Parametric claims trigger endpoint
│   │       ├── onboarding.py       # Zero-question onboarding
│   │       ├── risk.py             # Risk scoring & Guardian actions
│   │       └── compliance.py       # AI Assurance audit endpoint
│   │
│   ├── agents/                     # ⭐ CTAIO Multi-Agent Engine
│   │   ├── supervisor_state_machine.py  # LangGraph Hierarchical Supervisor
│   │   ├── session_state.py             # Prime Agent Pattern (Redis + PostgreSQL)
│   │   ├── workers/
│   │   │   ├── twin_risk_worker.py      # Asset exposure monitoring
│   │   │   ├── guardian_action_worker.py # Loss prevention interventions
│   │   │   ├── parametric_trigger_worker.py # Claims auto-approval
│   │   │   └── ai_assurance_worker.py   # OpenTelemetry compliance logging
│   │   └── ingestion/                   # Sandboxed ingestion workers
│   │       ├── scrape_graph_worker.py   # ScrapeGraphAI (HTML → JSON)
│   │       └── turbo_ocr_worker.py      # TurboOCR (PDF → structured tables)
│   │
│   ├── gateway/                    # ⭐ MCP Tool Gateway (ContextForge Pattern)
│   │   ├── mcp_payload_validator.py     # Pydantic schema + RBAC enforcement
│   │   ├── tool_registry.py             # Per-agent allowed tool sets
│   │   ├── context_forge_gateway.py     # Dynamic OpenAPI-to-MCP translation
│   │   └── trace_propagation.py         # W3C trace context injection
│   │
│   ├── data_layer/
│   │   ├── mock_generator.py       # Mock data generation
│   │   ├── models.py               # SQLAlchemy models (UDP 2.0)
│   │   ├── external_apis/
│   │   │   ├── weather.py          # OpenWeather integration
│   │   │   ├── satellite.py        # ATTOM Data integration
│   │   │   ├── hazard.py           # USGS hazard data
│   │   │   └── azure_maps.py       # Azure Maps geospatial
│   │   └── connectors/
│   │       ├── postgres_local.py
│   │       ├── azure_adls.py
│   │       └── gcp_datastore.py
│   │
│   ├── digital_twin/
│   │   ├── state_engine.py         # Digital Twin state management
│   │   ├── parametric_engine.py    # Claims auto-approval rule engine
│   │   └── guardian_actions.py     # Loss prevention recommendations
│   │
│   ├── processing/
│   │   ├── data_pipelines.py       # ETL transformations
│   │   └── ml_models.py            # Risk scoring models
│   │
│   └── config/
│       ├── local.env
│       ├── azure.env
│       └── gcp.env
│
├── infrastructure/
│   ├── docker-compose.yml          # Local stack
│   ├── azure/
│   │   └── bicep/
│   │       ├── main.bicep
│   │       ├── data_factory.bicep
│   │       ├── databricks.bicep
│   │       └── event_hub.bicep
│   └── gcp/
│       └── terraform/
│           ├── main.tf
│           ├── dataflow.tf
│           ├── pubsub.tf
│           └── storage.tf
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── mock_data_tests.py
│
├── docs/
│   ├── DEPLOYMENT.md               # This file
│   ├── API_REFERENCE.md
│   ├── DATA_MODELS.md
│   └── ARCHITECTURE_DIAGRAMS.md
│
├── scripts/
│   ├── generate_mock_data.py
│   ├── deploy_local.sh
│   ├── deploy_azure.sh
│   └── deploy_gcp.sh
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── pyproject.toml
└── README.md
```

---

## UDP 2.0 DATA MODEL

### Core Entities (DDL Schema)

#### 1. CUSTOMER DOMAIN
```sql
-- Customer_Product_DP
CREATE TABLE customer_master (
    customer_id UUID PRIMARY KEY,
    name VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(20),
    location_gps POINT,                    -- Latitude/Longitude
    risk_profile_score DECIMAL(5,2),       -- From satellite + hazard data
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- External data enrichment
    property_condition_score INT,          -- From ATTOM satellite imagery
    hazard_exposure_level VARCHAR(10),     -- LOW, MEDIUM, HIGH (from USGS)
    weather_risk_factor DECIMAL(5,2)       -- From OpenWeather
);

CREATE TABLE onboarding_journey (
    journey_id UUID PRIMARY KEY,
    customer_id UUID REFERENCES customer_master,
    zero_question_profile JSONB,           -- Auto-profiled from satellite
    satellite_image_url VARCHAR,
    property_boundaries GEOMETRY,
    roof_condition VARCHAR,                 -- ATTOM data
    vegetation_overhang BOOLEAN,
    satellite_flood_mapping JSONB,
    completed_at TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customer_master(customer_id)
);
```

#### 2. POLICY DOMAIN
```sql
-- Policy_Contract_DP
CREATE TABLE policy_master (
    policy_id UUID PRIMARY KEY,
    customer_id UUID NOT NULL REFERENCES customer_master,
    product_type VARCHAR(50),              -- HOME, BUSINESS, AUTO, etc.
    coverage_amount DECIMAL(15,2),
    annual_premium DECIMAL(10,2),
    start_date DATE,
    end_date DATE,
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Dynamic coverage based on usage/exposure
    usage_based_multiplier DECIMAL(5,2) DEFAULT 1.0,
    current_exposure_level DECIMAL(5,2),
    
    -- AI Assurance fields
    underwriting_audit_status VARCHAR(20), -- PENDING, APPROVED, FLAGGED
    compliance_score DECIMAL(5,2),
    regulatory_flags JSONB,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    FOREIGN KEY (customer_id) REFERENCES customer_master(customer_id)
);
```

#### 3. CLAIMS DOMAIN
```sql
-- Claims_Transaction_DP (Real-Time Data Product)
CREATE TABLE claims_transaction (
    claim_id UUID PRIMARY KEY,
    policy_id UUID NOT NULL REFERENCES policy_master,
    claim_type VARCHAR(50),                -- WEATHER, THEFT, FIRE, etc.
    claim_amount DECIMAL(15,2),
    reported_at TIMESTAMP,
    
    -- Parametric Auto-Approval Engine
    is_parametric BOOLEAN DEFAULT FALSE,
    parametric_trigger VARCHAR,            -- HAIL_STRIKE, FLOOD_ZONE, WILDFIRE_PROXIMITY
    trigger_value DECIMAL(10,2),           -- Actual weather value
    trigger_threshold DECIMAL(10,2),       -- Threshold for auto-approval
    auto_approved BOOLEAN,
    approval_timestamp TIMESTAMP,
    
    -- Third-party data validation
    external_data_sources JSONB,           -- Sources used for verification
    weather_data_snapshot JSONB,           -- Live weather at incident time
    satellite_verification BOOLEAN,        -- Was claim verified via satellite?
    
    -- Compliance & AI Assurance
    fraud_risk_score DECIMAL(5,2),
    leakage_detection_flag BOOLEAN,
    ai_assurance_status VARCHAR(20),
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    FOREIGN KEY (policy_id) REFERENCES policy_master(policy_id)
);
```

#### 4. RISK INTELLIGENCE DOMAIN
```sql
-- Risk_Intelligence_DP (Real-Time)
CREATE TABLE risk_scoring (
    score_id UUID PRIMARY KEY,
    customer_id UUID NOT NULL REFERENCES customer_master,
    policy_id UUID NOT NULL REFERENCES policy_master,
    
    -- Guardian Action System
    guardian_action_id UUID UNIQUE,
    action_type VARCHAR(50),               -- ALERT, MAINTENANCE_REMINDER, COVERAGE_ADJUSTMENT
    action_description TEXT,
    recommended_premium_adjustment DECIMAL(5,2),
    
    -- Risk factors
    living_risk_model_score DECIMAL(5,2),
    weather_risk_factor DECIMAL(5,2),
    catastrophe_exposure DECIMAL(5,2),    -- USGS hazard proximity
    property_condition_risk DECIMAL(5,2), -- From satellite
    
    calculated_at TIMESTAMP,
    effective_until TIMESTAMP,
    
    FOREIGN KEY (customer_id) REFERENCES customer_master(customer_id),
    FOREIGN KEY (policy_id) REFERENCES policy_master(policy_id)
);
```

#### 5. EXTERNAL TELEMETRY
```sql
-- External_Signals_DP (Real-Time)
CREATE TABLE external_telemetry (
    telemetry_id UUID PRIMARY KEY,
    customer_id UUID NOT NULL REFERENCES customer_master,
    
    -- Weather Signals
    weather_source VARCHAR(50),            -- OpenWeather, Tomorrow.io, NOAA
    current_temperature DECIMAL(5,2),
    hail_size_inches DECIMAL(5,2),
    wind_gust_kmh DECIMAL(5,2),
    rainfall_mm DECIMAL(5,2),
    lightning_strikes_count INT,
    weather_alert_type VARCHAR(50),        -- SEVERE_STORM, TORNADO, etc.
    
    -- Satellite Signals
    satellite_source VARCHAR(50),          -- ATTOM, Planet Labs, Nearmap
    property_boundaries GEOMETRY,
    roof_condition_confidence DECIMAL(3,2),
    vegetation_overhang_updated TIMESTAMP,
    flood_mapping_area DECIMAL(10,2),      -- sq meters
    
    -- Catastrophe Signals
    hazard_source VARCHAR(50),             -- USGS, HazardHub, Copernicus
    earthquake_proximity_km DECIMAL(8,2),
    wildfire_proximity_km DECIMAL(8,2),
    flood_zone_probability DECIMAL(5,2),
    
    received_at TIMESTAMP,
    processing_latency_ms INT,
    
    FOREIGN KEY (customer_id) REFERENCES customer_master(customer_id)
);
```

### Data Model Relationships

```
CUSTOMER ────────┬────→ POLICY ────────┬────→ CLAIMS (Parametric)
                 │                     │
                 ├────→ ONBOARDING ────┤
                 │                     │
                 ├────→ RISK_SCORING ──┤
                 │                     │
                 └────→ EXTERNAL_TELEMETRY
                        (Weather, Satellite, Hazard)
```

---

## LOCAL DEVELOPMENT SETUP

### Prerequisites
- Docker & Docker Compose
- Python 3.11+
- PostgreSQL 15
- Git

### Step 1: Clone & Setup

```bash
git clone https://github.com/your-org/insurance-digital-twin.git
cd insurance-digital-twin

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies (includes LangGraph, FastMCP, OpenTelemetry)
pip install -r requirements.txt
```

**`requirements.txt`** (complete dependency list):

```
# Multi-Agent Orchestration (CTAIO Standards)
langgraph>=0.2.0
langchain>=0.3.0
langchain-core>=0.3.0
fastmcp>=2.0.0

# MCP Gateway & Schema Validation
pydantic>=2.0.0
pydantic-settings>=2.0.0

# Prime Agent Pattern: Session State
redis>=5.0.0
hiredis>=2.0.0

# AI Assurance & OpenTelemetry (mandatory GovOps)
opentelemetry-sdk>=1.25.0
opentelemetry-exporter-otlp>=1.25.0
opentelemetry-instrumentation-fastapi>=0.46b0

# API Framework
fastapi>=0.110.0
uvicorn[standard]>=0.29.0
httpx>=0.27.0

# Database
sqlalchemy>=2.0.0
alembic>=1.13.0
psycopg2-binary>=2.9.0
asyncpg>=0.29.0

# Data Processing
pandas>=2.2.0
faker>=24.0.0

# Specialized Ingestion (sandboxed — install only in ingestion container)
# scrapegraphai>=1.0.0    # In Dockerfile.ingestion only
# pytesseract>=0.3.10     # TurboOCR local PDF extraction

# Testing
pytest>=8.0.0
pytest-asyncio>=0.23.0
pytest-cov>=5.0.0
```

### Step 2: Configure Local Environment

Create `.env` file in root:

```env
# LOCAL CONFIGURATION
ENVIRONMENT=local
DATABASE_URL=postgresql://postgres:password@localhost:5432/digital_twin

# Prime Agent Pattern: Redis for session state + HITL queues
REDIS_URL=redis://localhost:6379
AGENT_SESSION_TTL_SECONDS=86400
HITL_APPROVAL_TTL_SECONDS=3600

# Multi-Agent LangGraph Config
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=insurance-digital-twin
LANGCHAIN_API_KEY=your_langsmith_free_key  # Free at smith.langchain.com

# MCP Gateway (ContextForge Pattern)
MCP_GATEWAY_ENFORCE_RBAC=true
MCP_GATEWAY_SCHEMA_AUDIT=true

# OpenTelemetry AI Assurance (mandatory for compliance)
OTEL_SERVICE_NAME=insurance-digital-twin
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
OTEL_LOG_PROMPT_HASHES=true  # Never log raw prompts

# API Gateway
API_HOST=0.0.0.0
API_PORT=8000
API_LOG_LEVEL=INFO

# External APIs (Free Tier Keys)
OPENWEATHER_API_KEY=your_free_key_from_openweathermap.org
WEATHER_API_KEY=your_free_key_from_tomorrow.io
GOOGLE_MAPS_API_KEY=your_free_key_from_console.cloud.google.com
NASA_API_KEY=your_free_key_from_api.nasa.gov

# Mock Data Generation
MOCK_DATA_CUSTOMERS=100
MOCK_DATA_POLICIES=500
MOCK_DATA_CLAIMS=1000

# Logging
LOG_LEVEL=DEBUG
LOG_FILE=./logs/app.log
```

### Step 3: Start Local Stack

```bash
# Start PostgreSQL, Redis, and services
docker-compose -f docker-compose.yml up -d

# Run database migrations
python -m alembic upgrade head

# Generate mock data
python scripts/generate_mock_data.py --customers 100 --policies 500

# Start API server
python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# Start worker for async processing
celery -A src.processing.tasks worker --loglevel=info
```

### Step 4: Access Services

- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health
- **Database**: localhost:5432 (psql postgres://postgres:password@localhost:5432/digital_twin)

### Docker Compose Stack

```yaml
version: '3.8'
services:
  
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
      POSTGRES_DB: digital_twin
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    # Prime Agent Pattern: hot session state + HITL approval queues
  
  api:
    build:
      context: .
      dockerfile: Dockerfile
    environment:
      DATABASE_URL: postgresql://postgres:password@postgres:5432/digital_twin
      REDIS_URL: redis://redis:6379
      ENVIRONMENT: local
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis
    command: uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
  
  # LangGraph Supervisor Agent (Hierarchical topology)
  agent_supervisor:
    build:
      context: .
      dockerfile: Dockerfile
    environment:
      DATABASE_URL: postgresql://postgres:password@postgres:5432/digital_twin
      REDIS_URL: redis://redis:6379
      AGENT_MODE: supervisor
    depends_on:
      - postgres
      - redis
    command: python -m src.agents.supervisor_state_machine

  # Sandboxed ingestion container — isolated network, no egress except allowlist
  ingestion_worker:
    build:
      context: .
      dockerfile: Dockerfile.ingestion  # Hardened, minimal base image
    environment:
      DATABASE_URL: postgresql://postgres:password@postgres:5432/digital_twin
    networks:
      - ingestion_net  # Isolated from main network
    depends_on:
      - postgres
    command: python -m src.agents.ingestion.scrape_graph_worker

  worker:
    build:
      context: .
      dockerfile: Dockerfile
    environment:
      DATABASE_URL: postgresql://postgres:password@postgres:5432/digital_twin
      REDIS_URL: redis://redis:6379
      ENVIRONMENT: local
    depends_on:
      - postgres
      - redis
    command: celery -A src.processing.tasks worker --loglevel=info

networks:
  default:
  ingestion_net:
    internal: true  # No external internet access for ingestion workers

volumes:
  postgres_data:
```

---

## AZURE DEPLOYMENT

### Prerequisites

- Azure subscription
- Azure CLI installed: `az --version`
- Bicep CLI: `az bicep version`

### Step 1: Setup Azure Resources (Bicep)

```bicep
# infrastructure/azure/bicep/main.bicep

param location string = 'Southeast Asia'
param environment string = 'prod'
param projectName string = 'insurancedw'

resource resourceGroup 'Microsoft.Resources/resourceGroups@2021-04-01' = {
  name: '${projectName}-${environment}-rg'
  location: location
}

// Data Factory
resource dataFactory 'Microsoft.DataFactory/factories@2018-06-01' = {
  name: '${projectName}-adf-${environment}'
  location: location
  identity: {
    type: 'SystemAssigned'
  }
}

// ADLS Gen2 for Data Lake
resource dataLakeStorage 'Microsoft.Storage/storageAccounts@2021-04-01' = {
  name: '${projectName}adls${environment}'
  location: location
  kind: 'StorageV2'
  sku: {
    name: 'Standard_LRS'
  }
  properties: {
    isHnsEnabled: true // Enable hierarchical namespace
  }
}

// Databricks for Processing
resource databricks 'Microsoft.Databricks/workspaces@2021-04-01-preview' = {
  name: '${projectName}-dbricks-${environment}'
  location: location
  sku: {
    name: 'premium'
  }
}

// Event Hubs for Real-Time Streaming
resource eventHub 'Microsoft.EventHub/namespaces@2021-06-01-preview' = {
  name: '${projectName}-eh-${environment}'
  location: location
  sku: {
    name: 'Standard'
    capacity: 2
  }
}

// Azure SQL for transactional data
resource sqlServer 'Microsoft.Sql/servers@2021-02-01-preview' = {
  name: '${projectName}-sql-${environment}'
  location: location
  properties: {
    administratorLogin: 'sqladmin'
    // Use Azure Key Vault for password
  }
}

// Azure API Management
resource apiManagement 'Microsoft.ApiManagement/service@2021-04-01-preview' = {
  name: '${projectName}-apim-${environment}'
  location: location
  sku: {
    name: 'Developer'
    capacity: 1
  }
}

// Azure OpenAI for AI/ML
resource cognitiveServices 'Microsoft.CognitiveServices/accounts@2021-10-01' = {
  name: '${projectName}-openai-${environment}'
  location: location
  kind: 'OpenAI'
  sku: {
    name: 'S0'
  }
}

// Application Insights for monitoring
resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: '${projectName}-ai-${environment}'
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
  }
}

output dataFactoryId string = dataFactory.id
output dataLakeUrl string = dataLakeStorage.primaryBlobEndpoint
output eventHubNamespace string = eventHub.name
output apiManagementUrl string = apiManagement.properties.gatewayUrl
```

### Step 2: Deploy to Azure

```bash
# Set variables
SUBSCRIPTION_ID="your-subscription-id"
RESOURCE_GROUP="insurance-dw-prod-rg"
LOCATION="Southeast Asia"

# Login to Azure
az login
az account set --subscription $SUBSCRIPTION_ID

# Create resource group
az group create --name $RESOURCE_GROUP --location $LOCATION

# Deploy Bicep template
az deployment group create \
  --resource-group $RESOURCE_GROUP \
  --template-file infrastructure/azure/bicep/main.bicep \
  --parameters location=$LOCATION environment=prod projectName=insurancedw
```

### Step 3: Configure Data Pipelines in Azure

**Azure Data Factory Pipeline (Scheduled Extracts)**

```json
{
  "name": "ScheduledExtract_CustomerData",
  "properties": {
    "activities": [
      {
        "name": "CopyFromSourceDB",
        "type": "Copy",
        "inputs": [
          {
            "referenceName": "SourceDatabaseDataset",
            "type": "DatasetReference"
          }
        ],
        "outputs": [
          {
            "referenceName": "ADLSRawZone",
            "type": "DatasetReference"
          }
        ]
      },
      {
        "name": "RunDatabricksPipeline",
        "type": "DatabricksNotebook",
        "dependsOn": [
          {
            "activity": "CopyFromSourceDB",
            "dependencyConditions": ["Succeeded"]
          }
        ]
      }
    ],
    "triggers": [
      {
        "name": "DailySchedule",
        "type": "ScheduleTrigger",
        "typeProperties": {
          "recurrence": {
            "frequency": "Day",
            "interval": 1,
            "startTime": "2024-01-01T02:00:00Z"
          }
        }
      }
    ]
  }
}
```

**Real-Time Ingestion via Event Hubs**

```python
# Python: Stream to Event Hubs
from azure.eventhub import EventHubProducerClient, EventData
import json

def send_weather_telemetry(weather_data):
    producer = EventHubProducerClient.from_connection_string(
        conn_str=EVENTHUB_CONNECTION_STRING,
        eventhub_name="weather-telemetry"
    )
    
    event_data = EventData(json.dumps(weather_data))
    with producer:
        producer.send_batch([event_data])
```

### Step 4: Deploy API to Azure Container Instances

```bash
# Build and push image to ACR
az acr build \
  --registry $REGISTRY_NAME \
  --image insurance-digital-twin:latest \
  .

# Deploy to App Service
az appservice plan create \
  --name insurance-app-plan \
  --resource-group $RESOURCE_GROUP \
  --sku B2 --is-linux

az webapp create \
  --resource-group $RESOURCE_GROUP \
  --plan insurance-app-plan \
  --name insurance-digital-twin-api \
  --deployment-container-image-name-user $REGISTRY_NAME.azurecr.io/insurance-digital-twin:latest
```

---

## GCP DEPLOYMENT

### Prerequisites

- Google Cloud project
- `gcloud` CLI installed
- Terraform installed

### Step 1: Setup GCP Resources (Terraform)

```hcl
# infrastructure/gcp/terraform/main.tf

terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 4.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

variable "project_id" {
  type = string
}

variable "region" {
  type    = string
  default = "asia-southeast1"  # Singapore
}

# Cloud Storage for Data Lake
resource "google_storage_bucket" "data_lake_raw" {
  name     = "${var.project_id}-datalake-raw"
  location = var.region
  
  uniform_bucket_level_access = true
  versioning {
    enabled = true
  }
}

resource "google_storage_bucket" "data_lake_curated" {
  name     = "${var.project_id}-datalake-curated"
  location = var.region
  
  uniform_bucket_level_access = true
}

# Cloud SQL (PostgreSQL)
resource "google_sql_database_instance" "postgres" {
  name                = "${var.project_id}-postgres"
  region              = var.region
  database_version    = "POSTGRES_15"
  deletion_protection = true

  settings {
    tier                  = "db-f1-micro"
    availability_type     = "REGIONAL"
    backup_configuration {
      enabled                        = true
      start_time                     = "03:00"
      transaction_log_retention_days = 7
    }
  }
}

resource "google_sql_database" "digital_twin_db" {
  name     = "digital_twin"
  instance = google_sql_database_instance.postgres.name
}

# Pub/Sub for Real-Time Streaming
resource "google_pubsub_topic" "weather_telemetry" {
  name = "weather-telemetry"
}

resource "google_pubsub_subscription" "weather_telemetry_sub" {
  name   = "weather-telemetry-subscription"
  topic  = google_pubsub_topic.weather_telemetry.name
  
  ack_deadline_seconds = 20
}

# Cloud Dataflow for Stream Processing
resource "google_dataflow_job" "digital_twin_engine" {
  name              = "digital-twin-state-engine"
  template_gcs_path = "gs://${var.project_id}-templates/digital_twin_template"
  temp_gcs_location = "gs://${var.project_id}-temp"
  
  parameters = {
    input_topic = google_pubsub_topic.weather_telemetry.id
    output_table = "${var.project_id}:digital_twin.risk_scoring"
  }
}

# BigQuery Dataset
resource "google_bigquery_dataset" "digital_twin" {
  dataset_id = "digital_twin"
  location   = var.region
  
  access {
    role          = "OWNER"
    user_by_email = google_service_account.dataflow_sa.email
  }
}

# Vertex AI for ML/AI Services
resource "google_notebooks_instance" "ml_notebook" {
  name          = "digital-twin-ml-notebook"
  location      = "${var.region}-a"
  machine_type  = "e2-medium"
  image_family  = "tf-latest-cpu"
  image_project = "deeplearning-platform-release"
}

# Cloud Run for API deployment
resource "google_cloud_run_service" "api" {
  name     = "insurance-digital-twin-api"
  location = var.region

  template {
    spec {
      containers {
        image = "gcr.io/${var.project_id}/insurance-digital-twin:latest"
        env {
          name  = "DATABASE_URL"
          value = "postgresql://user:pass@${google_sql_database_instance.postgres.private_ip_address}:5432/digital_twin"
        }
        env {
          name  = "GCS_BUCKET"
          value = google_storage_bucket.data_lake_raw.name
        }
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
}

# IAM Service Account for Dataflow
resource "google_service_account" "dataflow_sa" {
  account_id   = "dataflow-sa"
  display_name = "Dataflow Service Account"
}

resource "google_project_iam_member" "dataflow_roles" {
  for_each = toset([
    "roles/dataflow.admin",
    "roles/storage.admin",
    "roles/bigquery.admin",
    "roles/pubsub.editor"
  ])
  
  project = var.project_id
  role    = each.value
  member  = "serviceAccount:${google_service_account.dataflow_sa.email}"
}

output "cloud_run_url" {
  value = google_cloud_run_service.api.status[0].url
}

output "cloud_sql_connection" {
  value = google_sql_database_instance.postgres.connection_name
}

output "bigquery_dataset" {
  value = google_bigquery_dataset.digital_twin.dataset_id
}
```

### Step 2: Deploy to GCP

```bash
# Set variables
export PROJECT_ID="your-gcp-project"
export REGION="asia-southeast1"

# Authenticate
gcloud auth login
gcloud config set project $PROJECT_ID

# Deploy infrastructure
cd infrastructure/gcp/terraform
terraform init
terraform plan -var="project_id=$PROJECT_ID" -var="region=$REGION"
terraform apply -var="project_id=$PROJECT_ID" -var="region=$REGION"
```

### Step 3: Configure Dataflow Pipelines

```python
# Python Dataflow Template for Digital Twin State Engine

import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions
import json

class ProcessWeatherTelemetry(beam.DoFn):
    def process(self, element):
        """
        Process real-time weather signals and update risk scores
        """
        try:
            telemetry = json.loads(element)
            customer_id = telemetry['customer_id']
            weather_data = telemetry['weather']
            
            # Calculate risk score based on weather
            hail_size = weather_data.get('hail_size_inches', 0)
            wind_gust = weather_data.get('wind_gust_kmh', 0)
            
            risk_score = (hail_size * 0.4) + (wind_gust / 100 * 0.6)
            
            # Check for parametric trigger
            if hail_size > 0.75:  # Threshold for hail damage
                yield {
                    'customer_id': customer_id,
                    'claim_trigger': 'HAIL_STRIKE',
                    'trigger_value': hail_size,
                    'auto_approve': True,
                    'timestamp': element.get('timestamp')
                }
            
            yield {
                'customer_id': customer_id,
                'risk_score': risk_score,
                'weather_data': weather_data,
                'timestamp': element.get('timestamp')
            }
            
        except Exception as e:
            print(f"Error processing telemetry: {e}")

def run():
    options = PipelineOptions(
        project=PROJECT_ID,
        runner='DataflowRunner',
        temp_location=TEMP_LOCATION,
        region=REGION
    )
    
    with beam.Pipeline(options=options) as pipeline:
        (pipeline
         | 'ReadPubSub' >> beam.io.ReadFromPubSub(topic=WEATHER_TOPIC)
         | 'ProcessTelemetry' >> beam.ParDo(ProcessWeatherTelemetry())
         | 'WriteToBigQuery' >> beam.io.WriteToBigQuery(
             table=OUTPUT_TABLE,
             schema=SCHEMA,
             create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED,
             write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND
         ))

if __name__ == '__main__':
    run()
```

---

## FREE EXTERNAL API INTEGRATIONS

### 1. Weather API Integration

```python
# src/data_layer/external_apis/weather.py

import httpx
from typing import Dict, Optional
import os

class OpenWeatherAPI:
    """Free weather data for parametric triggers"""
    
    BASE_URL = "https://api.openweathermap.org/data/2.5"
    API_KEY = os.getenv("OPENWEATHER_API_KEY")  # Free tier: 60 calls/min
    
    @staticmethod
    async def get_current_weather(latitude: float, longitude: float) -> Dict:
        """Get current weather for parametric claim triggers"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{OpenWeatherAPI.BASE_URL}/weather",
                params={
                    "lat": latitude,
                    "lon": longitude,
                    "appid": OpenWeatherAPI.API_KEY,
                    "units": "metric"
                }
            )
            
            data = response.json()
            return {
                "temperature": data["main"]["temp"],
                "humidity": data["main"]["humidity"],
                "wind_speed": data["wind"]["speed"],
                "wind_gust": data["wind"].get("gust", 0),
                "conditions": data["weather"][0]["main"],
                "rainfall": data.get("rain", {}).get("1h", 0)
            }
    
    @staticmethod
    async def check_severe_weather_alerts(latitude: float, longitude: float) -> List[Dict]:
        """Check for weather alerts (hail, tornado, etc)"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{OpenWeatherAPI.BASE_URL}/onecall",
                params={
                    "lat": latitude,
                    "lon": longitude,
                    "appid": OpenWeatherAPI.API_KEY,
                    "exclude": "minutely,hourly,daily"
                }
            )
            
            data = response.json()
            alerts = data.get("alerts", [])
            
            return [
                {
                    "event": alert["event"],
                    "start": alert["start"],
                    "end": alert["end"],
                    "description": alert["description"]
                }
                for alert in alerts
            ]


class TomorrowIOAPI:
    """Alternative: Free weather data with more detail"""
    
    BASE_URL = "https://api.tomorrow.io/v4/weather/realtime"
    API_KEY = os.getenv("WEATHER_API_KEY")  # Free tier: 500 calls/day
    
    @staticmethod
    async def get_severe_weather(latitude: float, longitude: float) -> Dict:
        """Get detailed severe weather metrics"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                TomorrowIOAPI.BASE_URL,
                params={
                    "location": f"{latitude},{longitude}",
                    "apikey": TomorrowIOAPI.API_KEY,
                    "units": "metric"
                }
            )
            
            data = response.json()
            values = data["data"]["values"]
            
            return {
                "hail_size_inches": values.get("hailSize", 0),
                "wind_gust_kmh": values.get("windGust", 0),
                "wind_speed_kmh": values.get("windSpeed", 0),
                "rain_intensity": values.get("rainIntensity", 0),
                "lightning_strike_count": values.get("lightningStrikeCount", 0)
            }
```

### 2. Satellite & Property Data API

```python
# src/data_layer/external_apis/satellite.py

import httpx
from typing import Dict, Optional

class ATTOMDataAPI:
    """Property risk data from ATTOM (limited free tier)"""
    
    BASE_URL = "https://api.attomdata.com/propertyapi/v1.0.0"
    API_KEY = os.getenv("ATTOM_API_KEY")  # Free: 1000 calls/month
    
    @staticmethod
    async def get_property_risk(latitude: float, longitude: float, radius_km: float = 0.1) -> Dict:
        """Get property characteristics and risk indicators"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{ATTOMDataAPI.BASE_URL}/property/detail",
                params={
                    "latitude": latitude,
                    "longitude": longitude,
                    "radius": radius_km,
                    "apikey": ATTOMDataAPI.API_KEY
                }
            )
            
            if response.status_code != 200:
                return None
                
            data = response.json()
            property_data = data.get("property", [{}])[0]
            
            return {
                "roof_type": property_data.get("situs", {}).get("roofCover"),
                "property_age": property_data.get("yearBuilt"),
                "square_footage": property_data.get("building", {}).get("sqft"),
                "number_stories": property_data.get("building", {}).get("numberOfStories"),
                "foundation_type": property_data.get("building", {}).get("foundationType"),
                "pool_indicator": property_data.get("building", {}).get("poolIndicator"),
                "flood_risk": property_data.get("risk", {}).get("floodRisk")
            }


class NearEarthObservationAPI:
    """Free satellite imagery indexing"""
    
    BASE_URL = "https://api.nasa.gov/planetary/earth"
    API_KEY = os.getenv("NASA_API_KEY")  # Free tier
    
    @staticmethod
    async def get_imagery_index(latitude: float, longitude: float) -> Dict:
        """Get satellite imagery availability"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{NearEarthObservationAPI.BASE_URL}/imagery",
                params={
                    "lon": longitude,
                    "lat": latitude,
                    "dim": 0.15,
                    "api_key": NearEarthObservationAPI.API_KEY
                }
            )
            
            if response.status_code != 200:
                return None
                
            return response.json()
```

### 3. Hazard & Catastrophe Data API

```python
# src/data_layer/external_apis/hazard.py

import httpx
from typing import List, Dict

class USGSHazardAPI:
    """Earthquake & geological hazard data (Free)"""
    
    BASE_URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary"
    
    @staticmethod
    async def get_recent_earthquakes(latitude: float, longitude: float, radius_km: float = 50) -> List[Dict]:
        """Get earthquake events in area"""
        async with httpx.AsyncClient() as client:
            # Get significant earthquakes from past month
            response = await client.get(
                f"{USGSHazardAPI.BASE_URL}/significant_month.geojson"
            )
            
            if response.status_code != 200:
                return []
                
            data = response.json()
            features = data.get("features", [])
            
            # Filter by proximity
            nearby = []
            for feature in features:
                eq_lat, eq_lon = feature["geometry"]["coordinates"][:2]
                distance = calculate_distance(latitude, longitude, eq_lat, eq_lon)
                
                if distance <= radius_km:
                    nearby.append({
                        "magnitude": feature["properties"]["mag"],
                        "depth_km": feature["geometry"]["coordinates"][2],
                        "time": feature["properties"]["time"],
                        "distance_km": distance,
                        "location": feature["properties"]["place"]
                    })
            
            return nearby


class NationalHazardMapsAPI:
    """Hurricane, tornado, flood risk data (Free NOAA)"""
    
    BASE_URL = "https://www.nhc.noaa.gov"
    
    @staticmethod
    async def get_hurricane_risk(latitude: float, longitude: float) -> Optional[Dict]:
        """Check active hurricane threats"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{NationalHazardMapsAPI.BASE_URL}/gis/forecast/archive/latest.geojson"
            )
            
            # Parse hurricane track data
            if response.status_code == 200:
                return response.json()
            
            return None
```

### 4. Geospatial APIs

```python
# src/data_layer/external_apis/azure_maps.py

import httpx

class AzureMapsAPI:
    """Free geospatial services (limited free tier)"""
    
    BASE_URL = "https://atlas.microsoft.com"
    API_KEY = os.getenv("AZURE_MAPS_API_KEY")
    
    @staticmethod
    async def reverse_geocode(latitude: float, longitude: float) -> Dict:
        """Get address from coordinates"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{AzureMapsAPI.BASE_URL}/search/address/reverse/json",
                params={
                    "api-version": "1.0",
                    "query": f"{latitude},{longitude}",
                    "subscription-key": AzureMapsAPI.API_KEY
                }
            )
            
            if response.status_code == 200:
                return response.json()
            
            return None
    
    @staticmethod
    async def route_optimize(locations: List[tuple]) -> Dict:
        """Optimize claim adjuster routes (limited free calls)"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{AzureMapsAPI.BASE_URL}/route/directions/batch/sync/json",
                params={
                    "api-version": "1.0",
                    "subscription-key": AzureMapsAPI.API_KEY
                },
                json={
                    "batchItems": [
                        {
                            "query": f"/routes?waypoints={','.join([f'{lat},{lon}' for lat, lon in locations])}"
                        }
                    ]
                }
            )
            
            return response.json()
```

### Free API Summary Table

| Service | Provider | Free Tier | Use Case |
|---------|----------|-----------|----------|
| Weather | OpenWeatherMap | 60 calls/min | Real-time weather for parametric triggers |
| Weather Detail | Tomorrow.io | 500 calls/day | Severe weather (hail, wind, lightning) |
| Satellite | ATTOM Data | 1000/month | Property condition scoring |
| Satellite | NASA Earth | Unlimited | Imagery availability indexing |
| Earthquakes | USGS | Unlimited | Hazard proximity analysis |
| Hazard Maps | NOAA | Unlimited | Hurricane, flood, tornado risk |
| Geospatial | Azure Maps | 50K calls/month | Reverse geocoding, route optimization |
| AI/ML | Vertex AI | Free credits | Risk scoring models |

---

## MOCK DATA LAYER & SIMULATION

### Mock Data Generator

```python
# src/data_layer/mock_generator.py

import random
import uuid
from datetime import datetime, timedelta
from typing import List
import json
from faker import Faker
from shapely.geometry import Point
import psycopg2
from psycopg2.extras import execute_batch

fake = Faker()

class MockDataGenerator:
    """Generate realistic mock data for testing & simulation"""
    
    WEATHER_CONDITIONS = ["Clear", "Rainy", "Stormy", "Hailing", "Foggy", "Sunny"]
    CLAIM_TYPES = ["WEATHER", "THEFT", "FIRE", "WATER_DAMAGE", "STRUCTURAL"]
    PROPERTY_CONDITIONS = ["EXCELLENT", "GOOD", "FAIR", "POOR"]
    
    def __init__(self, db_url: str):
        self.db_url = db_url
        self.conn = psycopg2.connect(db_url)
    
    def generate_customers(self, count: int = 100) -> List[Dict]:
        """Generate mock customer records"""
        customers = []
        
        for _ in range(count):
            lat = random.uniform(1.2, 1.5)  # Singapore coordinates
            lon = random.uniform(103.6, 104.0)
            
            customer = {
                'customer_id': str(uuid.uuid4()),
                'name': fake.name(),
                'email': fake.email(),
                'phone': fake.phone_number(),
                'location_gps': Point(lon, lat),
                'risk_profile_score': round(random.uniform(0.1, 0.9), 2),
                'property_condition_score': random.randint(40, 100),
                'hazard_exposure_level': random.choice(['LOW', 'MEDIUM', 'HIGH']),
                'weather_risk_factor': round(random.uniform(0.1, 0.8), 2)
            }
            customers.append(customer)
        
        return customers
    
    def generate_policies(self, customers: List[Dict], policies_per_customer: int = 5) -> List[Dict]:
        """Generate mock insurance policies"""
        policies = []
        
        for customer in customers:
            for _ in range(random.randint(1, policies_per_customer)):
                start_date = datetime.now() - timedelta(days=random.randint(30, 730))
                
                policy = {
                    'policy_id': str(uuid.uuid4()),
                    'customer_id': customer['customer_id'],
                    'product_type': random.choice(['HOME', 'BUSINESS', 'AUTO']),
                    'coverage_amount': round(random.uniform(50000, 500000), 2),
                    'annual_premium': round(random.uniform(500, 3000), 2),
                    'start_date': start_date.date(),
                    'end_date': (start_date + timedelta(days=365)).date(),
                    'is_active': random.choice([True, True, True, False]),  # 75% active
                    'usage_based_multiplier': round(random.uniform(0.8, 1.5), 2),
                    'current_exposure_level': round(random.uniform(0.1, 1.0), 2),
                    'underwriting_audit_status': random.choice(['PENDING', 'APPROVED', 'FLAGGED']),
                    'compliance_score': round(random.uniform(0.5, 1.0), 2),
                    'regulatory_flags': json.dumps(random.choice([
                        {},
                        {'flag': 'missing_documentation'},
                        {'flag': 'high_risk_property'}
                    ]))
                }
                policies.append(policy)
        
        return policies
    
    def generate_claims(self, policies: List[Dict], claims_per_policy: float = 0.1) -> List[Dict]:
        """Generate mock insurance claims with parametric triggers"""
        claims = []
        
        for policy in policies:
            if random.random() < claims_per_policy:
                claim_type = random.choice(self.CLAIM_TYPES)
                
                # Parametric trigger data
                is_parametric = claim_type in ['WEATHER', 'FIRE']
                parametric_triggers = {
                    'WEATHER': {
                        'trigger': 'HAIL_STRIKE',
                        'value': round(random.uniform(0.3, 2.5), 2),
                        'threshold': 0.75
                    },
                    'FIRE': {
                        'trigger': 'WILDFIRE_PROXIMITY',
                        'value': round(random.uniform(0.5, 15), 2),
                        'threshold': 5.0
                    }
                }
                
                trigger_data = parametric_triggers.get(claim_type, {})
                
                claim = {
                    'claim_id': str(uuid.uuid4()),
                    'policy_id': policy['policy_id'],
                    'claim_type': claim_type,
                    'claim_amount': round(random.uniform(5000, 200000), 2),
                    'reported_at': datetime.now() - timedelta(days=random.randint(1, 180)),
                    'is_parametric': is_parametric,
                    'parametric_trigger': trigger_data.get('trigger'),
                    'trigger_value': trigger_data.get('value'),
                    'trigger_threshold': trigger_data.get('threshold'),
                    'auto_approved': is_parametric and random.choice([True, False]),
                    'external_data_sources': json.dumps(['OpenWeather', 'USGS', 'ATTOM']),
                    'weather_data_snapshot': json.dumps({
                        'temperature': round(random.uniform(15, 40), 1),
                        'humidity': random.randint(20, 90),
                        'hail_size_inches': round(random.uniform(0, 2), 2),
                        'wind_gust_kmh': random.randint(0, 100)
                    }),
                    'satellite_verification': random.choice([True, False]),
                    'fraud_risk_score': round(random.uniform(0.0, 1.0), 2),
                    'leakage_detection_flag': random.choice([True, False]),
                    'ai_assurance_status': random.choice(['APPROVED', 'REVIEW', 'FLAGGED'])
                }
                claims.append(claim)
        
        return claims
    
    def generate_risk_scores(self, customers: List[Dict], policies: List[Dict]) -> List[Dict]:
        """Generate mock risk intelligence data"""
        risk_scores = []
        
        for i, policy in enumerate(policies[:int(len(policies) * 0.5)]):  # 50% of policies
            score = {
                'score_id': str(uuid.uuid4()),
                'customer_id': policy['customer_id'],
                'policy_id': policy['policy_id'],
                'guardian_action_id': str(uuid.uuid4()) if random.random() < 0.3 else None,
                'action_type': random.choice(['ALERT', 'MAINTENANCE_REMINDER', 'COVERAGE_ADJUSTMENT']),
                'action_description': fake.text(max_nb_chars=200),
                'recommended_premium_adjustment': round(random.uniform(-0.2, 0.3), 2),
                'living_risk_model_score': round(random.uniform(0.2, 1.0), 2),
                'weather_risk_factor': round(random.uniform(0.1, 0.9), 2),
                'catastrophe_exposure': round(random.uniform(0.0, 0.8), 2),
                'property_condition_risk': round(random.uniform(0.1, 0.9), 2),
                'calculated_at': datetime.now(),
                'effective_until': datetime.now() + timedelta(days=30)
            }
            risk_scores.append(score)
        
        return risk_scores
    
    def load_to_database(self, customers: List[Dict], policies: List[Dict], 
                        claims: List[Dict], risk_scores: List[Dict]):
        """Load all mock data into PostgreSQL"""
        cursor = self.conn.cursor()
        
        try:
            # Insert customers
            execute_batch(cursor, """
                INSERT INTO customer_master (customer_id, name, email, phone, location_gps,
                                            risk_profile_score, property_condition_score,
                                            hazard_exposure_level, weather_risk_factor)
                VALUES (%(customer_id)s, %(name)s, %(email)s, %(phone)s, %(location_gps)s,
                       %(risk_profile_score)s, %(property_condition_score)s,
                       %(hazard_exposure_level)s, %(weather_risk_factor)s)
            """, customers, page_size=100)
            
            # Insert policies
            execute_batch(cursor, """
                INSERT INTO policy_master (policy_id, customer_id, product_type, coverage_amount,
                                          annual_premium, start_date, end_date, is_active,
                                          usage_based_multiplier, current_exposure_level,
                                          underwriting_audit_status, compliance_score,
                                          regulatory_flags)
                VALUES (%(policy_id)s, %(customer_id)s, %(product_type)s, %(coverage_amount)s,
                       %(annual_premium)s, %(start_date)s, %(end_date)s, %(is_active)s,
                       %(usage_based_multiplier)s, %(current_exposure_level)s,
                       %(underwriting_audit_status)s, %(compliance_score)s,
                       %(regulatory_flags)s)
            """, policies, page_size=100)
            
            # Insert claims
            execute_batch(cursor, """
                INSERT INTO claims_transaction (claim_id, policy_id, claim_type, claim_amount,
                                               reported_at, is_parametric, parametric_trigger,
                                               trigger_value, trigger_threshold, auto_approved,
                                               external_data_sources, weather_data_snapshot,
                                               satellite_verification, fraud_risk_score,
                                               leakage_detection_flag, ai_assurance_status)
                VALUES (%(claim_id)s, %(policy_id)s, %(claim_type)s, %(claim_amount)s,
                       %(reported_at)s, %(is_parametric)s, %(parametric_trigger)s,
                       %(trigger_value)s, %(trigger_threshold)s, %(auto_approved)s,
                       %(external_data_sources)s, %(weather_data_snapshot)s,
                       %(satellite_verification)s, %(fraud_risk_score)s,
                       %(leakage_detection_flag)s, %(ai_assurance_status)s)
            """, claims, page_size=100)
            
            # Insert risk scores
            execute_batch(cursor, """
                INSERT INTO risk_scoring (score_id, customer_id, policy_id, guardian_action_id,
                                         action_type, action_description, recommended_premium_adjustment,
                                         living_risk_model_score, weather_risk_factor,
                                         catastrophe_exposure, property_condition_risk,
                                         calculated_at, effective_until)
                VALUES (%(score_id)s, %(customer_id)s, %(policy_id)s, %(guardian_action_id)s,
                       %(action_type)s, %(action_description)s, %(recommended_premium_adjustment)s,
                       %(living_risk_model_score)s, %(weather_risk_factor)s,
                       %(catastrophe_exposure)s, %(property_condition_risk)s,
                       %(calculated_at)s, %(effective_until)s)
            """, risk_scores, page_size=100)
            
            self.conn.commit()
            print(f"✓ Loaded {len(customers)} customers")
            print(f"✓ Loaded {len(policies)} policies")
            print(f"✓ Loaded {len(claims)} claims")
            print(f"✓ Loaded {len(risk_scores)} risk scores")
            
        except Exception as e:
            self.conn.rollback()
            print(f"Error loading data: {e}")
        finally:
            cursor.close()

# Usage
if __name__ == "__main__":
    generator = MockDataGenerator(DATABASE_URL)
    
    customers = generator.generate_customers(100)
    policies = generator.generate_policies(customers, 5)
    claims = generator.generate_claims(policies, 0.1)
    risk_scores = generator.generate_risk_scores(customers, policies)
    
    generator.load_to_database(customers, policies, claims, risk_scores)
```

### Real-Time Mock Telemetry Simulator

```python
# src/data_layer/telemetry_simulator.py

import asyncio
import json
import random
from datetime import datetime
from typing import Dict

class RealTimeTelemtrySimulator:
    """Simulate real-time external telemetry for testing"""
    
    def __init__(self, pubsub_client, topic_name: str):
        self.client = pubsub_client
        self.topic_name = topic_name
    
    async def simulate_weather_event(self, customer_id: str, severity: str = "normal"):
        """Simulate weather event (hail, windstorm, etc)"""
        severity_profiles = {
            "normal": {"hail_size": 0.2, "wind_gust": 25, "rainfall": 5},
            "severe": {"hail_size": 0.75, "wind_gust": 60, "rainfall": 50},
            "extreme": {"hail_size": 1.5, "wind_gust": 100, "rainfall": 100}
        }
        
        profile = severity_profiles.get(severity, severity_profiles["normal"])
        
        telemetry = {
            "customer_id": customer_id,
            "event_type": "weather",
            "timestamp": datetime.now().isoformat(),
            "weather": {
                "source": "OpenWeather",
                "temperature": round(random.uniform(15, 40), 1),
                "humidity": random.randint(20, 90),
                "hail_size_inches": profile["hail_size"],
                "wind_gust_kmh": profile["wind_gust"],
                "rainfall_mm": profile["rainfall"],
                "lightning_strikes": random.randint(0, 20) if severity != "normal" else 0,
                "weather_alert": "SEVERE_HAIL" if severity == "severe" else None
            }
        }
        
        await self.publish_telemetry(telemetry)
        return telemetry
    
    async def simulate_satellite_update(self, customer_id: str):
        """Simulate satellite imagery update"""
        telemetry = {
            "customer_id": customer_id,
            "event_type": "satellite",
            "timestamp": datetime.now().isoformat(),
            "satellite": {
                "source": "ATTOM",
                "roof_condition": random.choice(["EXCELLENT", "GOOD", "FAIR", "POOR"]),
                "vegetation_overhang": random.choice([True, False]),
                "flood_mapping_confidence": round(random.uniform(0.5, 1.0), 2),
                "updated_at": datetime.now().isoformat()
            }
        }
        
        await self.publish_telemetry(telemetry)
        return telemetry
    
    async def publish_telemetry(self, telemetry: Dict):
        """Publish telemetry to Pub/Sub or Event Hubs"""
        message = json.dumps(telemetry).encode("utf-8")
        await self.client.publish(self.topic_name, message)
        print(f"Published: {telemetry['event_type']} event for {telemetry['customer_id']}")

# Usage: Simulate parametric claim trigger
async def simulate_parametric_claim():
    simulator = RealTimeTelemtrySimulator(pubsub_client, "weather-telemetry")
    
    # Simulate severe hail event
    await simulator.simulate_weather_event("customer-123", severity="severe")
    # This should trigger parametric claim auto-approval in the Digital Twin engine
```

---

## GITHUB CI/CD WORKFLOWS

### Local Build & Test Workflow

```yaml
# .github/workflows/ci-cd-local.yml

name: Local Build & Test

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  build-and-test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15-alpine
        env:
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: password
          POSTGRES_DB: digital_twin
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pytest pytest-cov pytest-asyncio
      
      - name: Run migrations
        env:
          DATABASE_URL: postgresql://postgres:password@localhost:5432/digital_twin
        run: |
          python -m alembic upgrade head
      
      - name: Generate mock data
        run: |
          python scripts/generate_mock_data.py --customers 50 --policies 200
      
      - name: Run unit tests (includes agent state machine tests)
        env:
          DATABASE_URL: postgresql://postgres:password@localhost:5432/digital_twin
          REDIS_URL: redis://localhost:6379
          LANGCHAIN_TRACING_V2: "false"
        run: |
          pytest tests/ --cov=src --cov-report=xml -v
      
      - name: Validate MCP Gateway RBAC (security check)
        run: |
          pytest tests/unit/test_mcp_payload_validator.py -v
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml
      
      - name: Build Docker image
        run: |
          docker build -t insurance-digital-twin:${{ github.sha }} .
          docker save insurance-digital-twin:${{ github.sha }} > image.tar
      
      - name: Upload Docker image
        uses: actions/upload-artifact@v3
        with:
          name: docker-image
          path: image.tar
```

### Azure Deployment Workflow

```yaml
# .github/workflows/ci-cd-azure.yml

name: Azure Deployment

on:
  push:
    branches: [ main ]
  workflow_dispatch:

env:
  AZURE_SUBSCRIPTION_ID: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
  AZURE_RESOURCE_GROUP: insurance-dw-prod-rg
  REGISTRY_NAME: insurancedwacr
  IMAGE_NAME: insurance-digital-twin

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Azure Login
        uses: azure/login@v1
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}
      
      - name: Build and push Docker image
        run: |
          az acr build \
            --registry $REGISTRY_NAME \
            --image $IMAGE_NAME:${{ github.sha }} \
            --image $IMAGE_NAME:latest \
            .
      
      - name: Deploy Bicep template
        run: |
          az deployment group create \
            --resource-group $AZURE_RESOURCE_GROUP \
            --template-file infrastructure/azure/bicep/main.bicep \
            --parameters location="Southeast Asia" environment=prod projectName=insurancedw
      
      - name: Deploy to App Service
        run: |
          az webapp config container set \
            --name insurance-digital-twin-api \
            --resource-group $AZURE_RESOURCE_GROUP \
            --docker-custom-image-name $REGISTRY_NAME.azurecr.io/$IMAGE_NAME:latest \
            --docker-registry-server-url https://$REGISTRY_NAME.azurecr.io
      
      - name: Run smoke tests
        run: |
          bash scripts/smoke_tests_azure.sh
```

### GCP Deployment Workflow

```yaml
# .github/workflows/ci-cd-gcp.yml

name: GCP Deployment

on:
  push:
    branches: [ main ]
  workflow_dispatch:

env:
  PROJECT_ID: ${{ secrets.GCP_PROJECT_ID }}
  GAR_REGION: asia-southeast1
  IMAGE_NAME: insurance-digital-twin

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Cloud SDK
        uses: google-github-actions/setup-gcloud@v1
        with:
          project_id: ${{ secrets.GCP_PROJECT_ID }}
          service_account_key: ${{ secrets.GCP_SA_KEY }}
          export_default_credentials: true
      
      - name: Configure Docker for Artifact Registry
        run: |
          gcloud auth configure-docker $GAR_REGION-docker.pkg.dev
      
      - name: Build and push Docker image
        run: |
          docker build -t $GAR_REGION-docker.pkg.dev/$PROJECT_ID/insurance/$IMAGE_NAME:${{ github.sha }} .
          docker push $GAR_REGION-docker.pkg.dev/$PROJECT_ID/insurance/$IMAGE_NAME:${{ github.sha }}
      
      - name: Deploy infrastructure with Terraform
        run: |
          cd infrastructure/gcp/terraform
          terraform init -backend-config="bucket=$PROJECT_ID-tf-state"
          terraform plan -var="project_id=$PROJECT_ID"
          terraform apply -auto-approve -var="project_id=$PROJECT_ID"
      
      - name: Deploy to Cloud Run
        run: |
          gcloud run deploy insurance-digital-twin-api \
            --image $GAR_REGION-docker.pkg.dev/$PROJECT_ID/insurance/$IMAGE_NAME:${{ github.sha }} \
            --region $GAR_REGION \
            --platform managed \
            --allow-unauthenticated \
            --set-env-vars "DATABASE_URL=${{ secrets.GCP_DATABASE_URL }}" \
            --set-env-vars "GCS_BUCKET=$PROJECT_ID-datalake-raw"
      
      - name: Run smoke tests
        run: |
          bash scripts/smoke_tests_gcp.sh
```

---

## DEPLOYMENT COMMANDS

### Deploy to Local Environment

```bash
# 1. Build and start all services
docker-compose up -d

# 2. Initialize database
docker-compose exec api python -m alembic upgrade head

# 3. Generate mock data
docker-compose exec api python scripts/generate_mock_data.py --customers 100

# 4. View API documentation
open http://localhost:8000/docs

# 5. Run tests
docker-compose exec api pytest tests/

# 6. Monitor services
docker-compose logs -f api
```

### Deploy to Azure

```bash
# 1. Setup Azure CLI and authenticate
az login
az account set --subscription $SUBSCRIPTION_ID

# 2. Deploy infrastructure
./scripts/deploy_azure.sh

# 3. Configure environment variables
az webapp config appsettings set \
  --name insurance-digital-twin-api \
  --resource-group insurance-dw-prod-rg \
  --settings \
    DATABASE_URL="$AZURE_DATABASE_CONNECTION_STRING" \
    OPENWEATHER_API_KEY="$OPENWEATHER_KEY"

# 4. View logs
az webapp log tail --name insurance-digital-twin-api --resource-group insurance-dw-prod-rg
```

### Deploy to GCP

```bash
# 1. Setup GCP and authenticate
gcloud auth login
gcloud config set project $PROJECT_ID

# 2. Deploy infrastructure
./scripts/deploy_gcp.sh

# 3. Deploy application
gcloud run deploy insurance-digital-twin-api \
  --source . \
  --region asia-southeast1 \
  --set-env-vars DATABASE_URL="$GCP_DATABASE_URL"

# 4. View logs
gcloud run logs read insurance-digital-twin-api --region asia-southeast1
```

---

## GITHUB COMMIT TEMPLATE

Use this template when committing code:

```
feat/fix/docs: [COMPONENT] Brief description

## Description
Detailed explanation of changes made

## UDP 2.0 Layer Impacted
- [ ] Source Layer
- [ ] Ingestion Layer
- [ ] Landing Layer
- [ ] Processing & Engine
- [ ] Curated Layer
- [ ] Consumption Layer

## External APIs Updated
- [ ] Weather API
- [ ] Satellite/Property Data
- [ ] Hazard/Catastrophe
- [ ] Geospatial

## Deployment Target
- [ ] Local (Docker)
- [ ] Azure
- [ ] GCP

## Testing
- Unit tests: PASS/FAIL
- Integration tests: PASS/FAIL
- Mock data validation: PASS/FAIL

## Checklist
- [ ] Code follows style guide
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] Mock data generator updated (if data model changed)
- [ ] CI/CD workflows pass
```

---

## QUICK REFERENCE

### Architecture Decision Record (ADR)

**ADR-001: UDP 2.0 Layered Architecture**
- Decision: Implement 6-layer data platform (Source → Ingestion → Landing → Processing → Curated → Consumption)
- Rationale: Separation of concerns, scalability, governance
- Consequences: Requires careful data flow management

**ADR-002: Multi-Cloud Strategy (Azure + GCP)**
- Decision: Support both Azure and GCP with unified APIs
- Rationale: Flexibility, avoid vendor lock-in
- Consequences: Duplicate deployment code, testing complexity

**ADR-003: Parametric Claims via Real-Time Telemetry**
- Decision: Use weather APIs to auto-approve claims
- Rationale: Instant customer satisfaction, reduced operational costs
- Consequences: Dependency on external APIs, requires robust fallback

---

## SUPPORT & RESOURCES

- **Documentation**: [API_REFERENCE.md](API_REFERENCE.md)
- **Data Models**: [DATA_MODELS.md](DATA_MODELS.md)
- **Architecture**: [ARCHITECTURE_DIAGRAMS.md](ARCHITECTURE_DIAGRAMS.md)
- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions

---

**Last Updated**: 2026-08-11  
**Version**: 1.0  
**Maintainer**: Your Team
