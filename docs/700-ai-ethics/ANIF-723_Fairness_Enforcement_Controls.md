# ANIF-723: Fairness Enforcement Controls

| Field        | Value                                              |
|--------------|----------------------------------------------------|
| Doc ID       | ANIF-723                                           |
| Series       | AI Ethics                                          |
| Version      | 0.1.0                                              |
| Status       | Draft                                              |
| Authors      | ANIF Working Group                                 |
| Reviewers    | —                                                  |
| Approved by  | —                                                  |
| Created      | 2026-04-07                                         |
| Last updated | 2026-04-07                                         |
| Replaces     | N/A                                                |
| Related docs | ANIF-703, ANIF-711, ANIF-720                       |

---

## Abstract

This document specifies three technical checks enforcing fairness at decision time: the SLA floor allocation check, the ground truth freshness gate, and the reproducibility check. These controls implement the fairness obligations defined in ANIF-703 and the bias detection policy in ANIF-711 at the code level. All three checks are blocking — failure routes to `manual_review`. The reproducibility check MUST run for every Tier 3 decision without exception.

---

## 1. Introduction

### 1.1 Purpose

Fairness must be enforced at the point of decision, not merely detected after the fact. This document specifies the three technical controls that enforce fairness during execution — before the action proceeds. Each control is independent and MUST run regardless of whether the others pass.

### 1.2 Scope

This document covers:

- SLA floor allocation check: specification, computation, and failure handling
- Ground truth freshness gate: threshold, enforcement, and logging
- Reproducibility check: parallel computation requirement, tolerance, and divergence handling

### 1.3 Out of Scope

This document does not cover:

- Fairness principles and definitions (see ANIF-703)
- Bias detection methods (see ANIF-711)
- The pipeline position of these checks (see ANIF-720)

### 1.4 Intended Audience

- Platform engineers implementing fairness checks
- AI engineers designing resource allocation agents
- Build-time council members verifying fairness control implementation

---

## 2. Normative References

- ANIF-703 — Bias and Fairness Principles
- ANIF-711 — Bias Detection and Fairness Controls
- ANIF-720 — Safeguard Architecture Overview
- ANIF-724 — Ethics Audit Trail Requirements
- RFC 2119 — Key words for use in RFCs to indicate requirement levels

---

## 3. Terms and Definitions

**SLA floor:** The minimum resource allocation a service MUST receive. Defined as 80% of the declared `availability_percent` constraint for that service.

**Post-action projection:** A computation of the expected resource allocation state for all affected services after the proposed action executes. Used to check whether any service would fall below its SLA floor.

**Deterministic shadow:** A deterministic computation running in parallel with an AI agent that produces the same type of output using rule-based logic. Used in the reproducibility check.

**Divergence tolerance:** The maximum acceptable difference between the AI output and the deterministic shadow output. If the divergence exceeds the tolerance, the AI output is suppressed.

---

## 4. Check 1 — SLA Floor Allocation Check

### 4.1 Purpose

Prevents resource allocation actions that would cause any service to fall below its SLA floor, regardless of whether the overall action is beneficial in aggregate.

### 4.2 Applicability

This check MUST run for every action of type `reroute_traffic`, `apply_qos`, or `scale_bandwidth` that affects two or more services with declared SLA tiers.

### 4.3 Computation

1. Identify all services affected by the proposed action
2. For each affected service, retrieve the declared `availability_percent` constraint
3. Compute the SLA floor for each service: `sla_floor = availability_percent × 0.80`
4. Project the post-action resource allocation for each service (the expected allocation after the action executes)
5. Compare: `projected_allocation ≥ sla_floor` for every affected service

### 4.4 Pass Condition

Every affected service has a projected post-action allocation at or above its SLA floor.

### 4.5 Failure Condition

Any affected service has a projected post-action allocation below its SLA floor.

### 4.6 Failure Actions

1. Block the action
2. Route to `manual_review`
3. Log: the failing service, its SLA floor, the projected allocation, the deficit
4. Do NOT increment the strike counter — the check working correctly is not an agent failure

### 4.7 Services Without Declared SLA

Services without a declared `availability_percent` constraint have no SLA floor and are exempt from this check. An implementation MUST NOT apply a default SLA floor to services that have not explicitly declared one.

---

## 5. Check 2 — Ground Truth Freshness Gate

### 5.1 Purpose

Prevents decisions made on stale canonical state from producing unfair outcomes. Stale data means the fairness check is evaluating a network state that may no longer be accurate.

### 5.2 Threshold

Every canonical state source contributing to a fairness decision MUST have a freshness score ≥ 0.7. This is a stricter threshold than the general freshness gate in ANIF-711 (which requires ≥ 0.6). The stricter threshold applies specifically to fairness-relevant decisions.

### 5.3 Source Identification

The fairness gate MUST identify which canonical state sources contributed data to the SLA floor allocation check in check 1. Only sources that contributed data to the check are subject to the freshness threshold.

### 5.4 Pass Condition

All canonical state sources that contributed data to check 1 have freshness scores ≥ 0.7.

### 5.5 Failure Condition

Any contributing canonical state source has a freshness score below 0.7, or there are insufficient fresh sources to complete a full assessment.

### 5.6 Failure Actions

1. Block the action
2. Route to `manual_review`
3. Log: the source with low freshness, its score, the threshold, the intent_id
4. Flag the stale source to the data governance function (ANIF-836) for investigation

### 5.7 Non-Configurable Threshold

The 0.7 freshness threshold for fairness decisions MUST NOT be lowered by configuration. An organisation MAY configure a stricter threshold for specific high-criticality environments.

---

## 6. Check 3 — Reproducibility Check

### 6.1 Purpose

Verifies that the AI agent's decision output is consistent with what a deterministic computation would produce for the same inputs. Enforces the Reproducibility value from ANIF-701 at the point of execution.

### 6.2 Applicability

The reproducibility check MUST run for every Tier 3 decision agent output. It is not optional and MUST NOT be disabled for cost or latency reasons.

### 6.3 Deterministic Shadow Requirement

Every Tier 3 decision agent MUST have a deterministic shadow (ANIF-807). The shadow runs in parallel and computes the same type of output using rule-based logic. The reproducibility check compares the AI output against the shadow output.

### 6.4 Pass Condition

The AI output and the deterministic shadow output are within the declared divergence tolerance for the agent. The tolerance MUST be declared in the agent manifest. Acceptable tolerances vary by action type:

| Action Type | Maximum Divergence Tolerance |
|---|---|
| reroute_traffic | Target path within 2 hops of shadow recommendation |
| apply_qos | QoS marking within one DSCP class of shadow recommendation |
| scale_bandwidth | Bandwidth target within 10% of shadow recommendation |
| isolate_segment | Exact segment match — no tolerance permitted |

### 6.5 Failure Conditions

Either of the following constitutes a reproducibility failure:

- The AI output and shadow output diverge beyond the declared tolerance for the action type
- The deterministic shadow is unavailable or returns an error

### 6.6 Failure Actions

**Divergence beyond tolerance:**
1. Suppress the AI output
2. If the deterministic shadow output satisfies all policy and risk constraints: use the shadow output and log the substitution
3. If the shadow output does not satisfy constraints or is itself uncertain: route to `manual_review`
4. Log: the AI output, the shadow output, the divergence measure, the tolerance, the action taken

**Shadow unavailable:**
1. Block the action — do NOT proceed without the shadow
2. Route to `manual_review`
3. Log: shadow unavailability reason, intent_id, timestamp
4. This is a Severity 2 ethics condition if the shadow is unavailable for more than 10 minutes

### 6.7 Deterministic Shadow as Fallback

Where the shadow output is used as a substitution for a suppressed AI output, the substitution MUST be transparent in the audit record and in the response to the caller. The caller MUST be informed that the action was taken using the deterministic shadow, not the AI output.

---

## 7. Audit Record Fields

The following fields MUST be written to the ethics audit record (ANIF-724) for every fairness check:

| Field | Type | Description |
|---|---|---|
| `sla_floor_check_result` | enum: pass/fail/not_applicable | Result of check 1 |
| `sla_floor_failing_service` | string | Service that failed check 1, if applicable |
| `sla_floor_deficit` | float | How far below the floor the projection was |
| `freshness_gate_result` | enum: pass/fail | Result of check 2 |
| `freshness_gate_failing_source` | string | Source that failed check 2, if applicable |
| `reproducibility_check_result` | enum: pass/fail/shadow_used/shadow_unavailable | Result of check 3 |
| `ai_output_divergence` | float | Measured divergence from shadow |
| `shadow_substitution_applied` | boolean | Whether shadow was used in place of AI output |

---

## 8. Conformance Requirements

The SLA floor allocation check MUST run for every multi-service resource allocation action.

The ground truth freshness gate for fairness MUST use a threshold of ≥ 0.7. This threshold MUST NOT be lowered.

The reproducibility check MUST run for every Tier 3 decision. Disabling the reproducibility check for cost or latency reasons is a conformance violation.

A Tier 3 agent without a deterministic shadow MUST NOT be deployed.

---

## 9. Security Considerations

The reproducibility check limits the damage an adversarially manipulated LLM can do. Even if a prompt injection causes the LLM to recommend an action outside normal parameters, the reproducibility check will detect the divergence from the deterministic shadow and suppress the manipulated output. The shadow becomes a ground truth reference that is harder to manipulate than the LLM itself.

---

## 10. Operational Considerations

Divergence tolerances SHOULD be calibrated during the initial deployment period by observing normal AI-to-shadow divergence under expected operating conditions. Tolerances set too tight will cause excessive `manual_review` routing; tolerances set too loose will fail to catch meaningful deviations. The AI Ethics Officer SHOULD review tolerance calibration at 30 and 90 days post-deployment.

---

## Appendix A: Change History

| Version | Date | Author | Changes |
|---|---|---|---|
| 0.1.0 | 2026-04-07 | ANIF Working Group | Initial draft |
