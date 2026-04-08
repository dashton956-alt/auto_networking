# ANIF-103: Autonomous Action Policy

| Field        | Value                                                          |
|--------------|----------------------------------------------------------------|
| Doc ID       | ANIF-103                                                       |
| Series       | Governance                                                     |
| Version      | 0.1.0                                                          |
| Status       | Draft                                                          |
| Authors      | ANIF Working Group                                             |
| Reviewers    | —                                                              |
| Approved by  | —                                                              |
| Created      | 2026-04-07                                                     |
| Last updated | 2026-04-07                                                     |
| Replaces     | N/A                                                            |
| Related docs | ANIF-001, ANIF-002, ANIF-104, ANIF-305, ANIF-306, ANIF-404   |

---

## Abstract

This document is the core safety policy governing all autonomous actions within an ANIF deployment. It defines the bounded set of permitted action types, the risk and authorisation requirements for each, the environment-specific thresholds that govern autonomous versus manual execution, rollback requirements, emergency halt procedures, and the consequences of policy violation. All ANIF pipeline implementations MUST comply with this policy.

---

## 1. Introduction

### 1.1 Purpose

The Autonomous Action Policy establishes the complete operational envelope within which ANIF may act autonomously. It answers four fundamental questions:

1. **What** actions may the system take? (Section 4.1 — Bounded Action Set)
2. **Who** may authorise each action in each environment? (Section 4.2 — Authorisation Matrix)
3. **When** does the system act autonomously versus escalate? (Section 4.3 — Risk Thresholds)
4. **How** does the system undo what it has done? (Section 4.5 — Rollback Requirements)

This policy is normative. Every claim made using MUST, MUST NOT, SHOULD, SHOULD NOT, or MAY in this document constitutes a binding requirement for conformant implementations.

### 1.2 Scope

This policy applies to:

- All autonomous actions executed by ANIF, including actions triggered by automation agents.
- All environments under ANIF management: production (prod), staging, development, and test.
- All roles that submit intents or approve actions.
- All four bounded action types: `reroute_traffic`, `apply_qos`, `scale_bandwidth`, `isolate_segment`.

### 1.3 Out of Scope

- Manual network operations performed outside the ANIF pipeline.
- Infrastructure provisioning not governed by ANIF intents.
- Security operations that do not involve the four bounded action types.
- Changes made directly to network devices bypassing the ANIF pipeline.

### 1.4 Intended Audience

| Audience                | Purpose                                                                   |
|-------------------------|---------------------------------------------------------------------------|
| Policy Administrator    | Primary owner and maintainer of this policy                               |
| Compliance Officer      | Verify enforcement; audit for violations                                  |
| Senior Engineer         | Understand approval obligations and escalation triggers                   |
| Network Engineer        | Understand permitted actions and submission requirements                  |
| Automation Agent        | Mandatory operational constraint; MUST NOT operate outside this envelope  |

---

## 2. Normative References

| Reference      | Title                                                          |
|----------------|----------------------------------------------------------------|
| ANIF-001       | ANIF Constitution and Guiding Principles                       |
| ANIF-002       | ANIF Core Glossary                                             |
| ANIF-100       | Governance Overview                                            |
| ANIF-104       | Change Management Policy                                       |
| ANIF-105       | Escalation and Exception Policy                                |
| ANIF-107       | Audit Trail Requirements                                       |
| ANIF-305       | Orchestration and Cross-Domain                                 |
| ANIF-306       | Action Execution Specification                                 |
| ANIF-307       | Risk Scoring Engine                                            |
| ANIF-404       | Operational Security Controls                                  |
| RFC 2119       | Key words for use in RFCs to Indicate Requirement Levels       |

---

## 3. Terms and Definitions

| Term                | Definition                                                                                            |
|---------------------|-------------------------------------------------------------------------------------------------------|
| Bounded Action Set  | The complete, exhaustive list of action types the ANIF system is permitted to execute.                |
| Risk Score          | A numeric value (0–100) produced by the Risk Scoring Engine (ANIF-307) indicating action risk.        |
| Mode Gate           | The pipeline component that evaluates an action and assigns: `auto`, `manual_review`, or `block`.     |
| Governance Mode     | The output of the mode gate: `auto`, `manual_review`, or `block`.                                     |
| Rollback Path       | A defined, independently callable sequence of operations that reverses a completed action.            |
| Emergency Halt      | An immediate suspension of all autonomous pipeline execution, initiated by any authorised operator.   |
| Trust Score         | A measure of confidence in the intent source and context (0–100).                                     |
| Policy Violation    | Any attempt to execute an action outside the terms of this policy.                                    |

---

## 4. Autonomous Action Policy

### 4.1 Permitted Action Types (Bounded Action Set)

ANIF MUST only select actions from the following bounded set. The system MUST NOT generate, invent, or execute any action type not listed here.

| Action Type         | Risk Level | Description                                                                        | Default Governance Mode |
|---------------------|------------|------------------------------------------------------------------------------------|-------------------------|
| `reroute_traffic`   | Medium     | Redirect network traffic flows to an alternate path or interface.                  | `auto` (risk-dependent) |
| `apply_qos`         | Low        | Apply Quality of Service rules to a network segment or flow.                       | `auto`                  |
| `scale_bandwidth`   | Low        | Increase or decrease allocated bandwidth for a segment or connection.              | `auto`                  |
| `isolate_segment`   | High       | Quarantine a network segment, removing it from the active topology.                | `manual_review` (always)|

**Critical Rule**: The system MUST NOT accept, generate, or execute any action type outside this set. Any intent that resolves to an action not in this set MUST be rejected at the validation stage with outcome `blocked` and reason `action_type_not_permitted`. This rule implements P-03 (Determinism) and P-07 (Fail Safe).

### 4.2 Action Authorisation Matrix

The following matrix defines which roles may authorise each action in each environment. "Auto" indicates the system may execute without human authorisation if risk thresholds permit. "Approve" indicates a human MUST explicitly approve before execution.

| Action Type       | Environment | automation_agent | network_engineer | senior_engineer | policy_administrator |
|-------------------|-------------|-----------------|-----------------|-----------------|----------------------|
| `apply_qos`       | prod        | Auto (risk ≤ 39) | Auto            | Approve (risk ≥ 40) | Approve           |
| `apply_qos`       | non-prod    | Auto (risk ≤ 59) | Auto            | Approve (risk ≥ 60) | Approve           |
| `scale_bandwidth` | prod        | Auto (risk ≤ 39) | Auto            | Approve (risk ≥ 40) | Approve           |
| `scale_bandwidth` | non-prod    | Auto (risk ≤ 59) | Auto            | Approve (risk ≥ 60) | Approve           |
| `reroute_traffic` | prod        | Auto (risk ≤ 39) | Auto (risk ≤ 39) | Approve (risk ≥ 40) | Approve          |
| `reroute_traffic` | non-prod    | Auto (risk ≤ 59) | Auto (risk ≤ 59) | Approve (risk ≥ 60) | Approve          |
| `isolate_segment` | prod        | PROHIBITED       | Propose only     | MUST approve    | MUST approve         |
| `isolate_segment` | non-prod    | PROHIBITED       | Propose only     | MUST approve    | MUST approve         |

**Notes**:
- `isolate_segment` MUST always route to `manual_review` regardless of risk score or environment. This requirement is absolute and MUST NOT be overridden by any policy.
- automation_agent MUST NOT directly approve actions; it MAY submit intents and MAY execute approved actions.
- `PROHIBITED` means the automation_agent role is not permitted to propose `isolate_segment` actions autonomously; this MUST be initiated by a human role.

### 4.3 Risk Thresholds

Risk thresholds govern when the mode gate assigns `auto`, `manual_review`, or `block`. Thresholds MUST differ by environment because production changes carry higher operational risk.

#### 4.3.1 Production Environment Thresholds

| Risk Score Range | Governance Mode   | Description                                              |
|------------------|-------------------|----------------------------------------------------------|
| 0 – 39           | `auto`            | Execute immediately; no manual review required           |
| 40 – 69          | `manual_review`   | Requires human approval before execution                 |
| ≥ 70             | `block`           | Action MUST NOT execute; escalation to senior_engineer   |

#### 4.3.2 Non-Production Environment Thresholds

| Risk Score Range | Governance Mode   | Description                                              |
|------------------|-------------------|----------------------------------------------------------|
| 0 – 59           | `auto`            | Execute immediately; no manual review required           |
| 60 – 84          | `manual_review`   | Requires human approval before execution                 |
| ≥ 85             | `block`           | Action MUST NOT execute; notification to network_engineer|

#### 4.3.3 Threshold Override Rules

- Thresholds MUST NOT be modified at runtime by automation_agent.
- Policy administrators MAY adjust thresholds for specific action types through formal policy updates.
- Any threshold adjustment MUST be logged in the audit trail with the adjusting operator's identity.
- Threshold adjustments MUST NOT take effect until the next pipeline restart or policy reload event.

### 4.4 Mandatory Governance Gate

4.4.1 Every candidate action MUST pass through the governance mode gate before execution. The pipeline MUST NOT permit any action to reach the execute stage without a recorded governance mode assignment.

4.4.2 The governance stage MUST write an audit record before returning (per ANIF-107). The audit record MUST include the assigned governance mode and the policy rules that produced it.

4.4.3 If the governance stage fails due to a system error, the pipeline MUST fail to `block` (P-07 Fail Safe). The system MUST NOT default to `auto` on governance errors.

4.4.4 The governance mode MUST be evaluated fresh for each intent submission. Cached governance decisions MUST NOT be reused across intent submissions.

### 4.5 Rollback Requirements

4.5.1 Every action in the bounded action set MUST have a defined rollback path before execution commences. The pipeline MUST validate rollback path availability during the pre-execution check.

4.5.2 Rollback MUST be independently callable. The rollback procedure MUST be executable without re-running the full pipeline (P-01 Reversibility). A dedicated rollback endpoint MUST exist per ANIF-306.

4.5.3 The rollback definition MUST include:
- The reverse operation for the action type.
- The pre-rollback state snapshot required to perform the rollback.
- The maximum time window within which rollback is guaranteed to succeed.
- The expected verification steps after rollback completion.

4.5.4 Rollback time windows by action type:

| Action Type         | Rollback Window | Notes                                                          |
|---------------------|-----------------|----------------------------------------------------------------|
| `apply_qos`         | 24 hours        | QoS rules may be reinstated within 24 hours                    |
| `scale_bandwidth`   | 24 hours        | Bandwidth changes reversible within 24 hours                   |
| `reroute_traffic`   | 4 hours         | Original route state MUST be captured before execution         |
| `isolate_segment`   | 1 hour          | Isolation is high-impact; rapid rollback MUST be available     |

4.5.5 If rollback is not available for a candidate action, the pipeline MUST block execution and write an audit record with `outcome: blocked` and `reason: rollback_path_unavailable`.

4.5.6 Post-rollback, the pipeline MUST execute post-change verification per ANIF-104 and write a rollback audit record per ANIF-107.

### 4.6 Emergency Halt Procedures

4.6.1 Any operator with network_engineer role or higher MUST be able to initiate an emergency halt at any time. The emergency halt MUST:
- Suspend all pending `auto` mode actions.
- Cancel all `manual_review` tickets in `pending` status.
- Prevent new intents from entering the pipeline.
- Write an emergency halt audit record.

4.6.2 The emergency halt MUST take effect within 5 seconds of invocation.

4.6.3 Actions already in the execute stage when a halt is invoked MUST complete their current atomic step, then stop. Partial executions MUST trigger automatic rollback.

4.6.4 To resume pipeline operation after an emergency halt, a senior_engineer or policy_administrator MUST explicitly authorise resumption. Resumption MUST be logged in the audit trail.

4.6.5 Emergency halt MUST NOT require a reason at invocation time. The invoking operator SHOULD provide a reason, which MUST be captured if provided.

### 4.7 Prohibited Actions and Free-Form Restriction

4.7.1 The system MUST NOT generate, propose, or execute any action outside the four bounded action types defined in Section 4.1. This prohibition is absolute.

4.7.2 Any external input (intent, API call, or agent-generated suggestion) that references an action type not in the bounded set MUST be rejected immediately at the validate stage.

4.7.3 The decision stage MUST NOT use language model or generative AI capabilities to invent novel action types. It MUST only select from the bounded set.

4.7.4 Attempts to encode unsupported actions as parameters within a permitted action type (e.g., encoding a firewall rule change as a `reroute_traffic` parameter) MUST be detected during policy evaluation and rejected.

---

## 5. Conformance Requirements

5.1 Conformant implementations MUST implement and enforce the complete bounded action set defined in Section 4.1 and MUST NOT permit actions outside this set.

5.2 Conformant implementations MUST implement the authorisation matrix in Section 4.2 and MUST enforce role-based action authorisation.

5.3 Conformant implementations MUST implement environment-specific risk thresholds per Section 4.3 and MUST apply the correct thresholds based on the `environment` field of the intent.

5.4 Conformant implementations MUST implement a rollback path for every action type and MUST validate rollback availability before execution (Section 4.5).

5.5 Conformant implementations MUST implement an emergency halt mechanism accessible to network_engineer and higher roles within 5 seconds of invocation (Section 4.6).

5.6 Conformant implementations MUST fail to `block` on governance stage errors (Section 4.4.3).

5.7 `isolate_segment` MUST always require `manual_review` regardless of risk score. No policy, threshold adjustment, or configuration MAY override this requirement.

---

## 6. Security Considerations

6.1 The bounded action set is a security boundary. Any vulnerability that allows action types outside this set to execute represents a critical security failure and MUST be treated as a P0 incident.

6.2 The authorisation matrix MUST be enforced at the governance stage, not merely at the API layer. Defense-in-depth requires enforcement at multiple points.

6.3 Risk scores MUST be generated by the Risk Scoring Engine (ANIF-307) using tamper-evident inputs. Any system that allows risk scores to be externally injected or modified in transit represents a critical governance bypass vulnerability.

6.4 Emergency halt must be protected against both misuse and suppression. The halt endpoint MUST require authentication and MUST be available even when the pipeline is under load.

6.5 Rollback state snapshots MUST be stored securely and MUST NOT be accessible to automation_agent roles.

---

## 7. Operational Considerations

7.1 Policy administrators SHOULD review the authorisation matrix quarterly and update role assignments as organisational structure changes.

7.2 Risk thresholds SHOULD be calibrated based on observed incident rates and rollback frequencies. Environments with high rollback rates SHOULD prompt a review of threshold values.

7.3 The emergency halt procedure MUST be tested during scheduled maintenance windows at minimum quarterly.

7.4 Operators SHOULD monitor the proportion of actions reaching each governance mode (`auto`, `manual_review`, `block`) as an operational health metric. A significant increase in `block` or `manual_review` rates may indicate a policy configuration problem or elevated risk environment.

7.5 `isolate_segment` approvals MUST have a maximum pending time of 15 minutes (consistent with ANIF-104 approval ticket expiry). Expired tickets MUST route to senior_engineer escalation.

---

## Appendix A: Examples

### A.1 Action Selection and Governance Mode Assignment

**Scenario**: Intent to reroute traffic in production, risk score = 55.

1. Action selected: `reroute_traffic` (within bounded set — permitted).
2. Environment: `prod`.
3. Risk score: 55 (between 40 and 69).
4. Mode gate assigns: `manual_review`.
5. Approval ticket created (ANIF-104).
6. network_engineer notified; 15-minute approval window begins.
7. If approved: execute + audit. If rejected or expired: block + audit.

**Scenario**: Intent to apply QoS in staging, risk score = 30.

1. Action selected: `apply_qos` (within bounded set — permitted).
2. Environment: `staging` (non-prod).
3. Risk score: 30 (below 60).
4. Mode gate assigns: `auto`.
5. Execute immediately. Audit record written.

### A.2 Policy Violation Example

**Scenario**: Automation agent attempts to execute an undeclared action `update_firewall_rules`.

1. Validate stage: action type `update_firewall_rules` not in bounded set.
2. Rejection: `outcome: blocked`, `reason: action_type_not_permitted`.
3. Audit record written with `stage: validate`, `outcome: failure`.
4. Pipeline halts; no further stages execute.
5. Policy violation logged; compliance officer notified.

### A.3 Rollback Example

**Scenario**: `reroute_traffic` action executed in prod; post-execution verification fails.

1. Post-execution verification: fails (per ANIF-104).
2. Rollback triggered automatically within rollback window (4 hours).
3. Pre-execution route state snapshot restored.
4. Rollback audit record written with `stage: rollback`, `outcome: success`.
5. Incident created in ITSM per ANIF-405.
6. Senior_engineer notified.

---

## Appendix B: Change History

| Version | Date       | Author             | Description          |
|---------|------------|--------------------|----------------------|
| 0.1.0   | 2026-04-07 | ANIF Working Group | Initial draft        |
