# ANIF-821: Regulatory and Standards Alignment

| Field        | Value                                              |
|--------------|----------------------------------------------------|
| Doc ID       | ANIF-821                                           |
| Series       | AI Agent Architecture                              |
| Version      | 0.1.0                                              |
| Status       | Draft                                              |
| Authors      | ANIF Working Group                                 |
| Reviewers    | —                                                  |
| Approved by  | —                                                  |
| Created      | 2026-04-08                                         |
| Last updated | 2026-04-08                                         |
| Replaces     | N/A                                                |
| Related docs | ANIF-101, ANIF-102, ANIF-839, ANIF-851             |

---

## Abstract

This document maps ANIF framework requirements to three external regulatory and standards frameworks: the EU AI Act, the NIST AI Risk Management Framework, and ISO 42001 (AI Management Systems). For each framework, this document identifies what ANIF satisfies, what additional organisational controls are required beyond ANIF, and which ANIF documents provide the evidence artefacts for audit and certification purposes. ANIF is designed to satisfy the obligations of high-risk AI systems as defined by the EU AI Act, the full GOVERN/MAP/MEASURE/MANAGE function set of the NIST AI RMF, and the core clause requirements of ISO 42001.

---

## 1. Introduction

### 1.1 Purpose

Organisations deploying ANIF-conformant systems operate within regulatory environments that impose AI governance obligations. This document provides the mapping between ANIF requirements and external frameworks, enabling compliance teams to identify what ANIF provides automatically and what additional organisational controls they must implement.

### 1.2 Scope

This document covers:

- EU AI Act mapping for high-risk AI systems
- NIST AI RMF function mapping
- ISO 42001 clause mapping
- For each framework: ANIF coverage, residual organisational requirements, and evidence artefacts

### 1.3 Out of Scope

This document does not cover:

- Industry-specific compliance (HIPAA, PCI-DSS, SOX, GDPR, NIST CSF, FedRAMP) — see ANIF-851
- NIST CSF cybersecurity alignment — see ANIF-102
- Detailed TMForum and ETSI ZSM compliance mapping — see ANIF-101

### 1.4 Intended Audience

- Legal and compliance officers preparing for regulatory audits
- Governance officers responsible for AI management system certification
- Implementation teams understanding the regulatory context of ANIF requirements
- External auditors assessing ANIF-conformant deployments

---

## 2. Normative References

| Reference | Title |
|---|---|
| ANIF-101 | Compliance Mapping (TMForum, ETSI ZSM) |
| ANIF-102 | NIST CSF Alignment |
| ANIF-700 | AI Ethics Framework Overview |
| ANIF-830 | AI Governance Overview |
| ANIF-839 | External Regulatory Compliance |
| ANIF-851 | Industry Compliance Framework Mapping |
| RFC 2119 | Key words for use in RFCs to Indicate Requirement Levels |

---

## 3. Terms and Definitions

| Term | Definition |
|---|---|
| EU AI Act | Regulation (EU) 2024/1689 of the European Parliament and of the Council on Artificial Intelligence |
| NIST AI RMF | NIST AI Risk Management Framework, published January 2023 |
| ISO 42001 | ISO/IEC 42001:2023 — Information technology — Artificial intelligence — Management system |
| High-risk AI system | An AI system defined in Annex III of the EU AI Act as requiring the most stringent obligations |
| Residual requirement | A compliance obligation that ANIF does not address and must be implemented by the deploying organisation |

---

## 4. EU AI Act Alignment

### 4.1 Risk Classification

ANIF-conformant systems that operate autonomously in critical network infrastructure fall within the definition of high-risk AI systems under Annex III, Category 1 (critical infrastructure management). Deploying organisations MUST treat ANIF deployments as high-risk AI systems for the purposes of EU AI Act compliance.

### 4.2 Requirement Mapping

| EU AI Act Obligation | ANIF Coverage | Residual Organisational Requirement |
|---|---|---|
| Risk management system (Article 9) | ANIF-304 (risk scoring), ANIF-710–716 (risk controls), ANIF-830 (governance) | Deploy and maintain the documented risk management process; assign a named risk owner |
| Data governance (Article 10) | ANIF-202 (data architecture), ANIF-714 (privacy and data ethics), ANIF-836 (data governance) | Conduct DPIA where personal data is processed; document training data provenance per ANIF-824 |
| Technical documentation (Article 11) | All ANIF normative documents serve as technical documentation | Produce deployment-specific technical documentation referencing ANIF documents |
| Record-keeping (Article 12) | ANIF-107, ANIF-724 (audit trail) | Retain audit records for minimum period required by applicable jurisdiction |
| Transparency (Article 13) | ANIF-402 (explainability), ANIF-815 (human interaction) | Provide user-facing transparency notices where required |
| Human oversight (Article 14) | ANIF-404, ANIF-808, ANIF-815 (human-in-loop, override) | Designate named human oversight roles; document oversight procedures |
| Accuracy, robustness, cybersecurity (Article 15) | ANIF-820 (testing), ANIF-819 (DR), ANIF-840–849 (security) | Conduct conformance assessment; engage accredited third-party for L5 claims |
| Conformity assessment (Article 43) | ANIF-500–506 (conformance framework) | Engage a notified body for Annex III systems; self-assessment is not sufficient |
| CE marking and registration | Not addressed by ANIF | Register system in EU database; apply CE marking after conformity assessment |

### 4.3 Evidence Artefacts

The primary evidence artefacts for EU AI Act audit are:

| Artefact | ANIF Source |
|---|---|
| Risk management records | ANIF-304 outputs, ANIF-831 audit reports |
| Technical documentation | All ANIF normative documents |
| Audit logs | ANIF-107 and ANIF-724 compliant records |
| Human oversight records | ANIF-808 override logs, ANIF-404 approval records |
| Testing records | ANIF-820 test results, red-team reports |
| Conformance certificate | ANIF-502 certification process output |

---

## 5. NIST AI RMF Alignment

The NIST AI RMF organises AI risk management into four functions: GOVERN, MAP, MEASURE, and MANAGE.

### 5.1 GOVERN Function

The GOVERN function establishes organisational policies, accountability, and culture for AI risk management.

| GOVERN Sub-Category | ANIF Coverage | Residual Requirement |
|---|---|---|
| GV-1: Policies established | ANIF-002 (principles), ANIF-103 (autonomous action policy), ANIF-104 (change management) | Adopt and publish a formal organisational AI policy endorsed by executive leadership |
| GV-2: Accountability assigned | ANIF-702 (accountability chain), ANIF-004 (RACI) | Name accountable officers for each layer of the accountability chain |
| GV-3: Workforce competence | ANIF-808 (collaboration model) | Define training programme for operators working with ANIF agents |
| GV-4: Organisational teams | ANIF-830 (governance overview), ANIF-900 (AI Council) | Formally charter the AI Council and assign its members |
| GV-5: Policies updated | ANIF-838 (human override management), ANIF-839 (regulatory compliance) | Schedule annual policy review |
| GV-6: Policies enforced | ANIF-725 (containment), ANIF-831 (audit) | Implement consequence process for policy violations |

### 5.2 MAP Function

The MAP function contextualises AI risks in terms of organisational mission and deployment context.

| MAP Sub-Category | ANIF Coverage | Residual Requirement |
|---|---|---|
| MP-1: Context established | ANIF-000 (introduction), ANIF-200 (architecture) | Document deployment-specific context: geography, regulatory jurisdiction, network criticality |
| MP-2: AI risk categories identified | ANIF-710 (risk control overview), ANIF-841 (threat model) | Conduct deployment-specific threat assessment |
| MP-3: Scientific evidence considered | ANIF-703 (bias principles), ANIF-711 (bias detection) | Document evidence basis for bias and fairness claims |
| MP-4: Affected parties identified | ANIF-000, ANIF-808 | Document all roles affected by autonomous operation |
| MP-5: Impacts understood | ANIF-712 (harm prevention), ANIF-704 (harm principles) | Conduct deployment-specific impact assessment |

### 5.3 MEASURE Function

The MEASURE function quantifies AI risks and tracks their evolution over time.

| MEASURE Sub-Category | ANIF Coverage | Residual Requirement |
|---|---|---|
| MS-1: Metrics established | ANIF-822 (AI observability), ANIF-401 (observability) | Define deployment-specific KPIs and alert thresholds |
| MS-2: Risks measured | ANIF-304 (risk scoring), ANIF-822 (model health) | Conduct regular risk measurement reviews |
| MS-3: Incident data tracked | ANIF-405 (incident modelling), ANIF-715 (ethics incident response) | Maintain incident registry linked to AI RMF categories |
| MS-4: Feedback incorporated | ANIF-812 (learning agent), ANIF-403 (closed-loop feedback) | Implement feedback review schedule |

### 5.4 MANAGE Function

The MANAGE function implements risk responses and tracks residual risk.

| MANAGE Sub-Category | ANIF Coverage | Residual Requirement |
|---|---|---|
| MG-1: Responses prioritised | ANIF-304 (risk scoring), ANIF-716 (progressive intervention) | Assign response ownership and timelines |
| MG-2: Strategies implemented | ANIF-725 (containment), ANIF-820 (testing) | Document residual risk acceptance for each unmitigated risk |
| MG-3: Risk response tested | ANIF-820 (testing), ANIF-819 (DR drills) | Maintain test evidence records |
| MG-4: Risk information shared | ANIF-837 (governance reporting) | Share AI risk information with supply chain partners where applicable |

---

## 6. ISO 42001 Alignment

ISO 42001 defines requirements for an AI management system (AIMS). The following mapping covers the core clauses.

| ISO 42001 Clause | Clause Title | ANIF Coverage | Residual Requirement |
|---|---|---|---|
| 4 | Context of the organisation | ANIF-000, ANIF-001 | Document legal and stakeholder context |
| 5 | Leadership | ANIF-900 (AI Council charter) | Obtain executive commitment and assign AI policy owner |
| 6 | Planning | ANIF-304 (risk), ANIF-830 (governance) | Conduct formal AIMS risk assessment |
| 7 | Support | ANIF-808, ANIF-003 (glossary) | Establish AI literacy training programme |
| 8 | Operation | ANIF-300–308 (core framework), ANIF-800–824 (agent architecture) | Implement operational procedures per ANIF documents |
| 9 | Performance evaluation | ANIF-822, ANIF-401, ANIF-837 | Conduct internal audits and management reviews |
| 10 | Improvement | ANIF-812 (learning), ANIF-715 (incident response) | Track and close corrective actions |
| Annex A | AI system impact assessment | ANIF-712, ANIF-304 | Complete documented impact assessment for each deployment |
| Annex B | AI policy elements | ANIF-002, ANIF-103, ANIF-700 | Publish an organisational AI policy incorporating ANIF principles |

---

## 7. Conformance Requirements

| ID | Requirement |
|---|---|
| CR-821-01 | Deploying organisations MUST treat ANIF deployments in critical network infrastructure as high-risk AI systems under the EU AI Act. |
| CR-821-02 | EU AI Act conformity assessment MUST engage a notified body. Self-assessment is not sufficient for Annex III systems. |
| CR-821-03 | Audit evidence artefacts listed in section 4.3 MUST be maintained and available for regulatory inspection. |
| CR-821-04 | Residual requirements identified in sections 4–6 MUST be implemented by the deploying organisation and MUST NOT be assumed to be covered by ANIF alone. |

---

## 8. Security Considerations

Regulatory documentation — conformance certificates, audit logs, red-team reports — is sensitive. Disclosure of these artefacts to adversaries could facilitate targeted attacks by revealing known weaknesses or control boundaries. Regulatory artefacts MUST be classified at the same level as security assessment reports and handled accordingly.

---

## 9. Operational Considerations

Regulatory frameworks evolve. The EU AI Act implementing acts, NIST AI RMF supplementary materials, and ISO 42001 technical reports are updated regularly. Organisations SHOULD designate a named regulatory watch function to track changes and assess their impact on ANIF deployment compliance annually.
