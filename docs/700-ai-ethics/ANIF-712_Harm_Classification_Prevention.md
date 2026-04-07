# ANIF-712: Harm Classification & Prevention Policy

| Field        | Value                                              |
|--------------|----------------------------------------------------|
| Doc ID       | ANIF-712                                           |
| Series       | AI Ethics                                          |
| Version      | 0.1.0                                              |
| Status       | Draft                                              |
| Authors      | ANIF Working Group                                 |
| Reviewers    | —                                                  |
| Approved by  | —                                                  |
| Created      | 2026-04-07                                         |
| Last updated | 2026-04-07                                         |
| Replaces     | N/A                                                |
| Related docs | ANIF-704, ANIF-710, ANIF-304, ANIF-308, ANIF-721  |

---

## Abstract

This document defines the operational policy for classifying proposed actions into harm classes and applying the appropriate prevention gate before execution. It specifies the harm classification algorithm, the severity scoring formula, the prevention gate behaviour per harm class, and the mandatory audit record fields. The technical gate implementation is in ANIF-720 and ANIF-721; the harm class principles are defined in ANIF-704.

---

## 1. Introduction

### 1.1 Purpose

Harm classification must happen on every proposed action before execution. This document provides the algorithm that performs that classification, the scoring formula that quantifies potential severity, and the gate behaviour that enforces the appropriate governance posture for each harm class.

### 1.2 Scope

This document covers:

- The harm classification algorithm: inputs, logic, and outputs
- The harm severity scoring formula and its components
- Prevention gate specifications per harm class
- Rollback confirmation requirements for service harm
- Digital twin simulation requirements for cascading harm
- Mandatory audit record fields for harm classification results

### 1.3 Out of Scope

This document does not cover:

- The harm class definitions themselves (see ANIF-704)
- The technical gate placement in the pipeline (see ANIF-720)
- Digital twin simulation mechanics (see ANIF-308)
- Rollback execution mechanics (see ANIF-306)

### 1.4 Intended Audience

- AI platform engineers implementing harm classification
- Pipeline architects integrating harm gates
- Risk and compliance officers calibrating harm thresholds
- Build-time council members reviewing agent risk profiles

---

## 2. Normative References

- ANIF-704 — Harm Prevention Principles
- ANIF-304 — Risk and Trust Quantification
- ANIF-306 — Action Execution Standard
- ANIF-308 — Digital Twin and Change Validation
- ANIF-720 — Safeguard Architecture Overview
- ANIF-721 — Agent Action Constraints
- ANIF-724 — Ethics Audit Trail Requirements
- RFC 2119 — Key words for use in RFCs to indicate requirement levels

---

## 3. Terms and Definitions

**Harm classification result:** The output of the harm classification algorithm: `harm_class`, `harm_severity_score`, and `blast_radius_estimate`. These three values are the input to the prevention gate.

**Rollback window:** The maximum time within which a rollback MUST complete, as defined per environment in ANIF-306. If rollback cannot complete within this window, the action MUST be treated as potentially irreversible.

**Blast radius estimate:** The set of network segments, services, and tenants estimated to be adversely affected if the action produces its worst-case outcome. Expressed as a count of affected segments and a list of affected SLA tiers.

**Prevention gate:** The decision logic that translates a harm classification result into a governance mode override. Gates are blocking — they either pass or force a governance mode escalation.

---

## 4. Harm Classification Algorithm

### 4.1 Inputs

The algorithm receives the following inputs for each proposed action:

| Input | Source | Description |
|---|---|---|
| `action_type` | Intent | One of: reroute_traffic, apply_qos, scale_bandwidth, isolate_segment |
| `target` | Intent | The network segment, device, or service targeted |
| `environment` | Intent | prod or non_prod |
| `constraints` | Intent | Declared constraints including availability_percent, encryption, pci_compliant |
| `canonical_state` | ANIF-307 | Current authoritative network topology for the affected segments |
| `rollback_plan` | Pipeline | Rollback plan submitted with the action (ANIF-306) |
| `rollback_sla` | Configuration | Maximum allowable rollback time for this environment |

### 4.2 Classification Logic

The algorithm evaluates the following conditions in order. The first matching condition assigns the harm class:

**Step 1 — Check for cascading harm potential:**
- Does the target segment have upstream or downstream dependencies that are not explicitly included in the intent scope?
- Could the proposed action create a routing loop, congestion cascade, or security propagation path beyond the target?
- If yes to either: classify as `cascading`.

**Step 2 — Check for infrastructure harm potential:**
- Does the proposed action modify firmware, routing protocol configuration, or security group rules?
- Is the rollback plan absent or does the rollback window exceed the rollback SLA?
- Does the target segment have a declared availability commitment of 99.999% (five-nines)?
- Is the harm severity score ≥ 60 (computed in section 5 below)?
- If yes to any: classify as `infrastructure`.

**Step 3 — Check for service harm potential:**
- Does the proposed action affect one or more services with a declared SLA?
- Could the action result in throughput reduction, latency increase, or availability degradation for a declared service?
- If yes to either: classify as `service`.

**Step 4 — No harm class applies:**
- If none of the above conditions match: classify as `none`.

Multiple harm classes MAY apply to a single action. When multiple classes match, the most severe class governs: cascading > infrastructure > service > none.

### 4.3 Outputs

The algorithm produces:

| Output | Type | Description |
|---|---|---|
| `harm_class` | enum | cascading \| infrastructure \| service \| none |
| `harm_severity_score` | integer 0–100 | Computed per section 5 |
| `blast_radius_estimate` | object | `{ segment_count: integer, affected_sla_tiers: array }` |
| `classification_rationale` | string | Human-readable explanation of the classification decision |

---

## 5. Harm Severity Scoring

The harm severity score measures the magnitude of harm if the action produces adverse effects. It is computed independently of the likelihood of adverse effects.

### 5.1 Formula

```
harm_severity = impact_score × blast_radius_multiplier
```

**impact_score (0–50):**

| Highest SLA tier of affected services | impact_score |
|---|---|
| No SLA declared | 5 |
| 99.0% availability | 10 |
| 99.9% availability | 20 |
| 99.99% availability | 35 |
| 99.999% availability (five-nines) | 50 |

**blast_radius_multiplier (1.0–2.0):**

| Estimated affected segment count | multiplier |
|---|---|
| 1 segment | 1.0 |
| 2–5 segments | 1.3 |
| 6–15 segments | 1.6 |
| > 15 segments | 2.0 |

### 5.2 Threshold Override

An action with a harm severity score ≥ 60 MUST be reclassified as `infrastructure` harm regardless of the class assigned by the classification logic in section 4.2. The severity score overrides the class assignment.

An action with a harm severity score ≥ 80 MUST trigger `council_review` governance mode, escalating beyond `manual_review` to the Runtime Council (ANIF-904).

### 5.3 Score Independence

The harm severity score MUST be computed independently of the risk score defined in ANIF-304. These are separate metrics serving different purposes: risk score measures likelihood-weighted impact; harm severity score measures worst-case magnitude. Both MUST be present in the audit record.

---

## 6. Prevention Gates

### 6.1 Service Harm Gate

**Trigger:** `harm_class == service`

**Gate logic:**
1. Check rollback plan: is a confirmed rollback plan present and within the rollback SLA?
2. If yes: pass. The action proceeds to the decision engine with its risk score.
3. If no: force governance mode to `manual_review`. The action MUST NOT proceed to execution without human approval.

**Override conditions:** None. Rollback MUST be confirmed. There is no configuration that permits service harm without a confirmed rollback.

### 6.2 Infrastructure Harm Gate

**Trigger:** `harm_class == infrastructure` or `harm_severity_score ≥ 60`

**Gate logic:**
1. Force governance mode to `manual_review` unconditionally.
2. This override applies regardless of the risk score, regardless of policy configuration, and regardless of the environment (prod or non_prod).

**Override conditions:** None. Infrastructure harm always produces `manual_review`. An implementation that permits infrastructure harm to proceed without `manual_review` is non-conformant.

### 6.3 Cascading Harm Gate

**Trigger:** `harm_class == cascading`

**Gate logic:**
1. Check digital twin simulation: has a simulation been completed for this action against current canonical state (ANIF-308)?
2. If simulation is complete and results are available: include simulation results in audit record. Proceed to decision engine with simulation results attached.
3. If simulation is unavailable or returns inconclusive results: force governance mode to `manual_review`.
4. If simulation result indicates high propagation risk (defined as: three or more secondary segments affected): force governance mode to `manual_review` regardless of the primary risk score.

**Override conditions:** None. Simulation MUST complete before execution. Incomplete simulation forces `manual_review`.

### 6.4 Council Review Escalation Gate

**Trigger:** `harm_severity_score ≥ 80`

**Gate logic:**
1. Force governance mode to `council_review`.
2. Convene the Runtime Council (ANIF-904).
3. The action MUST NOT proceed until the council reaches a decision.
4. If council does not reach a decision within the time limit defined in ANIF-906: halt and escalate to human governance.

---

## 7. Audit Record Requirements

The following fields MUST be included in the audit record for every action:

| Field | Type | Required | Description |
|---|---|---|---|
| `harm_class` | enum | MUST | Classification result: cascading/infrastructure/service/none |
| `harm_severity_score` | integer 0–100 | MUST | Computed severity score |
| `blast_radius_estimate` | object | MUST | Segment count and affected SLA tiers |
| `classification_rationale` | string | MUST | Human-readable classification reasoning |
| `rollback_confirmed` | boolean | MUST if service harm | Whether rollback was confirmed before gate |
| `simulation_completed` | boolean | MUST if cascading harm | Whether digital twin simulation completed |
| `simulation_result` | object | MUST if cascading harm | Summary of simulation output |
| `gate_outcome` | enum | MUST | pass / manual_review_forced / council_review_forced |
| `gate_override_applied` | boolean | MUST | Whether severity threshold override was applied |

---

## 8. Conformance Requirements

An implementation MUST run harm classification for every proposed action before execution. Bypassing harm classification is a non-conformant configuration.

Infrastructure harm MUST always produce `manual_review`. This requirement MUST NOT be configurable.

An action with harm_severity_score ≥ 60 MUST be treated as infrastructure harm. An action with harm_severity_score ≥ 80 MUST trigger `council_review`.

Cascading harm actions MUST complete digital twin simulation before execution.

All harm classification fields MUST be written to the audit record.

---

## 9. Security Considerations

An adversary who can manipulate the inputs to the harm classification algorithm — for example, by injecting false canonical state that understates the blast radius, or by suppressing SLA metadata — can cause the algorithm to produce a lower harm class than is warranted. Canonical state integrity (ANIF-711 freshness gate) and input validation (ANIF-842) are the primary defences.

---

## 10. Operational Considerations

Harm classification thresholds (the 15-segment blast radius boundary, the five-nines impact score mapping) SHOULD be calibrated for the specific network topology. Organisations with unusually large or small segment counts may need to adjust blast radius multiplier boundaries to produce appropriate classifications.

Adjustments to harm classification thresholds MUST be reviewed by the AI Ethics Officer and approved by the governance committee before taking effect.

---

## Appendix A: Change History

| Version | Date | Author | Changes |
|---|---|---|---|
| 0.1.0 | 2026-04-07 | ANIF Working Group | Initial draft |
