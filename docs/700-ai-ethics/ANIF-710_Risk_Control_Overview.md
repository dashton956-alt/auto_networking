# ANIF-710: Risk Control Overview

| Field        | Value                                                                    |
|--------------|--------------------------------------------------------------------------|
| Doc ID       | ANIF-710                                                                 |
| Series       | AI Ethics                                                                |
| Version      | 0.1.0                                                                    |
| Status       | Draft                                                                    |
| Authors      | ANIF Working Group                                                       |
| Reviewers    | —                                                                        |
| Approved by  | —                                                                        |
| Created      | 2026-04-07                                                               |
| Last updated | 2026-04-07                                                               |
| Replaces     | N/A                                                                      |
| Related docs | ANIF-700, ANIF-701, ANIF-711, ANIF-712, ANIF-713, ANIF-714, ANIF-715, ANIF-716 |

---

## Abstract

This document is the entry point for Layer 2 of the ANIF ethics framework. It provides complete traceability from every ethics value defined in ANIF-701 to the operational policy that enforces it (ANIF-711–716) and the technical safeguard that constrains it at the code level (ANIF-720–725). Layer 2 translates principles into binding, decision-time operational rules. Implementers MUST read this document before consulting any other document in the ANIF-710–716 range.

---

## 1. Introduction

### 1.1 Purpose

The ethics constitution in ANIF-701 states what values agents must uphold. Layer 2 — the risk controls defined in ANIF-711 through ANIF-716 — states what operational rules enforce those values at decision time. Without Layer 2, the constitution is a statement of intent. With Layer 2, each value becomes a set of specific, testable policies that an agent either satisfies or does not.

This document maps the traceability path. For every value, it identifies the policy that enforces it and the safeguard that implements that policy architecturally.

### 1.2 Scope

This document covers:

- The principle-to-control traceability table
- The trigger conditions that activate each Layer 2 policy
- The relationship between Layer 2 policies and Layer 3 safeguards
- The reading order for ANIF-711–716

### 1.3 Out of Scope

This document does not cover:

- The normative detail of any individual risk control (see ANIF-711–716)
- Technical safeguard specifications (see ANIF-720–725)
- The ethics constitution itself (see ANIF-700–705)

### 1.4 Intended Audience

- AI platform engineers implementing the full ethics stack
- Ethics officers performing traceability reviews
- Auditors verifying that every value has an enforcing control
- Build-time council members assessing completeness of an agent's ethics compliance

---

## 2. Normative References

- ANIF-701 — Ethics Constitution and Core Values
- ANIF-711 — Bias Detection and Fairness Controls
- ANIF-712 — Harm Classification and Prevention Policy
- ANIF-713 — LLM Guardrails Policy
- ANIF-714 — Privacy and Data Ethics Policy
- ANIF-715 — Ethics Incident Response Policy
- ANIF-716 — Agent Failure and Progressive Intervention
- RFC 2119 — Key words for use in RFCs to indicate requirement levels

---

## 3. Terms and Definitions

**Risk control:** An operational policy that translates an ethics value into a binding, decision-time rule. Activated by a specific trigger condition. Defined in ANIF-711–716.

**Trigger condition:** The specific event or state that activates a risk control. Controls are not continuously running evaluations — they are activated when defined conditions are met.

**Policy activation:** The process by which a trigger condition causes a risk control to be evaluated and its output used in the pipeline decision.

**Traceability:** The ability to trace from any ethics value through its enforcing policy to its implementing safeguard, and from any safeguard back to the value it enforces. Complete traceability is a requirement for L5 conformance.

---

## 4. Principle-to-Control Traceability

Every ethics value defined in ANIF-701 MUST have at least one enforcing risk control and at least one implementing technical safeguard. The table below provides the complete traceability map.

| Value (ANIF-701) | Risk Control | Technical Safeguard |
|---|---|---|
| Non-maleficence | ANIF-712 Harm Classification and Prevention | ANIF-721 Agent Action Constraints |
| Beneficence | ANIF-711 Bias Detection and Fairness Controls | ANIF-723 Fairness Enforcement Controls |
| Autonomy preservation | ANIF-715 Ethics Incident Response | ANIF-721 (hardcoded human override) |
| Justice | ANIF-711 Bias Detection and Fairness Controls | ANIF-723 Fairness Enforcement Controls |
| Transparency | ANIF-713 LLM Guardrails Policy | ANIF-722 LLM Output Validation |
| Proportionality | ANIF-712 Harm Classification and Prevention | ANIF-721 Agent Action Constraints |
| Reversibility | ANIF-712 Harm Classification and Prevention | ANIF-725 Agent Containment |
| Accountability | ANIF-715 Ethics Incident Response | ANIF-724 Ethics Audit Trail |
| Reproducibility | ANIF-713 LLM Guardrails Policy | ANIF-722 LLM Output Validation |

An implementation MUST be able to demonstrate this traceability chain for every value. A value with no enforcing control, or a control with no implementing safeguard, is a gap that MUST be declared as a deviation per ANIF-504 section 4.11.

---

## 5. Policy Activation Triggers

Each risk control is activated by specific conditions. Controls are not passive background processes — they are triggered, evaluated, and their results written to the pipeline state.

| Risk Control | Trigger Condition | Pipeline Stage |
|---|---|---|
| ANIF-711 Bias Detection | Any action involving resource allocation across two or more services with different SLA tiers | After intent validation, before policy check |
| ANIF-712 Harm Classification | Every proposed action without exception | After risk scoring, before decision engine |
| ANIF-713 LLM Guardrails | Any pipeline stage that received input from an LLM component | Immediately after LLM output, before that output is used |
| ANIF-714 Privacy and Data Ethics | Any intent that involves telemetry collection, model training data, or PII-adjacent network data | At intent validation stage |
| ANIF-715 Ethics Incident Response | Any ethics gate failure; any Severity 1, 2, or 3 classification | At the point of classification; post-execution for drift detection |
| ANIF-716 Progressive Intervention | Any event that would constitute a strike under the four-strike model | Immediately upon qualifying event detection |

---

## 6. Coverage of Privacy and Accountability

Two values — Accountability and Privacy (implicit in Justice and Transparency) — are enforced by controls that operate across the full pipeline rather than at a single trigger point.

**Accountability (ANIF-715, ANIF-724):** The accountability chain (ANIF-702) must be complete before any action executes. The ethics audit trail requirement (ANIF-724) applies to every action involving an AI component. There is no single trigger — it is a continuous obligation.

**Privacy (ANIF-714):** The data ethics policy applies whenever network telemetry is processed for AI purposes. It is not triggered by a specific pipeline event — it governs the data handling practices of the system as a whole.

These two controls differ from the others in that their scope is the full system lifecycle, not a specific pipeline stage. Implementations MUST treat them as always-active, not as conditionally triggered.

---

## 7. Layer 2 Reading Order

ANIF-711 and ANIF-712 are the most frequently activated controls — bias and harm classification apply to the broadest set of actions. Read these first.

**Recommended reading order:**
1. ANIF-711 — Bias Detection and Fairness Controls
2. ANIF-712 — Harm Classification and Prevention Policy
3. ANIF-713 — LLM Guardrails Policy (if LLM components are in scope)
4. ANIF-714 — Privacy and Data Ethics Policy
5. ANIF-715 — Ethics Incident Response Policy
6. ANIF-716 — Agent Failure and Progressive Intervention

---

## 8. Conformance Requirements

An implementation MUST be able to demonstrate complete traceability from every ethics value in ANIF-701 to an enforcing risk control and an implementing technical safeguard.

An implementation MUST activate each risk control when its trigger condition is met. Deactivating or bypassing a risk control is a conformance violation and MUST be declared as a deviation per ANIF-504 section 4.11.

An implementation claiming L5 conformance MUST implement all six risk controls defined in ANIF-711–716 without exception.

---

## 9. Security Considerations

The traceability map is itself an audit artefact. Implementations SHOULD maintain a machine-readable version of the traceability map to support automated compliance verification. Modifications to the traceability map that remove or weaken enforcement of any value MUST be subject to build-time council review (ANIF-903).

---

## 10. Operational Considerations

When a new ethics value is proposed for addition to ANIF-701, a corresponding risk control MUST be specified in the ANIF-710 series before the value is adopted. Values without enforcing controls MUST NOT be added to the constitution — they create false assurance that the value is being upheld.

---

## Appendix A: Change History

| Version | Date | Author | Changes |
|---|---|---|---|
| 0.1.0 | 2026-04-07 | ANIF Working Group | Initial draft |
