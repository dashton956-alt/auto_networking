# ANIF-200: Reference Architecture

| Field        | Value                                                      |
|--------------|------------------------------------------------------------|
| Doc ID       | ANIF-200                                                   |
| Series       | Architecture                                               |
| Version      | 0.1.0                                                      |
| Status       | Draft                                                      |
| Authors      | ANIF Working Group                                         |
| Reviewers    | —                                                          |
| Approved by  | —                                                          |
| Created      | 2026-04-07                                                 |
| Last updated | 2026-04-07                                                 |
| Replaces     | N/A                                                        |
| Related docs | ANIF-201, ANIF-202, ANIF-203, ANIF-204, ANIF-205, ANIF-300 |

---

## Abstract

This document defines the Reference Architecture for the Autonomous Networking & Infrastructure
Framework (ANIF). It establishes the architectural blueprint for an intent-driven, closed-loop,
fully auditable, and vendor-neutral autonomous networking system. The architecture governs how
business intent is received, validated, evaluated against policy, risk-scored, decided upon,
reviewed by governance, executed, and permanently logged. All derived architecture documents in
the 200-series MUST conform to the constraints and patterns described herein.

---

## 1. Introduction

### 1.1 Purpose

This document establishes the authoritative reference architecture for ANIF. It defines the
seven core components, their relationships, data flows, deployment patterns, and the integration
boundaries through which vendor-specific adapters connect without polluting core logic.

### 1.2 Scope

This document covers:

- The overall architectural philosophy and governing principles
- The seven core components and their responsibilities
- Data flow between pipeline stages
- Synchronous prototype pipeline and future asynchronous production patterns
- Deployment models: single-container prototype and multi-service production
- API boundary design
- Adapter and plugin layer placement
- Conformance to TOGAF ADM architecture domains

### 1.3 Out of Scope

- Vendor-specific adapter implementations
- Network device configuration languages or protocols
- Physical or virtual network topology design
- Operational runbooks and procedures (see 400-series)
- Detailed security controls (see ANIF-205)

### 1.4 Intended Audience

This document is intended for:

- Solution architects designing ANIF deployments
- Core contributors implementing or extending ANIF components
- Technical leads reviewing conformance of derived systems
- Integration engineers connecting vendor adapters to the ANIF platform

---

## 2. Normative References

- RFC 2119: Key words for use in RFCs to Indicate Requirement Levels
- TOGAF ADM (The Open Group Architecture Framework — Architecture Development Method)
- ETSI GS ZSM 002: Zero-touch network and Service Management — Reference Architecture
- TMForum IG1253: Autonomous Networks Technical Architecture
- IETF RFC 8969: A Framework for Automating Service and Network Management with YANG
- NIST SP 800-207: Zero Trust Architecture
- ANIF-000: Framework Constitution
- ANIF-103: Governance Principles
- ANIF-300: Core Pipeline Specification

---

## 3. Terms and Definitions

| Term              | Definition                                                                                   |
|-------------------|----------------------------------------------------------------------------------------------|
| Intent            | A declarative statement of a desired network outcome, independent of implementation detail.  |
| Pipeline          | The ordered sequence of processing stages an intent traverses from receipt to execution.     |
| Governance Gate   | The decision point that determines whether an action proceeds automatically or requires human approval. |
| Action Executor   | A component that translates a Decision into concrete network configuration changes via adapters. |
| Adapter           | A vendor- or protocol-specific module that connects an Action Executor to external infrastructure. |
| Closed Loop       | An operational pattern where execution outcomes feed back into the system to refine future decisions. |
| Audit Record      | An immutable, append-only log entry capturing the state and rationale of each pipeline stage. |
| Governance Mode   | One of three operational states: `auto`, `manual_review`, or `block`.                       |
| Trace ID          | A unique identifier propagated through all pipeline stages for end-to-end correlation.       |

---

## 4. Reference Architecture

### 4.1 Architectural Philosophy

ANIF is built on four foundational properties:

1. **Intent-Driven**: Operators express desired outcomes; the system determines the mechanism.
2. **Closed-Loop**: Execution results and feedback flow back to improve future decisions.
3. **Fully Auditable**: Every decision, approval, and action MUST be permanently recorded with full rationale.
4. **Vendor-Neutral**: Core logic MUST NOT contain vendor-specific code. Vendor integration lives exclusively in adapters.

These properties directly reflect the governing principles P-01 through P-12 defined in the
ANIF constitution. Implementations MUST satisfy all twelve principles.

### 4.2 Core Components

ANIF defines exactly seven core components:

| # | Component          | Module Path             | Primary Responsibility                                        |
|---|--------------------|-------------------------|---------------------------------------------------------------|
| 1 | Intent Engine      | `src/anif/intent/`      | Validate, parse, and normalise incoming intent objects.       |
| 2 | Policy Engine      | `src/anif/policy/`      | Evaluate intent against policy sets; resolve conflicts.       |
| 3 | Risk Engine        | `src/anif/risk/`        | Compute a quantified risk score for the proposed action.      |
| 4 | Decision Engine    | `src/anif/decision/`    | Select the bounded action that satisfies intent within policy.|
| 5 | Governance Gate    | `src/anif/governance/`  | Apply mode rules and RBAC; route to auto, review, or block.   |
| 6 | Action Executors   | `src/anif/actions/`     | Execute the decision; manage rollback on failure.             |
| 7 | Audit Service      | `src/anif/audit/`       | Write and expose immutable audit records.                     |

### 4.3 Architecture Diagram

```
                        ┌─────────────────────────────────────────────────────┐
                        │                    ANIF Platform                    │
                        │                                                     │
  Business Intent       │  ┌───────────────┐    ┌───────────────┐            │
  ─────────────────────►│  │ Intent Engine │───►│ Policy Engine │            │
  POST /validate-intent │  │               │    │               │            │
                        │  │ • Validate    │    │ • Evaluate    │            │
                        │  │ • Normalise   │    │ • Conflicts   │            │
                        │  │ • Schema check│    │ • Precedence  │            │
                        │  └───────┬───────┘    └──────┬────────┘            │
                        │          │                   │                     │
                        │          │  Intent Object    │  PolicyResult       │
                        │          └─────────┬─────────┘                    │
                        │                    ▼                               │
                        │           ┌────────────────┐                      │
                        │           │  Risk Engine   │                      │
                        │           │                │                      │
                        │           │ • Score risk   │                      │
                        │           │ • Trust quant  │                      │
                        │           └───────┬────────┘                      │
                        │                   │  RiskScore                    │
                        │                   ▼                               │
                        │          ┌─────────────────┐                      │
                        │          │ Decision Engine │                      │
                        │          │                 │                      │
                        │          │ • Action select │                      │
                        │          │ • Bounded types │                      │
                        │          └────────┬────────┘                      │
                        │                   │  Decision                     │
                        │                   ▼                               │
                        │        ┌──────────────────────┐                   │
                        │        │   Governance Gate    │                   │
                        │        │                      │                   │
                        │        │ • Mode check         │                   │
                        │        │ • RBAC check         │                   │
                        │        │ • Approval workflow  │                   │
                        │        └────────┬─────────────┘                  │
                        │                 │                                 │
                        │         ┌───────┴──────┬──────────┐               │
                        │         ▼              ▼          ▼               │
                        │       auto      manual_review   block             │
                        │         │              │                          │
                        │         │         (human approves/rejects)        │
                        │         │              │                          │
                        │         └──────┬────────┘                         │
                        │                ▼                                  │
                        │     ┌─────────────────────┐                       │
                        │     │   Action Executors  │──────────────────────►│ Network
                        │     │                     │   Adapter Layer       │ Infrastructure
                        │     │ • reroute_traffic   │  ┌────────────────┐   │
                        │     │ • apply_qos         │  │ Vendor Adapter │   │
                        │     │ • scale_bandwidth   │  │ Mock Adapter   │   │
                        │     │ • isolate_segment   │  │ Future Adapter │   │
                        │     │ • Rollback handlers │  └────────────────┘   │
                        │     └──────────┬──────────┘                       │
                        │                │  ExecutionRecord                 │
                        │                ▼                                  │
                        │     ┌─────────────────────┐                       │
                        │     │    Audit Service    │◄──────────────────────│ (all stages write)
                        │     │                     │                       │
                        │     │ • Append-only log   │                       │
                        │     │ • Queryable records │                       │
                        │     │ • Explainability    │                       │
                        │     └─────────────────────┘                       │
                        │                                                   │
                        │  ┌──────────────────────────────────────────────┐ │
                        │  │              Feedback Loop                   │ │
                        │  │  Execution outcomes → Learning suggestions   │ │
                        │  │  GET /feedback/analysis → policy refinement  │ │
                        │  └──────────────────────────────────────────────┘ │
                        └─────────────────────────────────────────────────────┘
```

### 4.4 Pipeline Data Flow

The pipeline is the ordered path an intent traverses. Each stage receives a defined input object
and produces a defined output object. All objects MUST be serialisable as JSON.

| Stage              | Input                         | Output                      | Key Fields Added                                         |
|--------------------|-------------------------------|-----------------------------|----------------------------------------------------------|
| Intent Engine      | Raw request body              | `Intent`                    | `intent_id`, `status`, `validated_at`, `constraints`    |
| Policy Engine      | `Intent`                      | `PolicyResult`              | `applicable_policies`, `conflicts`, `recommendation`    |
| Risk Engine        | `Intent` + `PolicyResult`     | `RiskScore`                 | `score` (0.0–1.0), `factors`, `trust_level`             |
| Decision Engine    | `Intent` + `RiskScore`        | `Decision`                  | `action_type`, `parameters`, `rationale`                |
| Governance Gate    | `Decision` + operator context | `GovernanceResult`          | `mode`, `ticket_id` (if manual), `outcome`              |
| Action Executors   | `Decision` + `GovernanceResult`| `ExecutionRecord`          | `execution_id`, `status`, `rollback_available`          |
| Audit Service      | All stage outputs             | `AuditRecord`               | `trace_id`, `timeline`, `why_summary`                   |

### 4.5 Component Interaction Patterns

#### 4.5.1 Prototype: Synchronous Pipeline

In the prototype deployment, components communicate via synchronous HTTP calls through the API
layer. The `/orchestrate` endpoint drives the full pipeline in a single request-response cycle.

```
Client ──POST /orchestrate──► API Layer
                                   │
                    ┌──────────────▼──────────────────┐
                    │  Orchestrator calls each stage  │
                    │  sequentially via internal      │
                    │  function calls or HTTP          │
                    └──────────────────────────────────┘
```

#### 4.5.2 Production: Asynchronous Event-Driven

In production, each component SHOULD publish domain events to a message bus. This decouples
components, enables independent scaling, and supports replay for audit purposes.

```
Intent Engine ──[IntentValidated]──► Message Bus
                                          │
                         ┌────────────────┴──────────────────┐
                         ▼                                    ▼
                  Policy Engine                         Audit Service
                  [PolicyEvaluated] ──►                (subscribes to all)
                         │
                         ▼
                  Risk Engine ...
```

This document defines the synchronous pattern as normative for prototype. The async pattern is
RECOMMENDED for production deployments handling >100 concurrent intents.

### 4.6 Deployment Architecture

#### 4.6.1 Prototype: Single Container

The prototype MUST run as a single Docker container with all components co-located. The
`docker-compose.yml` MUST define a single `anif` service exposing the FastAPI application.

```
┌─────────────────────────────────────────────┐
│              Docker Container               │
│                                             │
│  FastAPI App (uvicorn, port 8000)           │
│  ├── /intent      → Intent Engine           │
│  ├── /policy      → Policy Engine           │
│  ├── /risk        → Risk Engine             │
│  ├── /decide      → Decision Engine         │
│  ├── /governance  → Governance Gate         │
│  ├── /execute     → Action Executors        │
│  ├── /audit       → Audit Service           │
│  └── /orchestrate → Orchestrator            │
│                                             │
│  In-Memory Store (dict/list)                │
└─────────────────────────────────────────────┘
```

#### 4.6.2 Production: Multi-Service

In production, each component SHOULD be deployed as an independent service with its own
data store. Service mesh (e.g., Istio) or API gateway handles routing and mTLS.

```
┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐
│   Intent   │  │   Policy   │  │    Risk    │  │  Decision  │
│  Service   │  │  Service   │  │  Service   │  │  Service   │
│  :8001     │  │  :8002     │  │  :8003     │  │  :8004     │
└────────────┘  └────────────┘  └────────────┘  └────────────┘
┌────────────┐  ┌────────────┐  ┌────────────┐
│ Governance │  │  Actions   │  │   Audit    │
│  Service   │  │  Service   │  │  Service   │
│  :8005     │  │  :8006     │  │  :8007     │
└────────────┘  └────────────┘  └────────────┘
       │                │               │
       └────────────────┴───────────────┘
                        │
              ┌─────────────────┐
              │  API Gateway /  │
              │  Orchestrator   │
              │  :8000          │
              └─────────────────┘
```

### 4.7 API Boundary Design

ANIF MUST expose every component via a discrete API endpoint. This satisfies P-09 (Incremental
Adoption): operators can integrate individual components into existing toolchains before
committing to the full pipeline.

All API responses MUST use the standard response envelope:

```json
{
  "status": "ok|error",
  "data": {},
  "errors": [],
  "trace_id": "uuid4"
}
```

HTTP status codes MUST accurately reflect outcomes (200 OK, 201 Created, 422 Unprocessable
Entity for validation failures, 403 Forbidden for authorisation failures, 500 for server errors).

### 4.8 Adapter and Plugin Layer

The adapter layer is the ONLY location where vendor-specific code is permitted in ANIF. Core
engines MUST NOT import or depend on vendor libraries.

```
┌─────────────────────────────────────────────────────┐
│                  Core ANIF Engine                   │
│  Intent | Policy | Risk | Decision | Governance     │
└─────────────────────────┬───────────────────────────┘
                          │ Defined Action Interface
                          ▼
┌─────────────────────────────────────────────────────┐
│                   Adapter Layer                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │
│  │ Mock Adapter│  │Vendor-A SDK │  │Vendor-B API │ │
│  │ (prototype) │  │  (future)   │  │  (future)   │ │
│  └─────────────┘  └─────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────┘
                          │
                          ▼
                 Network Infrastructure
```

Adapters MUST implement the canonical Action interface. They MUST NOT call the Audit Service
directly. Execution results MUST be returned to the Action Executor, which writes the audit record.

### 4.9 Bounded Action Types

ANIF defines exactly four bounded action types in the prototype:

| Action Type       | Description                                                    |
|-------------------|----------------------------------------------------------------|
| `reroute_traffic` | Redirect traffic flows between network paths or segments.      |
| `apply_qos`       | Apply Quality of Service policies to traffic classes.          |
| `scale_bandwidth` | Increase or decrease allocated bandwidth on a link or circuit. |
| `isolate_segment` | Quarantine a network segment; requires explicit capability declaration. |

Implementations MUST NOT execute action types not in this list without extending the framework
per the plugin specification in ANIF-203.

### 4.10 Conformance to TOGAF ADM

ANIF maps to the following TOGAF ADM architecture domains:

| TOGAF Domain          | ANIF Coverage                                              |
|-----------------------|------------------------------------------------------------|
| Business Architecture | ANIF-201: capability map, value streams, stakeholder model |
| Data Architecture     | ANIF-202: data entities, flow, lineage, retention          |
| Application Architecture | ANIF-203: service decomposition, module boundaries, API design |
| Technology Architecture | ANIF-204: stack, containers, testing, code standards    |

The Security Architecture (ANIF-205) spans all TOGAF domains and is treated as a cross-cutting
concern consistent with TOGAF's security architecture guidance.

### 4.11 External Standard Alignments

| Standard          | Relevant ANIF Capability                                           |
|-------------------|--------------------------------------------------------------------|
| ETSI ZSM          | Closed-loop automation, intent translation, governance domain      |
| TMForum AN        | Autonomous network levels, intent lifecycle, closed-loop assurance |
| NIST CSF          | Risk scoring, audit, governance controls                           |
| IETF ANIMA        | Intent-based networking, autonomic control loops                   |
| ITIL 4            | Change governance, approval workflow, audit trails                 |

---

## 5. Conformance Requirements

1. Implementations MUST include all seven core components.
2. Every pipeline stage MUST write an audit record via the Audit Service.
3. Vendor-specific code MUST NOT appear outside the adapter layer.
4. All action types MUST be limited to the four bounded types unless extended via the plugin mechanism in ANIF-203.
5. All API responses MUST conform to the standard response envelope.
6. The Governance Gate MUST be traversed before any action is executed; it MUST NOT be bypassed.
7. Rollback handlers MUST be registered for every action type at system startup.
8. Every intent MUST receive a globally unique `intent_id` and `trace_id` at the Intent Engine stage.

---

## 6. Security Considerations

Security architecture is fully specified in ANIF-205. The following constraints apply at the
reference architecture level:

- The Audit Service write path MUST NOT be accessible to external callers or plugins directly.
- The Governance Gate MUST enforce RBAC before routing any decision to execution.
- All inter-service communication in production MUST use mTLS.
- Adapters MUST NOT have access to governance or audit internals.
- All inputs MUST be validated against Pydantic schemas before entering the pipeline.

---

## 7. Operational Considerations

- The orchestration endpoint (`POST /orchestrate`) provides a single entry point for the full
  pipeline; individual stage endpoints support modular integration and testing.
- Each stage MUST be independently testable via its own API endpoint.
- Health check endpoints SHOULD be provided for each service in production deployments.
- The feedback loop (`GET /feedback/analysis`) SHOULD be reviewed regularly to identify policy
  or risk model improvements.
- The rollback handler for each action MUST be tested in CI as part of every pipeline build.

---

## Appendix A: Examples

### A.1 Minimal Intent Object

```json
{
  "intent_id": "a1b2c3d4-0000-0000-0000-000000000001",
  "action": "reroute_traffic",
  "target": "segment-east-01",
  "constraints": {
    "max_latency_ms": 20,
    "region": "us-east-1",
    "allowed_zones": ["zone-a", "zone-b"]
  },
  "priority": "high",
  "requestor": "automation_agent_7",
  "trace_id": "trace-0000-0001"
}
```

### A.2 Full Pipeline Sequence (Prototype)

```
POST /orchestrate
  └─► validate-intent   → intent_id assigned
  └─► evaluate-policy   → policy conflicts resolved
  └─► score-risk        → risk_score = 0.32
  └─► decide            → action: reroute_traffic, params: {...}
  └─► governance/check  → mode: auto (score < 0.5 threshold)
  └─► execute           → execution_id assigned, status: success
  └─► audit             → audit record written (append-only)
```

---

## Appendix B: Change History

| Version | Date       | Author             | Summary                  |
|---------|------------|--------------------|--------------------------|
| 0.1.0   | 2026-04-07 | ANIF Working Group | Initial draft            |
