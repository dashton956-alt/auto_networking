# ANIF-838: AI Governance Roles and Responsibilities

| Field        | Value                                              |
|--------------|----------------------------------------------------|
| Doc ID       | ANIF-838                                           |
| Series       | AI Governance                                      |
| Version      | 0.1.0                                              |
| Status       | Draft                                              |
| Authors      | ANIF Working Group                                 |
| Reviewers    | —                                                  |
| Approved by  | —                                                  |
| Created      | 2026-04-08                                         |
| Last updated | 2026-04-08                                         |
| Replaces     | N/A                                                |
| Related docs | ANIF-004, ANIF-830, ANIF-831, ANIF-900             |

---

## Abstract

This document defines four AI-specific governance roles — Chief AI Officer, AI Ethics Officer, AI Risk Officer, and the AI-specific duties of the Data Protection Officer — and provides a RACI matrix covering all governance activities. Each role has defined accountabilities, authorities, and AI Council seat assignments. These roles extend the general roles defined in ANIF-004 with AI-specific responsibilities that do not exist in conventional network operations governance.

---

## 1. Introduction

### 1.1 Purpose

AI governance requires roles with defined, non-overlapping accountabilities. Without role clarity, governance activities fall into gaps or are duplicated without coordination. This document specifies the four new roles introduced by ANIF governance, their responsibilities, and their positions in the governance committee and AI Council.

### 1.2 Scope

Four AI governance roles, their responsibilities and authorities, AI Council seat assignments, and the full governance RACI matrix.

### 1.3 Out of Scope

This document does not cover general network operations roles (see ANIF-004) or AI Council role descriptions beyond seat assignments (see ANIF-900).

### 1.4 Intended Audience

- HR and executive teams hiring or designating governance role holders
- Governance committee members understanding role boundaries
- AI Council seat holders understanding their responsibilities
- Conformance assessors verifying governance role coverage

---

## 2. Normative References

| Reference | Title |
|---|---|
| ANIF-004 | Roles and RACI |
| ANIF-830 | AI Governance Overview |
| ANIF-831 | AI Governance Structure and Accountability |
| ANIF-900 | AI Council Overview |
| RFC 2119 | Key words for use in RFCs to Indicate Requirement Levels |

---

## 3. Role Definitions

### 3.1 Chief AI Officer

**Purpose:** Holds ultimate organisational accountability for the AI programme and chairs the governance committee.

**Key responsibilities:**
- Sets the AI strategy and programme objectives
- Chairs the governance committee; holds casting vote in tied decisions
- Represents the AI programme to executive leadership and the board
- Signs off on all programme milestone gate approvals
- Owns the organisational AI policy

**Authority:**
- Approves emergency fast-track policy changes (as Chair)
- Authorises Level 4 incident response activation
- Approves vendor selection at programme level

**AI Council seat:** Non-voting observer; may invoke chair authority to escalate any council decision to the governance committee

### 3.2 AI Ethics Officer

**Purpose:** Owns the ethics framework, stewards the ANIF-700 series requirements within the organisation, and ensures ethics governance is active and effective.

**Key responsibilities:**
- Maintains the ethics framework (ANIF-700–725) in conformance with the ANIF standard
- Reviews all Critical and High ethics incidents
- Chairs the ethics incident review panel
- Proposes ethics policy changes through the policy lifecycle (ANIF-833)
- Reports ethics status to the governance committee monthly
- Monitors ethics strike patterns and escalates concerns

**Authority:**
- Recommends suspension of agent types pending ethics review
- Commissions ethics audits

**AI Council seat:** Voting member with special authority to call a vote on agent suspension on ethics grounds

### 3.3 AI Risk Officer

**Purpose:** Manages the AI risk register, maintains the risk appetite statements, and ensures risk information flows to governance and enterprise risk management.

**Key responsibilities:**
- Maintains and updates the AI risk register (ANIF-832)
- Monitors risk against appetite statements and escalates breaches
- Provides risk input to programme milestone gate assessments
- Integrates AI risk with the enterprise risk management process
- Produces the risk section of the monthly governance report

**Authority:**
- Recommends risk acceptance or rejection to the governance committee
- Requests risk assessments for new agent deployments or capability expansions

**AI Council seat:** Non-voting risk advisor; provides risk assessment on escalated intents

### 3.4 Data Protection Officer — AI-Specific Duties

The DPO's standard duties are defined by applicable data protection law. The following AI-specific duties are additional obligations that apply to ANIF deployments.

**AI-specific responsibilities:**
- Reviews all training data provenance records where personal data may be involved (ANIF-824, ANIF-836)
- Signs off on Data Protection Impact Assessments for network telemetry used in training (ANIF-836)
- Advises on inference data handling — specifically, whether inference inputs or outputs constitute personal data
- Reviews privacy implications of AI-generated decisions affecting individuals
- Provides data governance input to the governance committee

**AI Council seat:** Non-voting privacy advisor on council decisions involving personal data

---

## 4. Governance RACI Matrix

Key: **R** = Responsible (does the work) | **A** = Accountable (owns the outcome) | **C** = Consulted (provides input) | **I** = Informed (notified of outcome)

| Governance Activity | CAIO | Ethics Officer | Risk Officer | DPO | CISO | Governance Committee | AI Council | Build-Time Council |
|---|---|---|---|---|---|---|---|---|
| Ethics framework maintenance | I | R/A | C | C | C | I | C | C |
| Ethics incident review | A | R | C | I | C | I | C | I |
| Risk register maintenance | I | C | R/A | I | C | I | I | I |
| Risk appetite setting | A | C | R | C | C | A | I | I |
| Policy proposal | C | R/A | C | C | C | A | C | C |
| Policy approval | A | C | C | C | C | R/A | C | C |
| Vendor selection | A | C | C | C | R | A | I | C |
| Model version approval | C | C | C | I | C | I | I | R/A |
| Agent deployment approval | I | C | C | I | C | I | C | R/A |
| Programme milestone gates | A | C | C | I | C | R/A | C | C |
| Monthly governance report | I | C | C | C | C | A | C | I |
| Security incident (L1–L2) | I | I | I | I | R/A | I | I | C |
| Security incident (L3–L4) | A | C | C | C | R | A | I | C |
| Council vote oversight | A | C | I | I | I | A | R | I |
| DR drill programme | I | I | C | I | C | A | I | I |

---

## 5. Conformance Requirements

| ID | Requirement |
|---|---|
| CR-838-01 | All four AI governance roles MUST be filled by named individuals before Phase 1 migration begins. |
| CR-838-02 | Role vacancies MUST NOT persist for more than 30 days without an acting appointment. |
| CR-838-03 | AI Council seat assignments MUST be confirmed for each role as defined in section 3. |
| CR-838-04 | Role holders MUST not hold conflicting roles that undermine governance independence. |

---

## 6. Security Considerations

Governance role holders are high-value targets for social engineering. Role holders with AI Council seats can influence agent governance decisions. Role holders with governance committee seats can influence policy. Access to governance systems MUST be protected with privileged access management, and role holder identities in governance records MUST be verified through established organisational identity processes.

---

## 7. Operational Considerations

The four roles defined here are new to most network operations organisations. Where existing staff are designated into these roles rather than specialist hires being made, a structured onboarding and training programme MUST be provided to ensure role holders understand the ANIF governance framework and their responsibilities within it.
