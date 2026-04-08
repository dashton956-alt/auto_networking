# ANIF-809: Agent Coordination Model

| Field        | Value                                              |
|--------------|----------------------------------------------------|
| Doc ID       | ANIF-809                                           |
| Series       | AI Agent Architecture                              |
| Version      | 0.1.0                                              |
| Status       | Draft                                              |
| Authors      | ANIF Working Group                                 |
| Reviewers    | —                                                  |
| Approved by  | —                                                  |
| Created      | 2026-04-08                                         |
| Last updated | 2026-04-08                                         |
| Replaces     | N/A                                                |
| Related docs | ANIF-800, ANIF-804, ANIF-811, ANIF-901             |

---

## Abstract

This document defines the coordination model for Tier 0 agents within an ANIF-conformant implementation. Tier 0 agents coordinate the flow of intents through the agent system — prioritising, delaying, escalating, and assigning work. Tier 0 agents MUST NOT approve, execute, or override ethics constraints. All coordination actions MUST be logged. When two Tier 0 agents issue conflicting coordination signals for the same intent, the conflict MUST be escalated to the Intent Manager Agent rather than resolved silently. Coordination power is broad but bounded: Tier 0 controls the flow of work, not the substance of decisions.

---

## 1. Introduction

### 1.1 Purpose

As the number of concurrent intents in an ANIF deployment grows, a coordination layer is required to manage intent flow without introducing bottlenecks or creating single points of decision authority. This document specifies the normative model for Tier 0 coordination agents — what actions they may take, what logging is required, and how coordination conflicts are resolved.

### 1.2 Scope

This document covers:

- The permitted and prohibited coordination actions for Tier 0 agents
- Coordination action logging requirements
- The conflict resolution procedure when two Tier 0 agents issue competing signals
- The relationship between Tier 0 coordination and the Intent Lifecycle (ANIF-811)

### 1.3 Out of Scope

This document does not cover:

- Tier 0 agent types and their human counterparts (see ANIF-801)
- Inter-agent messaging protocol (see ANIF-804)
- Intent lifecycle state model (see ANIF-811)
- AI Council deliberation and escalation model (see ANIF-901)

### 1.4 Intended Audience

- AI engineers implementing Tier 0 coordination agents
- Platform architects designing multi-agent orchestration
- Governance officers reviewing coordination audit records
- Conformance assessors verifying Tier 0 capability boundaries

---

## 2. Normative References

| Reference | Title |
|---|---|
| ANIF-800 | Agent Architecture Overview |
| ANIF-801 | Agent Types, Roles and Human Counterparts |
| ANIF-804 | Agent Communication Protocol |
| ANIF-811 | Intent Lifecycle Management |
| ANIF-901 | AI Council Overview |
| RFC 2119 | Key words for use in RFCs to Indicate Requirement Levels |

---

## 3. Terms and Definitions

| Term | Definition |
|---|---|
| Tier 0 agent | A coordination-layer agent responsible for managing intent flow. Tier 0 agents do not execute network actions. |
| Coordination action | An action taken by a Tier 0 agent that modifies the state, priority, or routing of an intent in the coordination queue |
| Intent Manager Agent | The designated Tier 0 agent responsible for resolving coordination conflicts |
| Coordination signal | A message sent by a Tier 0 agent indicating a coordination action to be applied to a specific intent |
| Conflict | A condition where two Tier 0 agents issue mutually incompatible coordination signals for the same intent |

---

## 4. Permitted and Prohibited Coordination Actions

Tier 0 agents MUST only perform coordination actions from the permitted list. Tier 0 agents MUST NOT perform any prohibited action, regardless of policy configuration or intent content.

| Action | Description | Permitted? | Notes |
|---|---|---|---|
| Prioritise | Change the relative priority of a queued intent | Yes | Priority changes MUST remain within the priority bounds declared in the intent manifest |
| Delay | Hold an intent in queue pending specified conditions | Yes | Delay reason and release condition MUST be logged |
| Escalate | Route an intent to a human review queue or the AI Council | Yes | Escalation MUST include the reason code |
| Assign | Allocate an intent to a specific downstream agent | Yes | Assignment MUST be to a registered, ACTIVE agent |
| Report | Generate status, queue state, and performance reports | Yes | Reports are read-only outputs with no side effects |
| Approve | Grant governance approval to an intent or action | No | Approval authority belongs to humans and the AI Council only |
| Execute | Directly invoke a network action | No | Execution is restricted to Tier 3 agents |
| Override ethics | Bypass, disable, or modify an ethics gate | No | Ethics gates are not subject to coordination authority |
| Modify intent content | Change the substance of an intent's declared goals | No | Coordination acts on intent routing, not intent content |

### 4.1 Priority Bounds Constraint

When a Tier 0 agent prioritises an intent, the new priority MUST remain within the bounds declared in the intent's `priority_range` field. If an intent does not declare a priority range, the Tier 0 agent MUST NOT adjust its priority. Priority adjustments that would move an intent above the maximum declared priority are a conformance violation and MUST be rejected.

### 4.2 Delay Release Conditions

A delayed intent MUST specify a release condition. Permitted release condition types are:

| Release Condition Type | Description |
|---|---|
| `timestamp` | Release after a specified ISO 8601 datetime |
| `event` | Release when a specified system event is observed (e.g., maintenance window close) |
| `human_release` | Release requires explicit human action |
| `queue_depth` | Release when queue depth falls below a specified threshold |

An intent MUST NOT be held in delay indefinitely. Delays without a release condition MUST be rejected by the coordination system.

---

## 5. Coordination Action Logging

All Tier 0 coordination actions MUST be logged to the audit trail (ANIF-724). Each coordination action log entry MUST contain the following fields:

| Field | Type | Description |
|---|---|---|
| `coordination_event_id` | UUID v4 | Unique identifier for this coordination event |
| `action_type` | enum | One of: `prioritise`, `delay`, `escalate`, `assign`, `report` |
| `intent_id` | UUID v4 | The intent affected by the coordination action |
| `agent_id` | string | The Tier 0 agent issuing the coordination signal |
| `reason` | string | Free-text reason for the action |
| `previous_state` | object | The intent's coordination state before the action |
| `new_state` | object | The intent's coordination state after the action |
| `timestamp` | ISO 8601 | Time the coordination action was applied |

The `reason` field MUST be populated. Coordination actions with empty reason fields MUST be rejected.

---

## 6. Coordination Conflict Resolution

### 6.1 Conflict Definition

A coordination conflict occurs when two Tier 0 agents issue mutually incompatible signals for the same intent within a single coordination cycle. Examples of incompatible signals include:

- One agent signals `prioritise` (raise priority) and another signals `delay`
- Two agents signal `assign` to different downstream agents
- One agent signals `escalate` and another signals `assign` to a non-escalation path

### 6.2 Conflict Resolution Procedure

When a coordination conflict is detected:

1. Both conflicting coordination signals MUST be held — neither signal MUST execute pending resolution.
2. The conflict MUST be escalated to the Intent Manager Agent within 5 seconds of detection.
3. The Intent Manager Agent MUST evaluate the conflict and issue a single authoritative coordination signal within 30 seconds.
4. The winning signal MUST be applied. The losing signal MUST be logged as `cancelled` with the cancellation reason citing the Intent Manager Agent's decision.
5. The full conflict event — both signals, the escalation, and the resolution — MUST be logged as a single coordination conflict record in the audit trail.

### 6.3 Intent Manager Agent Requirements

The Intent Manager Agent MUST be:

- A registered Tier 0 agent with `role: intent_manager` in its manifest
- A singleton — only one Intent Manager Agent MUST be active at any time in a deployment
- Assigned exclusive authority for conflict resolution — no other agent MUST issue coordination signals during a pending conflict on the same intent

If the Intent Manager Agent is unavailable when a conflict is detected, the intent MUST be escalated to the human-in-loop queue (ANIF-404) and both conflicting signals MUST remain held until human resolution.

### 6.4 Repeated Conflicts

If the same intent experiences three or more coordination conflicts within its lifecycle, this MUST be treated as an indicator of policy misconfiguration. The intent MUST be escalated to the AI Council (ANIF-901) for review. Repeated conflicts on the same intent class — defined as the same `intent_type` experiencing conflicts at a rate above 5% of instances — MUST be reported to governance within 24 hours.

---

## 7. Conformance Requirements

| ID | Requirement |
|---|---|
| CR-809-01 | Tier 0 agents MUST NOT be granted approval, execute, or ethics override capabilities. |
| CR-809-02 | These capabilities MUST be absent from Tier 0 agent manifests. |
| CR-809-03 | Priority adjustments MUST remain within the intent's declared priority bounds. |
| CR-809-04 | Delay actions MUST specify a valid release condition. Indefinite delays MUST be rejected. |
| CR-809-05 | All coordination actions MUST be logged with all fields defined in section 5. |
| CR-809-06 | Coordination actions with empty `reason` fields MUST be rejected. |
| CR-809-07 | When a coordination conflict is detected, both signals MUST be held pending resolution. |
| CR-809-08 | Conflicts MUST be escalated to the Intent Manager Agent within 5 seconds. |
| CR-809-09 | The Intent Manager Agent MUST resolve conflicts within 30 seconds. |
| CR-809-10 | Only one Intent Manager Agent MUST be active at any time. |
| CR-809-11 | If the Intent Manager Agent is unavailable, conflicting intents MUST be escalated to the human-in-loop queue. |
| CR-809-12 | Three or more conflicts on a single intent MUST trigger AI Council escalation. |

---

## 8. Security Considerations

Coordination authority is a form of indirect influence over intent execution. A compromised Tier 0 agent cannot execute network actions directly, but can delay, misdirect, or suppress intents — effectively creating a denial-of-coordination attack. Coordination action logs MUST be monitored for anomalous patterns: unusually high delay rates, repeated escalations to slow queues, or systematic assignment of intents to degraded agents are all indicators of coordination manipulation.

The Intent Manager Agent is a high-value target: compromising it allows an attacker to control conflict resolution outcomes. The Intent Manager Agent MUST be subject to the same hardening requirements as Tier 3 agents, including cryptographic identity verification (ANIF-843) and supply chain integrity checks (ANIF-824).

---

## 9. Operational Considerations

Coordination conflict rates are a useful operational metric. A healthy deployment will have a near-zero conflict rate. Conflicts indicate overlapping policy scopes or misconfigured agent assignments. Operators SHOULD alert on conflict rates above 1% and treat sustained conflict rates as a policy review trigger rather than a normal operational condition.

The Intent Manager Agent SHOULD be monitored with dedicated health checks separate from the standard agent health signal (ANIF-806). Because it is a singleton, its unavailability has system-wide impact on conflict resolution.
