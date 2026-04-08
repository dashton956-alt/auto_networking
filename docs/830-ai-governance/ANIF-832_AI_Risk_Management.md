# ANIF-832: AI Risk Management Framework

| Field        | Value                                              |
|--------------|----------------------------------------------------|
| Doc ID       | ANIF-832                                           |
| Series       | AI Governance                                      |
| Version      | 0.1.0                                              |
| Status       | Draft                                              |
| Authors      | ANIF Working Group                                 |
| Reviewers    | —                                                  |
| Approved by  | —                                                  |
| Created      | 2026-04-08                                         |
| Last updated | 2026-04-08                                         |
| Replaces     | N/A                                                |
| Related docs | ANIF-304, ANIF-830, ANIF-831, ANIF-837             |

---

## Abstract

This document defines the AI risk management framework for ANIF-conformant deployments, including quantified risk appetite statements, the AI risk register schema, risk thresholds that trigger governance committee involvement, and the integration requirements with enterprise risk management processes. Risk appetite is expressed as quantified thresholds — not vague qualitative statements. The governance committee MUST be involved whenever a risk exceeds its defined threshold, regardless of whether the risk is currently controlled.

---

## 1. Introduction

### 1.1 Purpose

AI autonomous operation introduces risks that require structured management separate from general IT risk management. This document establishes the framework for identifying, assessing, recording, and responding to AI-specific risks in ANIF deployments.

### 1.2 Scope

This document covers the AI-specific risk management framework including risk appetite, risk register, thresholds, and enterprise integration. It does not duplicate general enterprise risk management methodology.

### 1.3 Out of Scope

This document does not cover:

- Operational risk scoring for individual intents (see ANIF-304)
- Ethics risk controls (see ANIF-710–716)
- Security threat model (see ANIF-841)

### 1.4 Intended Audience

- AI Risk Officers managing the AI risk register
- Governance committee members reviewing risk status
- Enterprise risk management teams integrating AI risk
- Conformance assessors evaluating risk governance claims

---

## 2. Normative References

| Reference | Title |
|---|---|
| ANIF-304 | Risk and Trust Quantification |
| ANIF-830 | AI Governance Overview |
| ANIF-831 | AI Governance Structure and Accountability |
| ANIF-837 | AI Governance Reporting and Metrics |
| RFC 2119 | Key words for use in RFCs to Indicate Requirement Levels |

---

## 3. Terms and Definitions

| Term | Definition |
|---|---|
| Risk appetite | The level of risk the organisation is willing to accept in pursuit of its AI programme objectives |
| Residual risk | The risk that remains after controls have been applied |
| Risk register | The authoritative record of identified AI risks, their assessments, controls, and ownership |
| Risk threshold | A quantified value above which a risk requires governance committee involvement |
| Risk owner | The named individual accountable for managing a specific risk item |

---

## 4. Risk Appetite Statements

Risk appetite MUST be stated as quantified thresholds. Qualitative statements such as "low appetite for operational risk" are insufficient for governance purposes.

| Risk Domain | Appetite Statement |
|---|---|
| Service disruption | No more than 2 autonomous agent-caused service disruptions per quarter with customer impact. Any third disruption within a quarter MUST trigger governance committee review. |
| Ethics violations | Zero tolerance for Critical ethics violations. More than 3 High ethics violations within any 30-day period requires governance committee review. |
| Autonomous action failure rate | No more than 5% of autonomously executed intents reaching FAILED state within any 7-day window. Exceeding this rate requires committee review. |
| Security incidents | Zero tolerance for Severity 1 security incidents caused by compromised agents. Any single Severity 1 incident requires immediate committee convening. |
| Data governance | Zero instances of personal data processed in AI training without documented consent or anonymisation. |
| Cost overrun | AI programme costs MUST NOT exceed approved budget by more than 15% in any quarter without committee approval for the overage. |

---

## 5. AI Risk Register

### 5.1 Schema

Every item in the AI risk register MUST conform to the following schema:

```yaml
risk_id: string (e.g., AI-RISK-001)
title: string
description: string
risk_category: enum [operational | ethics | security | compliance | data | financial]
likelihood: integer (1–5, where 5 is almost certain)
impact: integer (1–5, where 5 is catastrophic)
inherent_risk_score: integer (likelihood × impact, range 1–25)
current_controls:
  - control_id: string
    description: string
    anif_reference: string
control_effectiveness: integer (1–5, where 5 is highly effective)
residual_risk_score: integer
risk_owner: string (named individual)
review_date: ISO 8601
status: enum [open | mitigated | accepted | closed]
acceptance_rationale: string (required if status is accepted)
```

### 5.2 Mandatory Risk Register Items

The following risk categories MUST have at least one item in the risk register at all times:

- Model drift or degradation
- Prompt injection attack
- Ethics gate bypass
- Governance manipulation (insider)
- Supply chain compromise
- Regulatory non-compliance
- Audit trail integrity compromise

### 5.3 Risk Register Maintenance

The risk register MUST be reviewed and updated quarterly. New risks identified between reviews MUST be added within 5 business days of identification.

---

## 6. Risk Thresholds Triggering Governance Committee Involvement

| Threshold | Action |
|---|---|
| Inherent risk score ≥ 20 | Governance committee must review before any associated control is removed or reduced |
| Residual risk score > 12 | Risk must be presented at the next committee meeting |
| Any risk in accepted status with residual score > 15 | Committee must re-evaluate acceptance annually |
| Risk owner vacancy (no named owner) | Committee must assign an owner within 5 business days |
| Risk exceeding appetite statement | Committee must convene within 5 business days of threshold breach |

---

## 7. Enterprise Risk Management Integration

### 7.1 Integration Requirement

The AI risk register MUST be integrated with the organisation's enterprise risk management (ERM) process. AI risks with an inherent risk score ≥ 15 MUST be escalated to the ERM register and reported in the organisation's standard risk reporting cycle.

### 7.2 Risk Taxonomy Alignment

AI risk categories in this document MUST be mapped to the organisation's ERM taxonomy. The mapping MUST be documented and approved by both the AI Risk Officer and the enterprise risk function.

### 7.3 Reporting Cadence

AI risk summary data MUST flow into the monthly governance reporting (ANIF-837) and the quarterly board report (ANIF-831).

---

## 8. Conformance Requirements

| ID | Requirement |
|---|---|
| CR-832-01 | Risk appetite MUST be expressed as quantified thresholds. Qualitative-only appetite statements do not satisfy this requirement. |
| CR-832-02 | The AI risk register MUST be maintained with all mandatory risk categories present. |
| CR-832-03 | Risk register items MUST be reviewed quarterly. |
| CR-832-04 | Risks exceeding committee involvement thresholds MUST trigger governance committee action within the timeframes specified. |
| CR-832-05 | AI risks with inherent score ≥ 15 MUST be escalated to the enterprise risk register. |

---

## 9. Security Considerations

The risk register itself is a sensitive document — it discloses known vulnerabilities and their control status. The risk register MUST be classified as confidential and access restricted to governance committee members, risk management staff, and auditors.

---

## 10. Operational Considerations

Risk registers that are only updated when prompted by incidents are symptoms of a governance programme that is reactive rather than preventive. The quarterly review cadence is a minimum. Risk owners SHOULD engage continuously with their risks and update the register whenever material changes in likelihood, impact, or control effectiveness occur.
