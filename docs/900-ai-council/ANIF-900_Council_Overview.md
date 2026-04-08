# ANIF-900: AI Council Overview

| Field        | Value                                              |
|--------------|----------------------------------------------------|
| Doc ID       | ANIF-900                                           |
| Series       | AI Council                                         |
| Version      | 0.1.0                                              |
| Status       | Draft                                              |
| Authors      | ANIF Working Group                                 |
| Reviewers    | —                                                  |
| Approved by  | —                                                  |
| Created      | 2026-04-08                                         |
| Last updated | 2026-04-08                                         |
| Replaces     | N/A                                                |
| Related docs | ANIF-830, ANIF-901, ANIF-902, ANIF-903, ANIF-904, ANIF-905 |

---

## Abstract

This document introduces the ANIF AI Council model: three distinct council types — Build-Time Council, Runtime Council, and Review Council — each with a defined scope, trigger, and authority. The council model provides human-governed deliberation for decisions that exceed the governance gate's automatic handling capacity. The council never executes; it governs, reviews, and advises. Execution authority remains with the pipeline (build-time decisions) or with human operators (runtime decisions). The ANIF Council model extends and formalises the GARTH-COUNCIL-001 governance pattern for autonomous network infrastructure deployments.

---

## 1. Introduction

### 1.1 Purpose

The governance gate (ANIF-301) handles the majority of intent governance automatically, routing to automatic execution, recommendation, or manual review. A subset of decisions — those with novel characteristics, high risk, or active ethics signals — require structured deliberation by a constituted body with defined seats, voting rules, and accountability. The AI Council provides that deliberation.

### 1.2 Scope

Three council types and their purposes, the council's relationship to the governance gate, the principle of non-execution, and the relationship to the GARTH-COUNCIL-001 governance pattern.

### 1.3 Out of Scope

Council composition and veto powers (see ANIF-901), mode selection logic (see ANIF-902), build-time council procedures (see ANIF-903), runtime council procedures (see ANIF-904), review council procedures (see ANIF-905), deliberation standards (see ANIF-906), council audit and accountability (see ANIF-907), and council integration with the Learning Agent (see ANIF-908).

### 1.4 Intended Audience

- AI Council seat holders understanding their roles and boundaries
- Governance committee members commissioning council governance
- Platform engineers implementing council trigger and routing logic
- Conformance assessors evaluating AI Council establishment

---

## 2. Normative References

| Reference | Title |
|---|---|
| ANIF-301 | Policy Engine and Governance Gate |
| ANIF-802 | Agent Capabilities and Permissions |
| ANIF-803 | Agent Lifecycle Management |
| ANIF-812 | Learning Agent |
| ANIF-820 | AI Agent Testing and Red-Team Standards |
| ANIF-824 | Agent Supply Chain Security |
| ANIF-830 | AI Governance Overview |
| ANIF-831 | AI Governance Structure and Accountability |
| ANIF-901 | AI Council Composition and Roles |
| ANIF-902 | Council Mode Selector |
| ANIF-903 | Build-Time Council |
| ANIF-904 | Runtime Council |
| ANIF-905 | Review Council |
| RFC 2119 | Key words for use in RFCs to Indicate Requirement Levels |

---

## 3. Council Types

The ANIF AI Council comprises three distinct council types. Each type has a defined trigger, authority scope, and mandatory output.

| Council Type | Trigger | Authority | Mandatory Output | Document |
|---|---|---|---|---|
| Build-Time Council | New agent deployment request; model version change; capability expansion | Approve, block, or conditionally approve agent for production | Deployment decision with rationale | ANIF-903 |
| Runtime Council | Governance gate routes intent to `council_review` mode | Approve, block, or defer the intent | Governance decision with rationale | ANIF-904 |
| Review Council | Severity 1 ethics incident; Level 3+ security incident | Accountability determination; policy change recommendations; learning packages | Formal review report within 72 hours | ANIF-905 |

---

## 4. The Non-Execution Principle

The AI Council MUST NOT execute actions on the network. Its authority is limited to:

- Approving or blocking agent deployments (build-time)
- Approving or blocking intent execution (runtime)
- Determining accountability and recommending policy changes (review)

Execution authority belongs to the pipeline (for approved automated actions) or to human operators (for all actions in manual mode). Council members MUST NOT issue operational commands through council governance channels. Any attempt to use council governance mechanisms to direct operational actions is a governance abuse scenario (see ANIF-848 section 6.2) and MUST be recorded as a security event.

---

## 5. Governance Gate Routing

The governance gate (ANIF-301) routes intents through one of four modes. The fourth mode — `council_review` — triggers the Runtime Council.

| Governance Mode | Handler | Council Involvement |
|---|---|---|
| `auto_execute` | Pipeline executes automatically | None |
| `recommend` | Pipeline generates recommendation for human approval | None |
| `manual_review` | Human operator reviews and decides | None |
| `council_review` | Runtime Council deliberates and decides | Runtime Council convened |

The Council Mode Selector (ANIF-902) evaluates the situation and selects the deliberation model before the Runtime Council convenes.

---

## 6. Relationship to GARTH-COUNCIL-001

The ANIF Council model extends and formalises the GARTH-COUNCIL-001 governance pattern. GARTH-COUNCIL-001 establishes the principle that autonomous systems with significant operational authority MUST have a constituted human governance body capable of structured deliberation on high-stakes decisions.

ANIF extends this pattern with:

- Three distinct council types with separate triggers and authorities
- Defined seat structure with veto powers (ANIF-901)
- A mode selector that adapts deliberation style to decision type (ANIF-902)
- Immutable council records with 10-year retention (ANIF-907)
- Feedback integration with the Learning Agent (ANIF-908)

---

## 7. Council Establishment Requirements

### 7.1 When Councils Are Required

| Conformance Level | Council Requirement |
|---|---|
| L1–L2 | No council required |
| L3 | Build-Time Council MUST be established before any agent deployment |
| L4 | Build-Time and Review Council MUST be established |
| L5 | All three council types MUST be established and operational |

### 7.2 Council Activation

A council is activated when its trigger condition is satisfied. An inactive council — one whose trigger condition has been satisfied but which has not been convened — is a conformance failure. The governance committee (ANIF-831) MUST be notified if a required council cannot be convened within 2 hours of trigger.

---

## 8. Conformance Requirements

| ID | Requirement |
|---|---|
| CR-900-01 | The Build-Time Council MUST be established before any agent is deployed to production in L3+ conformance claims. |
| CR-900-02 | The AI Council MUST NOT execute operational commands on the network. |
| CR-900-03 | L5 conformance claims MUST demonstrate all three council types are established and operational. |
| CR-900-04 | A required council that cannot be convened within 2 hours of trigger MUST be escalated to the governance committee. |

---

## 9. Security Considerations

The AI Council is a governance target. Council members with veto authority can block legitimate agent deployments and halt intents. Social engineering of council members is a threat scenario identified in ANIF-848. Council member identities MUST be verified through the organisation's privileged identity management processes before seat assignments are made. Council decision records MUST be stored with tamper-evident protection.

---

## 10. Operational Considerations

Council deliberation requires available, qualified seat holders at the time of trigger. Build-Time Council triggers are predictable (before deployment). Runtime Council triggers are not. Organisations MUST establish deputy seat policies (ANIF-901) and on-call arrangements for Runtime Council seats to ensure the council can be convened within the required timeframes under ANIF-906.
