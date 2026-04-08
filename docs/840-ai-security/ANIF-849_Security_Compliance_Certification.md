# ANIF-849: Security Compliance and Certification

| Field        | Value                                              |
|--------------|----------------------------------------------------|
| Doc ID       | ANIF-849                                           |
| Series       | AI Security                                        |
| Version      | 0.1.0                                              |
| Status       | Draft                                              |
| Authors      | ANIF Working Group                                 |
| Reviewers    | —                                                  |
| Approved by  | —                                                  |
| Created      | 2026-04-08                                         |
| Last updated | 2026-04-08                                         |
| Replaces     | N/A                                                |
| Related docs | ANIF-821, ANIF-839, ANIF-843, ANIF-848             |

---

## Abstract

This document maps ANIF AI security requirements to five external security and compliance frameworks: the EU AI Act (AI-specific security obligations), NIS2 (critical infrastructure security requirements), NIST AI RMF (MANAGE function security controls), ISO 27001 (control set mapping), and ISO 42001 (AI management system security clauses). For each framework, this document specifies what ANIF satisfies, what additional organisational controls are required, and which ANIF documents provide the evidence artefacts. L5 certification requires: passing ANIF-848 red-team with no Critical findings, completing ANIF-839 external audit with no major findings, and demonstrating ANIF-843 cryptographic identity for all agents.

---

## 1. Introduction

### 1.1 Purpose

Security compliance for AI-autonomous systems spans multiple regulatory and standards frameworks. This document provides the consolidated mapping between ANIF security requirements and the external frameworks that deploying organisations must satisfy, enabling compliance teams to understand their obligations and the evidence ANIF provides.

### 1.2 Scope

EU AI Act security obligations, NIS2 requirements, NIST AI RMF MANAGE function, ISO 27001 controls, and ISO 42001 security clauses.

### 1.3 Out of Scope

General regulatory compliance mapping (see ANIF-821), industry-specific compliance (see ANIF-851), governance compliance (see ANIF-839).

### 1.4 Intended Audience

- Security compliance officers
- External auditors assessing security compliance
- Legal counsel advising on regulatory obligations
- Conformance assessors evaluating L5 security claims

---

## 2. Normative References

| Reference | Title |
|---|---|
| ANIF-821 | Regulatory and Standards Alignment |
| ANIF-839 | AI Governance Compliance and Audit |
| ANIF-843 | Agent Zero Trust and Authentication |
| ANIF-848 | Security Testing and Penetration Testing |
| RFC 2119 | Key words for use in RFCs to Indicate Requirement Levels |

---

## 3. EU AI Act — Security Obligations

The EU AI Act imposes specific security obligations on high-risk AI systems. ANIF deployments in critical network infrastructure MUST be treated as high-risk systems.

| EU AI Act Obligation | ANIF Coverage | Residual Organisational Requirement |
|---|---|---|
| Robustness and resilience (Article 15) | ANIF-819 (DR), ANIF-820 (testing), ANIF-842 (injection defence) | Conduct conformity assessment with notified body for robustness claims |
| Cybersecurity (Article 15.5) | ANIF-840–849 (full security series) | Apply NIS2 obligations where the organisation qualifies as an essential entity |
| Security by design | ANIF-843 (zero trust), ANIF-844 (secure comms), ANIF-845 (infrastructure) | Document security-by-design decisions in technical documentation |
| Supply chain security | ANIF-824, ANIF-845 | Conduct supplier security assessments; include ANIF-824 requirements in procurement contracts |
| Logging for security | ANIF-107, ANIF-724, ANIF-846 | Retain logs for the minimum period required by Article 12 |

---

## 4. NIS2 — Critical Infrastructure Security Requirements

Organisations operating critical network infrastructure that qualify as essential entities under NIS2 (Directive (EU) 2022/2555) MUST meet the following requirements. ANIF provides significant coverage.

| NIS2 Requirement | Article | ANIF Coverage | Residual Requirement |
|---|---|---|---|
| Risk management measures | Article 21 | ANIF-832, ANIF-841, ANIF-846 | Document NIS2-specific risk assessment; submit to competent authority if required |
| Incident handling | Article 21(2)(b) | ANIF-847, ANIF-715 | Align ANIF-847 incident levels to NIS2 significant incident classification |
| Business continuity | Article 21(2)(c) | ANIF-819, ANIF-405 | Maintain tested BCM plan covering AI failure scenarios |
| Supply chain security | Article 21(2)(d) | ANIF-824, ANIF-835 | Extend supply chain security to all third-party suppliers, not only AI model vendors |
| Security in network acquisition | Article 21(2)(e) | ANIF-845, ANIF-844 | Apply secure development practices; conduct SAST/DAST where agent code is developed in-house |
| Cryptography | Article 21(2)(h) | ANIF-843, ANIF-844 | Maintain cryptographic policy aligned to applicable national standards |
| Human resources security | Article 21(2)(i) | ANIF-838 (role definitions) | Implement security awareness training for governance role holders |
| Incident notification | Article 23 | ANIF-847 Level 4 | Register with national CSIRT; implement notification workflow within required timeframes |

---

## 5. NIST AI RMF — MANAGE Function Security Controls

The NIST AI RMF MANAGE function addresses implementation of risk responses. Security controls are a primary response to AI risks.

| MANAGE Sub-Category | ANIF Coverage | Residual Requirement |
|---|---|---|
| MG-1: Risk responses implemented | ANIF-840–849 (security series) | Document risk response selection rationale |
| MG-2: Residual risk accepted | ANIF-832 (risk register acceptance) | Formally accept residual risk for each unmitigated threat in ANIF-841 |
| MG-3: Responses tested | ANIF-820, ANIF-848 | Maintain test evidence records linked to risk responses |
| MG-4: Incidents tracked | ANIF-847, ANIF-846 | Maintain incident registry with AI RMF category tagging |
| MG-5: Processes updated | ANIF-833 (policy lifecycle) | Update security controls in response to incident findings |

---

## 6. ISO 27001 Control Mapping

ISO 27001:2022 Annex A controls relevant to AI agent security.

| ISO 27001 Control | ANIF Coverage | Residual Requirement |
|---|---|---|
| 5.8 Information security in project management | ANIF-834 (programme governance) | Include security in project gating |
| 5.23 Information security for use of cloud services | ANIF-835 (vendor governance) | Extend cloud security policy to AI inference services |
| 7.11 Clear desk and screen | Not addressed | Organisational policy for governance documentation handling |
| 8.7 Protection against malware | ANIF-845 (container security), ANIF-824 | Extend malware protection to agent infrastructure |
| 8.9 Configuration management | ANIF-802 (agent manifests), ANIF-807 (version pinning) | Integrate agent manifests with CMDB |
| 8.15 Logging | ANIF-107, ANIF-724, ANIF-846 | Align log retention to ISO 27001 requirements |
| 8.24 Use of cryptography | ANIF-843, ANIF-844 | Maintain cryptographic policy; key management register |
| 8.29 Security testing in development | ANIF-820, ANIF-848 | Include AI-specific test cases in development pipeline |
| 8.30 Outsourced development | ANIF-835 (vendor governance) | Apply ISO 27001 Annex A 8.30 to AI model vendors |

---

## 7. ISO 42001 — AI Management System Security Clauses

ISO 42001 includes AI management system requirements with security dimensions.

| ISO 42001 Clause | Title | ANIF Coverage | Residual Requirement |
|---|---|---|---|
| 6.1 | Actions to address risks | ANIF-832, ANIF-841 | Formal AIMS risk treatment plan |
| 8.3 | AI system impact assessment | ANIF-712 (harm prevention), ANIF-841 | Complete formal impact assessment for each deployment |
| 8.4 | AI system lifecycle | ANIF-803, ANIF-820, ANIF-824 | Document lifecycle management policy |
| 9.1 | Monitoring, measurement, analysis and evaluation | ANIF-846, ANIF-822 | Define security measurement programme |
| 10.1 | Nonconformity and corrective action | ANIF-847, ANIF-715 | Implement corrective action tracking for security nonconformities |
| Annex B, B.6 | Data privacy | ANIF-714, ANIF-836 | Privacy impact assessment process |

---

## 8. L5 Certification Security Requirements

An organisation claiming L5 ANIF conformance MUST demonstrate the following security-specific conditions to the external auditor:

| Condition | Evidence Required |
|---|---|
| ANIF-848 red-team with no Critical findings | Red-team report with build-time council sign-off |
| ANIF-839 external audit with no major findings | External audit report dated within 12 months of L5 claim |
| ANIF-843 cryptographic identity for all agents | Certificate registry with entries for all production agents; API gateway configuration confirming per-request verification |
| Security testing programme operational | Evidence of quarterly injection testing, annual penetration testing, and annual red-team |
| Incident response tested | ANIF-847 Level 2 response tested as part of DR drill programme |

---

## 9. Conformance Requirements

| ID | Requirement |
|---|---|
| CR-849-01 | Organisations qualifying as NIS2 essential entities MUST align ANIF-847 incident levels to NIS2 significant incident classification. |
| CR-849-02 | L5 certification MUST NOT be claimed without satisfying all five conditions in section 8. |
| CR-849-03 | Security evidence artefacts required for external compliance frameworks MUST be maintained for the minimum retention periods required by those frameworks. |

---

## 10. Security Considerations

Security compliance frameworks evolve. NIS2 implementing acts, ISO 27001 updates, and NIST AI RMF supplementary materials are all subject to revision. Organisations SHOULD assign a named compliance watch function to track changes and assess their impact on ANIF deployment compliance annually.

---

## 11. Operational Considerations

Multiple compliance frameworks create the risk of duplicated control assessment effort. Organisations SHOULD implement a consolidated compliance programme that maps ANIF controls to all applicable frameworks in a single control inventory, reducing the overhead of separate assessments for each framework.
