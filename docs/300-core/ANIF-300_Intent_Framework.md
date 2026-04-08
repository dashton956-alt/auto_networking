# ANIF-300: Intent Framework Overview

| Field        | Value                              |
|--------------|------------------------------------|
| Doc ID       | ANIF-300                           |
| Series       | Core                               |
| Version      | 0.1.0                              |
| Status       | Draft                              |
| Authors      | ANIF Working Group                 |
| Reviewers    | —                                  |
| Approved by  | —                                  |
| Created      | 2026-04-07                         |
| Last updated | 2026-04-07                         |
| Replaces     | N/A                                |
| Related docs | ANIF-301, ANIF-302, ANIF-304, ANIF-305 |

---

## Abstract

This document provides the entry-point overview for the ANIF Core series. It defines what a network intent is, describes the intent lifecycle from authoring through audit, establishes the identity model for intents, and explains how intents relate to policy evaluation, risk quantification, and autonomous decision-making. Implementers MUST read this document before consulting any other document in the 300-series.

---

## 1. Introduction

### 1.1 Purpose

The Autonomous Networking and Infrastructure Framework (ANIF) replaces imperative, operator-driven change procedures with a declarative intent model. This document defines the foundational concept of an **intent** and establishes the structural relationships between the components that process it: the policy engine, risk quantifier, decision engine, and action executor. It provides the conceptual grounding required to interpret all normative specifications in the ANIF-300 series.

### 1.2 Scope

This document covers:

- The definition and properties of a network intent.
- The full intent lifecycle from creation to audit.
- The intent identity model and immutability guarantee.
- The relationship chain: intent → policy evaluation → risk scoring → decision → governance → execution → audit.
- A non-normative schema overview (normative authoring standard is in ANIF-301).
- A comparison between intent-based automation and traditional change management.

### 1.3 Out of Scope

This document does not cover:

- Normative field-level validation rules (see ANIF-301).
- Policy engine internals (see ANIF-302, ANIF-303).
- Risk scoring algorithms (see ANIF-304).
- Decision engine logic (see ANIF-305).
- Execution mechanics (see ANIF-306).
- Observability and audit record formats (see ANIF-400 series).

### 1.4 Intended Audience

- Network architects and engineers adopting ANIF.
- Platform teams integrating the ANIF pipeline into existing orchestration systems.
- Policy authors and governance stakeholders.
- Auditors and compliance reviewers requiring a high-level process overview.

---

## 2. Normative References

- ANIF-001: Framework Charter
- ANIF-301: Intent Authoring Standard
- ANIF-302: Policy Engine Specification
- ANIF-304: Risk and Trust Quantification
- ANIF-305: Decision Engine Specification
- ANIF-306: Action Execution Standard
- RFC 2119: Key words for use in RFCs to indicate requirement levels

---

## 3. Terms and Definitions

**Intent**
A declarative, machine-readable statement that specifies what a network or infrastructure service SHOULD achieve in terms of its observable outcomes, without prescribing the implementation path.

**Intent ID**
A universally unique identifier (UUID v4) assigned to an intent at the moment of successful validation. The intent_id is immutable and persists throughout the lifecycle.

**Intent Lifecycle**
The ordered sequence of processing stages an intent passes through, from initial authoring to final audit record creation.

**Policy Evaluation**
The deterministic process of testing an intent against the active policy set to produce a pass, fail, or warn result for each applicable policy rule.

**Risk Score**
An integer in the range 0–100 that quantifies the operational risk of executing an intent based on its characteristics, policy results, and observed network state.

**Trust Score**
An integer in the range 0–100 that quantifies the system's confidence that the intent is safe to execute autonomously.

**Safety Decision**
The output of the risk/trust engine: one of `allow`, `warn`, or `block`.

**Recommended Action**
The bounded action selected by the decision engine in response to the intent. One of: `reroute_traffic`, `apply_qos`, `scale_bandwidth`, `isolate_segment`, or null (when action is blocked).

**Governance Mode**
The operational mode that determines whether an action may proceed autonomously (`auto`), requires human approval (`manual_review`), or is prohibited (`block`).

**Canonical State**
The authoritative, merged view of the current network state, as defined in ANIF-307.

---

## 4. The Intent Model

### 4.1 What an Intent Is

An intent is a **declarative statement** of what a network or infrastructure service MUST achieve in terms of its observable outcomes. Intents express goals, not instructions. An intent states that a payments service MUST maintain 99.99% availability and MUST NOT exceed 50 ms latency. It does not state which routing path to use, which node to scale, or which QoS policy to apply — those decisions belong to the decision engine.

This separation between desired outcomes and implementation means:

- Intents remain stable across infrastructure changes.
- The system can choose optimal actions without operator micro-management.
- Intent authoring requires domain knowledge of service requirements, not platform internals.

An intent MUST contain three required components: a **service identifier**, one or more **objectives** (measurable outcome targets), and one or more **constraints** (boundaries within which the outcome must be achieved).

### 4.2 How Intents Differ from Traditional Change Requests

Traditional change management is **imperative**: an operator specifies exactly what to do ("apply ACL 42 to interface eth0/1 on router R3"). This approach has well-understood failure modes:

- Instructions become stale when the network changes.
- Errors in instructions cause direct configuration damage.
- Automation is fragile because it depends on stable implementation details.
- Compliance validation must happen outside the change process.

ANIF intents are **declarative**: an operator specifies what must be true ("the payments service must have < 50 ms latency and encryption enabled"). This yields:

| Property              | Traditional Change Request  | ANIF Intent              |
|-----------------------|-----------------------------|--------------------------|
| Specification style   | Imperative (how)            | Declarative (what)       |
| Stability             | Tied to topology            | Topology-independent     |
| Validation point      | After execution             | Before execution         |
| Policy check          | Manual, often post-hoc      | Automated, pre-execution |
| Audit linkage         | Separate ticket system      | Embedded in lifecycle    |
| Rollback definition   | Ad hoc                      | Required at decision time|
| Autonomous execution  | Not possible                | Explicitly supported     |

### 4.3 Intent Schema Overview

An intent document consists of the following top-level fields. Full normative authoring rules are defined in ANIF-301.

| Field        | Type    | Required | Description                                                   |
|--------------|---------|----------|---------------------------------------------------------------|
| service      | string  | Yes      | Identifier of the service this intent governs.               |
| objectives   | object  | Yes      | Measurable outcome targets (latency, availability, throughput).|
| constraints  | object  | Yes      | Boundaries within which outcomes must be achieved.            |
| environment  | enum    | No       | Deployment environment: `prod`, `staging`, or `dev`.          |
| policies     | array   | No       | Named policy tags to apply in addition to defaults.           |
| priority     | enum    | No       | Urgency classification: `low`, `medium`, `high`, `critical`.  |

A minimal valid intent MUST specify `service`, `objectives`, and `constraints`. All other fields are optional but carry default behaviours when omitted (see ANIF-301 Section 4).

### 4.4 Intent Identity

Every intent MUST be assigned a stable, globally unique identifier at validation time.

- The `intent_id` MUST be a UUID v4 string.
- The `intent_id` MUST be assigned by the framework on successful completion of the `/validate-intent` endpoint call.
- The `intent_id` MUST NOT be supplied by the intent author; author-supplied IDs MUST be rejected.
- Once assigned, the `intent_id` MUST NOT be changed at any subsequent lifecycle stage.

#### 4.4.1 Intent Immutability

An intent is **immutable once validated**. This means:

- The `service`, `objectives`, `constraints`, `policies`, `priority`, and `environment` fields of a validated intent MUST NOT be modified by any pipeline component.
- If an operator requires a different intent, they MUST submit a new intent document via `/validate-intent`, which receives a new `intent_id`.
- Re-submission with updated fields is the standard mechanism for intent updates (see ANIF-301 Section 6).

This immutability guarantee ensures that audit records, risk scores, and decision rationales always correspond to exactly the intent that was submitted.

---

## 5. The Intent Lifecycle

An intent passes through eight ordered stages. Each stage produces a durable state record that is referenced by subsequent stages. The lifecycle MUST be traversed in the order defined in this section; no stage MAY be skipped except where explicitly permitted.

```
authored → validated → policy-checked → risk-scored → decided → governed → executed → audited
```

### 5.1 Stage 1: Authored

An operator or automated system composes an intent document conforming to the schema defined in ANIF-301. At this stage, the intent has no system-assigned identity; it exists only as a candidate document.

**Entry:** Intent document created by author.
**Exit:** Intent submitted to `/validate-intent`.

### 5.2 Stage 2: Validated

The framework receives the intent via `POST /validate-intent`. It performs syntactic and semantic validation:

- Schema conformance is checked against the normative intent schema (ANIF-301).
- Custom validation rules are applied (e.g., production environment requires `high` or `critical` priority).
- On success: `intent_id` (UUID) is assigned; intent is stored as immutable record.
- On failure: validation errors are returned; no `intent_id` is assigned.

**Entry:** Intent submitted to `/validate-intent`.
**Exit:** Validated intent record with assigned `intent_id`; available via `GET /intent/{intent_id}`.

### 5.3 Stage 3: Policy-Checked

The validated intent is submitted to `POST /evaluate-policy`. The policy engine (ANIF-302) evaluates the intent against the active policy set, including built-in policies (zero_trust, no_public_ingress, pci_compliant, data_residency) and any operator-declared policy tags. Conflict resolution (ANIF-303) runs within this stage.

**Entry:** Validated intent with `intent_id`.
**Exit:** Policy evaluation result with `overall_result` (pass/fail/warn), individual `policy_results`, resolved policy set, and any detected conflicts.

### 5.4 Stage 4: Risk-Scored

The intent and its policy evaluation result are submitted to `POST /score-risk`. The risk/trust engine (ANIF-304) computes a numeric risk score and trust score, applies environment-specific thresholds, and produces a `safety_decision` (allow/warn/block).

**Entry:** Intent + policy evaluation result.
**Exit:** Risk record with `risk_score`, `trust_score`, `safety_decision`, `justification` list, and `threshold_applied`.

### 5.5 Stage 5: Decided

The intent, policy result, and risk record are submitted to `POST /decide`. The decision engine (ANIF-305) applies its deterministic rule tree to select a bounded recommended action and determine the governance mode.

**Entry:** Intent + policy result + risk record.
**Exit:** Decision record with `recommended_action`, `confidence_score`, `risk_level`, `mode`, `reasoning_chain`, and `rollback_plan`.

### 5.6 Stage 6: Governed

`POST /governance/check` evaluates the decision record against the governance mode gate. If `mode = auto`, execution may proceed immediately. If `mode = manual_review`, an approval ticket is created and execution is gated pending human approval via `POST /governance/approve/{ticket_id}` or `POST /governance/reject/{ticket_id}`. If `mode = block`, the pipeline terminates; no execution occurs.

**Entry:** Decision record.
**Exit:** Governance result with approved ticket (if required) or terminal block record.

### 5.7 Stage 7: Executed

`POST /execute` triggers the action executor (ANIF-306) with the approved decision. The executor delegates to the appropriate adapter, captures the outcome, and records rollback availability. On failure, rollback is attempted automatically.

**Entry:** Approved decision record + governance clearance.
**Exit:** Execution record with `execution_id`, `status`, `adapter_response`, `duration_ms`, and `rollback_available`.

### 5.8 Stage 8: Audited

All lifecycle events — validation, policy evaluation, risk scoring, decision, governance actions, and execution — MUST be written to the audit log and retrievable via `GET /audit/{intent_id}`. The audit record constitutes the durable, tamper-evident record of the full lifecycle.

**Entry:** Completion of any lifecycle stage event.
**Exit:** Persistent audit record. Accessible via `GET /audit/{intent_id}`, `GET /audit/{intent_id}/why`, `GET /audit`.

### 5.9 Abbreviated Pipeline: /orchestrate

For testing and simplified integration, `POST /orchestrate` executes the full pipeline (stages 2–8) in a single synchronous call. Orchestrate mode MUST enforce the same stage ordering and MUST NOT skip governance checks.

---

## 6. Component Relationships

The intent drives a strict linear dependency chain. No component receives inputs from a later stage.

```
Intent
  │
  ▼
Policy Engine (ANIF-302)
  │ policy_result
  ▼
Conflict Resolution (ANIF-303)
  │ resolved_policy_set
  ▼
Risk / Trust Engine (ANIF-304)
  │ risk_score, trust_score, safety_decision
  ▼
Decision Engine (ANIF-305)
  │ recommended_action, mode, reasoning_chain
  ▼
Governance Gate (ANIF-306)
  │ approval / block
  ▼
Action Executor (ANIF-306)
  │ execution_id, status
  ▼
Audit Log (ANIF-404)
```

The canonical network state (ANIF-307) is a read-only input to the risk engine and decision engine. The digital twin (ANIF-308) is a read-only simulation input consulted before execution.

---

## 5. Conformance Requirements

1. Implementations MUST assign a UUID v4 `intent_id` on successful validation and MUST NOT accept author-supplied IDs.
2. Implementations MUST treat a validated intent as immutable; modifications to validated intent fields are PROHIBITED.
3. Implementations MUST traverse the lifecycle stages in the order defined in Section 5.
4. Implementations MUST NOT execute an action unless the governance stage has produced a clearance record.
5. Implementations MUST write audit records at every lifecycle stage.
6. Implementations MUST expose the pipeline endpoints defined in Section 5 with the specified HTTP methods and path patterns.

---

## 6. Security Considerations

- Intent documents MAY contain service names and environment identifiers that are operationally sensitive. Access to `/validate-intent` and all read endpoints MUST be protected by authentication and authorisation controls.
- The `intent_id` is a UUID and provides no information about the intent content; it MUST be treated as an opaque identifier in logs and external references.
- Governance approval endpoints (`/governance/approve/{ticket_id}`, `/governance/reject/{ticket_id}`) MUST require elevated privileges beyond those required to submit an intent.
- The audit log MUST be append-only and MUST NOT be writable by the components that generate lifecycle events.

---

## 7. Operational Considerations

- The `/orchestrate` endpoint is intended for development and testing. Production deployments SHOULD use stage-by-stage API calls to allow intermediate inspection and intervention.
- Intent re-submission (updating an intent) causes a new `intent_id` to be issued. Operators MUST track the relationship between successive intents for a given service through their own tooling; ANIF does not maintain an intent update lineage in this version.
- High-frequency automated intent submission (e.g., from an autonomous controller) SHOULD include rate limiting and back-pressure mechanisms at the submission layer to prevent audit log flooding.

---

## Appendix A: Examples

### A.1 Minimal Valid Intent (JSON)

```json
{
  "service": "payments-gateway",
  "objectives": {
    "availability_percent": 99.9
  },
  "constraints": {
    "region": "EU"
  }
}
```

### A.2 Full Production Intent (JSON)

```json
{
  "service": "payments-gateway",
  "environment": "prod",
  "objectives": {
    "latency_ms": 45,
    "availability_percent": 99.99,
    "throughput_mbps": 500
  },
  "constraints": {
    "region": "EU",
    "encryption": true,
    "allowed_zones": ["eu-west-1a", "eu-west-1b"]
  },
  "policies": ["zero_trust", "pci_compliant", "data_residency"],
  "priority": "critical"
}
```

### A.3 Lifecycle Status Response

```json
{
  "intent_id": "f3a9b2c1-4d7e-4f88-9012-abcdef012345",
  "service": "payments-gateway",
  "status": "decided",
  "stages_completed": ["validated", "policy_checked", "risk_scored", "decided"],
  "current_stage": "governance",
  "created_at": "2026-04-07T10:00:00Z",
  "last_updated": "2026-04-07T10:00:04Z"
}
```

---

## Appendix B: Change History

| Version | Date       | Author             | Description          |
|---------|------------|--------------------|----------------------|
| 0.1.0   | 2026-04-07 | ANIF Working Group | Initial draft        |
