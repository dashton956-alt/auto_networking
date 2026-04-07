# ANIF-720: Safeguard Architecture Overview

| Field        | Value                                              |
|--------------|----------------------------------------------------|
| Doc ID       | ANIF-720                                           |
| Series       | AI Ethics                                          |
| Version      | 0.1.0                                              |
| Status       | Draft                                              |
| Authors      | ANIF Working Group                                 |
| Reviewers    | —                                                  |
| Approved by  | —                                                  |
| Created      | 2026-04-07                                         |
| Last updated | 2026-04-07                                         |
| Replaces     | N/A                                                |
| Related docs | ANIF-700, ANIF-710, ANIF-721, ANIF-722, ANIF-723, ANIF-724, ANIF-725 |

---

## Abstract

This document maps the placement of all Layer 3 technical safeguards across the ANIF pipeline. Every safeguard defined in ANIF-721 through ANIF-725 blocks — it does not warn and continue. Safeguard positions are normative: repositioning a safeguard to a later pipeline stage is a conformance deviation that MUST be declared. Implementers MUST read this document before implementing any safeguard in the ANIF-720 series.

---

## 1. Introduction

### 1.1 Purpose

Layer 3 safeguards are code-enforced constraints at defined positions in the pipeline. Their effectiveness depends on their position — a safeguard placed after the action it is meant to prevent is useless. This document defines where each safeguard sits in the pipeline, why it sits there, and what happens when it fires.

### 1.2 Scope

This document covers:

- The complete annotated pipeline showing every safeguard position
- The block-only posture principle and its rationale
- Safeguard independence requirements
- The normative status of safeguard positions
- Cross-references to the individual safeguard specifications

### 1.3 Out of Scope

This document does not cover:

- The implementation detail of any individual safeguard (see ANIF-721–725)
- The risk controls that the safeguards enforce (see ANIF-710–716)
- The ethics values the risk controls serve (see ANIF-701–705)

### 1.4 Intended Audience

- Pipeline architects designing ANIF-conformant systems
- Platform engineers implementing the execution pipeline
- Auditors verifying safeguard placement
- Build-time council members assessing pipeline conformance

---

## 2. Normative References

- ANIF-721 — Agent Action Constraints
- ANIF-722 — LLM Output Validation
- ANIF-723 — Fairness Enforcement Controls
- ANIF-724 — Ethics Audit Trail Requirements
- ANIF-725 — Agent Containment and Governance Enforcement
- RFC 2119 — Key words for use in RFCs to indicate requirement levels

---

## 3. Terms and Definitions

**Safeguard position:** The defined stage in the ANIF pipeline at which a safeguard MUST operate. Positions are normative — they cannot be changed without declaring a deviation.

**Block-only posture:** A safeguard that either passes or stops the pipeline. There is no intermediate state in which a safeguard fires a warning but allows the pipeline to continue.

**Safeguard independence:** The requirement that each safeguard operates independently of the others. A failure or unavailability of one safeguard MUST NOT prevent other safeguards from running.

**Hard gate:** A safeguard whose blocking decision cannot be overridden by configuration, policy, or agent reasoning. Hard gates can only be modified through code changes reviewed by the build-time council.

---

## 4. Annotated Pipeline

The following is the complete ANIF pipeline with safeguard positions annotated. Safeguards are shown in brackets at their normative positions.

```
Intent IN
  │
  ├─► [ANIF-722] LLM Output Validation
  │     Applies if: the intent was produced or modified by an LLM component
  │     Position: immediately after LLM output, before the output is used
  │     On failure: block, route to manual_review, increment strike counter
  │
  ▼
Intent Validation
  │
  ├─► [ANIF-711] Canonical State Freshness Gate
  │     Applies if: any canonical state source contributes to the decision
  │     Position: after intent validation, before policy check
  │     On failure: block, route to manual_review
  │
  ▼
Policy Check
  │
  ├─► [ANIF-723] Fairness Enforcement Check
  │     Applies if: the action involves resource allocation across SLA tiers
  │     Position: after policy check, before risk scoring
  │     On failure: block, route to manual_review
  │
  ▼
Risk Scoring
  │
  ├─► [ANIF-712] Harm Classification Gate
  │     Applies to: every proposed action without exception
  │     Position: after risk scoring, before decision engine
  │     On infrastructure harm: force manual_review
  │     On cascading harm: require simulation before decision engine
  │     On harm_severity ≥ 80: force council_review
  │
  ▼
Decision Engine
  │
  ├─► [ANIF-721] Bounded Action Enum Check
  │     Applies to: every action type produced by the decision engine
  │     Position: immediately after decision engine output
  │     On failure: compile-time error or startup validation failure
  │
  ▼
Governance Gate
  │
  ├─► [ANIF-725] Containment Enforcement
  │     Applies to: every execute() call
  │     Position: at the execute() function signature
  │     On missing parameters: reject call, do not proceed
  │
  ▼
Action Execution
  │
  ├─► [ANIF-724] Ethics Audit Write
  │     Applies to: every action involving an AI component
  │     Position: after execution, before API response is returned
  │     Requirement: write MUST complete before response returns
  │     On write failure: hold response until write succeeds or escalate
  │
  ▼
API Response returned to caller

  │
  ▼
Audit LOG
```

---

## 5. Block-Only Posture

Every safeguard in the ANIF-720 series blocks. None produce a warning that allows the pipeline to continue.

This is a design principle, not an implementation choice. The rationale is operational: in an automated pipeline processing hundreds of intents per hour, there is no human watching each decision to act on a warning. A warning that is not acted upon provides no protection. If the safeguard fires, the action stops and a human is notified.

An implementation that converts any Layer 3 safeguard into a warning-and-continue control is non-conformant, regardless of the configuration that produced this behaviour.

---

## 6. Safeguard Independence

Each safeguard MUST operate independently. Specifically:

- A failure or exception in one safeguard MUST NOT prevent other safeguards from running
- Safeguards MUST NOT share mutable state that could cause one to affect another's result
- The unavailability of a safeguard (for example, due to a service outage) MUST cause the pipeline to fail safe — halting the intent rather than proceeding without the safeguard

An implementation that allows the pipeline to proceed when a mandatory safeguard is unavailable is non-conformant. If ANIF-722 (LLM output validation) is offline, LLM-involved intents MUST halt, not bypass the validation.

---

## 7. Normative Positions

The pipeline positions defined in section 4 are normative. An implementation MUST position each safeguard at or before its defined position — a safeguard placed later in the pipeline than its defined position provides reduced protection.

Repositioning a safeguard to a later stage is a conformance deviation and MUST be declared per ANIF-504 section 4.11 with:
- The safeguard moved
- Its defined position (from section 4)
- Its actual position in the implementation
- The justification for the repositioning
- The risk assessment of the reduced protection window

---

## 8. Hard Gates

The following safeguards are hard gates — their blocking decisions CANNOT be overridden by configuration, policy, or agent reasoning:

| Safeguard | Hard Gate Condition |
|---|---|
| ANIF-721 Bounded Action Enum | Action type not in the bounded enum |
| ANIF-721 Human Override | Override endpoint availability is unconditional |
| ANIF-712 Infrastructure Harm | manual_review is mandatory — not configurable |
| ANIF-725 Containment | execute() rejects calls with missing parameters |

Modifying a hard gate to become configurable requires a code change that MUST be reviewed by the build-time council (ANIF-903). Hard gates cannot be softened through configuration management alone.

---

## 9. Conformance Requirements

An implementation MUST position all safeguards at or before their defined pipeline positions.

A safeguard MUST NOT be implemented as a warning-and-continue control. All safeguards MUST block on failure.

When a mandatory safeguard is unavailable, the pipeline MUST halt the affected intent rather than proceeding without the safeguard.

Safeguard repositioning MUST be declared as a deviation per ANIF-504 section 4.11.

---

## 10. Security Considerations

The safeguard architecture is itself a security boundary. An adversary who can disable or reposition a safeguard can undermine the ethics framework. Build-time council review of pipeline architecture changes is the primary defence. Runtime monitoring for safeguard availability (ANIF-846) provides detection if a safeguard becomes unavailable in production.

---

## 11. Operational Considerations

Safeguard availability MUST be monitored in production. A safeguard that is unavailable but silently failing (not blocking intents as it should) is more dangerous than one that correctly halts the pipeline. Monitoring MUST verify that safeguards are actively blocking when they should, not merely that the safeguard service is running.

---

## Appendix A: Change History

| Version | Date | Author | Changes |
|---|---|---|---|
| 0.1.0 | 2026-04-07 | ANIF Working Group | Initial draft |
