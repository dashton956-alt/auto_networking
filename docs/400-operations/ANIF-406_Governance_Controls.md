# ANIF-406: Governance Controls

| Field        | Value                                        |
|--------------|----------------------------------------------|
| Doc ID       | ANIF-406                                     |
| Series       | Operations                                   |
| Version      | 0.1.0                                        |
| Status       | Draft                                        |
| Authors      | ANIF Working Group                           |
| Reviewers    | —                                            |
| Approved by  | —                                            |
| Created      | 2026-04-07                                   |
| Last updated | 2026-04-07                                   |
| Replaces     | N/A                                          |
| Related docs | ANIF-404, ANIF-103, ANIF-107                 |

---

## Abstract

This document defines the governance control requirements for ANIF-conformant deployments. Governance controls are the runtime operational enforcement of the governance policies defined in ANIF-103 and ANIF-104. This document specifies the governance mode gate implementation (`POST /governance/check`), all normative governance rules and their evaluation order, the governance audit trail requirements, the approval ticket lifecycle, governance operational metrics, and the conditions under which policy overrides are permitted and by whom.

---

## 1. Introduction

### 1.1 Purpose

This document establishes normative requirements for the runtime governance controls within ANIF systems. While ANIF-103 defines governance policy and ANIF-404 defines the human workflow that follows a governance decision, this document focuses on the governance engine itself: the rules it evaluates, the decisions it produces, and the audit obligations it must satisfy before returning any response.

### 1.2 Scope

This document covers:

- The governance mode gate: `POST /governance/check` endpoint specification.
- All normative governance mode rules (R-01 through R-06).
- Rule evaluation order and precedence.
- The governance audit trail: when and what MUST be logged.
- The approval ticket lifecycle: created, pending, approved, rejected, expired.
- Governance operational metrics and their definitions.
- Policy override controls: who can override, under what conditions, and with what audit obligations.

### 1.3 Out of Scope

- Human approval workflow (covered in ANIF-404).
- Policy authoring and the policy hierarchy (covered in ANIF-103).
- Risk scoring algorithm (covered in ANIF-305 or risk engine specification).
- Long-term audit retention (covered in ANIF-107).

### 1.4 Intended Audience

| Audience                     | Usage                                                             |
|------------------------------|-------------------------------------------------------------------|
| Platform Engineers           | Implementing the governance engine and mode gate                  |
| Network Operations Engineers | Understanding governance decisions and their basis                |
| Governance and Compliance    | Auditing governance decisions and override usage                  |
| Architecture Teams           | Integrating the governance gate into the pipeline                 |

---

## 2. Normative References

- ANIF-103: Governance Policy Framework
- ANIF-104: Policy Evaluation Engine
- ANIF-107: Audit and Immutable Logging Standard
- ANIF-305: Intent Execution Pipeline
- ANIF-400: Operations Overview
- ANIF-404: Human-in-Loop Controls
- RFC 2119: Key words for use in RFCs to Indicate Requirement Levels

---

## 3. Terms and Definitions

| Term                   | Definition                                                                                                        |
|------------------------|-------------------------------------------------------------------------------------------------------------------|
| Governance Gate        | The mandatory check that every intent execution MUST pass before any network action is taken.                    |
| Mode                   | The governance engine output: one of `auto`, `manual_review`, or `block`.                                        |
| Governance Rule        | A normative condition that, when true, determines or constrains the mode output.                                  |
| Policy Override        | An authorised exception to a governance rule, applied by a senior stakeholder under defined conditions.          |
| RBAC                   | Role-Based Access Control — the assignment of permissions to roles rather than individuals.                       |
| Immutable Audit Record | A log record that, once written, MUST NOT be modified, deleted, or overwritten.                                   |
| Ticket Lifecycle       | The sequence of states an approval ticket passes through: created → pending → (approved/rejected/expired).       |

---

## 4. Governance Control Requirements

### 4.1 Governance Mode Gate

The governance mode gate is the central enforcement point for all governance decisions. Every intent execution MUST call the mode gate before proceeding to execution.

#### 4.1.1 Mode Gate Endpoint

`POST /governance/check`

Evaluates the governance rules for the provided context and returns a mode decision.

**Request Schema:**

```json
{
  "intent_id":     "<UUID v4>",
  "operator_id":   "<string — authenticated identity of the submitter>",
  "operator_roles": ["<string>", "..."],
  "action_type":   "<string — the proposed network action type>",
  "environment":   "<string — prod, staging, dev>",
  "risk_score":    "<integer 0-100>",
  "trust_score":   "<integer 0-100>",
  "policy_results": [
    {
      "policy_id":       "<string>",
      "outcome":         "<string — pass/fail>",
      "safety_decision": "<string or null — block/warn/null>"
    }
  ],
  "trace_id":      "<UUID v4>"
}
```

**Response Schema:**

```json
{
  "intent_id":         "<UUID v4>",
  "mode":              "<string — auto|manual_review|block>",
  "triggered_rule":    "<string — the rule ID(s) that determined the mode>",
  "rationale":         "<string — plain-English explanation of the mode decision>",
  "ticket_id":         "<string or null — present only if mode=manual_review>",
  "ticket_expires_at": "<ISO 8601 datetime or null>",
  "audit_record_id":   "<string — the ID of the audit record written for this decision>",
  "trace_id":          "<UUID v4>"
}
```

**Requirements:**

1. The governance engine MUST evaluate all rules before returning a response.
2. An audit record MUST be written before the response is returned; if the audit write fails, the endpoint MUST return HTTP 503 and MUST NOT proceed with execution.
3. The response MUST include `audit_record_id` referencing the written record.
4. The `trace_id` from the request MUST be echoed in the response.

### 4.2 Governance Rules

The following rules MUST be implemented by the governance engine. Rules are evaluated in the order listed. `block` rules are evaluated first; `manual_review` rules are evaluated second.

#### 4.2.1 Block Rules (evaluated first)

| Rule ID | Condition                                                                           | Resulting Mode |
|---------|-------------------------------------------------------------------------------------|----------------|
| R-05    | Caller's `operator_roles` does not include `network_engineer` or `automation_agent` | `block`        |
| R-06    | Any entry in `policy_results` has `safety_decision = block`                         | `block`        |

If any block rule is triggered, the governance engine MUST set `mode = block` immediately and MUST NOT proceed to evaluate manual_review rules. The response MUST identify which block rule was triggered.

#### 4.2.2 Manual Review Rules (evaluated if no block rule triggered)

| Rule ID | Condition                                                                                              | Resulting Mode   |
|---------|--------------------------------------------------------------------------------------------------------|------------------|
| R-01    | `action_type = isolate_segment`                                                                        | `manual_review`  |
| R-02    | `risk_score` ≥ 70                                                                                      | `manual_review`  |
| R-03    | `environment = prod` AND would-be mode is `auto` AND `trust_score` < 60                               | `manual_review`  |
| R-04    | Two or more `policy_results` entries have equal precedence and produce conflicting `outcome` values    | `manual_review`  |

If any manual_review rule is triggered, the mode MUST be `manual_review`. If multiple rules are triggered, all triggered rule IDs MUST be listed in `triggered_rule`.

#### 4.2.3 Auto Mode

`auto` is returned only when:

- No block rule is triggered.
- No manual_review rule is triggered.
- All policy_results have `outcome: pass`.

#### 4.2.4 Rule Precedence Summary

```
1. R-05 (role check) → block if triggered
2. R-06 (safety_decision) → block if triggered
3. R-01 (isolate_segment) → manual_review if triggered
4. R-02 (risk_score ≥ 70) → manual_review if triggered
5. R-03 (prod + trust_score < 60) → manual_review if triggered
6. R-04 (policy conflict) → manual_review if triggered
7. Otherwise → auto
```

### 4.3 Governance Audit Trail

#### 4.3.1 Mandatory Audit Record

The governance engine MUST write an audit record for every governance check before returning its response. The audit record MUST contain:

| Field              | Value                                                                         |
|--------------------|-------------------------------------------------------------------------------|
| `timestamp`        | ISO 8601 datetime with millisecond precision (UTC)                           |
| `trace_id`         | Propagated from the incoming request                                          |
| `intent_id`        | From the governance check request                                             |
| `stage`            | `governance`                                                                  |
| `event_type`       | `decision`                                                                    |
| `operator_id`      | The authenticated submitter identity                                          |
| `outcome`          | The mode decision: `auto`, `manual_review`, or `block`                       |
| `duration_ms`      | Time elapsed for the governance evaluation                                     |
| `payload.mode`     | The mode decision                                                              |
| `payload.triggered_rules` | List of rule IDs that triggered the decision                          |
| `payload.risk_score` | The risk score from the request                                             |
| `payload.trust_score` | The trust score from the request                                           |
| `payload.policy_results_summary` | Summary of policy evaluation outcomes                          |
| `payload.ticket_id` | Ticket ID if mode=manual_review, else null                                  |

#### 4.3.2 Audit Immutability

- Governance audit records MUST be written to an append-only store (ANIF-107).
- Governance audit records MUST NOT be modified or deleted after writing.
- Any attempt to modify a governance audit record MUST be itself logged as a security event.

### 4.4 Approval Ticket Lifecycle

The governance engine is responsible for creating approval tickets when `mode = manual_review`. The complete human workflow (notification, approval, rejection) is defined in ANIF-404. This section defines the lifecycle state machine.

#### 4.4.1 Ticket States

```
created → pending → approved
                 → rejected
                 → expired (if not actioned within 15 minutes)
```

| State    | Description                                                                       |
|----------|-----------------------------------------------------------------------------------|
| created  | Ticket initialised by governance engine; transitions immediately to `pending`    |
| pending  | Awaiting human action; ticket is visible in the approval queue                   |
| approved | A senior_engineer has approved the ticket; intent may proceed to execution       |
| rejected | An operator has rejected the ticket; intent MUST NOT proceed                     |
| expired  | 15 minutes elapsed without action; intent MUST NOT proceed                       |

#### 4.4.2 State Transition Rules

- `pending` → `approved`: MUST require `senior_engineer` role; MUST be a different person from the submitter.
- `pending` → `rejected`: MUST require `network_engineer` role or above; MUST include a rejection reason.
- `pending` → `expired`: Automatically triggered by the system when `now > expires_at`; MUST be logged.
- Any transition from `approved`, `rejected`, or `expired` is FORBIDDEN; these are terminal states.

#### 4.4.3 Ticket Expiry Enforcement

- The governance engine MUST run a background process that monitors pending tickets and transitions them to `expired` when `expires_at` is reached.
- The expiry check MUST run at least every 60 seconds.
- An audit record MUST be written for each ticket expiry event.

### 4.5 Governance Metrics

The following metrics MUST be tracked and exposed by the governance engine:

| Metric                              | Type    | Labels                       | Description                                                    |
|-------------------------------------|---------|------------------------------|----------------------------------------------------------------|
| `anif_governance_auto_total`        | Counter | environment                  | Total executions routed as auto                                |
| `anif_governance_manual_review_total` | Counter | environment               | Total executions routed to manual_review                       |
| `anif_governance_block_total`       | Counter | environment, triggered_rule  | Total executions blocked, by triggering rule                   |
| `anif_ticket_approved_total`        | Counter | environment, approver_role   | Total tickets approved, by approver role                       |
| `anif_ticket_rejected_total`        | Counter | environment                  | Total tickets rejected                                         |
| `anif_ticket_expired_total`         | Counter | environment                  | Total tickets that expired without action                      |
| `anif_ticket_pending_age_seconds`   | Histogram | environment               | Age of pending tickets at time of action or expiry             |
| `anif_governance_rule_triggers_total` | Counter | rule_id, environment       | Total times each governance rule was triggered                  |

#### 4.5.1 Derived Governance Metrics

| Derived Metric        | Formula                                                              | Target (Level 2) |
|-----------------------|----------------------------------------------------------------------|------------------|
| Approval Rate         | `approved / (approved + rejected + expired)` (of manual_review tickets) | > 70%         |
| Rejection Rate        | `rejected / (approved + rejected + expired)`                         | < 20%            |
| Expiry Rate           | `expired / (approved + rejected + expired)`                          | < 10%            |
| Auto Rate             | `auto / total`                                                       | 40–60% (Level 2) |

### 4.6 Policy Override Controls

#### 4.6.1 Override Definition

A policy override is an authorised exception that allows an intent to proceed to execution despite a governance rule that would otherwise result in `manual_review` or `block`. Overrides are a risk control mechanism and MUST be used sparingly and with full accountability.

#### 4.6.2 Override Permissions

| Override Type                    | Who Can Authorise                 | Conditions                                                  |
|----------------------------------|-----------------------------------|-------------------------------------------------------------|
| Override `manual_review` → `auto`| `senior_engineer` role or above   | Only for pre-approved action types in non-prod environments |
| Override `block` (R-05)          | NOT permitted; role checks are mandatory | — |
| Override `block` (R-06: safety)  | NOT permitted; safety_decision=block is non-overridable | — |
| Emergency war room mode          | Requires approval by two `senior_engineer` stakeholders | Activates adjusted thresholds for defined incident window |

Overrides of `block` due to rule R-05 (missing role) and rule R-06 (safety_decision=block) MUST NOT be permitted under any circumstances.

#### 4.6.3 Override Audit Requirements

All policy overrides MUST be logged with:

1. The identity of the person who authorised the override.
2. The specific rule being overridden.
3. The stated justification for the override.
4. The `intent_id` and `ticket_id` the override applies to.
5. The timestamp of the override.

Override audit records MUST be flagged with `event_type: override` so they can be specifically queried and reported.

---

## 5. Conformance Requirements

1. An ANIF deployment MUST implement `POST /governance/check` with all six governance rules (R-01 through R-06) as specified in Section 4.2.
2. An audit record MUST be written before the governance check response is returned; failure to write the audit record MUST result in HTTP 503.
3. Block rules MUST be evaluated before manual_review rules.
4. Approval tickets MUST use the lifecycle state machine defined in Section 4.4.
5. Overrides of block rules R-05 and R-06 MUST NOT be permitted.
6. All policy overrides MUST be logged with the full fields specified in Section 4.6.3.
7. Governance metrics MUST be exposed as specified in Section 4.5.

---

## 6. Security Considerations

- The governance engine MUST NOT trust caller-supplied role claims; roles MUST be verified against the authoritative identity store on every request.
- Governance audit records MUST be written to a store that is physically separate from the governance engine's operational database, to prevent tampering via database-level access.
- The governance engine MUST be designed to fail closed: if the governance engine is unavailable or returns an error, the pipeline MUST NOT default to `auto`; it MUST treat the failure as `block` and notify operators.
- Override capabilities MUST be rate-limited; more than 3 overrides by the same operator within a 1-hour window MUST trigger an alert.
- Governance check requests MUST be authenticated; unauthenticated requests MUST be refused with HTTP 401.

---

## 7. Operational Considerations

- The governance engine SHOULD be monitored for response time; a governance check SHOULD complete within 200 ms in the 99th percentile.
- If the expiry rate for approval tickets rises above 10%, this indicates that the on-call staffing model or escalation procedures are insufficient for the ticket volume being generated.
- Governance rule trigger metrics SHOULD be reviewed weekly to identify rules that are triggering unexpectedly frequently or infrequently, as this may indicate policy miscalibration.
- War room mode (adjusted thresholds during incident response) SHOULD be a pre-approved configuration change, not an ad hoc override, to maintain auditability.

---

## Appendix A: Examples

### A.1 Governance Check — manual_review Due to Risk Score

**Request:**
```json
{
  "intent_id":      "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "operator_id":    "jsmith@example.com",
  "operator_roles": ["network_engineer"],
  "action_type":    "update_routing",
  "environment":    "prod",
  "risk_score":     74,
  "trust_score":    80,
  "policy_results": [
    { "policy_id": "no_direct_internet", "outcome": "pass", "safety_decision": null }
  ],
  "trace_id":       "3fa85f64-5717-4562-b3fc-2c963f66afa6"
}
```

**Response:**
```json
{
  "intent_id":         "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "mode":              "manual_review",
  "triggered_rule":    "R-02",
  "rationale":         "Governance mode set to manual_review because risk_score (74) is greater than or equal to the manual review threshold of 70 (Rule R-02). An approval ticket has been created. A senior_engineer must approve within 15 minutes.",
  "ticket_id":         "GOV-20260407-001",
  "ticket_expires_at": "2026-04-07T14:38:01.452Z",
  "audit_record_id":   "aud-20260407-gov-001",
  "trace_id":          "3fa85f64-5717-4562-b3fc-2c963f66afa6"
}
```

### A.2 Governance Check — block Due to Missing Role

**Request:**
```json
{
  "intent_id":      "aaaabbbb-cccc-dddd-eeee-ffffaaaabbbb",
  "operator_id":    "contractor@external.com",
  "operator_roles": ["read_only"],
  "action_type":    "scale_bandwidth",
  "environment":    "staging",
  "risk_score":     30,
  "trust_score":    50,
  "policy_results": [],
  "trace_id":       "aaaabbbb-0000-4000-8000-000000000001"
}
```

**Response:**
```json
{
  "intent_id":         "aaaabbbb-cccc-dddd-eeee-ffffaaaabbbb",
  "mode":              "block",
  "triggered_rule":    "R-05",
  "rationale":         "Governance mode set to block because the caller (contractor@external.com) does not hold the network_engineer or automation_agent role. The caller's roles are: read_only. This action cannot proceed.",
  "ticket_id":         null,
  "ticket_expires_at": null,
  "audit_record_id":   "aud-20260407-gov-002",
  "trace_id":          "aaaabbbb-0000-4000-8000-000000000001"
}
```

---

## Appendix B: Change History

| Version | Date       | Author             | Change                    |
|---------|------------|--------------------|---------------------------|
| 0.1.0   | 2026-04-07 | ANIF Working Group | Initial draft             |
