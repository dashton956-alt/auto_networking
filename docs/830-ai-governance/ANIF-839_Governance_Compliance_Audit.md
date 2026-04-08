# ANIF-839: AI Governance Compliance and Audit

| Field        | Value                                              |
|--------------|----------------------------------------------------|
| Doc ID       | ANIF-839                                           |
| Series       | AI Governance                                      |
| Version      | 0.1.0                                              |
| Status       | Draft                                              |
| Authors      | ANIF Working Group                                 |
| Reviewers    | —                                                  |
| Approved by  | —                                                  |
| Created      | 2026-04-08                                         |
| Last updated | 2026-04-08                                         |
| Replaces     | N/A                                                |
| Related docs | ANIF-107, ANIF-502, ANIF-830, ANIF-821             |

---

## Abstract

This document defines the internal audit programme, evidence requirements for regulatory inspections, continuous compliance monitoring requirements, and the audit standards that govern L5 certification. Internal audits MUST be conducted quarterly. External audits MUST be conducted annually. Continuous compliance monitoring applies automated checks against governance policy rules to provide real-time compliance visibility between point-in-time audits. L5 certification requires an external audit with no major findings.

---

## 1. Introduction

### 1.1 Purpose

Governance without independent verification is self-declaration. This document establishes the audit programme that provides objective assurance that the governance framework is operating as designed and that ANIF conformance claims are supportable by evidence.

### 1.2 Scope

Internal and external audit programme structure, evidence requirements for regulatory inspections, continuous compliance monitoring, and L5 certification audit requirements.

### 1.3 Out of Scope

Conformance certification process (see ANIF-502), regulatory compliance mapping (see ANIF-821), security testing (see ANIF-848).

### 1.4 Intended Audience

- Internal audit teams conducting governance reviews
- External auditors assessing ANIF conformance
- Compliance officers preparing for regulatory inspections
- Governance committee members commissioning and reviewing audits

---

## 2. Normative References

| Reference | Title |
|---|---|
| ANIF-107 | Audit Trail Requirements |
| ANIF-502 | Certification Process |
| ANIF-724 | Ethics Audit Trail Requirements |
| ANIF-821 | Regulatory and Standards Alignment |
| ANIF-830 | AI Governance Overview |
| RFC 2119 | Key words for use in RFCs to Indicate Requirement Levels |

---

## 3. Internal Audit Programme

### 3.1 Quarterly Internal Audit

An internal audit of AI governance controls MUST be conducted quarterly. The audit MUST be conducted by a team independent of the AI operations and engineering functions. The internal audit function MUST report findings to the governance committee, not to the AI programme lead.

### 3.2 Internal Audit Scope

Each quarterly internal audit MUST cover:

| Audit Area | What Is Assessed |
|---|---|
| Policy compliance | Are governance policies being followed? Are policy versions current? |
| Ethics control effectiveness | Are ethics gates functioning? Are strike thresholds being correctly applied? |
| Audit trail integrity | Are audit records complete, tamper-evident, and within retention policy? |
| Override review | Are override logs complete? Are override reasons documented? Are over-20% rates being escalated? |
| Risk register currency | Has the risk register been reviewed? Are risk owners current? |
| Reporting compliance | Were monthly governance reports delivered on time? Were they complete? |
| DR drill compliance | Were required drills conducted? Did they pass? |

### 3.3 Internal Audit Findings

Audit findings MUST be classified as:

| Classification | Definition |
|---|---|
| Critical | A governance control is absent or has failed — the control is not operating as intended |
| Major | A significant deviation from required governance practices that poses material risk |
| Minor | A process gap or documentation issue that does not impair control effectiveness |
| Observation | An improvement opportunity with no current risk |

Critical findings MUST be escalated to the governance committee within 5 business days. Remediation plans for Critical findings MUST be submitted within 10 business days.

---

## 4. Annual External Audit

### 4.1 Requirement

An external audit of ANIF governance conformance MUST be conducted annually by an independent, qualified auditor. The external auditor MUST NOT have a consulting relationship with the organisation that creates a conflict of interest.

### 4.2 External Audit Scope

The external audit MUST cover all areas of the internal audit programme plus:

- Verification of conformance claims against ANIF normative requirements
- Review of L5 certification status (where claimed)
- Assessment of governance committee independence and effectiveness
- Review of AI Council decision records for pattern and process compliance
- Verification of security testing completion and finding resolution

### 4.3 External Audit Report

The external audit report MUST be presented to the governance committee within 30 days of audit completion. The report MUST be retained for a minimum of 5 years.

---

## 5. Evidence Requirements for Regulatory Inspections

The following evidence MUST be maintained and available for production to regulatory authorities within 5 business days of request.

| Regulatory Requirement | Evidence Artefact | ANIF Source |
|---|---|---|
| Technical documentation | All ANIF normative documents, deployment configuration | ANIF-000–849 |
| Human oversight | Override logs, approval records, human review records | ANIF-808, ANIF-404 |
| Audit trail | Complete audit records within retention period | ANIF-107, ANIF-724 |
| Risk management | AI risk register, risk appetite statements | ANIF-832 |
| Testing records | ANIF-820 test results, red-team reports, penetration test reports | ANIF-820, ANIF-848 |
| Incident records | All security incidents, ethics incidents, and their resolution | ANIF-715, ANIF-847 |
| Governance records | Governance committee minutes, policy versions, AI Council decisions | ANIF-831, ANIF-833, ANIF-900 |
| Training data provenance | Provenance records for all models in production | ANIF-824, ANIF-836 |
| Conformance certificate | ANIF-502 certification output | ANIF-502 |

Evidence MUST be stored in a format that is accessible and readable without specialist tools. Document retention MUST meet the requirements of applicable law in the jurisdictions where the organisation operates.

---

## 6. Continuous Compliance Monitoring

### 6.1 Purpose

Point-in-time audits provide assurance at the time of the audit. Continuous compliance monitoring provides real-time visibility into compliance status between audits and detects drift before it becomes a finding.

### 6.2 Automated Compliance Checks

The following checks MUST be automated and run continuously:

| Check | Frequency | Alert Condition |
|---|---|---|
| Policy version currency | Daily | Any active policy version is more than 24 months old without review |
| Override rate monitoring | Daily | Any agent override rate exceeds 20% |
| Ethics strike monitoring | Real-time | Any agent holds 2 or more active ethics strikes |
| Audit trail completeness | Hourly | Any gap in audit log sequence |
| Certificate expiry | Daily | Any agent certificate expiring within 14 days |
| DR drill schedule adherence | Monthly | Required drill not completed within its due window |
| Report delivery compliance | Monthly | Monthly governance report not delivered by the 10th |

### 6.3 Continuous Monitoring Reporting

Continuous compliance monitoring results MUST be included in the monthly governance report (ANIF-837). Any automated check alert that is not resolved within 5 business days MUST be escalated to the governance committee.

---

## 7. L5 Certification Audit Requirements

L5 certification (ANIF-502) requires an external audit with specific outcomes:

1. The external audit MUST be conducted by an accredited conformance assessor with no prior consulting relationship with the organisation.
2. The audit MUST find no Critical or Major findings against ANIF conformance requirements.
3. Minor findings are permitted but MUST have documented remediation plans.
4. The auditor MUST specifically verify: L5 minimum viable implementation (ANIF-823 section 7), AI Council operation (ANIF-900), ethics safeguard effectiveness (ANIF-720–725), and security testing completion (ANIF-848).
5. The L5 certification MUST NOT be self-declared — it MUST be issued by the external auditor on the basis of audit evidence.

---

## 8. Conformance Requirements

| ID | Requirement |
|---|---|
| CR-839-01 | Quarterly internal audits MUST be conducted by a team independent of AI operations and engineering. |
| CR-839-02 | Critical internal audit findings MUST be escalated to the governance committee within 5 business days. |
| CR-839-03 | Annual external audits MUST be conducted by an independent, qualified auditor. |
| CR-839-04 | Regulatory evidence artefacts MUST be available for production within 5 business days of request. |
| CR-839-05 | All automated compliance checks in section 6.2 MUST be operational. |
| CR-839-06 | L5 certification MUST be issued by an external auditor with no Critical or Major findings. |

---

## 9. Security Considerations

Audit records are evidence of the organisation's governance posture. They MUST be protected against modification. The audit trail integrity check (ANIF-724) applies equally to governance audit records as to operational audit records. External audit reports MUST be stored with the same access controls as security test reports — they disclose governance gaps that an attacker could exploit.

---

## 10. Operational Considerations

Preparing for external audits requires significant operational effort. Organisations SHOULD maintain an "audit-ready" posture year-round rather than scrambling to prepare evidence at audit time. The evidence requirements in section 5 should inform ongoing record-keeping practices, not be treated as a one-time collection exercise.
