# ANIF-202: Data Architecture

| Field        | Value                    |
|--------------|--------------------------|
| Doc ID       | ANIF-202                 |
| Series       | Architecture             |
| Version      | 0.1.0                    |
| Status       | Draft                    |
| Authors      | ANIF Working Group       |
| Reviewers    | —                        |
| Approved by  | —                        |
| Created      | 2026-04-07               |
| Last updated | 2026-04-07               |
| Replaces     | N/A                      |
| Related docs | ANIF-200, ANIF-307, ANIF-600 |

---

## Abstract

This document defines the Data Architecture for the Autonomous Networking & Infrastructure
Framework (ANIF). It specifies all data entities, their schemas, lifecycle rules, immutability
constraints, retention requirements, storage models, data sovereignty enforcement, schema
versioning strategy, and data lineage traceability. All ANIF components that produce or consume
data MUST conform to the entity definitions and lifecycle rules described herein.

---

## 1. Introduction

### 1.1 Purpose

This document establishes authoritative definitions for all data entities in the ANIF pipeline.
It ensures consistent data contracts across components, supports compliance through defined
retention and immutability rules, and enables full traceability from a network state change
back to the originating business intent.

### 1.2 Scope

This document covers:

- All nine core data entities and their field-level schemas
- Data creation, read, and transformation responsibilities at each pipeline stage
- Immutability rules and append-only constraints
- Data retention requirements by entity type
- In-memory (prototype) vs. persistent (production) storage models
- Data sovereignty: how intent constraints flow through to execution
- Schema versioning strategy
- Data lineage and traceability

### 1.3 Out of Scope

- Database technology selection (vendor-specific)
- Backup and disaster recovery procedures
- Data encryption at rest (see ANIF-205)
- Network telemetry data ingested from external monitoring systems

### 1.4 Intended Audience

- Data architects and database engineers implementing ANIF storage layers
- Core contributors who create or consume ANIF data entities
- Compliance officers verifying data governance controls
- Integration engineers mapping ANIF schemas to external systems

---

## 2. Normative References

- RFC 2119: Key words for use in RFCs to Indicate Requirement Levels
- ANIF-000: Framework Constitution
- ANIF-200: Reference Architecture
- ANIF-307: Audit Log Specification
- ANIF-600: Schema Registry and Versioning
- Pydantic v2 Documentation: Data validation using Python type annotations
- ISO 8601: Date and time format standard

---

## 3. Terms and Definitions

| Term              | Definition                                                                                     |
|-------------------|------------------------------------------------------------------------------------------------|
| Entity            | A named, structured data object with defined fields, types, and lifecycle rules.               |
| Immutable         | A record that MUST NOT be modified after it is written. Only creation is permitted.            |
| Append-Only       | A store where records may only be added; no updates or deletes are permitted.                  |
| Schema Version    | A semantic version string identifying the structure of a data entity at a point in time.       |
| Data Lineage      | The traceable chain of causality from a network change back to its originating intent.         |
| Trace ID          | A UUID4 propagated through all pipeline stages, linking all records for a single intent invocation. |
| Data Residency    | The requirement that certain data is stored and processed only within specified geographic zones.|
| In-memory Store   | A transient storage mechanism (Python dict/list) used in the prototype for simplicity.         |

---

## 4. Data Architecture

### 4.1 Data Entity Overview

ANIF defines nine canonical data entities. Each entity is owned by exactly one pipeline
component. Ownership means the owning component is solely responsible for creating and
validating instances of that entity.

| Entity              | Owner Component    | Mutability      | Storage (Prototype) | Storage (Production)    |
|---------------------|-------------------|-----------------|---------------------|-------------------------|
| `Intent`            | Intent Engine     | Immutable after validation | In-memory dict | Relational / Document DB |
| `PolicyResult`      | Policy Engine     | Immutable       | In-memory dict      | Relational / Document DB |
| `RiskScore`         | Risk Engine       | Immutable       | In-memory dict      | Relational / Document DB |
| `Decision`          | Decision Engine   | Immutable       | In-memory dict      | Relational / Document DB |
| `GovernanceResult`  | Governance Gate   | Immutable       | In-memory dict      | Relational / Document DB |
| `ApprovalTicket`    | Governance Gate   | Mutable (status only) | In-memory dict | Relational DB        |
| `ExecutionRecord`   | Action Executors  | Immutable       | In-memory dict      | Relational / Document DB |
| `AuditRecord`       | Audit Service     | Append-only     | In-memory list      | Append-only log store   |
| `FeedbackSuggestion`| Feedback Module   | Mutable (status only) | In-memory dict | Relational DB        |

### 4.2 Entity Schemas

All schemas MUST be implemented as Pydantic v2 models. Field names use snake_case. All
datetime fields MUST use ISO 8601 format with UTC timezone.

#### 4.2.1 Intent

```
Intent {
  intent_id:       UUID4       -- REQUIRED. Assigned by Intent Engine at validation.
  schema_version:  str         -- REQUIRED. Entity schema version (e.g., "1.0.0").
  trace_id:        UUID4       -- REQUIRED. Propagated through all pipeline stages.
  action:          ActionType  -- REQUIRED. Enum: reroute_traffic | apply_qos |
                               --           scale_bandwidth | isolate_segment
  target:          str         -- REQUIRED. Identifier of the target network resource.
  constraints:     dict        -- REQUIRED. Key-value constraints (max_latency_ms,
                               --           region, allowed_zones, etc.)
  priority:        Priority    -- REQUIRED. Enum: low | medium | high | critical
  requestor:       str         -- REQUIRED. Identity of the requesting entity.
  requestor_role:  Role        -- REQUIRED. RBAC role of the requestor.
  submitted_at:    datetime    -- REQUIRED. UTC timestamp of submission.
  validated_at:    datetime    -- OPTIONAL. UTC timestamp of successful validation.
  status:          IntentStatus-- REQUIRED. Enum: pending | validated | rejected |
                               --           executed | failed | rolled_back
  dry_run:         bool        -- REQUIRED. If true, no action is executed.
  metadata:        dict        -- OPTIONAL. Arbitrary caller-defined key-value pairs.
}
```

#### 4.2.2 PolicyResult

```
PolicyResult {
  result_id:           UUID4    -- REQUIRED. Unique identifier for this result.
  intent_id:           UUID4    -- REQUIRED. Foreign key to Intent.
  trace_id:            UUID4    -- REQUIRED.
  schema_version:      str      -- REQUIRED.
  applicable_policies: list[str]-- REQUIRED. Policy IDs that matched the intent.
  conflicts_detected:  bool     -- REQUIRED. True if any policy conflicts were found.
  conflicts:           list[dict]-- REQUIRED. Descriptions of each detected conflict.
  recommendation:      str      -- REQUIRED. Enum: proceed | proceed_with_caution | block
  policy_metadata:     dict     -- OPTIONAL.
  evaluated_at:        datetime -- REQUIRED.
}
```

#### 4.2.3 RiskScore

```
RiskScore {
  score_id:       UUID4   -- REQUIRED. Unique identifier.
  intent_id:      UUID4   -- REQUIRED. Foreign key to Intent.
  trace_id:       UUID4   -- REQUIRED.
  schema_version: str     -- REQUIRED.
  score:          float   -- REQUIRED. Value in range [0.0, 1.0]. Higher = more risk.
  trust_level:    str     -- REQUIRED. Enum: high | medium | low | untrusted
  factors:        list[dict] -- REQUIRED. Individual risk factors and their contributions.
                           --   Each factor: { name: str, weight: float, value: float }
  blast_radius:   str     -- REQUIRED. Enum: minimal | contained | broad | critical
  reversibility:  bool    -- REQUIRED. Whether the action is fully reversible.
  scored_at:      datetime-- REQUIRED.
}
```

#### 4.2.4 Decision

```
Decision {
  decision_id:    UUID4      -- REQUIRED.
  intent_id:      UUID4      -- REQUIRED. Foreign key to Intent.
  trace_id:       UUID4      -- REQUIRED.
  schema_version: str        -- REQUIRED.
  action_type:    ActionType -- REQUIRED. Must match intent.action.
  parameters:     dict       -- REQUIRED. Action-specific execution parameters.
  rationale:      str        -- REQUIRED. Human-readable explanation of the decision.
  risk_score_id:  UUID4      -- REQUIRED. Foreign key to RiskScore used.
  policy_result_id: UUID4    -- REQUIRED. Foreign key to PolicyResult used.
  decided_at:     datetime   -- REQUIRED.
}
```

#### 4.2.5 GovernanceResult

```
GovernanceResult {
  governance_id:  UUID4           -- REQUIRED.
  decision_id:    UUID4           -- REQUIRED. Foreign key to Decision.
  intent_id:      UUID4           -- REQUIRED.
  trace_id:       UUID4           -- REQUIRED.
  schema_version: str             -- REQUIRED.
  mode:           GovernanceMode  -- REQUIRED. Enum: auto | manual_review | block
  outcome:        str             -- REQUIRED. Enum: approved | pending | rejected | blocked
  ticket_id:      UUID4 | null    -- REQUIRED when mode = manual_review, else null.
  operator_role:  str             -- REQUIRED. Role of the operator who triggered governance.
  evaluated_at:   datetime        -- REQUIRED.
  resolved_at:    datetime | null -- Set when outcome is finalised.
}
```

#### 4.2.6 ApprovalTicket

```
ApprovalTicket {
  ticket_id:      UUID4       -- REQUIRED.
  decision_id:    UUID4       -- REQUIRED.
  intent_id:      UUID4       -- REQUIRED.
  trace_id:       UUID4       -- REQUIRED.
  schema_version: str         -- REQUIRED.
  status:         TicketStatus-- REQUIRED. Enum: pending | approved | rejected | expired
  created_at:     datetime    -- REQUIRED.
  expires_at:     datetime    -- REQUIRED. MUST be created_at + 15 minutes.
  resolved_at:    datetime | null -- Set when approved/rejected.
  resolved_by:    str | null  -- Identity of approver or rejecter.
  resolution_note:str | null  -- Optional note from approver.
}
```

Note: `ApprovalTicket.status` is the ONLY mutable field across all entities. All other
entity fields MUST NOT be modified after the entity is created.

#### 4.2.7 ExecutionRecord

```
ExecutionRecord {
  execution_id:       UUID4           -- REQUIRED.
  decision_id:        UUID4           -- REQUIRED.
  intent_id:          UUID4           -- REQUIRED.
  trace_id:           UUID4           -- REQUIRED.
  schema_version:     str             -- REQUIRED.
  action_type:        ActionType      -- REQUIRED.
  adapter_used:       str             -- REQUIRED. Identifier of the adapter that executed.
  parameters_applied: dict            -- REQUIRED. Exact parameters sent to adapter.
  status:             ExecutionStatus -- REQUIRED. Enum: success | failed | rolled_back
  rollback_available: bool            -- REQUIRED.
  rollback_id:        UUID4 | null    -- Set if a rollback was subsequently executed.
  started_at:         datetime        -- REQUIRED.
  completed_at:       datetime        -- REQUIRED.
  error_detail:       str | null      -- Populated on failure; MUST NOT contain stack traces.
}
```

#### 4.2.8 AuditRecord

```
AuditRecord {
  audit_id:       UUID4    -- REQUIRED. Unique per audit entry.
  intent_id:      UUID4    -- REQUIRED.
  trace_id:       UUID4    -- REQUIRED.
  schema_version: str      -- REQUIRED.
  stage:          str      -- REQUIRED. Enum: intent_validated | policy_evaluated |
                           --   risk_scored | decision_made | governance_checked |
                           --   executed | rolled_back | feedback_submitted
  actor:          str      -- REQUIRED. Component or user identity writing the record.
  actor_role:     str      -- REQUIRED.
  summary:        str      -- REQUIRED. Human-readable description of the event.
  payload:        dict     -- REQUIRED. Complete snapshot of the stage output object.
  previous_hash:  str      -- OPTIONAL (RECOMMENDED for production). SHA-256 of previous record.
  recorded_at:    datetime -- REQUIRED.
}
```

#### 4.2.9 FeedbackSuggestion

```
FeedbackSuggestion {
  suggestion_id:  UUID4          -- REQUIRED.
  source_intent_id: UUID4        -- REQUIRED. Intent that generated this suggestion.
  trace_id:       UUID4          -- REQUIRED.
  schema_version: str            -- REQUIRED.
  suggestion_type:str            -- REQUIRED. Enum: policy_update | risk_threshold |
                                 --   action_parameter | escalation_rule
  description:    str            -- REQUIRED.
  proposed_change:dict           -- REQUIRED. Machine-readable change proposal.
  status:         SuggestionStatus-- REQUIRED. Enum: pending | accepted | rejected
  generated_at:   datetime       -- REQUIRED.
  resolved_at:    datetime | null-- Set when accepted or rejected.
  resolved_by:    str | null     -- Identity of the policy administrator.
}
```

### 4.3 Data Flow Through the Pipeline

The following table describes what data is created or consumed at each pipeline stage.

| Stage              | Creates             | Reads                                  | Key Data Actions                                          |
|--------------------|---------------------|----------------------------------------|-----------------------------------------------------------|
| Intent Engine      | `Intent`            | Raw request body                       | Assigns intent_id, trace_id; validates schema; sets status=validated |
| Policy Engine      | `PolicyResult`      | `Intent`                               | Evaluates applicable policies; detects conflicts; sets recommendation |
| Risk Engine        | `RiskScore`         | `Intent`, `PolicyResult`               | Computes score 0.0–1.0; assesses blast_radius; checks reversibility |
| Decision Engine    | `Decision`          | `Intent`, `PolicyResult`, `RiskScore`  | Selects action_type; constructs parameters; writes rationale |
| Governance Gate    | `GovernanceResult`, `ApprovalTicket`(if manual) | `Decision`, operator context | Routes based on mode; creates ticket if manual_review |
| Action Executors   | `ExecutionRecord`   | `Decision`, `GovernanceResult`         | Invokes adapter; records exact parameters applied; captures outcome |
| Audit Service      | `AuditRecord`       | All stage outputs                      | Appends record; computes hash chain in production |
| Feedback Module    | `FeedbackSuggestion`| `AuditRecord` history, `ExecutionRecord`| Analyses patterns; generates suggestions for policy admin |

### 4.4 Immutability Rules

The following immutability rules MUST be enforced at the application layer and, where possible,
at the storage layer.

1. `Intent` objects MUST NOT be modified after `status` transitions to `validated`. The
   `validated_at` field MUST be set at that transition and never changed thereafter.
2. `PolicyResult`, `RiskScore`, `Decision`, `ExecutionRecord` MUST be treated as write-once
   records. There are no update endpoints for these entities.
3. `AuditRecord` is append-only. The Audit Service MUST NOT expose any endpoint to update or
   delete records.
4. `ApprovalTicket.status` is the sole mutable field permitted across all entities. It MAY
   transition: `pending` → `approved`, `pending` → `rejected`, `pending` → `expired`.
   Once in a terminal state (`approved`, `rejected`, `expired`), it MUST NOT change again.
5. `FeedbackSuggestion.status` MAY transition: `pending` → `accepted`, `pending` → `rejected`.
   Terminal states are not reversible.

### 4.5 Data Retention Requirements

| Entity              | Minimum Retention | Rationale                                                       |
|---------------------|-------------------|-----------------------------------------------------------------|
| `Intent`            | 7 years           | Regulatory compliance; basis for audit evidence                 |
| `PolicyResult`      | 7 years           | Required to reconstruct decision rationale                      |
| `RiskScore`         | 7 years           | Required for audit and forensic analysis                        |
| `Decision`          | 7 years           | Required for compliance review                                  |
| `GovernanceResult`  | 7 years           | Required for governance audit                                   |
| `ApprovalTicket`    | 7 years           | Approval trail for compliance                                   |
| `ExecutionRecord`   | 7 years           | Evidence of actions taken on network infrastructure             |
| `AuditRecord`       | 7 years (minimum) | Primary compliance artefact; SHOULD be retained indefinitely    |
| `FeedbackSuggestion`| 3 years           | Operational improvement record                                  |

Organisations in regulated industries MUST verify applicable retention obligations and extend
minimum periods accordingly. Retention periods begin from the `recorded_at` or `created_at`
timestamp of the entity.

### 4.6 Storage Models

#### 4.6.1 Prototype: In-Memory Store

In the prototype, all entities are stored in Python dictionaries or lists held in process memory.
The prototype store MUST be structured as:

```python
# Prototype in-memory store structure
store = {
    "intents":          {},   # dict[str, Intent]
    "policy_results":   {},   # dict[str, PolicyResult]
    "risk_scores":      {},   # dict[str, RiskScore]
    "decisions":        {},   # dict[str, Decision]
    "governance":       {},   # dict[str, GovernanceResult]
    "tickets":          {},   # dict[str, ApprovalTicket]
    "executions":       {},   # dict[str, ExecutionRecord]
    "audit_log":        [],   # list[AuditRecord] -- append-only enforced in code
    "feedback":         {},   # dict[str, FeedbackSuggestion]
}
```

The prototype store is transient; data does not survive process restarts. This is acceptable
for development and testing but MUST NOT be used in production.

#### 4.6.2 Production: Persistent Store

In production, each entity type SHOULD be stored in an appropriate persistent store:

| Entity Type               | Recommended Store Type      | Notes                                             |
|---------------------------|-----------------------------|---------------------------------------------------|
| Intents, Results, Scores  | Relational DB or Document DB| Indexed on intent_id, trace_id                   |
| AuditRecord               | Append-only log store        | e.g., immutable blob storage, write-once DB tables|
| ApprovalTicket            | Relational DB               | Requires update capability for status transitions |
| FeedbackSuggestion        | Relational DB               | Requires update capability for status transitions |

The Audit Service MUST be backed by a store that enforces append-only constraints at the
storage layer in production, not only at the application layer.

### 4.7 Data Sovereignty

Data sovereignty is enforced through Intent constraints that MUST be propagated to all
downstream stages without modification.

```
Intent.constraints = {
  "region": "us-east-1",
  "allowed_zones": ["zone-a", "zone-b"],
  "data_residency": "EU"          -- optional; restricts audit log storage region
}
```

1. The Intent Engine MUST validate that `region` and `allowed_zones` are present when required
   by the applicable policy set.
2. The Decision Engine MUST pass `constraints` unmodified to the Action Executor via the
   `Decision.parameters` object.
3. The Action Executor MUST enforce `allowed_zones` when selecting the adapter target. An
   executor MUST NOT execute an action in a zone not listed in `allowed_zones`.
4. If `data_residency` is specified in the Intent constraints, the Audit Service MUST write
   audit records to a store located in the specified region. This MAY require routing to a
   region-specific audit endpoint in production.
5. Constraints MUST NOT be removed or overridden by any pipeline component. Violations MUST
   result in a `block` governance outcome.

### 4.8 Schema Versioning Strategy

All entity schemas carry a `schema_version` field using semantic versioning (`MAJOR.MINOR.PATCH`).

| Change Type          | Version Bump | Backward Compatible? | Migration Required? |
|----------------------|--------------|----------------------|---------------------|
| Add optional field   | MINOR        | Yes                  | No                  |
| Add required field   | MAJOR        | No                   | Yes                 |
| Remove field         | MAJOR        | No                   | Yes                 |
| Rename field         | MAJOR        | No                   | Yes                 |
| Change field type    | MAJOR        | No                   | Yes                 |
| Add enum value       | MINOR        | Yes                  | No                  |
| Remove enum value    | MAJOR        | No                   | Yes                 |

ANIF implementations MUST:

1. Include `schema_version` in every serialised entity.
2. Validate incoming entities against the expected schema version at each component boundary.
3. Reject entities with an unsupported schema version with HTTP 422.
4. Maintain schema history in the schema registry (see ANIF-600).
5. Never silently ignore unknown fields; log a warning and reject if `strict` mode is enabled.

### 4.9 Data Lineage

Data lineage allows a network state change to be traced back to its originating intent.
The `trace_id` is the primary lineage key. Every entity MUST carry the same `trace_id`
as the `Intent` that initiated the pipeline run.

```
Lineage Query: "Why is segment-east-01 rerouted?"

1. Find ExecutionRecord where action_type = reroute_traffic AND target matches segment-east-01
2. Retrieve trace_id from ExecutionRecord
3. GET /audit/{intent_id}/why → Returns full pipeline timeline for this trace_id
4. Timeline includes:
   - Intent: who submitted, when, what constraints
   - PolicyResult: which policies applied, any conflicts
   - RiskScore: computed score and factors
   - Decision: rationale for action selection
   - GovernanceResult: mode used, approver if applicable
   - ExecutionRecord: adapter used, parameters applied
```

The `GET /audit/{intent_id}/why` endpoint MUST return a human-readable summary of the
complete decision chain, satisfying P-04 (Explainability).

For production deployments, an additional hash-chained integrity check SHOULD be implemented.
Each `AuditRecord.previous_hash` MUST contain the SHA-256 hash of the immediately preceding
record's serialised payload. This enables detection of any tampering with the audit log.

---

## 5. Conformance Requirements

1. All nine data entities MUST be implemented as Pydantic v2 models with the fields defined in Section 4.2.
2. `AuditRecord` MUST be stored in an append-only structure; no delete or update operations are permitted.
3. `ApprovalTicket` and `FeedbackSuggestion` status fields MAY be mutated; all other fields MUST NOT be modified after creation.
4. All entities MUST include `schema_version`, `trace_id`, and a creation timestamp.
5. Data sovereignty constraints from `Intent.constraints` MUST be propagated unmodified through all pipeline stages.
6. In production deployments, audit records MUST be backed by an append-only store at the storage layer.
7. All entities MUST be serialisable as JSON with no loss of information.
8. Retention periods defined in Section 4.5 MUST be configured in production deployments.

---

## 6. Security Considerations

- All entity fields containing personally identifiable information (PII) or secrets MUST be
  identified and protected per applicable data protection regulations.
- `AuditRecord.payload` snapshots MUST NOT include secrets, credentials, or raw API keys.
- Audit log integrity MUST be protected using hash chaining in production (Section 4.2.8).
- Access to entity data MUST be governed by the RBAC model in ANIF-205.
- `ExecutionRecord.error_detail` MUST NOT include stack traces or internal system paths.

---

## 7. Operational Considerations

- The in-memory prototype store MUST be replaced with a persistent store before any production
  use or load testing that requires data survival across restarts.
- Schema migrations MUST be tested in a staging environment before production deployment.
- A schema registry (ANIF-600) SHOULD be deployed before the first MAJOR version schema change.
- Data lineage queries (`GET /audit/{intent_id}/why`) SHOULD be indexed by `trace_id` in
  production to ensure response times meet the performance target of < 100ms.

---

## Appendix A: Examples

### A.1 Sample Intent JSON

```json
{
  "intent_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "schema_version": "1.0.0",
  "trace_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "action": "reroute_traffic",
  "target": "segment-east-01",
  "constraints": {
    "max_latency_ms": 20,
    "region": "us-east-1",
    "allowed_zones": ["zone-a", "zone-b"]
  },
  "priority": "high",
  "requestor": "automation_agent_7",
  "requestor_role": "automation_agent",
  "submitted_at": "2026-04-07T14:30:00Z",
  "validated_at": "2026-04-07T14:30:00.045Z",
  "status": "validated",
  "dry_run": false,
  "metadata": {}
}
```

### A.2 Sample Audit Record (with hash chain)

```json
{
  "audit_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "intent_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "trace_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "schema_version": "1.0.0",
  "stage": "executed",
  "actor": "action_executor",
  "actor_role": "system",
  "summary": "reroute_traffic executed on segment-east-01 via mock_adapter. Status: success.",
  "payload": {
    "execution_id": "1b9d6bcd-bbfd-4b2d-9b5d-ab8dfbbd4bed",
    "status": "success",
    "adapter_used": "mock_adapter",
    "rollback_available": true
  },
  "previous_hash": "a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3",
  "recorded_at": "2026-04-07T14:30:00.312Z"
}
```

---

## Appendix B: Change History

| Version | Date       | Author             | Summary                  |
|---------|------------|--------------------|--------------------------|
| 0.1.0   | 2026-04-07 | ANIF Working Group | Initial draft            |
