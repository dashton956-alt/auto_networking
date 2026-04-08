# ANIF-902: Council Mode Selector

| Field        | Value                                              |
|--------------|----------------------------------------------------|
| Doc ID       | ANIF-902                                           |
| Series       | AI Council                                         |
| Version      | 0.1.0                                              |
| Status       | Draft                                              |
| Authors      | ANIF Working Group                                 |
| Reviewers    | —                                                  |
| Approved by  | —                                                  |
| Created      | 2026-04-08                                         |
| Last updated | 2026-04-08                                         |
| Replaces     | N/A                                                |
| Related docs | ANIF-900, ANIF-901, ANIF-903, ANIF-904, ANIF-905, ANIF-906 |

---

## Abstract

This document defines the Council Mode Selector: a deterministic evaluation process that selects the appropriate deliberation model before any council convenes. Six input factors — reversibility, risk score, ethics flags, time pressure, novelty of situation, and agent strike history — are evaluated against a decision matrix to produce one of four deliberation model selections: consensus, majority, weighted, or adversarial. The mode selection rationale MUST be logged in the council record before deliberation begins. The Mode Selector is itself a deterministic component; it MUST NOT use LLM inference to select the deliberation model.

---

## 1. Introduction

### 1.1 Purpose

Different decisions require different deliberation styles. A novel, ethics-flagged decision requires the full consensus model with all seats. A time-critical reversible decision can be handled under majority rules with fewer procedural requirements. Applying the same deliberation model to every decision creates either unnecessary overhead for routine cases or insufficient rigour for high-stakes cases. The Mode Selector resolves this by evaluating each decision's characteristics and selecting the appropriate model.

### 1.2 Scope

Six input factors, the decision matrix for mode selection, and the logging requirement for mode selection rationale.

### 1.3 Out of Scope

Deliberation time limits and voting procedures for each model (see ANIF-906), council composition and quorum requirements (see ANIF-901), Build-Time Council procedures (see ANIF-903), Runtime Council procedures (see ANIF-904), Review Council procedures (see ANIF-905).

### 1.4 Intended Audience

- Platform engineers implementing the Mode Selector agent
- Council seat holders understanding how their deliberation model was selected
- Governance committee members reviewing mode selection decisions
- Conformance assessors verifying Mode Selector implementation

---

## 2. Normative References

| Reference | Title |
|---|---|
| ANIF-803 | Agent Lifecycle Management |
| ANIF-841 | AI Threat Model |
| ANIF-900 | AI Council Overview |
| ANIF-901 | AI Council Composition and Roles |
| ANIF-906 | Council Deliberation Standards |
| ANIF-907 | Council Audit and Accountability |
| RFC 2119 | Key words for use in RFCs to Indicate Requirement Levels |

---

## 3. Input Factors

The Mode Selector evaluates six input factors for each council decision. All six factors MUST be evaluated. No factor may be skipped.

| Factor | Definition | Values |
|---|---|---|
| Reversibility | Whether the action or decision can be undone if the outcome is wrong | `reversible` / `partially_reversible` / `irreversible` |
| Risk score | The risk score associated with the intent or agent decision | Numeric: 0–100 |
| Ethics flag | Whether an active ethics signal is present | `present` / `absent` |
| Time pressure | Whether the decision must be reached within a constrained window | `critical` (< 15 min) / `elevated` (< 60 min) / `normal` |
| Novelty | Whether the decision has a precedent in council records or episodic memory | `novel` (no precedent) / `precedented` |
| Strike history | Whether the agent or capability under review has an active or historical ethics strike record | `active_strike` / `historical_strike` / `none` |

---

## 4. Mode Selection Decision Matrix

The Mode Selector evaluates factors in priority order. The first matching rule determines the deliberation model. Rules are evaluated top to bottom; the first match applies.

| Priority | Condition | Deliberation Model Selected |
|---|---|---|
| 1 | `ethics_flag = present` | Consensus |
| 2 | `strike_history = active_strike` | Adversarial |
| 3 | `irreversible = true` AND `risk_score ≥ 70` | Consensus |
| 4 | `novelty = novel` AND `risk_score ≥ 50` | Adversarial |
| 5 | `time_pressure = critical` AND `reversibility = reversible` | Majority |
| 6 | `risk_score ≥ 80` | Weighted |
| 7 | `strike_history = historical_strike` | Weighted |
| 8 | `irreversible = true` | Weighted |
| 9 | All other cases | Majority |

### 4.1 Tie-Breaking

No ties are possible in the decision matrix — rules are ordered and the first match applies. If two conditions in the same rule are simultaneously met (e.g., ethics flag present AND active strike), the higher-priority rule (the ethics flag rule, priority 1) applies.

### 4.2 Override Prohibition

The selected deliberation model MUST NOT be overridden by a council seat holder or the governance committee after mode selection is complete. If a seat holder believes the wrong model has been selected, the objection MUST be recorded in the council record and the Mode Selector evaluation MUST be reviewed, but deliberation MUST proceed under the selected model unless the Mode Selector evaluation is demonstrated to have used incorrect input values.

---

## 5. Mode Selection Logging

The Mode Selector MUST record the following in the council record (ANIF-907) before deliberation begins:

| Field | Content |
|---|---|
| `input_reversibility` | Value assessed |
| `input_risk_score` | Numeric value |
| `input_ethics_flag` | `present` or `absent` |
| `input_time_pressure` | Value assessed |
| `input_novelty` | Value assessed |
| `input_strike_history` | Value assessed |
| `rule_matched` | Priority number of the matching rule |
| `mode_selected` | The deliberation model selected |
| `mode_selector_timestamp` | ISO 8601 timestamp of selection |

This record is immutable once written. Deliberation MUST NOT begin until the mode selection record is written.

---

## 6. Implementation Requirements

The Mode Selector MUST be implemented as a deterministic component. It MUST NOT use LLM inference for any part of the evaluation. Mode selection MUST produce the same output for the same input values every time. Non-deterministic mode selection is a conformance violation.

The Mode Selector MUST be subject to build-time council review (ANIF-903) as part of the governance platform deployment. Changes to the Mode Selector decision matrix require build-time council approval and a new council record documenting the change.

---

## 7. Conformance Requirements

| ID | Requirement |
|---|---|
| CR-902-01 | The Mode Selector MUST evaluate all six input factors for every council decision. |
| CR-902-02 | The Mode Selector MUST be deterministic; LLM inference MUST NOT be used in mode selection. |
| CR-902-03 | The mode selection rationale MUST be logged in the council record before deliberation begins. |
| CR-902-04 | The selected deliberation model MUST NOT be overridden after mode selection is complete. |
| CR-902-05 | Changes to the Mode Selector decision matrix MUST be approved by the Build-Time Council. |

---

## 8. Security Considerations

The Mode Selector is a governance target. Manipulating input values — specifically the ethics flag or risk score — can influence the deliberation model selected, potentially downgrading a decision from consensus to majority and reducing the rigour of the review. Input values MUST be sourced from tamper-evident audit records and the governance gate output, not from the intent submitter or the agent under review. Any discrepancy between Mode Selector input values and governance gate records MUST be treated as a potential manipulation attempt and escalated as a Level 2 security event (ANIF-847).

---

## 9. Operational Considerations

The Mode Selector runs before council members are notified. Its output determines the quorum requirement (ANIF-901) and therefore which seat holders must be available. The mode selection output MUST be included in the council convening notification so that seat holders know immediately which deliberation model applies and can plan their availability accordingly.
