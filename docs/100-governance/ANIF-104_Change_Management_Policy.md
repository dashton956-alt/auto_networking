# ANIF-104: Change Management Policy

| Field        | Value                                                          |
|--------------|----------------------------------------------------------------|
| Doc ID       | ANIF-104                                                       |
| Series       | Governance                                                     |
| Version      | 0.1.0                                                          |
| Status       | Draft                                                          |
| Authors      | ANIF Working Group                                             |
| Reviewers    | —                                                              |
| Approved by  | —                                                              |
| Created      | 2026-04-07                                                     |
| Last updated | 2026-04-07                                                     |
| Replaces     | N/A                                                            |
| Related docs | ANIF-103, ANIF-107, ANIF-305, ANIF-306, ANIF-404, ANIF-405   |

---

## Abstract

This document defines the change management policy for all autonomous network changes executed through ANIF. It classifies changes into standard, normal, and emergency types; specifies the lifecycle for each; defines pre-authorised change patterns that bypass manual review; establishes change freeze and blackout window procedures; mandates rollback requirements; defines post-change verification steps; specifies the approval ticket schema for manual review escalations; and sets audit trail requirements for all changes. This policy implements P-01 (Reversibility) and P-10 (Test-First).

---

## 1. Introduction

### 1.1 Purpose

Autonomous network changes introduce risk at scale: a single mis-configured intent can affect thousands of flows simultaneously. This policy ensures that every change — whether executed automatically or after human approval — follows a defined, auditable, and reversible lifecycle. It provides the governance bridge between the technical pipeline (ANIF-103, ANIF-306) and organisational change management obligations (ITSM integration, compliance evidence).

### 1.2 Scope

This policy applies to:

- All network changes executed through the ANIF pipeline, regardless of governance mode (`auto`, `manual_review`).
- All four bounded action types: `reroute_traffic`, `apply_qos`, `scale_bandwidth`, `isolate_segment`.
- All environments: prod, staging, development, test.
- All change initiators: human roles and automation agents.

### 1.3 Out of Scope

- Manual changes to network devices performed outside the ANIF pipeline.
- Infrastructure provisioning (server, storage, cloud resource creation).
- Software deployments to ANIF pipeline components (governed by DevOps change policy).
- Emergency security patches applied directly to network devices.

### 1.4 Intended Audience

| Audience                | Purpose                                                                   |
|-------------------------|---------------------------------------------------------------------------|
| Policy Administrator    | Define and maintain standard change patterns; set change windows          |
| Senior Engineer         | Approve normal and emergency changes; manage change freeze exceptions      |
| Network Engineer        | Submit change requests; monitor execution and verification                 |
| Compliance Officer      | Verify change audit trail completeness; produce evidence for audits        |
| Automation Agent        | Operate within pre-authorised change patterns; produce audit-quality records |

---

## 2. Normative References

| Reference      | Title                                                          |
|----------------|----------------------------------------------------------------|
| ANIF-001       | ANIF Constitution and Guiding Principles                       |
| ANIF-002       | ANIF Core Glossary                                             |
| ANIF-103       | Autonomous Action Policy                                       |
| ANIF-105       | Escalation and Exception Policy                                |
| ANIF-107       | Audit Trail Requirements                                       |
| ANIF-305       | Orchestration and Cross-Domain                                 |
| ANIF-306       | Action Execution Specification                                 |
| ANIF-404       | Operational Security Controls                                  |
| ANIF-405       | Incident Management                                            |
| RFC 2119       | Key words for use in RFCs to Indicate Requirement Levels       |

---

## 3. Terms and Definitions

| Term                    | Definition                                                                                             |
|-------------------------|--------------------------------------------------------------------------------------------------------|
| Standard Change         | A pre-authorised change pattern that meets defined safety criteria and may execute without manual review.|
| Normal Change           | A change that requires risk assessment and may require manual review depending on risk score.           |
| Emergency Change        | A change required immediately to resolve a P0 or P1 incident; follows an expedited approval path.      |
| Change Window           | A defined period during which changes are permitted; changes outside windows are blocked or deferred.   |
| Change Freeze           | A period during which no changes are permitted (e.g., peak trading hours, major events).               |
| Approval Ticket         | A structured record created for `manual_review` changes, capturing the approval workflow state.        |
| Rollback Window         | The maximum time after execution within which rollback is guaranteed to be possible.                   |
| Post-Change Verification| Automated checks performed after execution to confirm the change achieved its intended outcome.        |
| CAB                     | Change Advisory Board — the human governance body for normal and emergency changes.                    |

---

## 4. Change Management Policy

### 4.1 Change Classification

All changes submitted to ANIF MUST be classified at the policy evaluation stage. The classification determines the governance path.

| Change Type | Risk Criteria                                         | Governance Path                | CAB Required |
|-------------|-------------------------------------------------------|--------------------------------|--------------|
| Standard    | Action matches pre-authorised pattern; risk score < threshold | `auto` mode; no manual review | No           |
| Normal      | Does not match pre-authorised pattern OR risk score ≥ threshold | `manual_review` or `block`   | If escalated |
| Emergency   | P0/P1 incident in progress; operator declares emergency | War-room path (ANIF-105)      | Post-hoc only|

The system MUST assign a change classification to every executed change. Classification MUST be written to the change audit record.

### 4.2 Change Request Lifecycle

All changes MUST follow the lifecycle below. Each stage MUST produce an audit record (ANIF-107).

```
Intent Submission
       │
       ▼
  ┌──────────┐
  │ Validate │  Schema check, semantic validation, change window check
  └────┬─────┘
       │ PASS
       ▼
  ┌──────────────┐
  │ Policy Check │  Policy evaluation, change classification, freeze check
  └──────┬───────┘
         │ PASS
         ▼
  ┌────────────┐
  │ Risk Score │  Numeric risk assignment (ANIF-307)
  └──────┬─────┘
         │
         ▼
  ┌────────────────────┐
  │ Governance / Gate  │  mode = auto | manual_review | block
  └──────┬─────────────┘
         │
    ┌────┴──────────────────────┐
    │ auto                      │ manual_review                        │ block
    ▼                           ▼                                      ▼
  Execute              Create Approval Ticket                    Record blocked
  immediately          Notify approver(s)                        Notify requester
                       15-min approval window
                              │
                    ┌─────────┴─────────┐
                    │ Approved          │ Rejected / Expired
                    ▼                   ▼
                  Execute            Record blocked
                                     Escalate per ANIF-105
         │
         ▼
  ┌───────────────────┐
  │ Post-Change Verify │  Automated verification checks
  └──────┬────────────┘
         │
    ┌────┴────────────┐
    │ PASS            │ FAIL
    ▼                 ▼
 Write audit      Trigger rollback
 record           Write rollback audit
 Close ticket     Create incident (ANIF-405)
```

### 4.3 Pre-Authorised Change Patterns (Standard Changes)

Standard changes MUST be defined in the standard change catalogue maintained by the policy_administrator. A standard change pattern MUST specify:

- Permitted action type(s).
- Permitted environments.
- Maximum risk score for pre-authorisation.
- Maximum scope (e.g., single segment, specific VLAN range).
- Required context fields (e.g., `environment`, `region`).
- Any mandatory constraints (e.g., `change_window: business_hours`).

#### 4.3.1 Default Standard Change Patterns

The following patterns are pre-authorised by default. Policy administrators MAY extend or restrict this list.

| Pattern ID | Action Type       | Environments     | Max Risk Score | Scope Constraint                        |
|------------|-------------------|------------------|----------------|-----------------------------------------|
| STD-001    | `apply_qos`       | non-prod         | 59             | Single segment; no production assets    |
| STD-002    | `scale_bandwidth` | non-prod         | 59             | Single connection; ≤ 50% capacity change|
| STD-003    | `apply_qos`       | prod             | 29             | Known QoS template; pre-approved profile|
| STD-004    | `scale_bandwidth` | prod             | 29             | Upscale only; pre-approved capacity plan|
| STD-005    | `reroute_traffic` | non-prod         | 49             | Pre-defined alternate path; dry-run passed|

**Note**: `isolate_segment` MUST NOT appear as a standard change pattern. It MUST always require `manual_review` (ANIF-103 §4.2).

#### 4.3.2 Standard Change Eligibility Checks

A change request MUST satisfy ALL of the following to be classified as standard:

1. Action type matches a defined standard change pattern.
2. Risk score is at or below the pattern's maximum.
3. No active change freeze applies to the environment.
4. Intent is within the declared change window (if one is configured).
5. No policy conflicts with equal precedence exist (per ANIF-105).

If any check fails, the change MUST be reclassified as normal.

### 4.4 Change Freeze Policies

4.4.1 Policy administrators MUST be able to declare change freeze periods for any environment. Freeze declarations MUST include: environment, start time, end time, and reason.

4.4.2 The ANIF pipeline MUST respect change windows and freeze periods declared as constraints in the policy store. When a change freeze is active, the pipeline MUST reject all non-emergency changes with `outcome: blocked` and `reason: change_freeze_active`.

4.4.3 During a change freeze, `manual_review` tickets MUST NOT be created for non-emergency changes. The requester MUST be notified of the freeze period and earliest permitted change time.

4.4.4 Emergency changes MAY proceed during a change freeze following the war-room path defined in ANIF-105. All emergency changes executed during a freeze MUST be flagged in the audit record and reviewed post-hoc by the policy_administrator.

4.4.5 Change window types:

| Window Type          | Description                                                              |
|----------------------|--------------------------------------------------------------------------|
| `always`             | Changes permitted at any time (default for non-prod)                     |
| `business_hours`     | Changes permitted Monday–Friday 08:00–18:00 local time                  |
| `maintenance_window` | Changes permitted only during declared maintenance windows               |
| `freeze`             | No changes permitted; emergency changes require war-room path            |

### 4.5 Rollback Requirements

4.5.1 Every change MUST have a documented rollback plan before execution commences. The rollback plan MUST be validated by the pipeline during the pre-execution check (per ANIF-103 §4.5).

4.5.2 For standard changes, rollback MUST be automated and executable without human intervention.

4.5.3 For normal changes, rollback SHOULD be automated. If rollback requires human steps, those steps MUST be documented in the approval ticket before the approver signs off.

4.5.4 For emergency changes, rollback MUST be identified and documented before the war-room approver signs off.

4.5.5 Rollback SLA: rollback MUST be initiated within 30 minutes of a failed post-change verification. Rollback MUST complete within the rollback windows defined in ANIF-103 §4.5.4.

4.5.6 Post-rollback verification MUST be executed using the same verification checks as post-change verification. If post-rollback verification fails, a P1 incident MUST be declared per ANIF-405.

### 4.6 Post-Change Verification

4.6.1 The pipeline MUST execute automated post-change verification checks after every execution. Verification MUST confirm that the intended outcome was achieved and that no unintended side-effects are detected.

4.6.2 Minimum post-change verification checks by action type:

| Action Type         | Required Verification Checks                                               |
|---------------------|----------------------------------------------------------------------------|
| `apply_qos`         | QoS policy active on target segment; traffic classification correct        |
| `scale_bandwidth`   | New bandwidth allocation confirmed; no packet loss on affected flows       |
| `reroute_traffic`   | Traffic flowing on intended path; original path traffic at expected level  |
| `isolate_segment`   | Target segment unreachable from non-isolated segments; no traffic leakage  |

4.6.3 Verification MUST complete within 5 minutes of execution completion. If verification does not complete within this window, it MUST be recorded as `failed`.

4.6.4 Verification results MUST be written to the audit record as part of the execute stage record (ANIF-107).

### 4.7 ITSM Integration and Approval Ticket Schema

4.7.1 For every change routed to `manual_review`, the pipeline MUST create an approval ticket in the ITSM system. The ticket MUST be created before the governance stage returns.

4.7.2 Approval ticket schema (all fields are mandatory):

| Field               | Type              | Description                                                           |
|---------------------|-------------------|-----------------------------------------------------------------------|
| `ticket_id`         | UUID              | Unique identifier for this approval ticket.                           |
| `intent_id`         | UUID              | The intent that triggered this ticket.                                |
| `decision_summary`  | string            | Human-readable summary of the proposed action and its context.        |
| `risk_score`        | integer (0–100)   | The risk score assigned by ANIF-307.                                  |
| `requested_by`      | string            | Identity of the operator or agent that submitted the intent.          |
| `created_at`        | ISO-8601 datetime | Timestamp of ticket creation.                                         |
| `expires_at`        | ISO-8601 datetime | Ticket expiry time; MUST be exactly 15 minutes after `created_at`.   |
| `status`            | enum              | One of: `pending`, `approved`, `rejected`, `expired`.                |
| `approver_id`       | string or null    | Identity of the approver (null until approved/rejected).              |
| `approval_notes`    | string or null    | Optional notes from the approver.                                     |
| `change_type`       | enum              | `standard`, `normal`, or `emergency`.                                 |
| `action_type`       | enum              | One of the four bounded action types.                                 |
| `environment`       | string            | Target environment (`prod`, `staging`, etc.).                         |

4.7.3 Approval tickets MUST expire after exactly 15 minutes. Expired tickets MUST have their status set to `expired` and the intent MUST be escalated per ANIF-105.

4.7.4 Approvers MUST be notified of pending tickets immediately upon creation via the escalation notification mechanism defined in ANIF-105.

4.7.5 Approval ticket records MUST be retained as part of the audit trail per ANIF-107 retention requirements.

### 4.8 Change History and Audit Trail Requirements

4.8.1 The pipeline MUST write audit records at every stage of the change lifecycle. Audit records MUST conform to the schema in ANIF-107.

4.8.2 For every change, the audit trail MUST include records for every stage executed: validate, policy, risk, decision, governance, execute (and rollback if triggered).

4.8.3 The audit record for the governance stage MUST include: change classification, governance mode assigned, ticket_id (if `manual_review`), and the policy rules that produced the classification.

4.8.4 Change history MUST be queryable per ANIF-107 query requirements: `GET /audit/{intent_id}` returns all records for the change lifecycle.

4.8.5 Audit records for changes in production environments MUST be retained for a minimum of 7 years per ANIF-106 and ANIF-107 retention requirements.

---

## 5. Conformance Requirements

5.1 Conformant implementations MUST classify every change as standard, normal, or emergency per Section 4.1.

5.2 Conformant implementations MUST create approval tickets for all `manual_review` changes using the schema defined in Section 4.7.2.

5.3 Conformant implementations MUST enforce change freeze periods and change windows. No change MUST execute during a freeze except via the emergency/war-room path.

5.4 Conformant implementations MUST execute post-change verification for every executed change and MUST trigger rollback on verification failure.

5.5 Conformant implementations MUST write audit records at every pipeline stage per ANIF-107.

5.6 Approval tickets MUST expire after exactly 15 minutes. Implementations MUST NOT permit approval of expired tickets.

5.7 `isolate_segment` MUST NOT be classified as a standard change under any circumstances.

---

## 6. Security Considerations

6.1 Approval tickets represent active authorisation grants. Ticket IDs MUST NOT be predictable or guessable. UUIDs (version 4, random) MUST be used.

6.2 The approval endpoint MUST require authentication and authorisation. Only operators with senior_engineer or policy_administrator roles MAY approve tickets.

6.3 Change freeze status MUST be readable by the pipeline but MUST NOT be writable by automation_agent roles.

6.4 The standard change catalogue represents a significant trust elevation. Additions to the catalogue MUST require policy_administrator sign-off and MUST be logged in the audit trail.

6.5 Post-change verification checks SHOULD be isolated from the change execution path to prevent a compromised execution from also compromising its own verification.

---

## 7. Operational Considerations

7.1 The standard change catalogue SHOULD be reviewed quarterly. Patterns that have not been used in 6 months SHOULD be considered for retirement.

7.2 Approval ticket expiry times (15 minutes) reflect the operational urgency of autonomous change decisions. Operators responsible for approvals MUST be reachable and responsive during operational hours.

7.3 Post-change verification failure rates SHOULD be monitored as an operational health metric. Rates above 5% SHOULD trigger a review of the change classification thresholds.

7.4 Change freeze schedules SHOULD be published to all operators at minimum 48 hours in advance except in emergency situations.

7.5 During high-traffic periods (e.g., product launches, year-end), policy administrators SHOULD pre-configure change windows to `freeze` for production environments.

---

## Appendix A: Examples

### A.1 Standard Change Execution (STD-003)

Intent: Apply pre-approved QoS template `voice-priority-v2` to segment `vlan-100` in prod.

1. Validate: schema valid; intent matches STD-003 pattern.
2. Policy Check: standard change pattern matched; no freeze active.
3. Risk Score: 22 (below STD-003 max of 29).
4. Governance: `auto` (standard change, risk within threshold).
5. Execute: QoS template applied.
6. Post-Change Verify: QoS policy confirmed active on vlan-100; no packet loss.
7. Audit: all stage records written; ITSM: auto-closed as standard change.

### A.2 Normal Change Approval Flow

Intent: Reroute traffic from `core-link-A` to `core-link-B` in prod.

1. Validate: schema valid.
2. Policy Check: does not match any standard change pattern (not in catalogue for this specific link pair).
3. Risk Score: 52.
4. Governance: `manual_review` (prod, risk 40–69).
5. Approval ticket created: ticket_id=`f47ac10b-...`, expires_at=`T+15min`.
6. Senior engineer notified.
7. Senior engineer approves at T+8min: status → `approved`.
8. Execute: traffic rerouted.
9. Post-Change Verify: traffic confirmed on core-link-B; core-link-A drain confirmed.
10. Audit: all records written; ITSM ticket closed approved.

### A.3 Approval Ticket Expiry Scenario

Intent: `isolate_segment` for `segment-42` in prod.

1. Approval ticket created at 14:00:00; expires at 14:15:00.
2. At 14:15:01: status automatically set to `expired`.
3. Escalation triggered per ANIF-105 (escalation path for expired tickets).
4. Intent re-queued for senior engineer review with escalation context.
5. Audit record written: `outcome: escalated`, `reason: ticket_expired`.

---

## Appendix B: Change History

| Version | Date       | Author             | Description          |
|---------|------------|--------------------|----------------------|
| 0.1.0   | 2026-04-07 | ANIF Working Group | Initial draft        |
