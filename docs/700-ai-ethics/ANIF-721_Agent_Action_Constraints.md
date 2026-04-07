# ANIF-721: Agent Action Constraints

| Field        | Value                                              |
|--------------|----------------------------------------------------|
| Doc ID       | ANIF-721                                           |
| Series       | AI Ethics                                          |
| Version      | 0.1.0                                              |
| Status       | Draft                                              |
| Authors      | ANIF Working Group                                 |
| Reviewers    | —                                                  |
| Approved by  | —                                                  |
| Created      | 2026-04-07                                         |
| Last updated | 2026-04-07                                         |
| Replaces     | N/A                                                |
| Related docs | ANIF-306, ANIF-720, ANIF-725, ANIF-002             |

---

## Abstract

This document specifies four code-level constraints that MUST be enforced in every ANIF-conformant implementation. These constraints cannot be bypassed through configuration, intent submission, policy rules, or agent reasoning. They are enforced at the earliest possible point — compile time where the language supports it, startup validation otherwise. The four constraints are: bounded action enum, rollback required as function parameter, human override hardcoded and non-configurable, and strike counter append-only.

---

## 1. Introduction

### 1.1 Purpose

Policy-based controls can be misconfigured. Intent-based controls can be exploited. The four constraints defined in this document operate below the policy and intent layer — they are properties of the code itself, enforced before any runtime logic runs. An agent cannot reason its way around a compile-time enum. It cannot configure away a hardcoded function signature.

### 1.2 Scope

This document covers:

- The normative specification of all four code-level constraints
- The enforcement mechanism for each constraint
- The consequence when each constraint is violated
- The modification process for hard-coded constraints

### 1.3 Out of Scope

This document does not cover:

- The pipeline position of the action enum check (see ANIF-720)
- The execute() function full signature (see ANIF-725)
- The strike counter data store (see ANIF-716)
- The human override endpoint API contract (see ANIF-404)

### 1.4 Intended Audience

- Platform engineers implementing the ANIF action execution layer
- Language-level architects choosing enforcement mechanisms
- Build-time council members reviewing constraint implementations
- Auditors verifying constraint presence and correctness

---

## 2. Normative References

- ANIF-002 — Principles (P-06 Human Override)
- ANIF-306 — Action Execution Standard
- ANIF-716 — Agent Failure and Progressive Intervention
- ANIF-720 — Safeguard Architecture Overview
- ANIF-725 — Agent Containment and Governance Enforcement
- RFC 2119 — Key words for use in RFCs to indicate requirement levels

---

## 3. Terms and Definitions

**Compile-time enforcement:** A constraint enforced by the compiler or type checker before the code runs. Violations produce build errors, not runtime exceptions.

**Startup validation:** A constraint checked when the application starts, before it begins processing requests. Violations cause startup failure, not runtime errors during processing.

**Hardcoded:** A value or behaviour that is specified directly in source code and cannot be changed through configuration files, environment variables, database settings, or runtime API calls without modifying and redeploying the source code.

**Append-only store:** A data store that supports write and read operations but not update or delete operations on existing records. Once a record is written, it cannot be modified or removed.

---

## 4. Constraint 1 — Bounded Action Enum

### 4.1 Specification

The set of valid action types is defined as a bounded enum. The four valid action types are:

```
reroute_traffic
apply_qos
scale_bandwidth
isolate_segment
```

No action type outside this enum is valid. This constraint applies to every component that produces, receives, or processes an action type value.

### 4.2 Enforcement Mechanism

**Statically typed implementations (Go, Rust, Java, TypeScript with strict mode, C#):** Action type MUST be represented as a compile-time enum or sealed type. Assigning or passing a value not in the enum MUST produce a compiler error. String literals MUST NOT be used where an action type is expected.

**Dynamically typed implementations (Python, JavaScript):** Action type MUST be validated at application startup using an explicit allowlist. Any request containing an action type not in the allowlist MUST be rejected with a 400 error before it reaches any processing logic. The validation MUST run at the application boundary — not deep in the processing stack.

### 4.3 Scope of Enforcement

The enum constraint applies at every point where an action type value is used:

- Intent parsing and validation
- Policy evaluation input
- Risk scoring input
- Decision engine output
- Action executor input
- Audit record writing

An action type that is valid at intent parsing but not re-validated at execution creates a bypass opportunity. Validation MUST occur at every boundary.

### 4.4 Violation Consequence

A request containing an invalid action type MUST be rejected immediately with a structured error response. The rejection MUST be logged. The agent that submitted the invalid action type MUST have the event recorded as a near-miss (ANIF-716).

---

## 5. Constraint 2 — Rollback Required as Parameter

### 5.1 Specification

The `execute()` function MUST require a `rollback_plan` parameter. This parameter MUST be validated as present and non-null before execution begins. Calls without a confirmed rollback plan MUST be rejected at the function signature level.

### 5.2 Enforcement Mechanism

**Statically typed implementations:** `rollback_plan` MUST be a non-optional, non-nullable parameter in the `execute()` function signature. Code that calls `execute()` without providing `rollback_plan` MUST produce a compiler error.

**Dynamically typed implementations:** `execute()` MUST validate the presence and structure of `rollback_plan` as the first operation in the function body, before any other logic. Validation failure MUST raise an exception that prevents further execution.

### 5.3 Rollback Plan Structure

A valid rollback plan MUST contain at minimum:

| Field | Type | Requirement |
|---|---|---|
| `rollback_action_type` | enum | One of the four valid action types |
| `rollback_target` | string | The network segment or service to roll back |
| `rollback_within_seconds` | integer | Maximum seconds to complete rollback |
| `rollback_confirmed_at` | ISO 8601 | Timestamp of rollback confirmation |

A rollback plan that references a `rollback_within_seconds` value exceeding the rollback SLA for the environment MUST NOT be accepted.

### 5.4 Violation Consequence

An `execute()` call without a valid rollback plan MUST be rejected with a structured error. The caller agent MUST have the rejection logged as a near-miss event (ANIF-716).

---

## 6. Constraint 3 — Human Override Hardcoded and Non-Configurable

### 6.1 Specification

The human override endpoint is hardcoded in the application and cannot be disabled, redirected, or rate-limited through configuration, intent submission, policy rules, or agent reasoning.

### 6.2 What "Hardcoded" Means

The following behaviours MUST be hardcoded — not configurable:

- The override endpoint path: `/override` (or the equivalent in the implementation's routing scheme)
- The override endpoint's availability: it MUST be available at all times the application is running
- The override action: a valid override request MUST halt the targeted action immediately
- The override effect: override MUST take effect within 5 seconds of a valid request

The following MUST NOT be configurable:

- Disabling the override endpoint
- Redirecting the override endpoint to a different handler
- Rate-limiting override requests (standard DoS protection MAY apply, but MUST NOT affect legitimate operator requests)
- Requiring additional authentication beyond the caller's standard operator credentials
- Introducing a delay between override request and override effect

### 6.3 Override Endpoint Availability

The override endpoint MUST remain available even when:

- The main pipeline is under high load
- An agent has been suspended or decommissioned
- The system is in disaster recovery operation (ANIF-819)
- The governance gate is routing all decisions to `manual_review`

The override endpoint is the last resort for human intervention. It MUST be prioritised above all other system functions in resource contention.

### 6.4 Modification Process

Modifying the override endpoint implementation requires a code change. That code change MUST be reviewed by the build-time council (ANIF-903) before deployment. No deployment pipeline MAY bypass this review for override endpoint changes.

### 6.5 Violation Consequence

Any condition in which the override endpoint is unavailable, rate-limited beyond normal DoS thresholds, or delayed beyond 5 seconds MUST be classified as a Severity 1 ethics incident (ANIF-715).

---

## 7. Constraint 4 — Strike Counter Append-Only

### 7.1 Specification

The strike counter data store MUST be append-only. The data store used for strike records MUST NOT support update or delete operations on existing records.

### 7.2 Enforcement Mechanism

The append-only property MUST be enforced at the data store level — not at the application level. An application-level check that simply refuses to call update or delete is not sufficient, because it can be bypassed by direct database access. The data store itself MUST enforce the constraint.

Acceptable implementations:

- Immutable audit log services that enforce write-once at the API level
- Write-once object storage (e.g., S3 Object Lock, Azure Immutable Blob Storage)
- Append-only database tables with row-level security preventing updates/deletes by any principal
- Distributed ledger or blockchain-based storage

Unacceptable implementations:

- A relational table without row-level security, relying on application code not to call UPDATE/DELETE
- A file system with application-enforced read-only flag (can be changed by OS-level access)
- Any store where a database administrator or platform engineer can modify records without audit

### 7.3 Violation Consequence

Any attempt to modify or delete a strike record MUST be detected and MUST trigger a Severity 1 ethics incident (ANIF-715). The detection mechanism MUST be independent of the application code — it MUST operate at the data store or infrastructure monitoring layer.

---

## 8. Conformance Requirements

An implementation MUST enforce all four constraints.

Constraint 1 (bounded action enum) MUST be enforced at compile time in statically typed implementations. Dynamic implementations MUST enforce at application startup.

Constraint 2 (rollback required) MUST be enforced before any execution logic runs in the `execute()` function.

Constraint 3 (human override) MUST be hardcoded. Any configuration option that can disable or delay the override endpoint is a conformance violation.

Constraint 4 (append-only) MUST be enforced at the data store level, not solely at the application level.

---

## 9. Security Considerations

These four constraints reduce the attack surface for adversarial manipulation of the autonomous system. An agent that has been manipulated via prompt injection cannot generate a free-form action type because the enum prevents it. A compromised deployer cannot disable the human override through a configuration change. A malicious insider cannot erase strike history through direct database access if the store is genuinely append-only.

---

## 10. Operational Considerations

Constraint implementations SHOULD be verified by the build-time council during initial deployment and annually thereafter. Verification confirms that: (a) the enum is the exhaustive source of action types, (b) the execute() function cannot be called without rollback, (c) the override endpoint responds within 5 seconds under load, and (d) strike record modification is rejected at the data store level.

---

## Appendix A: Change History

| Version | Date | Author | Changes |
|---|---|---|---|
| 0.1.0 | 2026-04-07 | ANIF Working Group | Initial draft |
