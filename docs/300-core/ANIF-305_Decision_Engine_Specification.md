# ANIF-305: Decision Engine Specification

| Field        | Value                              |
|--------------|------------------------------------|
| Doc ID       | ANIF-305                           |
| Series       | Core                               |
| Version      | 0.1.0                              |
| Status       | Draft                              |
| Authors      | ANIF Working Group                 |
| Reviewers    | —                                  |
| Approved by  | —                                  |
| Created      | 2026-04-07                         |
| Last updated | 2026-04-07                         |
| Replaces     | N/A                                |
| Related docs | ANIF-304, ANIF-306, ANIF-404       |

---

## Abstract

This document is the normative specification for the ANIF Decision Engine. The decision engine takes the validated intent, the resolved policy set, and the risk scoring result as inputs, and produces a single bounded action recommendation with a full reasoning chain, a governance mode, and a mandatory rollback plan. The decision engine MUST ONLY select from four predefined action types; free-form action generation is PROHIBITED. All decision logic MUST be deterministic and traceable.

---

## 1. Introduction

### 1.1 Purpose

To define, normatively and completely, the rules by which the ANIF Decision Engine maps intent characteristics and risk assessments to specific, bounded, reversible actions, and to specify the structure of the decision output that governance and execution layers depend on.

### 1.2 Scope

This document covers:

- The bounded action type constraint and the prohibition on free-form generation.
- The complete decision tree, expressed as normative rules.
- The governance mode determination rules.
- The recommended action output schema.
- The rollback plan requirement.
- The reasoning chain format.
- Audit requirements for every decision.

### 1.3 Out of Scope

- Risk scoring algorithms that produce the safety_decision input (see ANIF-304).
- Governance approval mechanics for manual_review mode (see ANIF-100 series).
- Execution mechanics for the recommended action (see ANIF-306).
- Digital twin simulation consulted before execution (see ANIF-308).

### 1.4 Intended Audience

- Implementers of the `/decide` endpoint.
- Governance stakeholders reviewing decision logic for compliance.
- Platform architects integrating the decision engine into the pipeline.
- Security reviewers verifying bounded execution constraints.

---

## 2. Normative References

- ANIF-304: Risk and Trust Quantification
- ANIF-306: Action Execution Standard
- ANIF-404: Audit Log Specification
- RFC 2119: Key words for use in RFCs to indicate requirement levels

---

## 3. Terms and Definitions

**Bounded Action**
An action drawn exclusively from the four predefined action types: `reroute_traffic`, `apply_qos`, `scale_bandwidth`, `isolate_segment`. No other action types are permitted.

**Decision**
The complete output of the decision engine: a recommended action (or null), a governance mode, a confidence score, a risk level, a reasoning chain, and a rollback plan.

**Governance Mode**
The operational mode that controls whether execution may proceed autonomously. One of: `auto`, `manual_review`, `block`.

**Reasoning Chain**
An ordered list of decision steps documenting, in sequence, every rule applied by the engine and the rationale for each step. The chain terminates at the final action selection or null output.

**Rollback Plan**
A structured description of the steps required to reverse the recommended action. REQUIRED for every non-null recommended action.

**Confidence Score**
An integer in the range 0–100 indicating the engine's assessed confidence that the recommended action will satisfy the intent's objectives.

---

## 4. Bounded Action Constraint

The decision engine MUST ONLY select from the following four predefined action types:

| Action Type        | Description                                              |
|--------------------|----------------------------------------------------------|
| `reroute_traffic`  | Redirect traffic flows to alternative paths or nodes.   |
| `apply_qos`        | Apply quality-of-service policies to traffic flows.     |
| `scale_bandwidth`  | Increase or decrease allocated bandwidth for a segment. |
| `isolate_segment`  | Isolate a network segment to prevent spread of a fault. |

**Free-form action generation is PROHIBITED.** The engine MUST NOT generate, infer, or return any action type outside this set. Any mechanism that would allow the engine to dynamically generate action types or parameters not covered by these four types MUST NOT be implemented.

If none of the four action types is appropriate for the intent (e.g., the safety decision is `block`), the engine MUST return `recommended_action: null`.

---

## 5. Decision Tree (Normative)

The decision tree is a sequence of rules evaluated in the order listed. The engine MUST evaluate all applicable rules in the order defined. The first applicable terminal rule that produces a `mode = block` result terminates the chain. For non-block outcomes, all rules MUST be evaluated before the final action is selected.

### 5.1 Rule Set

**Rule D-001: Block on safety_decision = block**
- Condition: `safety_decision = block`
- Effect: `mode = block`, `recommended_action = null`
- This is a terminal rule. No further rules are evaluated.
- Rationale: Risk/trust assessment has determined execution is unsafe.

**Rule D-002: Manual review on safety_decision = warn**
- Condition: `safety_decision = warn`
- Effect: `mode = manual_review`
- This is NOT terminal; action selection continues.
- Rationale: Risk is elevated; human oversight is required before execution.

**Rule D-003: Manual review on equal-precedence conflict**
- Condition: `policy_result.conflicts` contains any entry with `resolution_type = escalated`
- Effect: `mode = manual_review`
- This rule applies in addition to, not instead of, D-002.
- Rationale: Unresolved policy conflict requires human adjudication.

**Rule D-004: High-availability + low-latency → reroute_traffic**
- Condition: `objectives.availability_percent >= 99.99` AND `objectives.latency_ms <= 50`
- Effect: Prefer `reroute_traffic` as recommended action.
- Rationale: These combined requirements indicate a topology-level response is needed.

**Rule D-005: Latency-primary concern → apply_qos**
- Condition: `objectives.latency_ms` is present AND NOT (`objectives.availability_percent >= 99.99` AND `objectives.latency_ms <= 50`)
- Effect: Prefer `apply_qos` as recommended action.
- Rationale: When latency is the primary concern and D-004 does not apply, QoS is the appropriate response.

**Rule D-006: Degraded network → prefer reroute_traffic over scale_bandwidth**
- Condition: `network_state.status = degraded`
- Effect: If both `reroute_traffic` and `scale_bandwidth` are candidates, `reroute_traffic` MUST be selected.
- Rationale: Scaling bandwidth on a degraded network is ineffective; rerouting avoids the degraded segment.

**Rule D-007: isolate_segment → always manual_review**
- Condition: `recommended_action = isolate_segment`
- Effect: `mode = manual_review` (REGARDLESS of risk score or safety_decision)
- Rationale: Segment isolation is a high-impact action with significant blast radius; autonomous execution is PROHIBITED.
- This rule MUST be applied after the action type is selected.

**Rule D-008: safety_decision = allow → auto mode (default)**
- Condition: `safety_decision = allow` AND no other rule has set `mode = manual_review` or `mode = block`
- Effect: `mode = auto`
- Rationale: Risk/trust assessment permits autonomous execution.

### 5.2 Rule Evaluation Order and Mode Precedence

Rules are evaluated in numeric order (D-001 through D-008). Mode escalation is additive and MUST NOT be downgraded:

- `block` can only be set by D-001 and MUST NOT be overridden.
- `manual_review` can be set by D-002, D-003, or D-007 and MUST NOT be downgraded to `auto`.
- `auto` applies only if no rule has set a higher mode.

### 5.3 Action Selection Priority

When multiple rules nominate different action types, priority is resolved as follows:

1. D-001 block: no action (null).
2. D-004 (availability + latency): `reroute_traffic`.
3. D-005 (latency primary): `apply_qos`.
4. D-006 (degraded network override): `reroute_traffic` over `scale_bandwidth`.
5. Default fallback (no specific rule matches): `apply_qos` (lowest risk action).

---

## 6. Recommended Action Schema

The `/decide` endpoint MUST return a response conforming to the following structure.

```json
{
  "intent_id": "<UUID>",
  "decision_id": "<UUID>",
  "recommended_action": {
    "action_type": "reroute_traffic | apply_qos | scale_bandwidth | isolate_segment | null",
    "parameters": {},
    "risk_level": "low | medium | high"
  },
  "confidence_score": 0,
  "mode": "auto | manual_review | block",
  "reasoning_chain": [
    {
      "step": 1,
      "rule_id": "D-001",
      "condition_evaluated": "<human-readable condition>",
      "condition_met": false,
      "outcome": "<what happened as a result>",
      "rationale": "<why this rule exists>"
    }
  ],
  "rollback_plan": {
    "action_type": "<reverse action type>",
    "description": "<human-readable description of rollback steps>",
    "estimated_duration_ms": 0,
    "preconditions": ["<list of conditions that must hold before rollback>"]
  },
  "decided_at": "<ISO 8601 timestamp>"
}
```

**Field requirements:**

| Field              | Required         | Notes                                                               |
|--------------------|------------------|---------------------------------------------------------------------|
| intent_id          | Always           | The intent this decision was made for.                              |
| decision_id        | Always           | UUID v4, assigned by the engine.                                    |
| recommended_action | Always           | `null` when mode is `block`.                                        |
| confidence_score   | Always           | 0 when mode is `block`.                                             |
| mode               | Always           | One of `auto`, `manual_review`, `block`.                            |
| reasoning_chain    | Always           | MUST contain one entry per evaluated rule.                          |
| rollback_plan      | When action ≠ null | REQUIRED for all non-null recommended actions. MUST be null when action is null. |
| decided_at         | Always           | ISO 8601 timestamp.                                                 |

### 6.1 Risk Level Assignment

The `risk_level` field in `recommended_action` MUST be set according to the following mapping:

| Action Type       | Risk Level |
|-------------------|------------|
| reroute_traffic   | medium     |
| apply_qos         | low        |
| scale_bandwidth   | low        |
| isolate_segment   | high       |

### 6.2 Confidence Score Calculation

The confidence score MUST reflect the engine's assessed probability that the recommended action will achieve the intent's objectives.

| Condition                                    | Confidence Score   |
|----------------------------------------------|--------------------|
| `mode = block`                               | 0                  |
| `mode = manual_review` (pre-approval)        | Computed (see below)|
| `mode = auto`                                | Computed (see below)|

**Confidence base value by action type:**

| Action Type       | Base Confidence |
|-------------------|-----------------|
| apply_qos         | 80              |
| reroute_traffic   | 75              |
| scale_bandwidth   | 70              |
| isolate_segment   | 60              |

**Confidence adjustments:**

| Condition                           | Adjustment |
|-------------------------------------|------------|
| `safety_decision = allow`           | +10        |
| `safety_decision = warn`            | −10        |
| `network_state.status = degraded`   | −15        |
| All policies pass (no denials/warns)| +10        |
| Any policy warning present          | −5         |

Confidence score MUST be clamped to [0, 100].

---

## 7. Rollback Plan Requirement

A rollback plan MUST be present in the decision output for every non-null recommended action. The rollback plan MUST be independently executable via `POST /rollback/{intent_id}` without requiring the original decision context (see ANIF-306).

The rollback plan MUST include:

- `action_type`: The type of action required to reverse the recommended action (MAY be the same type with inverse parameters).
- `description`: A human-readable description of the rollback steps sufficient for a network engineer to execute manually if needed.
- `estimated_duration_ms`: Estimated time to complete rollback.
- `preconditions`: A list of conditions that MUST hold before rollback can be safely executed (MAY be empty).

**Example rollback plan for reroute_traffic:**
```json
{
  "action_type": "reroute_traffic",
  "description": "Restore original traffic routing by reverting routing table entries to pre-action state. Re-advertise original BGP prefixes from primary path.",
  "estimated_duration_ms": 5000,
  "preconditions": [
    "Original path must be reachable",
    "No active sessions on the new path that would be disrupted"
  ]
}
```

---

## 8. Reasoning Chain Format

The reasoning chain MUST be an ordered list of decision steps. Every rule in Section 5.1 (D-001 through D-008) MUST appear in the reasoning chain, whether or not its condition was met. The chain MUST be ordered by rule ID.

Each step MUST contain:

| Field               | Type    | Description                                              |
|---------------------|---------|----------------------------------------------------------|
| step                | integer | Sequential step number (1-based).                        |
| rule_id             | string  | Rule identifier (e.g., "D-001").                         |
| condition_evaluated | string  | Human-readable description of the condition tested.      |
| condition_met       | boolean | Whether the condition was true for this intent.           |
| outcome             | string  | What the engine did as a result (even if nothing).        |
| rationale           | string  | Why this rule exists and why the outcome is appropriate.  |

---

## 9. Audit Requirements

- Every call to `/decide` MUST produce an audit record, regardless of the outcome.
- The audit record MUST include the full `decision_id`, `intent_id`, `mode`, `recommended_action`, `confidence_score`, `reasoning_chain`, and `decided_at`.
- Audit records for decisions MUST be written before the result is returned to the caller, to ensure no decision escapes the audit trail.
- The audit record MUST be immutable after creation.

---

## 10. Conformance Requirements

1. The engine MUST ONLY return action types from the four permitted action types; all other outputs are PROHIBITED.
2. All decision tree rules D-001 through D-008 MUST be evaluated in order for every call.
3. `mode = block` MUST be terminal; no action is selected and the chain stops.
4. `mode = manual_review` MUST NOT be downgraded to `auto` by any subsequent rule.
5. `isolate_segment` MUST always produce `mode = manual_review` (rule D-007), regardless of risk score.
6. A rollback plan MUST be present for every non-null recommended action and MUST be null for null actions.
7. The reasoning chain MUST contain one entry per rule.
8. The decision MUST be audited on every call before the result is returned.
9. The engine MUST be deterministic: identical inputs MUST always produce identical outputs.
10. A `decision_id` (UUID v4) MUST be assigned by the engine on every call.

---

## 11. Security Considerations

- Decision outputs directly determine whether autonomous network changes are executed. The `/decide` endpoint MUST require authentication and MUST be protected from replay attacks (e.g., by validating that the `intent_id` and `scoring_id` match a current, un-decided pipeline state).
- The reasoning chain MUST NOT be modifiable after creation; it forms part of the non-repudiation record.
- Rollback plans are operationally sensitive. They MAY be included in restricted audit views accessible only to authorised operators.

---

## 12. Operational Considerations

- Teams SHOULD monitor the distribution of `mode` outputs (auto vs manual_review vs block) to assess the health of the pipeline. A sudden increase in `block` outcomes indicates either infrastructure degradation or a policy configuration change.
- Decision engine logic (the rule set in Section 5) is versioned. Any change to the rule set MUST produce a new version of this specification and MUST be deployed as a coordinated release with the governance team.
- The default fallback action (`apply_qos`) is the lowest-risk action type and is appropriate as a conservative default. Teams operating in zero-tolerance environments MAY configure the default to `null` (no autonomous action).

---

## Appendix A: Examples

### A.1 Full Decision — Auto Mode, Reroute Traffic

**Input:** prod, priority: critical, availability_percent: 99.99, latency_ms: 45, safety_decision: allow, network: normal.

```json
{
  "intent_id": "f3a9b2c1-4d7e-4f88-9012-abcdef012345",
  "decision_id": "d9e8f7a6-0001-4abc-b000-ccccdddd0001",
  "recommended_action": {
    "action_type": "reroute_traffic",
    "parameters": {},
    "risk_level": "medium"
  },
  "confidence_score": 80,
  "mode": "auto",
  "reasoning_chain": [
    {
      "step": 1,
      "rule_id": "D-001",
      "condition_evaluated": "safety_decision = block",
      "condition_met": false,
      "outcome": "No block applied",
      "rationale": "Safety decision is allow; block rule does not apply"
    },
    {
      "step": 2,
      "rule_id": "D-002",
      "condition_evaluated": "safety_decision = warn",
      "condition_met": false,
      "outcome": "manual_review not set by this rule",
      "rationale": "Safety decision is allow; warn rule does not apply"
    },
    {
      "step": 4,
      "rule_id": "D-004",
      "condition_evaluated": "availability_percent >= 99.99 AND latency_ms <= 50",
      "condition_met": true,
      "outcome": "Preferred action set to reroute_traffic",
      "rationale": "High availability and low latency requirements indicate topology-level response"
    },
    {
      "step": 8,
      "rule_id": "D-008",
      "condition_evaluated": "safety_decision = allow AND no manual_review/block mode",
      "condition_met": true,
      "outcome": "mode set to auto",
      "rationale": "Risk assessment permits autonomous execution"
    }
  ],
  "rollback_plan": {
    "action_type": "reroute_traffic",
    "description": "Restore original routing table state by reverting all routing changes made during execution.",
    "estimated_duration_ms": 5000,
    "preconditions": ["Original path must be reachable"]
  },
  "decided_at": "2026-04-07T10:00:03Z"
}
```

### A.2 Block Decision

**Input:** prod, safety_decision: block.

```json
{
  "intent_id": "aabbccdd-0000-4abc-8000-000011112222",
  "decision_id": "d9e8f7a6-0002-4abc-b000-ccccdddd0002",
  "recommended_action": null,
  "confidence_score": 0,
  "mode": "block",
  "reasoning_chain": [
    {
      "step": 1,
      "rule_id": "D-001",
      "condition_evaluated": "safety_decision = block",
      "condition_met": true,
      "outcome": "mode set to block; recommended_action set to null; chain terminated",
      "rationale": "Risk/trust assessment has determined execution is unsafe"
    }
  ],
  "rollback_plan": null,
  "decided_at": "2026-04-07T10:00:03Z"
}
```

### A.3 Isolate Segment — Always Manual Review

**Input:** prod, priority: high, safety_decision: allow, selected action: isolate_segment.

```json
{
  "mode": "manual_review",
  "recommended_action": {
    "action_type": "isolate_segment",
    "risk_level": "high"
  },
  "reasoning_chain": [
    {
      "step": 7,
      "rule_id": "D-007",
      "condition_evaluated": "recommended_action = isolate_segment",
      "condition_met": true,
      "outcome": "mode escalated to manual_review",
      "rationale": "Segment isolation has significant blast radius; autonomous execution is prohibited"
    }
  ]
}
```

---

## Appendix B: Change History

| Version | Date       | Author             | Description   |
|---------|------------|--------------------|---------------|
| 0.1.0   | 2026-04-07 | ANIF Working Group | Initial draft |
