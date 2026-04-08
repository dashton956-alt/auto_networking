# ANIF-811: Intent Lifecycle Management

| Field        | Value                                              |
|--------------|----------------------------------------------------|
| Doc ID       | ANIF-811                                           |
| Series       | AI Agent Architecture                              |
| Version      | 0.1.0                                              |
| Status       | Draft                                              |
| Authors      | ANIF Working Group                                 |
| Reviewers    | —                                                  |
| Approved by  | —                                                  |
| Created      | 2026-04-08                                         |
| Last updated | 2026-04-08                                         |
| Replaces     | N/A                                                |
| Related docs | ANIF-300, ANIF-301, ANIF-809, ANIF-813             |

---

## Abstract

This document defines the normative state machine governing every intent from creation through to terminal state within an ANIF-conformant implementation. An intent transitions through eight defined states: DRAFT, SUBMITTED, QUEUED, IN_PIPELINE, PENDING_APPROVAL, EXECUTING, COMPLETED, and FAILED or CANCELLED. Each transition has defined triggers, permitted actors, and mandatory audit events. Concurrent intents targeting the same network segment MUST default to queue serialisation with human notification. Intents that exceed their declared expiry time MUST be cancelled automatically and escalated for review.

---

## 1. Introduction

### 1.1 Purpose

The intent lifecycle model provides the normative contract that all components — coordinators, pipeline stages, governance systems, and human operators — rely on to understand the current state of any intent and the valid transitions available. Consistent lifecycle management prevents intents from becoming stranded, executing in unexpected states, or consuming resources beyond their declared scope.

### 1.2 Scope

This document covers:

- The complete intent state machine with all states and transitions
- Transition triggers and permitted actors for each transition
- Concurrent intent conflict detection and resolution
- Intent expiry handling
- Required audit events at each lifecycle transition

### 1.3 Out of Scope

This document does not cover:

- Intent authoring format and schema (see ANIF-301)
- Policy evaluation logic (see ANIF-302)
- Risk scoring algorithm (see ANIF-304)
- Tier 0 coordination actions on queued intents (see ANIF-809)

### 1.4 Intended Audience

- AI engineers implementing intent processing pipeline components
- Platform architects designing intent coordination systems
- Governance officers monitoring intent completion rates
- Conformance assessors evaluating pipeline state management

---

## 2. Normative References

| Reference | Title |
|---|---|
| ANIF-300 | Intent Framework Overview |
| ANIF-301 | Intent Authoring Standard |
| ANIF-302 | Policy Engine Specification |
| ANIF-304 | Risk and Trust Quantification |
| ANIF-404 | Human-in-Loop Controls |
| ANIF-809 | Agent Coordination Model |
| ANIF-813 | Intent Integration Architecture |
| RFC 2119 | Key words for use in RFCs to Indicate Requirement Levels |

---

## 3. Terms and Definitions

| Term | Definition |
|---|---|
| Intent | A declarative statement of desired network outcome, authored to the ANIF-301 standard |
| Intent lifecycle | The complete set of states and transitions an intent passes through from creation to terminal state |
| Terminal state | A state from which no further transitions are possible: COMPLETED, FAILED, or CANCELLED |
| Concurrent conflict | A condition where two or more active intents target the same network segment or resource simultaneously |
| Queue serialisation | The process of ordering conflicting concurrent intents for sequential execution |
| Intent expiry | The automatic cancellation of an intent that has not reached a terminal state within its declared TTL |

---

## 4. Intent State Machine

### 4.1 State Definitions

| State | Description |
|---|---|
| DRAFT | Intent has been created but not yet submitted for processing |
| SUBMITTED | Intent has been submitted and is undergoing initial validation |
| QUEUED | Intent has passed validation and is waiting for pipeline capacity |
| IN_PIPELINE | Intent is actively being processed by pipeline stages |
| PENDING_APPROVAL | Intent has completed pipeline processing and is awaiting human approval |
| EXECUTING | Intent has been approved and is being executed by Tier 3 agents |
| COMPLETED | Intent execution has finished successfully |
| FAILED | Intent execution has failed after exhausting retry attempts |
| CANCELLED | Intent has been cancelled by a human operator or by the system |

### 4.2 State Transition Table

| From State | To State | Trigger | Permitted Actor |
|---|---|---|---|
| — | DRAFT | Intent created by operator or external system | Operator, Integration Adapter |
| DRAFT | SUBMITTED | Operator submits intent | Operator |
| DRAFT | CANCELLED | Operator discards draft | Operator |
| SUBMITTED | QUEUED | Validation passes (schema, policy pre-check) | Intent Validation Agent |
| SUBMITTED | FAILED | Validation fails | Intent Validation Agent |
| QUEUED | IN_PIPELINE | Pipeline capacity available, intent dequeued | Tier 0 Coordinator |
| QUEUED | CANCELLED | Operator cancels, or intent TTL expires | Operator, Expiry Manager |
| IN_PIPELINE | PENDING_APPROVAL | Pipeline processing complete, risk score ≥ 50 | Decision Engine |
| IN_PIPELINE | EXECUTING | Pipeline processing complete, risk score < 50, auto-approval | Decision Engine |
| IN_PIPELINE | FAILED | Pipeline processing fails unrecoverably | Pipeline Stage Agent |
| IN_PIPELINE | CANCELLED | Operator cancels during processing | Operator |
| PENDING_APPROVAL | EXECUTING | Human approves | Authorised Approver |
| PENDING_APPROVAL | CANCELLED | Human rejects or TTL expires | Authorised Approver, Expiry Manager |
| EXECUTING | COMPLETED | All execution steps succeed | Execution Agent |
| EXECUTING | FAILED | Execution fails and rollback completes | Execution Agent |
| EXECUTING | CANCELLED | Operator halts execution (triggers rollback) | Operator |

No transition that is not listed in the table above is permitted. Agents or systems that attempt unlisted transitions MUST be rejected and the attempt MUST be logged as a governance event.

### 4.3 Terminal State Immutability

Once an intent reaches COMPLETED, FAILED, or CANCELLED, its state MUST NOT be modified. Terminal state records are immutable in the audit trail (ANIF-724).

---

## 5. Concurrent Intent Conflict Detection

### 5.1 Conflict Definition

A concurrent conflict exists when two or more intents that are in states QUEUED, IN_PIPELINE, PENDING_APPROVAL, or EXECUTING declare overlapping scope — targeting the same network segment, device, policy, or resource.

### 5.2 Conflict Detection Timing

Concurrent conflict detection MUST run at two points:

1. When an intent transitions from SUBMITTED to QUEUED (pre-queue check)
2. When an intent transitions from QUEUED to IN_PIPELINE (pre-execution check)

### 5.3 Default Resolution: Queue Serialisation

When a concurrent conflict is detected, the default resolution is queue serialisation:

1. The later-arriving intent MUST be held in QUEUED state.
2. A human operator MUST be notified of the conflict within 60 seconds, with: `intent_id` of both intents, the overlapping scope, and the expected resolution time.
3. The held intent proceeds to IN_PIPELINE only after the earlier intent reaches a terminal state.
4. The notification MUST be acknowledged by an operator. Unacknowledged conflict notifications MUST be re-sent every 10 minutes until acknowledged.

### 5.4 Operator Override of Serialisation

An operator MAY override queue serialisation and allow concurrent execution when the overlapping scope is non-interfering (e.g., two intents targeting different interfaces on the same device). The override MUST be logged with the operator's justification. Concurrent execution following an operator override MUST be recorded in both intent audit records.

---

## 6. Intent Expiry

### 6.1 TTL Declaration

Every intent MUST declare a `ttl_seconds` field specifying the maximum time from SUBMITTED state to terminal state. If `ttl_seconds` is not declared, a system-wide default of 3600 seconds (1 hour) applies.

### 6.2 Expiry Handling

The Expiry Manager component MUST monitor all non-terminal intents against their TTL. When an intent's TTL is exceeded:

1. The intent MUST be transitioned to CANCELLED.
2. If the intent is in EXECUTING state at expiry, a rollback MUST be triggered before cancellation is recorded.
3. A TTL expiry event MUST be logged with: `intent_id`, `state_at_expiry`, `ttl_seconds`, `elapsed_seconds`, `timestamp`.
4. The submitting operator MUST be notified of the expiry.

### 6.3 TTL Extension

An operator MAY extend an intent's TTL while the intent is in QUEUED or PENDING_APPROVAL state. TTL extension MUST be logged. TTL extension of an intent in IN_PIPELINE or EXECUTING state is not permitted — the intent must complete or fail within its original TTL.

---

## 7. Required Audit Events

Every state transition MUST produce an audit event in the audit trail (ANIF-724) containing:

| Field | Type | Description |
|---|---|---|
| `lifecycle_event_id` | UUID v4 | Unique identifier for the lifecycle event |
| `intent_id` | UUID v4 | The intent undergoing the transition |
| `from_state` | enum | The state before the transition |
| `to_state` | enum | The state after the transition |
| `actor_id` | string | The agent or operator that triggered the transition |
| `trigger_reason` | string | The reason for the transition |
| `timestamp` | ISO 8601 | Time the transition occurred |

---

## 8. Conformance Requirements

| ID | Requirement |
|---|---|
| CR-811-01 | Every intent MUST pass through the state machine defined in section 4. No transitions other than those listed in the table are permitted. |
| CR-811-02 | Terminal states MUST be immutable. Intent records in COMPLETED, FAILED, or CANCELLED state MUST NOT be modified. |
| CR-811-03 | Concurrent conflict detection MUST run at both the pre-queue and pre-execution stages. |
| CR-811-04 | Concurrent conflicts MUST default to queue serialisation. Human notification MUST occur within 60 seconds. |
| CR-811-05 | Operator overrides of queue serialisation MUST be logged with justification. |
| CR-811-06 | Every intent MUST declare a `ttl_seconds` value or inherit the system default. |
| CR-811-07 | Intents in EXECUTING state at TTL expiry MUST have rollback triggered before cancellation is recorded. |
| CR-811-08 | Every state transition MUST produce an audit event with all fields defined in section 7. |

---

## 9. Security Considerations

The intent lifecycle is a primary target for manipulation. An attacker who can advance an intent to EXECUTING state without passing through PENDING_APPROVAL bypasses the human approval gate. All state transition authorisation checks MUST be enforced by a component that is independent of the intent's originating agent — an agent MUST NOT be permitted to advance its own intent through approval stages.

---

## 10. Operational Considerations

High FAILED rates indicate policy misconfiguration, network instability, or agent logic errors. Operators SHOULD monitor the FAILED-to-COMPLETED ratio and alert when the FAILED rate exceeds 10% within any 24-hour window. High CANCELLED rates at PENDING_APPROVAL indicate approval bottlenecks — if approval SLAs defined in ANIF-404 are being breached, the approval workflow SHOULD be reviewed before TTL values are adjusted.
