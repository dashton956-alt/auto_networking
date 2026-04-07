# ANIF-700: Ethics Framework Overview

| Field        | Value                                              |
|--------------|----------------------------------------------------|
| Doc ID       | ANIF-700                                           |
| Series       | AI Ethics                                          |
| Version      | 0.1.0                                              |
| Status       | Draft                                              |
| Authors      | ANIF Working Group                                 |
| Reviewers    | —                                                  |
| Approved by  | —                                                  |
| Created      | 2026-04-07                                         |
| Last updated | 2026-04-07                                         |
| Replaces     | N/A                                                |
| Related docs | ANIF-000, ANIF-002, ANIF-701, ANIF-710, ANIF-720  |

---

## Abstract

This document is the entry point for the ANIF-700 series. It defines the three-layer ethics enforcement model — constitution, risk controls, and technical safeguards — and maps each layer to the documents that specify it in normative detail. It establishes how AI ethics extends the twelve ANIF principles defined in ANIF-002, and introduces the L5 conformance level for organisations implementing the full AI governance framework. Implementers MUST read this document before consulting any other document in the 700 series.

---

## 1. Introduction

### 1.1 Purpose

Deploying AI agents in autonomous networking environments introduces ethical obligations that go beyond the governance requirements of deterministic automation. A deterministic system does precisely what its code specifies. An AI agent reasons, infers, and selects — and in doing so, it can cause harm in ways that were not anticipated, assign resources unfairly, produce outputs that cannot be explained, and resist accountability.

The ANIF-700 series establishes the normative ethics framework that governs all AI agent behaviour within ANIF-conformant systems. It is not advisory guidance — it is a binding set of principles, policies, and technical constraints that every AI component in the system MUST satisfy.

### 1.2 Scope

This document covers:

- The three-layer ethics enforcement model and its structure
- The relationship between ethics layers and ANIF-002 principles
- The mapping of each ethics value to its enforcing documents
- The L5 conformance level introduced by the 700 series
- The reading order for the 700 series

### 1.3 Out of Scope

This document does not cover:

- The normative detail of any individual ethics value (see ANIF-701)
- Specific policy implementations (see ANIF-710–716)
- Technical safeguard specifications (see ANIF-720–725)
- Agent architecture (see ANIF-800 series)
- Governance structures (see ANIF-830 series)

### 1.4 Intended Audience

- AI platform engineers implementing ANIF-conformant agent systems
- Ethics officers and governance stakeholders reviewing the framework
- Architects designing systems that include AI components
- Auditors and compliance reviewers assessing L5 conformance

---

## 2. Normative References

- ANIF-000 — Introduction and Problem Statement
- ANIF-002 — Principles
- ANIF-701 — Ethics Constitution and Core Values
- ANIF-710 — Risk Control Overview
- ANIF-720 — Safeguard Architecture Overview
- ANIF-501 — Conformance Level Definitions
- RFC 2119 — Key words for use in RFCs to indicate requirement levels

---

## 3. Terms and Definitions

**Ethics constitution:** The set of normative values every AI agent MUST uphold, defined in ANIF-701. Values are not advisory — they are enforceable constraints.

**Risk control:** An operational policy that translates an ethics value into a binding decision-time rule. Defined in ANIF-710–716.

**Technical safeguard:** A code-enforced constraint placed at a specific point in the ANIF pipeline that blocks non-compliant actions. Defined in ANIF-720–725. Safeguards block — they do not warn and continue.

**L5 conformance:** The fifth conformance level, introduced by this series. An organisation achieves L5 by implementing the full AI governance framework (ANIF-700–725, ANIF-800–824, ANIF-900–908) on top of a verified L4 base.

---

## 4. Three-Layer Enforcement Model

The ANIF ethics framework operates in three layers. Each layer enforces the layer above it.

```
Layer 1 — Ethics Constitution (ANIF-700–705)
  WHY — the values and principles AI agents must uphold
  Defines what is right. Does not specify how to enforce it.

Layer 2 — Ethical Risk Controls (ANIF-710–716)
  WHAT — binding operational policies derived from the constitution
  Translates values into decision-time rules. Activated by specific triggers.

Layer 3 — Technical Safeguards (ANIF-720–725)
  HOW — code-enforced constraints at defined pipeline positions
  Enforces policies architecturally. Cannot be overridden by configuration.
```

A violation at Layer 3 is a safeguard failure. A violation at Layer 2 is a policy breach. A violation at Layer 1 is an ethics incident. All three trigger different response procedures. The severity increases from Layer 3 upward: a safeguard failure is detectable and recoverable; an ethics incident at Layer 1 represents a fundamental breach of the system's values.

### 4.1 Layer Independence

Each layer is independently specified and independently testable. A Layer 3 safeguard MUST function correctly regardless of whether a Layer 2 policy check preceded it. Layers are defence-in-depth — not sequential gates where passing one removes the obligation to pass the next.

### 4.2 Layer 3 Cannot Be Overridden

Technical safeguards at Layer 3 are enforced by code, not by configuration. No intent submission, policy setting, governance decision, or agent reasoning can override a Layer 3 safeguard. Modification requires a code change, which requires build-time council review (ANIF-903).

---

## 5. Extension of ANIF-002 Principles

ANIF-002 defines twelve framework principles (P-01 through P-12) that apply to all ANIF-conformant implementations. The 700 series extends these principles with AI-specific obligations. The principles are not replaced — they are strengthened.

| Principle | Statement | AI Ethics Extension |
|---|---|---|
| P-01 Reversibility | Actions MUST be reversible | AI actions involving cascading harm MUST be simulated before execution (ANIF-704, ANIF-712) |
| P-02 Auditability | Every decision MUST be auditable | AI decisions MUST include ethics audit fields: agent_id, prompt hash, fairness result, harm score (ANIF-724) |
| P-03 Determinism | Same inputs produce same outputs | Non-determinism MUST be declared. LLM agents MUST run deterministic shadows (ANIF-705, ANIF-807) |
| P-04 Explainability | Decisions MUST be explainable | LLM outputs MUST include human-readable reasoning. Confidence MUST be calibrated (ANIF-705, ANIF-713) |
| P-05 Least Privilege | Agents operate with minimum necessary authority | Agent capability scope is signed and read-only at runtime (ANIF-725, ANIF-802) |
| P-06 Human Override | Humans MUST be able to halt any action | Override endpoint is hardcoded and non-configurable. No agent may disable it (ANIF-721) |
| P-07 Fail Safe | On uncertainty, halt and escalate | Confidence below threshold MUST suppress output. Missing data MUST block decision (ANIF-713, ANIF-711) |
| P-08 Vendor Neutrality | No vendor lock-in in framework | Ethics framework applies regardless of LLM provider or agent framework (ANIF-701) |
| P-09 Incremental Adoption | Framework supports phased adoption | L5 is additive on top of L1–L4. Organisations adopt AI capabilities progressively (ANIF-823) |
| P-10 Test-First | Capabilities MUST be tested before deployment | Build-time council review required before any agent is deployed (ANIF-903, ANIF-820) |
| P-11 Data Residency | Data MUST respect declared residency constraints | AI training data MUST be processed in declared zones. PII MUST NOT persist beyond intent scope (ANIF-714) |
| P-12 Continuous Learning | Systems improve from operational experience | Learning Agent routes approved knowledge updates to relevant agents (ANIF-812). No auto-apply |

---

## 6. Ethics Value to Document Mapping

Each ethics value defined in ANIF-701 is enforced by at least one risk control and one technical safeguard. This table provides the traceability path.

| Value | Risk Control | Technical Safeguard |
|---|---|---|
| Non-maleficence | ANIF-712 Harm Classification | ANIF-721 Action Constraints |
| Beneficence | ANIF-711 Bias Detection | ANIF-723 Fairness Enforcement |
| Autonomy preservation | ANIF-715 Ethics Incident Response | ANIF-721 (hardcoded override) |
| Justice | ANIF-711 Bias Detection | ANIF-723 Fairness Enforcement |
| Transparency | ANIF-713 LLM Guardrails | ANIF-722 Output Validation |
| Proportionality | ANIF-712 Harm Classification | ANIF-721 Action Constraints |
| Reversibility | ANIF-712 Harm Classification | ANIF-725 Containment |
| Accountability | ANIF-715 Ethics Incident Response | ANIF-724 Audit Trail |
| Reproducibility | ANIF-713 LLM Guardrails | ANIF-722 Output Validation |

---

## 7. L5 Conformance Level

The ANIF-700 series introduces a fifth conformance level: **L5 — AI-Native**.

An organisation achieves L5 by implementing the full AI governance framework on top of a verified L4 base:

- ANIF-700–725: AI Ethics Framework (all seventeen documents)
- ANIF-800–824: AI Agent Architecture (all twenty-five documents)
- ANIF-900–908: AI Council Governance (all nine documents)

### 7.1 L5 Requirements

An implementation claiming L5 MUST:

- Have current, valid L4 certification before claiming L5
- Satisfy all normative requirements in ANIF-700–725, ANIF-800–824, and ANIF-900–908
- Pass third-party verification of the full AI governance framework
- Demonstrate that all Layer 3 technical safeguards are in place and cannot be bypassed
- Have completed at least one build-time council review (ANIF-903) for every deployed agent
- Have no unresolved Severity 1 ethics incidents at the time of L5 assessment

### 7.2 L5 Cannot Be Self-Declared

An implementation MUST NOT claim L5 on the basis of self-assessment. L5 requires third-party verification by a qualified certification body per ANIF-502. Self-declaration is not permitted for L5.

### 7.3 L5 Partial Compliance

An implementation MUST NOT claim L5 on the basis of implementing a subset of the required series. Partial series compliance may be declared as progress toward L5 but MUST NOT be labelled as L5 conformance.

---

## 8. Reading Order for the 700 Series

The 700 series is organised in layer order. Read Layer 1 before Layer 2; read Layer 2 before Layer 3.

**Layer 1 — Ethics Constitution (read first):**
ANIF-700 (this document) → ANIF-701 → ANIF-702 → ANIF-703 → ANIF-704 → ANIF-705

**Layer 2 — Risk Controls (read after Layer 1):**
ANIF-710 → ANIF-711 → ANIF-712 → ANIF-713 → ANIF-714 → ANIF-715 → ANIF-716

**Layer 3 — Technical Safeguards (read after Layer 2):**
ANIF-720 → ANIF-721 → ANIF-722 → ANIF-723 → ANIF-724 → ANIF-725

---

## 9. Conformance Requirements

An implementation claiming L5 MUST satisfy all normative requirements in ANIF-700–725, ANIF-800–824, and ANIF-900–908. Partial series compliance does not constitute L5 conformance.

An implementation MUST NOT claim L5 without current, valid L4 certification.

An implementation MUST NOT claim L5 on the basis of self-assessment or self-declaration.

Layer 3 technical safeguards MUST be present in any implementation that deploys AI agents, regardless of the conformance level claimed. An implementation that deploys AI agents without Layer 3 safeguards in place MUST declare this as a deviation per ANIF-504 section 4.11.

---

## 10. Security Considerations

The ethics framework is itself a security control. Agents that are constrained by ethics values are harder to exploit through adversarial inputs because their action space is bounded. The relationship between ethics constraints and security controls is detailed in ANIF-840.

---

## 11. Operational Considerations

The ethics framework SHOULD be reviewed whenever a new category of AI agent is introduced, a new action type is added to the framework, or an ethics incident reveals a gap in the current controls. Reviews SHOULD be conducted by the AI Ethics Officer (ANIF-838) with input from the Review Council (ANIF-905).

---

## Appendix A: Change History

| Version | Date | Author | Changes |
|---|---|---|---|
| 0.1.0 | 2026-04-07 | ANIF Working Group | Initial draft |
