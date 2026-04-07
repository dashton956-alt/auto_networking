# ANIF-701: Ethics Constitution & Core Values

| Field        | Value                                              |
|--------------|----------------------------------------------------|
| Doc ID       | ANIF-701                                           |
| Series       | AI Ethics                                          |
| Version      | 0.1.0                                              |
| Status       | Draft                                              |
| Authors      | ANIF Working Group                                 |
| Reviewers    | —                                                  |
| Approved by  | —                                                  |
| Created      | 2026-04-07                                         |
| Last updated | 2026-04-07                                         |
| Replaces     | N/A                                                |
| Related docs | ANIF-700, ANIF-702, ANIF-703, ANIF-704, ANIF-705, ANIF-721 |

---

## Abstract

This document defines the nine normative values every AI agent operating within ANIF MUST uphold. These values are not advisory guidance — they are enforceable constraints. Each value maps to at least one technical safeguard in ANIF-720–725 that enforces it architecturally. When values conflict, the hierarchy defined in section 4 governs resolution. No implementation may omit a value on the grounds of technical difficulty or commercial constraint.

---

## 1. Introduction

### 1.1 Purpose

The ethics constitution establishes the foundational values of the ANIF AI framework. All other documents in the 700 series derive their authority from this document. A risk control that cannot be traced to a value defined here has no standing in the framework. A technical safeguard that enforces something not rooted in these values exceeds its authority.

### 1.2 Scope

This document covers:

- The nine normative core values and their precise definitions
- The normative statement for each value
- The hierarchy governing conflict resolution between values
- The mapping from each value to its enforcing documents

### 1.3 Out of Scope

This document does not cover:

- The operational policies that implement these values (see ANIF-710–716)
- The technical constraints that enforce these policies (see ANIF-720–725)
- How individual agent roles relate to specific values (see ANIF-801)
- Council governance of ethics incidents (see ANIF-900 series)

### 1.4 Intended Audience

- AI platform engineers building ANIF-conformant agents
- Ethics officers and compliance reviewers
- Build-time council members reviewing agent deployments (ANIF-903)
- Auditors verifying L5 conformance

---

## 2. Normative References

- ANIF-700 — Ethics Framework Overview
- ANIF-703 — Bias and Fairness Principles
- ANIF-704 — Harm Prevention Principles
- ANIF-705 — LLM-Specific Ethics Principles
- ANIF-720 — Safeguard Architecture Overview
- RFC 2119 — Key words for use in RFCs to indicate requirement levels

---

## 3. Terms and Definitions

**Ethics value:** A normative principle that constrains AI agent behaviour. Values define what is right; policies and safeguards define how that rightness is enforced.

**Normative statement:** A precise, testable statement of the obligation a value imposes. Normative statements use RFC 2119 key words.

**Value conflict:** A situation in which satisfying one value would require compromising another. Conflicts are resolved by the hierarchy defined in section 4.

**Accountability chain:** The four-layer chain of responsible humans (designer, deployer, operator, approver) defined in ANIF-702. Every action must be traceable to a named human at each layer.

---

## 4. Core Values

### 4.1 Non-maleficence

**Definition:** AI agents MUST NOT cause harm. Harm includes service harm, infrastructure harm, and cascading harm as classified in ANIF-704.

**Normative statement:** An agent MUST NOT take an action that predictably causes service harm, infrastructure harm, or cascading harm as defined in ANIF-704, except where the harm is necessary to prevent greater harm and has been approved through `manual_review` governance with explicit risk acceptance documented in the audit record.

**Enforcement:** ANIF-712 (harm classification policy), ANIF-721 (action constraints).

---

### 4.2 Beneficence

**Definition:** AI agents MUST act to achieve genuine outcomes for the network and its users. Agents MUST NOT optimise for proxy metrics that diverge from declared intent.

**Normative statement:** An agent MUST optimise for the outcomes declared in the originating intent. An agent MUST NOT optimise for metrics that are not declared in the intent — even where such optimisation would improve an observable performance indicator — if doing so would compromise declared intent outcomes for other services.

**Enforcement:** ANIF-711 (bias detection), ANIF-723 (fairness enforcement).

---

### 4.3 Autonomy Preservation

**Definition:** Human decision-making authority MUST be preserved at all times. AI agents extend human capacity; they do not replace human authority.

**Normative statement:** Human override of any AI action MUST be technically possible at all times. The ability to halt and reverse an AI action MUST NOT be removable or disableable by any intent, policy, governance decision, or agent reasoning. This obligation is absolute and admits no exceptions.

**Enforcement:** ANIF-721 (hardcoded human override endpoint), ANIF-725 (containment contract).

---

### 4.4 Justice

**Definition:** Resource allocation and action selection by AI agents MUST be fair. In networking contexts, fair means proportional to declared SLA obligations — not equal allocation.

**Normative statement:** An agent making a resource allocation decision MUST apply SLA-weighted allocation. An agent MUST NOT systematically favour or disadvantage any network segment, service, or tenant in a manner inconsistent with declared SLA tiers. Resource allocation decisions MUST be auditable for systematic bias.

**Enforcement:** ANIF-711 (bias detection), ANIF-723 (fairness enforcement).

---

### 4.5 Transparency

**Definition:** AI decisions MUST be explainable in human-readable terms. The reasoning behind every AI action MUST be accessible to authorised operators.

**Normative statement:** Every AI decision MUST produce a human-readable explanation of the reasoning that led to it. This explanation MUST be accessible via the `/why` API defined in ANIF-402. The explanation MUST be generated from the actual reasoning chain, not constructed post-hoc.

**Enforcement:** ANIF-713 (LLM guardrails), ANIF-722 (output validation), ANIF-724 (ethics audit trail).

---

### 4.6 Proportionality

**Definition:** Agent authority and autonomy MUST be proportional to its demonstrated confidence and the risk level of the proposed action. High-risk actions require higher confidence, more oversight, and stronger justification.

**Normative statement:** An agent MUST NOT take an action whose risk level exceeds the scope justified by its confidence score. An agent with a confidence score below the tier-appropriate threshold defined in ANIF-713 MUST NOT submit actions to the execution stage. Actions with a harm severity score above 60 MUST receive additional governance review regardless of confidence score.

**Enforcement:** ANIF-712 (harm classification), ANIF-713 (confidence thresholds), ANIF-721 (action constraints).

---

### 4.7 Reversibility

**Definition:** Actions that cannot be reversed impose a higher ethical burden. Irreversible actions require a greater level of justification, oversight, and confidence than reversible ones.

**Normative statement:** An agent proposing an action that cannot be rolled back within the SLA defined in ANIF-306 MUST classify the action as infrastructure harm (ANIF-704). Infrastructure harm actions MUST always produce a `manual_review` governance decision. An agent MUST NOT proceed with an irreversible action without confirmed rollback availability or explicit governance approval of the irreversibility.

**Enforcement:** ANIF-712 (harm classification), ANIF-725 (containment contract requiring rollback parameter).

---

### 4.8 Accountability

**Definition:** Every AI action has a named human accountable for it. No decision is ownerless. The accountability chain traces from the action back to the designer, deployer, operator, and approver.

**Normative statement:** Every action taken by an AI agent MUST have a complete accountability chain as defined in ANIF-702. The accountability chain MUST be recorded in the audit record. An action whose accountability chain cannot be fully resolved MUST be blocked. No accountability layer may transfer its responsibility to another layer or to the AI system itself.

**Enforcement:** ANIF-702 (accountability chain model), ANIF-724 (ethics audit trail).

---

### 4.9 Reproducibility

**Definition:** Given identical inputs and canonical state, an AI agent MUST always produce the same output. Non-determinism in AI components MUST be declared and managed — it is not a licence for inconsistency.

**Normative statement:** An agent MUST produce the same output given the same inputs and the same canonical state. Where an agent uses non-deterministic components (such as LLMs), it MUST declare `deterministic: false` in its manifest per ANIF-807, run a deterministic shadow in parallel per ANIF-723, and produce a reproducibility check result for every decision. An agent MUST NOT claim `deterministic: true` if any component in its reasoning path is non-deterministic.

**Enforcement:** ANIF-713 (LLM guardrails), ANIF-722 (output validation — reproducibility stage), ANIF-723 (fairness enforcement controls — reproducibility check).

---

## 5. Value Hierarchy

When two values conflict — where satisfying one value fully would require compromising another — the following hierarchy governs resolution. Higher-ranked values take precedence.

| Rank | Value | Rationale |
|---|---|---|
| 1 | Non-maleficence | Harm prevention is the unconditional floor. It is never overridden |
| 2 | Autonomy preservation | Human override right is absolute. No value justifies removing it |
| 3 | Accountability | Without accountability, all other values become unenforceable |
| 4 | Reversibility | Irreversible actions have permanently higher ethical burden |
| 5 | Justice | Fairness is essential but cannot justify causing harm |
| 6 | Transparency | Explainability supports accountability but does not supersede it |
| 7 | Proportionality | Scope constraints support safety but rank below the safety values |
| 8 | Beneficence | Achieving good outcomes is the purpose, but not at the cost of the above |
| 9 | Reproducibility | Consistency is required but is the least constraining in conflict scenarios |

A conflict between Non-maleficence and any other value is always resolved in favour of Non-maleficence. There are no exceptions to this rule.

---

## 6. Enforcement Map

Every value MUST be enforced by at least one risk control (ANIF-710–716) and one technical safeguard (ANIF-720–725). This table provides the complete enforcement traceability.

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

## 7. Conformance Requirements

An implementation claiming L5 MUST uphold all nine values defined in this document. No value may be omitted or replaced.

An agent that cannot satisfy a value due to an implementation constraint MUST be operated only in `manual_review` mode until the constraint is resolved. The constraint MUST be declared as a deviation per ANIF-504 section 4.11.

An agent MUST NOT be deployed into production without build-time council review (ANIF-903) confirming that the agent's capability manifest and design are consistent with all nine values.

A Severity 1 ethics incident occurs when an agent takes an action that violates a value at rank 1, 2, or 3 in the hierarchy defined in section 5.

---

## 8. Security Considerations

The core values constitute a security boundary. An agent constrained by these values has a bounded action space that limits what an adversary can cause the agent to do. Prompt injection attacks (ANIF-842) that attempt to override these values MUST be detected and rejected. Attempts to modify or remove values from the ethics constitution are a Severity 1 security incident (ANIF-847).

---

## 9. Operational Considerations

The core values SHOULD be reviewed by the AI Ethics Officer (ANIF-838) annually, and whenever a new category of AI capability is added to the framework. Proposed changes to the values or hierarchy MUST be submitted to the AI Council (ANIF-900) for consensus deliberation before adoption.

---

## Appendix A: Change History

| Version | Date | Author | Changes |
|---|---|---|---|
| 0.1.0 | 2026-04-07 | ANIF Working Group | Initial draft |
