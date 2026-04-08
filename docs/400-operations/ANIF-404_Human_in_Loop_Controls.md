# ANIF-404: Human-in-Loop Controls

| Field        | Value                                        |
|--------------|----------------------------------------------|
| Doc ID       | ANIF-404                                     |
| Series       | Operations                                   |
| Version      | 0.1.0                                        |
| Status       | Draft                                        |
| Authors      | ANIF Working Group                           |
| Reviewers    | —                                            |
| Approved by  | —                                            |
| Created      | 2026-04-07                                   |
| Last updated | 2026-04-07                                   |
| Replaces     | N/A                                          |
| Related docs | ANIF-406, ANIF-103, ANIF-305                 |

---

## Abstract

This document defines the human-in-loop control requirements for ANIF-conformant deployments. Human-in-loop controls are the mechanisms by which human operators retain meaningful authority over automated network actions at all maturity levels. Core principles include the absolute nature of human override (P-06), the mandatory mode gate that every execution path MUST traverse, normative manual review trigger conditions, the approval ticket workflow with 15-minute expiry, role requirements for submission and approval, the emergency halt capability, and the information requirements for human review interfaces.

---

## 1. Introduction

### 1.1 Purpose

This document establishes normative requirements for human-in-loop controls within ANIF systems. While ANIF enables progressive automation up to full autonomy (Level 4), human authority is never relinquished. This document specifies the mechanisms by which that authority is exercised, the conditions under which human review is mandatory, and the interfaces through which operators act.

### 1.2 Scope

This document covers:

- The absolute human override principle (P-06).
- The mandatory mode gate and its trigger conditions.
- Manual review trigger rules (normative).
- The approval ticket lifecycle: creation, notification, expiry, re-submission.
- Role requirements for ticket submission and approval.
- The emergency halt capability.
- Human review interface information requirements.

### 1.3 Out of Scope

- The governance engine's rule evaluation logic (covered in ANIF-406).
- The audit logging of governance decisions (covered in ANIF-107 and ANIF-406).
- Operational governance metrics (covered in ANIF-406).
- ITSM tool integration (implementation-specific).

### 1.4 Intended Audience

| Audience                     | Usage                                                               |
|------------------------------|---------------------------------------------------------------------|
| Network Operations Engineers | Understanding approval flows, halt procedures, and role requirements|
| Senior Engineers             | Understanding high-risk approval responsibilities                   |
| Platform Engineers           | Implementing approval ticket workflow and halt capability           |
| Governance and Compliance    | Auditing human oversight mechanisms                                 |

---

## 2. Normative References

- ANIF-103: Governance Policy Framework
- ANIF-305: Intent Execution Pipeline
- ANIF-400: Operations Overview
- ANIF-406: Governance Controls
- ANIF-107: Audit and Immutable Logging Standard
- RFC 2119: Key words for use in RFCs to Indicate Requirement Levels

---

## 3. Terms and Definitions

| Term                 | Definition                                                                                                     |
|----------------------|----------------------------------------------------------------------------------------------------------------|
| Mode Gate            | The governance check that every execution path MUST pass through, returning auto, manual_review, or block.    |
| Manual Review        | A governance outcome requiring a human operator to explicitly approve an action before it proceeds.            |
| Approval Ticket      | A structured record created when an action requires manual_review; the mechanism for human approval.          |
| Emergency Halt       | An operator-initiated action that immediately stops an in-progress execution.                                  |
| P-06                 | ANIF Principle 6: Human override is absolute; any human with appropriate role MAY halt or reverse any automated action at any time. |
| trust_score          | A numeric value (0–100) representing confidence in the operator's or agent's historical decision reliability. |
| risk_score           | A numeric value (0–100) representing the assessed risk of a proposed action.                                  |

---

## 4. Human-in-Loop Control Requirements

### 4.1 Absolute Human Override (P-06)

ANIF Principle P-06 is normative and unconditional:

1. Any human operator with the `network_engineer` role or above MAY halt or reverse any automated action at any time, regardless of the current maturity level.
2. This override capability MUST remain available even when the primary automation infrastructure is operating normally and even at Level 4 (Full Autonomy).
3. No automated system component MUST ever prevent a human operator from exercising this override.
4. The override capability MUST be available through a mechanism that does not depend solely on the main pipeline being available (e.g., an independent halt endpoint or out-of-band control path).

### 4.2 Mandatory Mode Gate

Every intent execution path MUST pass through the governance mode gate before any network action is taken. The mode gate is implemented via `POST /governance/check` (specified in ANIF-406).

The mode gate MUST return one of three outcomes:

| Outcome        | Meaning                                                                          |
|----------------|----------------------------------------------------------------------------------|
| `auto`         | Action may proceed immediately without human approval                            |
| `manual_review`| Action MUST NOT proceed until a human operator approves an approval ticket        |
| `block`        | Action MUST NOT proceed; no approval path is available                           |

No execution stage in the pipeline MUST proceed to network action without having received a `mode` determination from the governance gate.

### 4.3 Manual Review Trigger Rules

The following conditions MUST trigger `manual_review` mode. These rules are normative and MUST be implemented exactly as stated:

| Rule ID | Condition                                                        | Required Mode    |
|---------|------------------------------------------------------------------|------------------|
| R-01    | Action type is `isolate_segment`                                 | `manual_review`  |
| R-02    | `risk_score` ≥ 70                                                | `manual_review`  |
| R-03    | `environment` = `prod` AND `mode` would be `auto` AND `trust_score` < 60 | `manual_review` |
| R-04    | Two or more policies of equal precedence reach conflicting conclusions | `manual_review` |

The following condition MUST trigger `block` mode:

| Rule ID | Condition                                                        | Required Mode    |
|---------|------------------------------------------------------------------|------------------|
| R-05    | Operator lacks `network_engineer` or `automation_agent` role     | `block`          |
| R-06    | Any policy evaluation returns `safety_decision: block`           | `block`          |

Rule precedence:

1. `block` rules (R-05, R-06) take precedence over all other rules.
2. `manual_review` rules (R-01 through R-04) take precedence over `auto`.
3. `auto` is the outcome only when no block or manual_review rule is triggered.

### 4.4 Approval Ticket Lifecycle

#### 4.4.1 Ticket Creation

When the mode gate returns `manual_review`, the system MUST:

1. Create an approval ticket immediately before returning the governance check response.
2. Assign a unique `ticket_id`.
3. Set initial status to `pending`.
4. Set `expires_at` to exactly 15 minutes after `created_at`.
5. Write an audit record for the ticket creation before returning.

**Approval Ticket Schema:**

```json
{
  "ticket_id":         "<string — unique identifier for this approval ticket>",
  "intent_id":         "<UUID v4>",
  "decision_summary":  "<string — plain-English summary of the action requiring approval>",
  "risk_score":        "<integer 0-100>",
  "requested_by":      "<string — operator_id of the submitter>",
  "created_at":        "<ISO 8601 datetime>",
  "expires_at":        "<ISO 8601 datetime — exactly 15 minutes after created_at>",
  "status":            "pending",
  "reasoning_chain_url": "<string — URL to GET /audit/{intent_id}/why>",
  "required_approver_role": "senior_engineer"
}
```

#### 4.4.2 Ticket Notification

Upon ticket creation, the system MUST:

1. Send a notification to the on-call operator queue via the configured notification channel.
2. Include in the notification: `ticket_id`, `decision_summary`, `risk_score`, `expires_at`, and a direct link to the approval interface.
3. The notification MUST be dispatched within 30 seconds of ticket creation.

#### 4.4.3 Ticket Expiry

1. If a ticket reaches `expires_at` without being approved or rejected, the system MUST automatically set its status to `expired`.
2. The expiry MUST be recorded as an audit event.
3. The intent associated with an expired ticket MUST NOT proceed to execution.
4. The operator who submitted the intent MUST be notified of the expiry.
5. To proceed after expiry, the operator MUST resubmit the intent. Resubmission creates a new pipeline execution and a new ticket; expired tickets MUST NOT be extended or reactivated.

#### 4.4.4 Ticket Approval

`POST /governance/approve/{ticket_id}`

**Requirements:**

1. The caller MUST have the `senior_engineer` role or above. Callers with `network_engineer` or `automation_agent` roles MUST be refused with HTTP 403.
2. The approver MUST be a different person from the submitter. Self-approval MUST be refused with HTTP 403.
3. The ticket MUST be in `pending` status. Approval of an `expired`, `rejected`, or `approved` ticket MUST be refused with HTTP 409.
4. The system MUST write an audit record for the approval before returning a success response.
5. Upon successful approval, the pipeline MUST be notified to proceed with execution.

**Request Body:**

```json
{
  "approver_role":  "senior_engineer",
  "notes":          "<string — optional approval notes>"
}
```

**Response:**

```json
{
  "ticket_id":      "<string>",
  "status":         "approved",
  "approved_by":    "<operator_id>",
  "approved_at":    "<ISO 8601 datetime>",
  "audit_record_id": "<string>"
}
```

#### 4.4.5 Ticket Rejection

`POST /governance/reject/{ticket_id}`

**Requirements:**

1. The caller MUST have the `network_engineer` role or above.
2. A `reason` field MUST be provided; rejection without a reason MUST be refused with HTTP 400.
3. The system MUST write an audit record for the rejection before returning.
4. Upon rejection, the intent MUST NOT proceed to execution.

**Request Body:**

```json
{
  "reason":  "<string — required; operator's reason for rejection>"
}
```

### 4.5 Role Requirements Summary

| Action                               | Minimum Role Required   |
|--------------------------------------|-------------------------|
| Submit intent for execution          | `network_engineer` or `automation_agent` |
| View pending approval tickets        | `network_engineer`       |
| Approve a manual_review ticket       | `senior_engineer`        |
| Reject a manual_review ticket        | `network_engineer`       |
| Invoke emergency halt                | `network_engineer`       |
| Override an automated rollback       | `network_engineer`       |

### 4.6 Emergency Halt

#### 4.6.1 Halt Capability Requirements

1. Any operator with the `network_engineer` role MUST be able to halt an in-progress execution at any time.
2. The halt endpoint MUST be available independently of the main pipeline; it MUST NOT depend on pipeline health to function.
3. A halt MUST take effect within 10 seconds of the halt request being received.
4. The halt MUST be logged as an audit record with `event_type: audit`, `stage: execution`, and `outcome: halted_by_operator` before the halt response is returned.

#### 4.6.2 Halt Endpoint

`POST /execution/{intent_id}/halt`

**Requirements:**

1. Caller MUST have `network_engineer` role or above.
2. A `reason` field MUST be provided.
3. If execution has already completed (success or failure), the system MUST return HTTP 409 with a message indicating that the execution is complete and an operator-initiated rollback may be appropriate.
4. If a partial configuration change has been applied, the system MUST initiate a rollback and include the rollback status in the response.

**Request Body:**

```json
{
  "reason":      "<string — required>",
  "operator_id": "<string — authenticated caller identity>"
}
```

**Response:**

```json
{
  "intent_id":      "<UUID v4>",
  "halt_status":    "halted",
  "rollback_initiated": true,
  "rollback_status": "in_progress",
  "audit_record_id": "<string>",
  "halted_by":      "<operator_id>",
  "halted_at":      "<ISO 8601 datetime>"
}
```

### 4.7 Human Review Interface Requirements

When presenting an approval ticket to an operator, the interface MUST provide all of the following information:

| Information Element           | Source                                      | Required |
|-------------------------------|---------------------------------------------|----------|
| Intent summary                | `decision_summary` from approval ticket     | Yes      |
| Proposed action details       | Intent payload                              | Yes      |
| Risk score                    | `risk_score` from approval ticket           | Yes      |
| Risk score justification      | Reasoning chain step for risk stage         | Yes      |
| Full reasoning chain          | `GET /audit/{intent_id}/why`                | Yes      |
| Governance rule triggered     | Reasoning chain step for governance stage   | Yes      |
| Rollback plan                 | Pipeline-generated rollback description     | Yes      |
| Time remaining before expiry  | `expires_at` minus current time             | Yes      |
| Submitter identity            | `requested_by` from approval ticket         | Yes      |
| Policy evaluation results     | Reasoning chain step for policy stage       | Yes      |
| Historical actions on same target | Query of recent audit log for same resource | Recommended |

The interface MUST display a countdown timer showing time remaining before ticket expiry.

The interface MUST provide clearly labelled Approve and Reject actions with a confirmation step before submission.

---

## 5. Conformance Requirements

1. An ANIF deployment MUST implement the mandatory mode gate as specified in Section 4.2.
2. An ANIF deployment MUST implement all manual review trigger rules R-01 through R-06 as stated in Section 4.3.
3. Approval tickets MUST have a 15-minute expiry; this value MUST NOT be configurable in the prototype.
4. The approver role MUST be `senior_engineer` or above; this requirement MUST be enforced at the API layer.
5. Self-approval MUST be refused.
6. Emergency halt MUST be available independently of the main pipeline.
7. Every halt, approval, and rejection MUST generate an audit record before returning a success response.
8. Human override capability (P-06) MUST be available at all maturity levels including Level 4.

---

## 6. Security Considerations

- Role verification MUST be performed server-side on every request; client-supplied role claims MUST NOT be trusted without server-side verification.
- Approval tickets MUST be single-use; an approved ticket MUST NOT be reusable.
- The emergency halt endpoint MUST be rate-limited to prevent abuse while remaining usable in genuine emergencies.
- Ticket IDs MUST NOT be predictable or sequential; they MUST be opaque random identifiers.
- Notification payloads MUST NOT include sensitive intent parameters that are not necessary for the approval decision.

---

## 7. Operational Considerations

- Operators MUST be trained on the approval workflow before the deployment advances beyond Level 1.
- The 15-minute ticket expiry is designed to maintain urgency and prevent stale approvals; in incident response scenarios (war room mode), organisations MAY define a separate policy with extended expiry subject to governance approval.
- Organisations SHOULD define an on-call rotation that ensures a `senior_engineer` is available to approve tickets within the 15-minute window during all operational hours.
- Approval queue depth SHOULD be monitored; more than 5 pending tickets at once may indicate staffing or threshold calibration issues.

---

## Appendix A: Examples

### A.1 Approval Workflow — Risk Score Escalation

```
1. Operator submits intent: update_routing for prod segment prod-42
2. Governance gate evaluates: risk_score=74, environment=prod
3. Rule R-02 triggered (risk_score ≥ 70) → mode=manual_review
4. Ticket created: ticket_id=GOV-20260407-042, expires_at=T+15min
5. On-call senior_engineer receives notification
6. Senior engineer reviews: GET /audit/{intent_id}/why → reads reasoning chain
7. Senior engineer approves: POST /governance/approve/GOV-20260407-042
8. Audit record written: approval logged
9. Pipeline proceeds to execution stage
10. Execution completes: outcome=success, rollback_available=true
```

### A.2 Emergency Halt Scenario

```
1. Automated action executing: reroute_traffic on prod segment
2. Network engineer observes unexpected side effect in monitoring
3. Engineer calls: POST /execution/{intent_id}/halt {"reason": "unexpected BGP state change observed"}
4. System halts execution within 10 seconds
5. Partial change triggers rollback: rollback_initiated=true
6. Audit record written: event_type=audit, outcome=halted_by_operator
7. Engineer notified: rollback_status=success
8. Post-incident review: GET /audit/{intent_id}/why used for analysis
```

---

## Appendix B: Change History

| Version | Date       | Author             | Change                    |
|---------|------------|--------------------|---------------------------|
| 0.1.0   | 2026-04-07 | ANIF Working Group | Initial draft             |
