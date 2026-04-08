# ANIF-203: Application Architecture

| Field        | Value                                          |
|--------------|------------------------------------------------|
| Doc ID       | ANIF-203                                       |
| Series       | Architecture                                   |
| Version      | 0.1.0                                          |
| Status       | Draft                                          |
| Authors      | ANIF Working Group                             |
| Reviewers    | —                                              |
| Approved by  | —                                              |
| Created      | 2026-04-07                                     |
| Last updated | 2026-04-07                                     |
| Replaces     | N/A                                            |
| Related docs | ANIF-200, ANIF-302, ANIF-305, ANIF-306         |

---

## Abstract

This document defines the Application Architecture for the Autonomous Networking & Infrastructure
Framework (ANIF). It specifies service decomposition, module responsibilities and boundaries,
inter-module communication patterns, API layer design, the plugin and extension architecture,
plugin manifest schema, security model for plugin isolation, and the plugin lifecycle. All ANIF
implementations MUST follow the module boundaries and API conventions described herein.

---

## 1. Introduction

### 1.1 Purpose

This document establishes the authoritative application-level design for ANIF. It defines how
the seven pipeline modules and the API layer are structured, what each module owns, how modules
interact, and how the system can be extended without modifying core logic.

### 1.2 Scope

This document covers:

- Service decomposition into seven modules plus the API layer
- Module responsibility boundaries and ownership rules
- Inter-module communication: synchronous (prototype) and event-driven (production)
- API layer design: FastAPI routers, response envelope, error handling
- Plugin and extension architecture
- Plugin manifest schema
- Plugin security model and capability scoping
- Plugin lifecycle management

### 1.3 Out of Scope

- Technology stack rationale (see ANIF-204)
- Security controls and RBAC implementation (see ANIF-205)
- Data schemas and retention rules (see ANIF-202)
- Deployment and containerisation (see ANIF-204)

### 1.4 Intended Audience

- Software engineers implementing or extending ANIF modules
- Plugin authors developing action adapters, policy plugins, or custom adapters
- Technical architects reviewing the system design
- DevOps engineers deploying and operating the ANIF platform

---

## 2. Normative References

- RFC 2119: Key words for use in RFCs to Indicate Requirement Levels
- ANIF-000: Framework Constitution
- ANIF-200: Reference Architecture
- ANIF-202: Data Architecture
- ANIF-302: Plugin Development Guide
- ANIF-305: Policy Plugin Specification
- ANIF-306: Action Adapter Specification
- FastAPI Documentation: https://fastapi.tiangolo.com
- Pydantic v2 Documentation: https://docs.pydantic.dev

---

## 3. Terms and Definitions

| Term             | Definition                                                                                    |
|------------------|-----------------------------------------------------------------------------------------------|
| Module           | A bounded, self-contained Python package within `src/anif/` with defined responsibilities.   |
| API Layer        | The FastAPI application in `src/anif/api/` that routes requests to modules.                  |
| Plugin           | A registered extension that adds capability to ANIF without modifying core module code.      |
| Adapter          | A plugin of type `action` or `adapter` that connects Action Executors to network infrastructure. |
| Policy Plugin    | A plugin of type `policy` that provides additional policy evaluation logic.                  |
| Plugin Manifest  | A structured declaration of a plugin's identity, type, version, and declared capabilities.   |
| Capability       | A named permission that a plugin must declare to perform a specific operation.               |
| Entry Point      | The importable Python path to the plugin's main class or function.                           |
| Response Envelope| The standard JSON wrapper for all API responses.                                             |

---

## 4. Application Architecture

### 4.1 Service Decomposition

ANIF is decomposed into exactly eight packages: seven pipeline modules and one API layer.
Each package MUST be a Python package (contains `__init__.py`) under `src/anif/`.

```
src/anif/
├── __init__.py
├── intent/          # Module 1: Intent Engine
├── policy/          # Module 2: Policy Engine
├── risk/            # Module 3: Risk Engine
├── decision/        # Module 4: Decision Engine
├── actions/         # Module 5: Action Executors
├── governance/      # Module 6: Governance Gate
├── audit/           # Module 7: Audit Service
└── api/             # API Layer (FastAPI routers)
```

Additional top-level packages MAY exist for shared utilities (`src/anif/core/` or
`src/anif/shared/`) but MUST NOT contain business logic belonging to any module.

### 4.2 Module Responsibilities and Boundaries

Each module owns a specific set of responsibilities. Ownership means the module is the sole
author of its data entities and the sole executor of its logic. Other modules MUST NOT
duplicate or replicate the logic of a module they call.

#### 4.2.1 Intent Module (`src/anif/intent/`)

**Owns**: `Intent` entity  
**Responsibilities**:
- Validate incoming intent request bodies against the Pydantic schema
- Assign `intent_id` (UUID4) and `trace_id` (UUID4)
- Normalise field values (e.g., lowercase action names, strip whitespace from targets)
- Transition intent `status` from `pending` to `validated` or `rejected`
- Expose intent retrieval by `intent_id`

**Must NOT**:
- Evaluate policy or risk
- Make decisions or call the Governance Gate
- Write audit records directly (delegates to Audit Service)

#### 4.2.2 Policy Module (`src/anif/policy/`)

**Owns**: `PolicyResult` entity, `PolicySet` configurations  
**Responsibilities**:
- Load and maintain policy sets from `schemas/` directory
- Evaluate a validated intent against all applicable policy sets
- Detect policy conflicts and surface them (never silently resolve)
- Determine precedence when multiple policies apply
- Return a structured `PolicyResult` with recommendation

**Must NOT**:
- Modify the `Intent` object
- Compute risk scores
- Make execution decisions

#### 4.2.3 Risk Module (`src/anif/risk/`)

**Owns**: `RiskScore` entity  
**Responsibilities**:
- Compute a risk score in `[0.0, 1.0]` from the intent and policy result
- Assess blast radius: `minimal | contained | broad | critical`
- Verify reversibility of the proposed action
- Decompose the score into named contributing factors with weights
- Provide trust level assessment: `high | medium | low | untrusted`

**Must NOT**:
- Access network state directly
- Make execution decisions
- Apply policy rules

#### 4.2.4 Decision Module (`src/anif/decision/`)

**Owns**: `Decision` entity  
**Responsibilities**:
- Select the bounded action type that best satisfies the intent given the risk and policy inputs
- Construct action parameters from intent constraints and decision logic
- Write a human-readable rationale string (P-04 Explainability)
- Reject intents where no safe bounded action exists

**Must NOT**:
- Execute any action directly
- Bypass the Governance Gate
- Modify the risk score or policy result

#### 4.2.5 Actions Module (`src/anif/actions/`)

**Owns**: `ExecutionRecord` entity, rollback handlers, adapter registry  
**Responsibilities**:
- Register and maintain the adapter registry at startup
- Invoke the appropriate adapter for the decided action type
- Record exact parameters applied in `ExecutionRecord`
- Execute rollback handlers on failure or explicit rollback request
- Return execution status to the orchestrator

**Must NOT**:
- Write to the audit log directly (delegates to Audit Service)
- Override governance decisions
- Select which action type to execute (that is the Decision module's role)
- Contain vendor-specific logic in the core module; that belongs in adapters

#### 4.2.6 Governance Module (`src/anif/governance/`)

**Owns**: `GovernanceResult` entity, `ApprovalTicket` entity  
**Responsibilities**:
- Determine governance mode (`auto | manual_review | block`) from risk score and configuration
- Check RBAC: verify operator role is authorised to proceed
- Create approval tickets for `manual_review` mode; enforce 15-minute expiry
- Process approval and rejection of tickets by authorised reviewers
- Block intents that exceed the configured risk threshold

**Must NOT**:
- Execute actions
- Modify the `Decision` object
- Grant more privileges than the RBAC model permits

#### 4.2.7 Audit Module (`src/anif/audit/`)

**Owns**: `AuditRecord` entity  
**Responsibilities**:
- Accept write calls from all pipeline stages and persist `AuditRecord` entries
- Enforce append-only semantics: no delete or update operations
- Provide read endpoints for audit retrieval by `intent_id`
- Provide the `/audit/{intent_id}/why` explainability summary
- Optionally compute hash chain in production mode

**Must NOT**:
- Accept direct writes from plugins or adapters
- Modify existing records
- Expose individual record payloads without authorisation

### 4.3 Module Boundary Rules

The following rules govern inter-module interactions:

1. Modules MUST communicate only via their defined public API (function calls in prototype;
   HTTP/events in production). Internal module implementation details are private.
2. A module MUST NOT import from another module's internal sub-packages. Only the module's
   top-level `__init__.py` exports are part of the public interface.
3. Circular imports between modules are PROHIBITED. The dependency direction MUST follow
   the pipeline order: intent → policy → risk → decision → governance → actions → audit.
4. The Audit module MAY be called by any upstream module (it is the single exception to
   strict pipeline ordering, as every stage writes audit records).
5. Modules MUST NOT share mutable state. The in-memory store MUST be accessed only through
   defined repository functions, not by direct dict manipulation from outside the module.

### 4.4 Inter-Module Communication

#### 4.4.1 Prototype: Direct Function Calls

In the prototype, the orchestrator calls module functions directly. This is acceptable for
a single-process deployment and simplifies testing.

```python
# Prototype orchestration pattern (illustrative)
intent = intent_engine.validate(request_body)
policy_result = policy_engine.evaluate(intent)
risk_score = risk_engine.score(intent, policy_result)
decision = decision_engine.decide(intent, policy_result, risk_score)
gov_result = governance_gate.check(decision, operator_context)
if gov_result.outcome == "approved":
    execution = action_executor.execute(decision)
audit_service.record(stage="executed", payload=execution)
```

#### 4.4.2 Production: Event-Driven Communication

In production, each module SHOULD publish domain events to a message broker. Consumers
subscribe to relevant event topics. This enables independent scaling and replay capability.

```
Topic: anif.intent.validated    → consumed by: policy, audit
Topic: anif.policy.evaluated    → consumed by: risk, audit
Topic: anif.risk.scored         → consumed by: decision, audit
Topic: anif.decision.made       → consumed by: governance, audit
Topic: anif.governance.result   → consumed by: actions, audit
Topic: anif.execution.completed → consumed by: feedback, audit
```

The event-driven pattern is RECOMMENDED for production deployments. The prototype MUST
provide the synchronous pattern as a baseline. Both patterns MUST produce identical
audit records.

### 4.5 API Layer Design

The API layer (`src/anif/api/`) MUST be implemented using FastAPI. Each module MUST have
a corresponding router module in `src/anif/api/`.

```
src/anif/api/
├── __init__.py
├── main.py          # FastAPI app instantiation; router registration
├── deps.py          # Shared dependencies (auth, store injection)
├── routers/
│   ├── intent.py    # POST /validate-intent, GET /intent/{intent_id}
│   ├── policy.py    # POST /evaluate-policy
│   ├── risk.py      # POST /score-risk
│   ├── decision.py  # POST /decide
│   ├── governance.py# POST /governance/check, POST /governance/approve/{ticket_id},
│   │                #   POST /governance/reject/{ticket_id}
│   ├── execution.py # POST /execute, POST /rollback/{intent_id},
│   │                #   GET /execution/{execution_id}
│   ├── audit.py     # GET /audit/{intent_id}, GET /audit/{intent_id}/why, GET /audit
│   ├── orchestrate.py # POST /orchestrate, GET /orchestrate/{intent_id}/status
│   └── feedback.py  # GET /feedback/analysis, POST /feedback/accept/{suggestion_id},
│                    #   POST /feedback/reject/{suggestion_id}
└── models/
    ├── requests.py  # Pydantic request body models for each endpoint
    └── responses.py # Standard response envelope and per-endpoint response models
```

#### 4.5.1 Standard Response Envelope

All API responses MUST use the following response envelope:

```json
{
  "status": "ok",
  "data": {},
  "errors": [],
  "trace_id": "uuid4-string"
}
```

- `status`: MUST be `"ok"` on success, `"error"` on any failure.
- `data`: MUST contain the primary response payload on success; MUST be `{}` on error.
- `errors`: MUST be an empty list on success; MUST contain structured error objects on failure.
  Each error object MUST include `{ "code": "string", "message": "string" }`.
  Error messages MUST NOT expose internal state, stack traces, or file paths.
- `trace_id`: MUST be present on all responses, including errors, for correlation.

#### 4.5.2 HTTP Status Code Conventions

| Scenario                        | HTTP Status |
|---------------------------------|-------------|
| Successful creation             | 201 Created |
| Successful retrieval/processing | 200 OK      |
| Validation failure (schema)     | 422 Unprocessable Entity |
| Authorisation failure           | 403 Forbidden |
| Resource not found              | 404 Not Found |
| Ticket expired                  | 410 Gone    |
| Governance block                | 403 Forbidden |
| Internal server error           | 500 Internal Server Error |

Implementations MUST NOT return 500 for validation errors. Pydantic validation failures
MUST result in 422 responses.

### 4.6 Plugin and Extension Architecture

The plugin architecture allows ANIF to be extended with new capabilities without modifying
core module code. This is required to satisfy P-08 (Vendor Neutrality) and P-09 (Incremental
Adoption).

Three plugin types are defined:

| Plugin Type | Purpose                                                            | Owner Module |
|-------------|--------------------------------------------------------------------|--------------|
| `action`    | Implements execution logic for one or more bounded action types.   | Actions      |
| `policy`    | Provides additional policy evaluation logic.                       | Policy       |
| `adapter`   | Translates a bounded action into vendor-specific API calls.        | Actions      |

#### 4.6.1 Plugin Manifest Schema

Every plugin MUST include a manifest file (`plugin.yaml`) at the package root. The manifest
MUST conform to the following schema:

```yaml
# plugin.yaml — Required for all ANIF plugins
name: string           # REQUIRED. Unique plugin identifier. snake_case.
version: string        # REQUIRED. Semantic version: MAJOR.MINOR.PATCH
type: string           # REQUIRED. Enum: action | policy | adapter
entry_point: string    # REQUIRED. Importable Python path to the plugin class or function.
                       #   Example: "my_vendor_adapter.adapter.MyVendorAdapter"
capabilities: list     # REQUIRED. List of capability strings the plugin declares.
                       #   Action plugins: must list each action type they handle.
                       #   Adapter plugins: must list vendor targets and zones.
                       #   Policy plugins: must list policy domains they cover.
api_version: string    # REQUIRED. ANIF API version this plugin is compatible with.
                       #   Example: "1.0"
description: string    # OPTIONAL. Human-readable description.
author: string         # OPTIONAL.
license: string        # OPTIONAL.
dependencies:          # OPTIONAL. Python package dependencies with version constraints.
  - package_name>=version
```

Example action adapter manifest:

```yaml
name: mock_network_adapter
version: 1.0.0
type: adapter
entry_point: anif.actions.adapters.mock.MockNetworkAdapter
capabilities:
  - action:reroute_traffic
  - action:apply_qos
  - action:scale_bandwidth
  - action:isolate_segment
  - zone:mock
api_version: "1.0"
description: Mock adapter for testing and development. Does not connect to real infrastructure.
author: ANIF Working Group
license: Apache-2.0
```

#### 4.6.2 Plugin Registration

Plugins MUST be registered at application startup. The Actions module and Policy module
each maintain a plugin registry. Registration MUST:

1. Load the `plugin.yaml` manifest
2. Validate the manifest against the manifest schema
3. Verify the `entry_point` is importable
4. Record declared capabilities in the registry
5. Fail startup if a required plugin (e.g., at least one action adapter) is not registered

```
Startup sequence:
  1. Load plugins from configured plugin paths
  2. Validate manifests
  3. Import entry points
  4. Register capabilities
  5. Verify required capability coverage (all four action types must have a handler)
  6. If verification fails → abort startup, do not proceed to listen for requests
```

#### 4.6.3 Plugin Security Model

Plugin security enforces P-05 (Least Privilege). A plugin MUST only access the capabilities
it has declared in its manifest. Undeclared capabilities MUST be denied at runtime.

```
Capability enforcement rules:

1. An adapter plugin declared for action:reroute_traffic MUST NOT be called for
   action:isolate_segment unless it also declares action:isolate_segment.

2. A policy plugin declared for domain:qos MUST NOT load policies in domain:security
   unless it declares domain:security.

3. All plugins MUST be called through the module's plugin registry, never imported directly
   by other modules or the API layer.

4. Plugins MUST NOT have direct access to:
   - The audit log write path (must go through Audit Service public API)
   - The in-memory store (must go through module repository functions)
   - The governance module internals
   - Other plugins' internals

5. Plugins run in the same process in the prototype. In production, plugins SHOULD be
   isolated in subprocess or container contexts to enforce boundaries at the OS level.
```

#### 4.6.4 Plugin Lifecycle

```
                    INSTALLED
                        │
                    (validate manifest)
                        │
                    REGISTERED
                        │
                    (enable in config)
                        │
                    ENABLED ◄────────────────────────────────┐
                        │                                    │
                    (in use by pipeline)                     │
                        │                                    │
              ┌─────────┴────────────────┐                  │
              │                          │                  │
           DISABLE                    UPDATE                │
              │                          │                  │
          DISABLED                  (new version            │
              │                     installed,              │
              │                     old unregistered)       │
              │                          │                  │
           UNINSTALL               RE-ENABLED ──────────────┘
              │
           REMOVED
```

- INSTALLED: Plugin package present in the filesystem or plugin directory.
- REGISTERED: Manifest validated; entry point imported; capabilities recorded.
- ENABLED: Plugin is active and will be called for declared capabilities.
- DISABLED: Plugin is registered but not active; existing records referencing it remain valid.
- REMOVED: Plugin unregistered and removed; MUST NOT be referenced in new pipeline runs.

Plugin rollback: if an updated plugin fails validation or causes errors, the previous version
MUST be re-enabled if still available. If not available, the affected action types MUST be
suspended and a governance `block` outcome returned for those action types until a working
plugin is registered.

---

## 5. Conformance Requirements

1. All seven modules MUST be implemented as separate Python packages under `src/anif/`.
2. Each module MUST expose a public interface through its `__init__.py`; internal sub-modules MUST NOT be imported directly by other modules.
3. All API endpoints MUST use the standard response envelope defined in Section 4.5.1.
4. HTTP status codes MUST follow the conventions in Section 4.5.2.
5. All plugins MUST include a conformant `plugin.yaml` manifest.
6. At least one action adapter plugin covering all four bounded action types MUST be registered at startup.
7. Plugins MUST NOT access modules they have not declared capabilities for.
8. The Audit Service write path MUST NOT be accessible to plugins directly.
9. Circular imports between modules are PROHIBITED.

---

## 6. Security Considerations

- Plugin manifests MUST be validated before loading; a malformed or unsigned manifest MUST
  cause the plugin to be rejected.
- In production, plugins from untrusted sources SHOULD be executed in isolated subprocess
  or container contexts.
- Plugin capability declarations MUST be enforced at call time, not only at registration.
- The API layer MUST authenticate all requests before routing to modules (see ANIF-205).
- Internal module errors MUST NOT propagate stack traces to API responses.

---

## 7. Operational Considerations

- Plugin registrations SHOULD be logged at INFO level with the plugin name, version, and
  declared capabilities at startup.
- Failed plugin registrations MUST be logged at ERROR level with the reason.
- Plugin capability gaps (action types with no registered handler) MUST prevent system
  startup to avoid silent failures in production.
- The plugin lifecycle state SHOULD be queryable via a `/status` or `/health` endpoint.
- Plugin updates SHOULD be performed without restarting the entire platform in production;
  the plugin registry SHOULD support hot-reload of individual plugins.

---

## Appendix A: Examples

### A.1 Minimal Plugin Directory Structure

```
my_vendor_adapter/
├── plugin.yaml              # Required manifest
├── __init__.py
├── adapter.py               # Entry point class
├── client.py                # Vendor API client (internal)
└── tests/
    └── test_adapter.py
```

### A.2 Sample FastAPI Router (Intent Module)

```python
# src/anif/api/routers/intent.py
from fastapi import APIRouter, Depends
from anif.api.models.requests import ValidateIntentRequest
from anif.api.models.responses import APIResponse
from anif.intent import validate_intent, get_intent

router = APIRouter(prefix="/validate-intent", tags=["intent"])

@router.post("", response_model=APIResponse, status_code=201)
async def validate(request: ValidateIntentRequest) -> APIResponse:
    """Validate and normalise an incoming intent."""
    intent = validate_intent(request)
    return APIResponse(status="ok", data=intent.model_dump(), trace_id=intent.trace_id)
```

### A.3 Plugin Capability Check (Illustrative)

```python
# src/anif/actions/registry.py
def get_adapter_for_action(action_type: ActionType) -> Adapter:
    """Return the registered adapter for the given action type.

    Raises CapabilityError if no adapter declares the required capability.
    """
    capability = f"action:{action_type.value}"
    adapter = _registry.get(capability)
    if adapter is None:
        raise CapabilityError(f"No adapter registered for capability: {capability}")
    return adapter
```

---

## Appendix B: Change History

| Version | Date       | Author             | Summary                  |
|---------|------------|--------------------|--------------------------|
| 0.1.0   | 2026-04-07 | ANIF Working Group | Initial draft            |
