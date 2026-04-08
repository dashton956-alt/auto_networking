# ANIF-834: AI Programme Governance

| Field        | Value                                              |
|--------------|----------------------------------------------------|
| Doc ID       | ANIF-834                                           |
| Series       | AI Governance                                      |
| Version      | 0.1.0                                              |
| Status       | Draft                                              |
| Authors      | ANIF Working Group                                 |
| Reviewers    | —                                                  |
| Approved by  | —                                                  |
| Created      | 2026-04-08                                         |
| Last updated | 2026-04-08                                         |
| Replaces     | N/A                                                |
| Related docs | ANIF-830, ANIF-831, ANIF-823, ANIF-837             |

---

## Abstract

This document defines the programme governance model for ANIF AI deployments, including programme board composition, investment governance requirements, milestone gates, and programme KPIs. Every expansion of AI autonomy MUST be preceded by a business case review and a milestone gate assessment demonstrating the criteria for that expansion have been met. Programme KPIs are aligned with the governance reporting requirements of ANIF-837 to ensure that programme performance and governance health are reported through the same mechanism.

---

## 1. Introduction

### 1.1 Purpose

ANIF deployments are long-running programmes that expand AI autonomy incrementally over time. Programme governance ensures that each expansion is justified, assessed, and approved — not assumed to be the natural continuation of prior success. This document specifies the governance structures that manage the programme over its full lifecycle.

### 1.2 Scope

This document covers:

- Programme board composition and authority
- Investment governance and business case requirements
- Milestone gates for each autonomy expansion
- Programme KPIs and their alignment with governance reporting

### 1.3 Out of Scope

This document does not cover:

- The migration phases and their technical entry/exit criteria (see ANIF-823)
- Governance committee composition (see ANIF-831)
- Governance reporting content (see ANIF-837)

### 1.4 Intended Audience

- Programme managers and project sponsors
- Governance committee members with programme oversight
- Finance officers reviewing AI programme investment
- Conformance assessors verifying programme governance claims

---

## 2. Normative References

| Reference | Title |
|---|---|
| ANIF-823 | Migration and Adoption Roadmap |
| ANIF-830 | AI Governance Overview |
| ANIF-831 | AI Governance Structure and Accountability |
| ANIF-837 | AI Governance Reporting and Metrics |
| RFC 2119 | Key words for use in RFCs to Indicate Requirement Levels |

---

## 3. Programme Board

### 3.1 Composition

The programme board MUST include:

| Seat | Role |
|---|---|
| Sponsor | Executive sponsor (board or C-suite level) — holds ultimate investment accountability |
| Programme Lead | Chief AI Officer or designated programme director |
| Finance | Finance controller with AI programme budget authority |
| Operations | Head of Network Operations |
| Risk | AI Risk Officer |
| Council Representative | AI Council representative providing operational governance perspective |

### 3.2 Authority

The programme board governs the investment, timeline, and scope of the AI programme. It does not govern operational or technical decisions — those belong to the AI Council and build-time council respectively.

The programme board MUST meet quarterly at minimum. Emergency meetings MUST be convened when any of the following occur: budget overrun exceeding 15% of quarterly allocation, programme timeline slippage exceeding 60 days, or a Severity 1 security incident with programme impact.

---

## 4. Investment Governance

### 4.1 Business Case Requirement

A business case MUST be produced and approved by the programme board before:

- Initial ANIF deployment
- Each migration phase transition (Phase 1, 2, and 3 per ANIF-823)
- Each Phase 3 autonomy expansion step (Steps 2–5)
- Any significant capability addition (new agent types, new integration domains)

### 4.2 Business Case Contents

Each business case MUST include:

- Objectives and measurable success criteria
- Investment required (capital, operational, and internal resource)
- Expected benefits (quantified where possible — avoided incidents, reduced operator time, improved SLA adherence)
- Risk assessment cross-referenced with the AI risk register (ANIF-832)
- Dependency on prior milestone gates being met
- Proposed timeline and decision points

### 4.3 Post-Investment Review

Every approved investment MUST be reviewed 90 days after implementation to assess whether the stated benefits are being realised. Post-investment reviews MUST be presented to the programme board.

---

## 5. Milestone Gates

Every expansion of AI autonomy MUST pass a milestone gate before the expansion proceeds. Milestone gates are assessed by the governance committee and approved by the AI Council per ANIF-823. The programme board receives confirmation of gate passage before releasing next-phase funding.

| Gate | Milestone | What Must Be Demonstrated |
|---|---|---|
| Gate 1 | Phase 1 entry | Pre-migration requirements complete; AI Council chartered; all agents passed ANIF-820 testing |
| Gate 2 | Phase 2 entry | Alignment gap below 15%; no open Critical red-team findings; governance committee approval |
| Gate 3 | Phase 3 entry | AI-deterministic disagreement rate below 10%; zero Critical violations in Phase 2; Level 2 DR drill passed in production |
| Gate 4 | Phase 3 Step 2 entry | Step 1 stable for 14 days; AI Council vote for expansion |
| Gate 5 | L5 claim | Step 5 stable for 30 days; zero Critical violations since Phase 3 entry; Level 4 DR drill passed; third-party conformance assessment complete |

---

## 6. Programme KPIs

Programme KPIs MUST be reported monthly per ANIF-837. The following KPIs are mandatory:

| KPI | Definition | Target |
|---|---|---|
| Intent success rate | Proportion of intents reaching COMPLETED state | ≥ 95% |
| Mean time to autonomous resolution | Average time from intent submission to COMPLETED state | Defined per deployment; reviewed quarterly |
| Human override rate | Proportion of agent recommendations overridden by humans | Tracked; review triggered if > 20% |
| Ethics violation rate | Ethics violations per 1,000 intents processed | Zero Critical; < 1 High per 1,000 intents |
| Availability of autonomous pipeline | Proportion of time all agents are operational at Level 0 | ≥ 99.5% |
| DR drill pass rate | Proportion of required drills completed and passed | 100% |
| Programme budget adherence | Actual vs approved spend | Within 15% of quarterly allocation |

---

## 7. Conformance Requirements

| ID | Requirement |
|---|---|
| CR-834-01 | A business case MUST be produced and approved before each migration phase transition and autonomy expansion step. |
| CR-834-02 | Each milestone gate MUST be formally assessed and approved before the associated expansion proceeds. |
| CR-834-03 | Post-investment reviews MUST be conducted 90 days after each major investment and presented to the programme board. |
| CR-834-04 | Programme KPIs MUST be reported monthly per ANIF-837. |
| CR-834-05 | The programme board MUST convene emergency meetings when any trigger condition in section 3.2 is met. |

---

## 8. Security Considerations

Programme documents — business cases, milestone gate assessments, investment approvals — contain sensitive information about deployment timelines, capability gaps, and known weaknesses. These documents MUST be classified as confidential and stored with access controls consistent with their sensitivity.

---

## 9. Operational Considerations

Programme governance overhead is real and should be proportionate. Early phases of a deployment, where risk is managed through parallel running and validation rather than autonomous execution, require lighter governance touch than Phase 3 Step 4 or 5 expansions into carrier-grade segments. Governance committee members SHOULD calibrate review depth to the risk level of the milestone being assessed.
