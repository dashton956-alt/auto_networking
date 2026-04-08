# ANIF-304: Risk and Trust Quantification

| Field        | Value                              |
|--------------|------------------------------------|
| Doc ID       | ANIF-304                           |
| Series       | Core                               |
| Version      | 0.1.0                              |
| Status       | Draft                              |
| Authors      | ANIF Working Group                 |
| Reviewers    | —                                  |
| Approved by  | —                                  |
| Created      | 2026-04-07                         |
| Last updated | 2026-04-07                         |
| Replaces     | N/A                                |
| Related docs | ANIF-303, ANIF-305, ANIF-600       |

---

## Abstract

This document is the normative specification for the ANIF Risk and Trust Quantification engine. It defines the risk score and trust score calculation algorithms, all contributing risk factors and their numeric weights, the threshold sets that map scores to safety decisions, and the justification format that makes every score traceable and auditable. All calculations MUST be deterministic: given identical inputs, the engine MUST always produce identical outputs.

---

## 1. Introduction

### 1.1 Purpose

To provide a complete, normative, and quantitative definition of how ANIF assesses the operational risk and trust level of an intent so that the decision engine (ANIF-305) and governance layer can act on objective, reproducible scores rather than heuristic judgement.

### 1.2 Scope

This document covers:

- The risk score and trust score definitions, ranges, and semantics.
- All risk factors, their conditions, and their numeric contributions.
- The safety decision derivation from risk and trust scores.
- The two threshold sets (production and non-production).
- The justification list format.
- Determinism requirements.
- The risk scoring result schema.

### 1.3 Out of Scope

- Policy evaluation that produces the policy result consumed as input (see ANIF-302, ANIF-303).
- Decision engine logic that consumes the risk result (see ANIF-305).
- Network state management and freshness scoring (see ANIF-307).

### 1.4 Intended Audience

- Implementers of the `/score-risk` endpoint.
- Platform architects understanding the quantitative basis for autonomous decisions.
- Governance and compliance reviewers auditing risk scoring rationale.
- Security teams verifying that risk thresholds are appropriate for their environment.

---

## 2. Normative References

- ANIF-303: Policy Conflict Resolution and Precedence
- ANIF-305: Decision Engine Specification
- ANIF-307: Distributed Source of Truth
- ANIF-600: Annexes (Schema Registry)
- RFC 2119: Key words for use in RFCs to indicate requirement levels

---

## 3. Terms and Definitions

**Risk Score**
An integer in the range 0–100 (inclusive) representing the estimated operational risk of executing the intent. 0 indicates no identified risk; 100 indicates maximum assessed risk.

**Trust Score**
An integer in the range 0–100 (inclusive) representing the system's confidence that the intent is safe to execute autonomously. 0 indicates no trust; 100 indicates full confidence.

**Safety Decision**
The binary-plus outcome derived from applying threshold logic to the risk and trust scores. One of: `allow`, `warn`, or `block`.

**Risk Factor**
A specific, identifiable property of the intent, its policy result, or the network state that contributes a defined number of points to the risk score.

**Threshold Set**
The pair of numeric thresholds that determine which safety decision applies for a given environment class (production vs non-production).

**Network State**
The canonical view of the current network condition, as provided by the Distributed Source of Truth (ANIF-307). The `network_state` field relevant to risk scoring is `status`, which is one of: `normal`, `degraded`, `critical`.

**Justification**
An ordered list of entries, each identifying a risk factor that contributed to the risk score, its numeric contribution, and its source.

---

## 4. Determinism Requirement

The risk scoring engine MUST be fully deterministic.

- Given the same intent, the same policy result (resolved policy set), and the same network state, the engine MUST always produce the same `risk_score`, `trust_score`, `safety_decision`, and `justification`.
- The engine MUST NOT incorporate any runtime-variable inputs (timestamps, random numbers, external API calls not included in the canonical state snapshot) during calculation.
- The network state used for scoring MUST be a snapshot captured before scoring begins and MUST NOT change mid-calculation.
- If any required input is unavailable (e.g., network state cannot be retrieved), the engine MUST apply defined fallback values (Section 6.6) rather than proceeding without them.

---

## 5. Risk Score and Trust Score

### 5.1 Risk Score

The risk score is an integer calculated by summing the contributions of all applicable risk factors (Section 6).

- Initial value: 0
- Each applicable risk factor adds its defined point value.
- The risk score MUST be clamped to the range [0, 100]. If the sum of all risk factors exceeds 100, the risk score MUST be recorded as 100. The score MUST NOT be negative.

### 5.2 Trust Score

The trust score is derived from the risk score and additional trust-modifying factors.

**Base formula:**
```
trust_score = 100 - risk_score
```

**Trust penalties** (applied after the base formula):

| Condition                           | Trust Penalty |
|-------------------------------------|---------------|
| `priority = critical`               | −10           |
| Any unresolved equal-precedence policy conflict exists | −15 |

Trust score MUST be clamped to the range [0, 100] after all penalties are applied. The trust score MUST NOT be negative.

### 5.3 Relationship Between Risk and Trust

Risk score and trust score are complementary but not strictly inverse when trust penalties apply. An intent may have `risk_score = 40` and `trust_score = 50` (if a −10 critical priority penalty was applied on top of the base formula). Both scores MUST appear in the result and MUST be independently justified.

---

## 6. Risk Factors (Normative)

All risk factors are normative. Implementations MUST apply every applicable factor. Factors that are not applicable (condition not met) MUST contribute 0 points and MUST still appear in the justification list with a 0 contribution.

### 6.1 Environment Weight

| Condition               | Risk Contribution | Factor ID |
|-------------------------|-------------------|-----------|
| `environment = prod`    | +30               | RF-001    |
| `environment = staging` | +10               | RF-001    |
| `environment = dev`     | +0                | RF-001    |

**Rationale:** Production environments carry higher blast radius for any action. Staging environments have moderate impact potential. Development environments are assumed isolated.

### 6.2 Priority Weight

| Condition               | Risk Contribution | Factor ID |
|-------------------------|-------------------|-----------|
| `priority = critical`   | +10               | RF-002    |
| `priority = high`       | +5                | RF-002    |
| `priority = medium`     | +0                | RF-002    |
| `priority = low`        | +0                | RF-002    |

**Note:** The `critical` priority also applies a −10 trust penalty (Section 5.2, separate from risk contribution). Risk contribution and trust penalty are independent calculations and MUST NOT be combined.

### 6.3 Policy Failure Weight

| Condition                                          | Risk Contribution | Factor ID |
|----------------------------------------------------|-------------------|-----------|
| Each policy in the resolved policy set with `deny` | +15 per denial    | RF-003    |
| Each policy in the resolved policy set with `warn` | +5 per warning    | RF-004    |

**Example:** If 2 policies produced `deny` and 1 produced `warn`, the contribution is (2 × 15) + (1 × 5) = 35.

The count of denials and warnings MUST be taken from the resolved policy set (after conflict resolution), not the raw policy results.

### 6.4 Network State Weight

| Condition                     | Risk Contribution | Factor ID |
|-------------------------------|-------------------|-----------|
| `network_state.status = degraded`  | +20          | RF-005    |
| `network_state.status = critical`  | +35          | RF-005    |
| `network_state.status = normal`    | +0           | RF-005    |

**Fallback:** If network state is unavailable, the engine MUST apply +20 (equivalent to degraded) and MUST record `"source: fallback (state unavailable)"` in the justification entry.

### 6.5 Action Type Risk Weight

The action type is sourced from the recommended action schema. If the risk engine is called before the decision engine has run (e.g., in a pre-decision risk assessment), the engine MUST use the candidate action type provided in the scoring request or apply 0 if no candidate action is specified.

| Action Type        | Risk Contribution | Factor ID |
|--------------------|-------------------|-----------|
| `isolate_segment`  | +25               | RF-006    |
| `reroute_traffic`  | +15               | RF-006    |
| `apply_qos`        | +5                | RF-006    |
| `scale_bandwidth`  | +5                | RF-006    |
| No action / null   | +0                | RF-006    |

### 6.6 Fallback Values for Missing Inputs

| Missing Input          | Fallback Value  | Additional Risk |
|------------------------|-----------------|-----------------|
| network_state.status   | degraded        | +20 (RF-005)    |
| action_type            | null            | +0 (RF-006)     |
| priority               | medium (default)| +0 (RF-002)     |
| environment            | dev (default)   | +0 (RF-001)     |

---

## 7. Safety Decision Thresholds (Normative)

The safety decision is derived by applying the threshold set appropriate to the intent's environment.

### 7.1 Production Threshold Set

Applied when `environment = prod`.

| Risk Score Range | Safety Decision |
|------------------|-----------------|
| 0 – 39           | `allow`         |
| 40 – 69          | `warn`          |
| 70 – 100         | `block`         |

### 7.2 Non-Production Threshold Set

Applied when `environment = staging` or `environment = dev` (or when environment defaults to `dev`).

| Risk Score Range | Safety Decision |
|------------------|-----------------|
| 0 – 59           | `allow`         |
| 60 – 84          | `warn`          |
| 85 – 100         | `block`         |

### 7.3 Threshold Selection Rule

The engine MUST select the threshold set based solely on the `environment` field of the validated intent (with defaults applied). The `threshold_applied` field in the result MUST record which threshold set was used: `"prod"` or `"non_prod"`.

---

## 8. Justification Format

The justification MUST be an ordered list of entries. Every risk factor (applicable and non-applicable) MUST have a corresponding entry. The list MUST be ordered by Factor ID (RF-001 through RF-006).

Each entry MUST contain:

| Field         | Type    | Description                                                           |
|---------------|---------|-----------------------------------------------------------------------|
| factor_id     | string  | The factor identifier (e.g., "RF-001").                               |
| factor_name   | string  | Human-readable name (e.g., "Environment Weight").                      |
| condition_met | boolean | Whether the factor condition was true for this intent.                 |
| contribution  | integer | Points added to risk score. 0 if condition not met.                    |
| source        | string  | Field path or source that triggered this factor (e.g., "environment: prod"). |
| note          | string  | Optional human-readable context (e.g., "fallback applied").           |

---

## 9. Risk Scoring Result Schema

The `/score-risk` endpoint MUST return a response conforming to the following structure.

```json
{
  "intent_id": "<UUID>",
  "scoring_id": "<UUID>",
  "risk_score": 55,
  "trust_score": 35,
  "safety_decision": "warn",
  "threshold_applied": "prod",
  "justification": [
    {
      "factor_id": "RF-001",
      "factor_name": "Environment Weight",
      "condition_met": true,
      "contribution": 30,
      "source": "environment: prod",
      "note": null
    },
    {
      "factor_id": "RF-002",
      "factor_name": "Priority Weight",
      "condition_met": true,
      "contribution": 10,
      "source": "priority: critical",
      "note": null
    },
    {
      "factor_id": "RF-003",
      "factor_name": "Policy Denial Weight",
      "condition_met": false,
      "contribution": 0,
      "source": "resolved_policy_set: 0 denials",
      "note": null
    },
    {
      "factor_id": "RF-004",
      "factor_name": "Policy Warning Weight",
      "condition_met": true,
      "contribution": 5,
      "source": "resolved_policy_set: 1 warning",
      "note": null
    },
    {
      "factor_id": "RF-005",
      "factor_name": "Network State Weight",
      "condition_met": true,
      "contribution": 20,
      "source": "network_state.status: degraded",
      "note": "fallback applied: network state unavailable"
    },
    {
      "factor_id": "RF-006",
      "factor_name": "Action Type Risk",
      "condition_met": false,
      "contribution": 0,
      "source": "action_type: null (pre-decision scoring)",
      "note": null
    }
  ],
  "trust_penalties": [
    {
      "reason": "priority: critical",
      "penalty": -10
    }
  ],
  "scored_at": "<ISO 8601 timestamp>"
}
```

All fields are REQUIRED. The `trust_penalties` array MAY be empty if no trust penalties apply.

---

## 10. Worked Example

**Intent:** payments-gateway, prod, priority: critical, 1 policy warning (zero_trust warn), network state: degraded, candidate action: reroute_traffic.

| Factor               | Condition            | Contribution |
|----------------------|----------------------|--------------|
| RF-001 Environment   | prod                 | +30          |
| RF-002 Priority      | critical             | +10          |
| RF-003 Policy Denial | 0 denials            | +0           |
| RF-004 Policy Warning| 1 warning            | +5           |
| RF-005 Network State | degraded             | +20          |
| RF-006 Action Type   | reroute_traffic      | +15          |
| **Total risk score** |                      | **80**       |

Trust score base: 100 − 80 = 20
Trust penalty (critical priority): −10
**Trust score: 10**

Threshold set: prod (environment = prod)
Risk score 80 ≥ 70 → **Safety decision: block**

---

## 11. Conformance Requirements

1. The risk score MUST be computed as the sum of all applicable risk factor contributions, clamped to [0, 100].
2. All six risk factors (RF-001 through RF-006) MUST be evaluated for every intent.
3. Non-applicable factors MUST contribute 0 and MUST appear in the justification.
4. The trust score MUST be derived as `100 − risk_score` minus any applicable trust penalties, clamped to [0, 100].
5. The threshold set MUST be selected based on the `environment` field; prod uses production thresholds; all other environments use non-production thresholds.
6. `threshold_applied` MUST be recorded in every result.
7. The justification list MUST contain one entry per factor, ordered by factor ID.
8. All calculations MUST be deterministic; random, time-based, or external inputs are PROHIBITED.
9. The scoring result MUST be assigned a unique `scoring_id` (UUID v4).
10. If any required input is missing, the engine MUST apply defined fallback values and MUST note the fallback in the justification.

---

## 12. Security Considerations

- Risk scores are operationally sensitive: they directly determine whether autonomous actions proceed. The `/score-risk` endpoint MUST require authentication and authorisation.
- Justification records MUST be stored immutably. Any attempt to modify a justification after the fact MUST be detected and alerted.
- The numeric weights defined in Section 6 MUST be hard-coded or stored in a tamper-evident configuration store. Runtime modification of weights MUST require a privileged operation and MUST produce an audit record.

---

## 13. Operational Considerations

- Teams deploying ANIF in high-security environments MAY wish to lower production thresholds (e.g., block at ≥50). Threshold adjustment is a governed configuration change and MUST be applied uniformly.
- Frequent `block` decisions in a `prod` environment indicate either overly conservative thresholds, a degraded network state that should be resolved, or policy configurations that add excessive risk. Teams SHOULD review contributing factors before relaxing thresholds.
- The risk score is a point-in-time calculation. An intent scored as `allow` may produce `warn` if the same intent is re-scored against a later network state. Operators SHOULD not cache risk scores beyond the current pipeline execution.

---

## Appendix A: Examples

### A.1 Low-Risk Non-Production Intent

**Intent:** dev environment, priority: medium, all policies pass, network: normal, action: apply_qos

| Factor               | Contribution |
|----------------------|--------------|
| RF-001 (dev)         | 0            |
| RF-002 (medium)      | 0            |
| RF-003 (0 denials)   | 0            |
| RF-004 (0 warnings)  | 0            |
| RF-005 (normal)      | 0            |
| RF-006 (apply_qos)   | 5            |
| **Risk score**       | **5**        |

Trust score: 100 − 5 = 95 (no penalties)
Threshold: non_prod. Score 5 < 60 → **Safety decision: allow**

### A.2 High-Risk Production Block

**Intent:** prod environment, priority: critical, 2 policy denials, network: degraded, action: isolate_segment

| Factor                      | Contribution |
|-----------------------------|--------------|
| RF-001 (prod)               | 30           |
| RF-002 (critical)           | 10           |
| RF-003 (2 × 15 = 30 denial) | 30           |
| RF-004 (0 warnings)         | 0            |
| RF-005 (degraded)           | 20           |
| RF-006 (isolate_segment)    | 25           |
| **Subtotal**                | **115 → clamped to 100** |

Trust score base: 100 − 100 = 0. Trust penalty (critical): −10 → clamped to 0.
**Risk score: 100. Trust score: 0. Safety decision: block**

---

## Appendix B: Change History

| Version | Date       | Author             | Description   |
|---------|------------|--------------------|---------------|
| 0.1.0   | 2026-04-07 | ANIF Working Group | Initial draft |
