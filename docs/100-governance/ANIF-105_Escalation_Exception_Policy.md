# ANIF-105: Escalation and Exception Policy

| Field        | Value                                                       |
|--------------|-------------------------------------------------------------|
| Doc ID       | ANIF-105                                                    |
| Series       | Governance                                                  |
| Version      | 0.1.0                                                       |
| Status       | Draft                                                       |
| Authors      | ANIF Working Group                                          |
| Reviewers    | —                                                           |
| Approved by  | —                                                           |
| Created      | 2026-04-07                                                  |
| Last updated | 2026-04-07                                                  |
| Replaces     | N/A                                                         |
| Related docs | ANIF-103, ANIF-104, ANIF-404, ANIF-405, ANIF-406           |

---

## Abstract

This document defines the escalation and exception policies governing the ANIF autonomous networking pipeline. It specifies the triggers that route decisions to human review, the escalation paths and notification requirements for each trigger type, the process for requesting and logging policy exceptions, the war-room emergency path for P0/P1 incidents, and the SLA targets that govern response times. Together with ANIF-103 and ANIF-104, this document ensures that human oversight (P-06) is preserved at all risk levels.

---

## 1. Introduction

### 1.1 Purpose

Autonomous systems must know when not to act alone. This policy defines the conditions under which ANIF escalates decisions to human operators, the structured paths those escalations follow, and the controlled mechanism for temporarily overriding policies when operational necessity demands it. The policy is designed to balance operational efficiency (minimal unnecessary escalations) against safety (guaranteed human involvement for high-stakes decisions).

### 1.2 Scope

This policy applies to:

- All escalation events triggered by the ANIF pipeline, including: risk threshold breaches, policy conflicts, trust score failures, and system errors.
- All exception requests for temporary policy overrides.
- P0 and P1 incident escalations requiring the war-room emergency path.
- All notification requirements for escalation events.

### 1.3 Out of Scope

- Standard `manual_review` ticket workflows governed by ANIF-104 (those are a routine part of the change lifecycle, not an escalation per se, though they share notification mechanisms).
- Incident investigation and root cause analysis procedures (ANIF-405, ANIF-406).
- Security incident response not triggered through the ANIF pipeline (ANIF-406).

### 1.4 Intended Audience

| Audience                | Purpose                                                                   |
|-------------------------|---------------------------------------------------------------------------|
| Senior Engineer         | Primary escalation responder; war-room approver                           |
| Network Engineer        | Understand escalation triggers; on-call obligations                       |
| Policy Administrator    | Define escalation policies; grant and log exceptions                      |
| Compliance Officer      | Verify exception logging; audit escalation SLA compliance                 |
| Automation Agent        | Understand when escalation is triggered; produce required context         |

---

## 2. Normative References

| Reference      | Title                                                          |
|----------------|----------------------------------------------------------------|
| ANIF-001       | ANIF Constitution and Guiding Principles                       |
| ANIF-002       | ANIF Core Glossary                                             |
| ANIF-103       | Autonomous Action Policy                                       |
| ANIF-104       | Change Management Policy                                       |
| ANIF-107       | Audit Trail Requirements                                       |
| ANIF-404       | Operational Security Controls                                  |
| ANIF-405       | Incident Management                                            |
| ANIF-406       | Incident Response                                              |
| RFC 2119       | Key words for use in RFCs to Indicate Requirement Levels       |

---

## 3. Terms and Definitions

| Term                   | Definition                                                                                              |
|------------------------|---------------------------------------------------------------------------------------------------------|
| Escalation             | The transfer of a decision or action from the automated pipeline to a human operator for review.        |
| Escalation Trigger     | A condition that automatically initiates an escalation.                                                 |
| Escalation Path        | The defined sequence of roles and notification channels for a given escalation.                         |
| Exception              | A time-limited, logged override of a specific policy rule, granted by an authorised approver.           |
| War-Room Path          | An expedited escalation path for P0/P1 incidents that bypasses normal approval but requires post-hoc review. |
| P0 Incident            | A critical incident causing immediate service outage or security breach; highest severity.              |
| P1 Incident            | A major incident causing significant service degradation; second-highest severity.                      |
| Post-Hoc Review        | A mandatory review of a war-room decision conducted after the incident is resolved.                     |
| SLA                    | Service Level Agreement — a defined target for response time or other operational metric.               |
| Acknowledgement        | A formal indication that a human operator has received and accepted an escalation.                      |

---

## 4. Escalation and Exception Policy

### 4.1 Escalation Triggers

The following conditions MUST automatically trigger an escalation. The pipeline MUST evaluate these triggers at the governance stage and MUST escalate before returning a response.

| Trigger ID | Condition                                                              | Severity  | Required Escalation Path |
|------------|------------------------------------------------------------------------|-----------|--------------------------|
| ESC-001    | `risk_score` ≥ 70 (any action, any environment)                        | High      | auto → manual_review → senior_engineer |
| ESC-002    | Action type = `isolate_segment` (any risk score, any environment)      | High      | auto → manual_review → senior_engineer |
| ESC-003    | `environment` = `prod` AND `trust_score` < 60                          | High      | auto → manual_review → senior_engineer |
| ESC-004    | Policy conflict with equal precedence detected                         | Medium    | auto → manual_review → policy_administrator |
| ESC-005    | System error in any pipeline stage (except validate)                   | High      | auto → block → senior_engineer notified |
| ESC-006    | Approval ticket expired (15-minute window elapsed)                     | Medium    | manual_review → senior_engineer (re-escalation) |
| ESC-007    | Post-change verification failed                                        | High      | rollback triggered → senior_engineer notified |
| ESC-008    | Rollback failed                                                        | Critical  | P1 incident declared → war-room path |
| ESC-009    | Change requested during active change freeze                           | Medium    | block → policy_administrator notified |

All escalation trigger evaluations MUST be logged in the audit record with the trigger ID and the condition values that caused the trigger.

### 4.2 Escalation Paths

#### 4.2.1 Standard Escalation Path (High Severity)

Used for ESC-001, ESC-002, ESC-003, ESC-007:

```
1. Pipeline assigns governance mode: manual_review
2. Approval ticket created (ANIF-104 §4.7)
3. Immediate notification to: network_engineer (on-call)
4. If no acknowledgement within 5 minutes:
   → Escalate to: senior_engineer (primary)
5. If no acknowledgement within 10 minutes:
   → Escalate to: senior_engineer (secondary / backup)
   → Notify: policy_administrator
6. If no acknowledgement within 15 minutes:
   → Ticket expires → ESC-006 triggered
   → Escalate to: senior_engineer + policy_administrator
   → Intent blocked; requester notified
```

#### 4.2.2 Policy Conflict Escalation Path (Medium Severity)

Used for ESC-004:

```
1. Pipeline holds intent; governance mode: manual_review
2. Immediate notification to: policy_administrator
3. Conflict summary included in notification (rule IDs, precedence values)
4. If no acknowledgement within 15 minutes:
   → Escalate to: senior_engineer + compliance_officer
5. If no resolution within 60 minutes:
   → Intent automatically blocked; audit record written
   → Policy conflict logged in policy conflict register
```

#### 4.2.3 System Error Escalation Path (High Severity)

Used for ESC-005:

```
1. Pipeline fails to: block (P-07 Fail Safe)
2. Immediate notification to: senior_engineer (on-call)
3. Error details included in notification: stage, error_type, error_message, intent_id
4. If no acknowledgement within 10 minutes:
   → Page senior_engineer secondary
   → Notify: policy_administrator
5. System MUST remain in safe state (no new auto executions) until senior_engineer acknowledges
```

#### 4.2.4 Policy Administrator Escalation Path (Medium Severity)

Used for ESC-006, ESC-009:

```
1. Pipeline blocks or holds intent
2. Notification to: policy_administrator
3. If no acknowledgement within 30 minutes:
   → Escalate to: senior_engineer
4. Requester notified of hold and expected resolution time
```

### 4.3 SLA Targets

The following SLA targets MUST be met for escalation acknowledgements.

| Severity | Event Type                       | Acknowledgement SLA | Resolution SLA  |
|----------|----------------------------------|---------------------|-----------------|
| Critical | Rollback failure (ESC-008)       | 5 minutes           | 60 minutes      |
| High     | Risk ≥ 70 escalation (ESC-001)   | 15 minutes          | 30 minutes      |
| High     | `isolate_segment` (ESC-002)      | 15 minutes          | 30 minutes      |
| High     | Trust score failure (ESC-003)    | 15 minutes          | 30 minutes      |
| High     | System error (ESC-005)           | 10 minutes          | As needed       |
| High     | Verification failed (ESC-007)    | 15 minutes          | 30 minutes      |
| Medium   | Policy conflict (ESC-004)        | 15 minutes          | 60 minutes      |
| Medium   | Ticket expired (ESC-006)         | 15 minutes          | 30 minutes      |
| Medium   | Change freeze violation (ESC-009)| 30 minutes          | N/A (blocked)   |
| P0       | Active P0 incident               | 5 minutes           | 4 hours         |
| P1       | Active P1 incident               | 15 minutes          | 8 hours         |

SLA compliance MUST be measured from the time the escalation notification is sent. SLA misses MUST be logged and included in weekly operational reports.

### 4.4 Escalation Notification Requirements

4.4.1 All escalation notifications MUST be delivered through at minimum two channels (e.g., email + SMS/pager). Single-channel notification is NOT sufficient for High or Critical severity events.

4.4.2 Escalation notifications MUST include the following information:

| Field              | Required For        | Description                                                  |
|--------------------|---------------------|--------------------------------------------------------------|
| `escalation_id`    | All severities      | Unique identifier for this escalation event.                 |
| `trigger_id`       | All severities      | The ESC-00X trigger that caused this escalation.             |
| `intent_id`        | All severities      | The intent that triggered the escalation.                    |
| `action_type`      | All severities      | The proposed action type.                                    |
| `environment`      | All severities      | Target environment.                                          |
| `risk_score`       | High/Critical       | Computed risk score.                                         |
| `decision_summary` | All severities      | Human-readable description of the proposed change.           |
| `acknowledge_url`  | All severities      | Direct URL to acknowledge and approve/reject in one click.   |
| `expires_at`       | All severities      | When the escalation window expires.                          |

4.4.3 Notification delivery MUST be confirmed. If delivery cannot be confirmed within 60 seconds, the system MUST attempt delivery via the backup channel and log the delivery failure.

4.4.4 Notification channels MUST be authenticated and integrity-protected. Unencrypted email-only escalation for High or Critical events MUST NOT be used.

### 4.5 War-Room Emergency Path

4.5.1 The war-room path is used for P0 and P1 incidents where immediate autonomous action is required to restore or protect service. It bypasses normal approval timing but does not bypass human oversight.

4.5.2 War-room path activation requirements:

- A P0 or P1 incident MUST be formally declared via ANIF-405 before the war-room path may be invoked.
- A senior_engineer or policy_administrator MUST explicitly activate the war-room path.
- Activation MUST be logged immediately in the audit trail.

4.5.3 War-room path procedure:

```
1. P0/P1 incident declared (ANIF-405)
2. Senior engineer activates war-room path (authenticated action; audit logged)
3. Governance mode override: manual_review → expedited_war_room
4. Approver has 5 minutes to approve/reject (vs. standard 15 minutes)
5. Approved action executes immediately
6. Post-execution audit record written with flag: war_room: true
7. Post-hoc review MUST be scheduled within 24 hours (see §4.5.5)
```

4.5.4 War-room approvers:

- A minimum of ONE senior_engineer or policy_administrator MUST approve the action.
- The approver MUST NOT be the same person who submitted the intent or declared the incident.

4.5.5 Post-hoc review requirements:

- Every war-room action MUST be reviewed within 24 hours of the incident being resolved.
- The review MUST include: intent context, action taken, outcome, risk score at time of execution, and whether a non-war-room path could have been used.
- Review findings MUST be written to the audit trail and stored with the original escalation record.
- If the review finds the war-room path was misused, the compliance_officer MUST be notified and the event treated as a policy violation (Section 4.7).

### 4.6 Exception Process

4.6.1 An exception is a time-limited, authorised override of a specific policy rule. Exceptions allow the pipeline to proceed past a policy that would otherwise block an action, under controlled conditions.

4.6.2 Exception request requirements. An exception request MUST include:

| Field               | Type              | Description                                                           |
|---------------------|-------------------|-----------------------------------------------------------------------|
| `exception_id`      | UUID              | System-generated unique identifier.                                   |
| `policy_rule_id`    | string            | The specific policy rule being overridden.                            |
| `intent_id`         | UUID              | The intent for which the exception is requested.                      |
| `justification`     | string (≥ 100 chars) | Detailed business justification for the exception.                 |
| `requested_by`      | string            | Identity of the requester.                                            |
| `requested_at`      | ISO-8601          | Timestamp of request submission.                                      |
| `valid_from`        | ISO-8601          | When the exception takes effect.                                      |
| `valid_until`       | ISO-8601          | When the exception expires; MUST NOT exceed 24 hours from `valid_from`.|
| `approved_by`       | string or null    | Identity of approver; null until approved.                            |
| `approved_at`       | ISO-8601 or null  | Timestamp of approval.                                                |

4.6.3 Exception approval authority:

| Policy Rule Type                  | Minimum Approver Role         |
|-----------------------------------|-------------------------------|
| Risk threshold adjustment         | policy_administrator          |
| Change window override            | senior_engineer               |
| Data residency constraint         | compliance_officer            |
| Action type restriction (standard)| policy_administrator          |
| `isolate_segment` routing         | PROHIBITED — cannot be excepted|

4.6.4 Exception logging: every exception MUST be written to the audit log. The exception record MUST include all fields in Section 4.6.2 plus: the pipeline stage it applies to and the specific condition being overridden.

4.6.5 Exception expiry: exceptions MUST expire at `valid_until`. The pipeline MUST NOT honour expired exceptions. Expired exceptions MUST be logged as expired in the audit trail.

4.6.6 The requirement that `isolate_segment` always routes to `manual_review` (ANIF-103 §4.2) is ABSOLUTE and MUST NOT be excepted under any circumstances.

### 4.7 Policy Violation Consequences and Escalation

4.7.1 A policy violation occurs when an action is executed outside the terms of ANIF-103 or this document without proper exception authorisation.

4.7.2 Policy violations MUST be detected by the pipeline through audit record analysis (reconciliation of executed actions against approved modes).

4.7.3 On detection of a policy violation, the following MUST occur:

1. Immediate notification to: compliance_officer, policy_administrator, senior_engineer.
2. Audit record flagged with `policy_violation: true`.
3. Responsible automation_agent or operator identity recorded.
4. P1 incident declared automatically if the violating action is in production.
5. The pipeline MAY be halted pending investigation at senior_engineer discretion.

4.7.4 Policy violation consequences by severity:

| Violation Type                              | Consequence                                                          |
|---------------------------------------------|----------------------------------------------------------------------|
| Automation agent exceeds authorisation      | Agent credential suspended; senior engineer review before reinstatement |
| Human operator bypasses governance gate     | Immediate escalation to compliance officer; disciplinary review      |
| War-room path misuse                        | Compliance officer review; policy administrator retraining           |
| Expired exception honoured by system        | P1 incident; root cause analysis required; patch required            |

---

## 5. Conformance Requirements

5.1 Conformant implementations MUST implement all nine escalation triggers defined in Section 4.1 and MUST fire the appropriate escalation path for each.

5.2 Conformant implementations MUST meet the SLA targets in Section 4.3 and MUST log SLA misses in the audit trail.

5.3 Conformant implementations MUST implement the war-room emergency path per Section 4.5 and MUST require post-hoc review within 24 hours.

5.4 Conformant implementations MUST implement the exception process per Section 4.6 and MUST write all exceptions to the audit trail.

5.5 Conformant implementations MUST deliver escalation notifications via at minimum two channels for High and Critical severity events.

5.6 The `isolate_segment` routing requirement (always `manual_review`) MUST NOT be overridden by any exception.

---

## 6. Security Considerations

6.1 Escalation notification channels are high-value targets: suppressing escalations can allow unauthorised actions to execute. Notification delivery MUST be monitored and alerting configured for delivery failures.

6.2 War-room path activation is a significant privilege. Activation audit records MUST be immutable and MUST NOT be deletable by any role, including policy_administrator.

6.3 Exception records represent deliberate policy overrides and MUST be treated with the same security level as policy documents. Access to create or approve exceptions MUST require multi-factor authentication.

6.4 The exception system MUST implement rate limiting. More than 3 exceptions for the same policy rule within 24 hours MUST trigger an alert to the compliance officer.

---

## 7. Operational Considerations

7.1 On-call rosters for network_engineer and senior_engineer roles MUST be maintained and kept current. The escalation system MUST automatically route to the current on-call operator.

7.2 SLA compliance reports MUST be generated weekly and reviewed by the policy_administrator. Persistent SLA misses indicate either under-staffing or overly aggressive escalation trigger thresholds.

7.3 The war-room path SHOULD be exercised in quarterly tabletop simulations. Procedures for war-room activation, approval, and post-hoc review SHOULD be documented in runbooks.

7.4 Exception usage SHOULD be reviewed monthly. High exception rates for specific policy rules indicate those rules may need to be revised rather than routinely excepted.

7.5 Escalation trigger thresholds (e.g., risk_score ≥ 70) SHOULD be reviewed semi-annually based on observed incident and false-positive rates.

---

## Appendix A: Examples

### A.1 Standard Escalation (ESC-001: risk_score ≥ 70)

Intent: `reroute_traffic` in prod, risk_score = 74.

1. Risk score computed: 74.
2. ESC-001 triggered at governance stage.
3. Governance mode: `manual_review`.
4. Approval ticket created; expires at T+15min.
5. Notification sent via email + SMS to network_engineer (on-call).
6. At T+5min: no acknowledgement → escalated to senior_engineer.
7. Senior engineer acknowledges at T+7min; approves at T+9min.
8. Execute: traffic rerouted.
9. Audit: all records including escalation record written.

### A.2 War-Room Path Activation (P0 Incident)

P0 incident: DDoS attack on core segment; immediate isolation required.

1. Network engineer declares P0 incident via ANIF-405.
2. senior_engineer activates war-room path (authenticated; audit logged).
3. Intent submitted: `isolate_segment` for `segment-core-A` in prod.
4. Escalation: war-room path; 5-minute approval window.
5. senior_engineer-2 (not the incident declarant) approves at T+3min.
6. Execute: segment isolated; audit record flagged `war_room: true`.
7. Incident resolved at T+240min.
8. Post-hoc review scheduled for T+24h.
9. Post-hoc review finds: war-room path appropriate; no misuse.

### A.3 Exception Request for Change Window Override

Scenario: Critical patch must be applied during declared change freeze.

1. senior_engineer submits exception request.
2. `policy_rule_id`: `change_window_freeze_prod_20260407`
3. `justification`: "Critical security vulnerability CVE-2026-XXXXX; patch required within 2 hours per security policy."
4. `valid_until`: T+4h (within 24h maximum).
5. senior_engineer (different approver) approves at T+5min.
6. Exception logged in audit trail.
7. Pipeline proceeds past change freeze check for this intent only.
8. Exception expires at T+4h; logged as expired.

---

## Appendix B: Change History

| Version | Date       | Author             | Description          |
|---------|------------|--------------------|----------------------|
| 0.1.0   | 2026-04-07 | ANIF Working Group | Initial draft        |
