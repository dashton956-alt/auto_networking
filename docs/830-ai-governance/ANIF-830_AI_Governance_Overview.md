# ANIF-830: AI Governance Overview

| Field        | Value                                              |
|--------------|----------------------------------------------------|
| Doc ID       | ANIF-830                                           |
| Series       | AI Governance                                      |
| Version      | 0.1.0                                              |
| Status       | Draft                                              |
| Authors      | ANIF Working Group                                 |
| Reviewers    | —                                                  |
| Approved by  | —                                                  |
| Created      | 2026-04-08                                         |
| Last updated | 2026-04-08                                         |
| Replaces     | N/A                                                |
| Related docs | ANIF-700, ANIF-800, ANIF-831, ANIF-900             |

---

## Abstract

This document defines the three-layer AI governance model for ANIF-conformant implementations and serves as the entry point for the ANIF-830 series. The three layers are: technical governance (ANIF-700 and ANIF-720 series), operational governance (ANIF-900 AI Council), and strategic governance (ANIF-830 series). Each layer has distinct authority, scope, and escalation obligations. When layers conflict, technical governance takes precedence unconditionally — no strategic or operational governance decision may override a technical safeguard. The ANIF-830 series addresses strategic governance: policy, risk, programme, data, reporting, roles, and compliance.

---

## 1. Introduction

### 1.1 Purpose

Autonomous operation of network infrastructure requires governance at multiple levels simultaneously. This document introduces the three-layer model and establishes the authority relationships between layers. It is the mandatory starting point for organisations implementing the ANIF-830 governance series.

### 1.2 Scope

This document covers:

- The three-layer governance model and the authority of each layer
- Escalation paths between layers
- The precedence rule for inter-layer conflicts
- The scope of each document in the ANIF-830 series

### 1.3 Out of Scope

This document does not cover:

- AI Council structure and deliberation processes (see ANIF-900)
- Ethics safeguard technical implementation (see ANIF-720–725)
- Individual governance policy content — those are defined in ANIF-831–839

### 1.4 Intended Audience

- Executive leadership and board members with AI programme oversight
- Governance committee members
- Compliance and risk officers implementing the governance framework
- Implementation teams understanding the governance context of ANIF requirements

---

## 2. Normative References

| Reference | Title |
|---|---|
| ANIF-700 | AI Ethics Framework Overview |
| ANIF-720 | Safeguard Architecture Overview |
| ANIF-800 | Agent Architecture Overview |
| ANIF-831 | AI Governance Structure and Accountability |
| ANIF-900 | AI Council Overview |
| RFC 2119 | Key words for use in RFCs to Indicate Requirement Levels |

---

## 3. Terms and Definitions

| Term | Definition |
|---|---|
| Strategic governance | Governance activities that set policy, risk appetite, programme direction, and organisational accountability |
| Operational governance | Governance activities that make real-time decisions about agent behaviour, policy interpretation, and escalated actions |
| Technical governance | Governance requirements that are enforced by code and cannot be overridden through policy or decision — the ethics safeguards and containment boundaries |
| Governance committee | The senior body responsible for strategic governance, composed of roles defined in ANIF-838 |
| AI Council | The operational governance body responsible for deliberation, decision-making, and council-level review, defined in ANIF-900 |

---

## 4. The Three-Layer Governance Model

### 4.1 Layer 1 — Technical Governance (Non-Negotiable)

Technical governance is enforced by the ANIF-700 ethics framework and ANIF-720 safeguard architecture. It operates at the code level and cannot be altered by configuration, policy decision, or council vote.

**What it controls:** ethics gate logic, containment boundaries, action constraint enforcement, ethics audit trail immutability.

**Who sets it:** the build-time council (ANIF-903), which must approve any change to safeguard code.

**Escalation:** technical governance issues escalate to the build-time council, not to the strategic governance committee or operational council.

### 4.2 Layer 2 — Operational Governance (AI Council)

Operational governance is performed by the AI Council (ANIF-900). It interprets policy, makes real-time decisions on escalated intents, reviews council-eligible actions, and monitors agent behaviour against strategic governance policy.

**What it controls:** council deliberation and voting, policy interpretation for ambiguous cases, review of agents proposed for lifecycle transitions, escalated intent approval or rejection.

**Who sets it:** the AI Council, composed per ANIF-900.

**Escalation:** unresolvable operational governance issues escalate to the governance committee (strategic governance).

### 4.3 Layer 3 — Strategic Governance (Governance Committee)

Strategic governance is performed by the governance committee. It sets the policy framework, defines risk appetite, governs the AI programme, and provides accountability to the organisation's executive and board.

**What it controls:** policy lifecycle (ANIF-833), risk management (ANIF-832), programme governance (ANIF-834), vendor and model governance (ANIF-835), data governance (ANIF-836), reporting (ANIF-837), roles (ANIF-838), compliance (ANIF-839).

**Who sets it:** the governance committee, composed per ANIF-831.

**Escalation:** strategic governance issues that require executive or board decision escalate outside the ANIF governance model to the organisation's standard executive governance processes.

---

## 5. Inter-Layer Conflict Resolution

### 5.1 Technical Governance Precedence

When a strategic or operational governance decision conflicts with a technical governance constraint, the technical governance constraint takes unconditional precedence. No governance committee resolution, council vote, or policy exception may override a technical safeguard.

This is not a failure of governance — it is the design. Technical governance represents the absolute ethical floor beneath which no autonomous system in critical infrastructure may operate, regardless of business, regulatory, or operational pressure.

### 5.2 Operational vs Strategic Conflict

When the AI Council's operational decisions appear to conflict with strategic governance policy, the matter MUST be escalated to the governance committee within 24 hours. The governance committee's interpretation MUST be recorded and used to update policy clarity. The AI Council MUST NOT continue operating in a way that contradicts governance committee direction.

---

## 6. Escalation Paths

```
Infrastructure Event
        ↓
Technical Governance (ANIF-720–725)
   — If beyond technical authority →
        ↓
AI Council (ANIF-900)
   — If beyond council authority →
        ↓
Governance Committee (ANIF-831–839)
   — If requires board or executive decision →
        ↓
Executive/Board Governance
```

---

## 7. ANIF-830 Series Document Map

| Doc ID | Title | Purpose |
|---|---|---|
| ANIF-830 | AI Governance Overview | Three-layer model entry point (this document) |
| ANIF-831 | Governance Structure and Accountability | Committee composition, quorum, accountability chain |
| ANIF-832 | AI Risk Management Framework | Risk appetite, risk register, thresholds |
| ANIF-833 | AI Policy Lifecycle Management | Policy proposal, approval, versioning, retirement |
| ANIF-834 | AI Programme Governance | Programme board, investment, milestone gates |
| ANIF-835 | AI Vendor and Model Governance | Vendor selection, model evaluation, exit strategy |
| ANIF-836 | AI Data Governance | Training data quality, lineage, retention |
| ANIF-837 | AI Governance Reporting and Metrics | Monthly reports, escalation triggers |
| ANIF-838 | AI Governance Roles and Responsibilities | CIAO, Ethics Officer, Risk Officer, DPO duties, RACI |
| ANIF-839 | AI Governance Compliance and Audit | Audit programme, evidence requirements, continuous compliance |

---

## 8. Conformance Requirements

| ID | Requirement |
|---|---|
| CR-830-01 | All ANIF deployments claiming L5 conformance MUST implement all three governance layers. |
| CR-830-02 | Technical governance constraints MUST NOT be overridden by strategic or operational governance decisions. |
| CR-830-03 | The governance committee MUST be formally chartered per ANIF-831 before Phase 1 migration begins. |
| CR-830-04 | Escalation paths between governance layers MUST be documented and tested as part of the annual DR drill. |

---

## 9. Security Considerations

Governance structures are themselves targets for manipulation. An attacker who can compromise strategic governance — for example, by obtaining governance committee credentials or manipulating committee composition — can direct policy changes that weaken operational or technical governance. Governance role assignments MUST be subject to the same identity and access controls as privileged system accounts.

---

## 10. Operational Considerations

The three-layer model requires each layer to understand its own authority boundaries. Governance committees that attempt to override technical safeguards, or AI Councils that set strategic policy, are both failure modes. Role clarity training MUST be part of onboarding for all governance participants.
