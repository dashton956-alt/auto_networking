# ANIF-851: Industry Compliance Framework Mapping

| Field        | Value                                              |
|--------------|----------------------------------------------------|
| Doc ID       | ANIF-851                                           |
| Series       | AI Compliance                                      |
| Version      | 0.1.0                                              |
| Status       | Draft                                              |
| Authors      | ANIF Working Group                                 |
| Reviewers    | —                                                  |
| Approved by  | —                                                  |
| Created      | 2026-04-08                                         |
| Last updated | 2026-04-08                                         |
| Replaces     | N/A                                                |
| Related docs | ANIF-106, ANIF-107, ANIF-724, ANIF-832, ANIF-839, ANIF-843, ANIF-847 |

---

## Abstract

This document maps ANIF requirements to eight industry compliance frameworks: PCI-DSS v4.0, HIPAA Security Rule, SOX Section 404, GDPR, ISO 27001, NIST 800-53, FedRAMP, and CCPA/CPRA. For each framework, this document specifies which ANIF documents provide coverage, what additional implementation constraints apply in that regulatory context, and which ANIF MUST requirements correspond to the framework's controls. Organisations deploying ANIF in regulated industries MUST implement the additional constraints defined here, which exceed baseline ANIF conformance requirements.

---

## 1. Introduction

### 1.1 Purpose

Regulated industries impose compliance requirements beyond baseline ANIF conformance. This document identifies the additional ANIF constraints that apply when a deployment operates in or adjacent to regulated environments, and maps those constraints to the applicable regulatory controls.

### 1.2 Scope

PCI-DSS v4.0, HIPAA Security Rule, SOX Section 404, GDPR, ISO 27001:2022, NIST SP 800-53 Rev. 5, FedRAMP Moderate and High, and CCPA/CPRA.

### 1.3 Out of Scope

General regulatory alignment (see ANIF-821), security compliance certification (see ANIF-849), governance compliance and audit (see ANIF-839). Sector-specific financial market infrastructure regulation, healthcare device regulation (MDR/MDCG), and telecommunications-specific national frameworks are outside the scope of this document.

### 1.4 Intended Audience

- Compliance officers deploying ANIF in regulated industries
- Legal counsel assessing regulatory obligations
- Security engineers implementing compliance-specific constraints
- External auditors assessing industry compliance claims

---

## 2. Normative References

| Reference | Title |
|---|---|
| ANIF-106 | Operational Compliance Policy |
| ANIF-107 | Audit Trail Requirements |
| ANIF-402 | Human-in-the-Loop Decision Framework |
| ANIF-714 | Privacy-by-Design Constraints |
| ANIF-715 | Ethics Incident Response Policy |
| ANIF-720 | Code-Enforced Ethics Constraints |
| ANIF-724 | Ethics Audit Trail Requirements |
| ANIF-802 | Agent Capabilities and Permissions |
| ANIF-803 | Agent Lifecycle Management |
| ANIF-806 | Agent Context Window and Memory Management |
| ANIF-816 | Context Window Management |
| ANIF-832 | AI Risk Management Framework |
| ANIF-833 | AI Policy Lifecycle Management |
| ANIF-836 | AI Data Governance |
| ANIF-839 | AI Governance Compliance and Audit |
| ANIF-841 | AI Threat Model |
| ANIF-843 | Agent Zero Trust and Authentication |
| ANIF-844 | Secure Agent Communication |
| ANIF-845 | AI Infrastructure Security |
| ANIF-846 | Security Monitoring and Threat Detection |
| ANIF-847 | AI Security Incident Response |
| ANIF-848 | Security Testing and Penetration Testing |
| RFC 2119 | Key words for use in RFCs to Indicate Requirement Levels |

---

## 3. PCI-DSS v4.0

Deployments managing or adjacent to payment card infrastructure MUST implement the following ANIF constraints in addition to baseline PCI-DSS controls.

| PCI-DSS Requirement | ANIF Coverage | Additional Constraint |
|---|---|---|
| Req 1 — Network security controls | ANIF-103, ANIF-725 | Agent tier boundaries MUST align to cardholder data environment (CDE) segmentation boundaries |
| Req 2 — Secure configurations | ANIF-802, ANIF-845 | Agent manifests MUST be reviewed as part of configuration management prior to deployment in CDE-adjacent networks |
| Req 6 — Secure development | ANIF-820, ANIF-824 | ANIF-820 testing cadence MUST be applied to all agents operating in CDE-adjacent contexts |
| Req 7 — Access control | ANIF-802, ANIF-843 | Agent permissions in CDE-adjacent networks MUST be limited to minimum necessary; no Tier 3 autonomous actions in CDE without human approval |
| Req 10 — Audit logs | ANIF-107, ANIF-724 | Audit records for CDE-adjacent operations MUST be retained for a minimum of 12 months online and 36 months total |
| Req 11 — Security testing | ANIF-848 | Annual penetration testing MUST cover CDE-adjacent agent infrastructure as a distinct scope |
| Req 12 — Policies | ANIF-833 | Policy changes affecting CDE-adjacent network operations MUST follow the standard policy lifecycle; emergency fast-track MUST NOT be used for CDE policy changes |

**PCI-specific intent constraint:** Intents operating in CDE-adjacent networks MUST declare `pci_compliant: true` in the intent constraints block. This constraint MUST force encryption throughout the pipeline and suppress any optimisation path that bypasses encryption validation.

---

## 4. HIPAA Security Rule

Deployments managing network infrastructure for, or adjacent to, systems holding electronic Protected Health Information (ePHI) MUST implement the following ANIF constraints.

| HIPAA Safeguard | ANIF Coverage | Additional Constraint |
|---|---|---|
| Technical — access controls (§164.312(a)) | ANIF-802, ANIF-843 | Role-based agent permissions MUST map to HIPAA workforce authorisation categories |
| Technical — audit controls (§164.312(b)) | ANIF-107, ANIF-724 | Audit logs for ePHI-adjacent operations MUST be retained for a minimum of 6 years |
| Technical — transmission security (§164.312(e)) | ANIF-844 | TLS 1.3 MUST be enforced on all agent communication in ePHI-adjacent deployments; no fallback to lower versions is permitted |
| Administrative — risk analysis (§164.308(a)(1)) | ANIF-832, ANIF-841 | Risk register MUST identify ePHI-adjacent networks as a distinct risk category with dedicated risk treatment |
| Administrative — workforce training (§164.308(a)(5)) | ANIF-838 | Governance role holders with authority over ePHI-adjacent networks MUST complete HIPAA-specific security awareness training |
| Physical — workstation security (§164.310(b)) | ANIF-845 | Monitoring consoles providing access to ePHI-adjacent agent observability MUST be subject to physical access controls |

**HIPAA-specific intent constraint:** Agents handling ePHI-adjacent network operations MUST declare `encryption: required` as a constraint in the intent constraints block. This constraint MUST prevent any pipeline stage from operating without encryption confirmation.

---

## 5. SOX Section 404

Deployments managing financial services infrastructure subject to Sarbanes-Oxley Act Section 404 MUST implement the following constraints. SOX Section 404 requires management to assess and report on the effectiveness of internal controls over financial reporting. Network infrastructure supporting financial transaction systems is in scope.

| SOX Control Objective | ANIF Coverage | Additional Constraint |
|---|---|---|
| Change management controls | ANIF-104, ANIF-833 | All changes to SOX-scoped infrastructure MUST follow the full policy lifecycle; no emergency fast-track on SOX-scoped systems |
| Audit trail completeness | ANIF-107, ANIF-724 | Audit records for SOX-scoped operations MUST be retained for a minimum of 7 years |
| Access controls | ANIF-802, ANIF-838 | Segregation of duties MUST be enforced; the same individual MUST NOT hold both change authorisation authority and change execution authority in SOX-scoped deployments |
| Documentation of controls | ANIF-839 | Internal audit reports covering SOX-scoped infrastructure MUST be retained and available for external auditor review |
| Management assessment | ANIF-831, ANIF-837 | Monthly governance reports MUST include a dedicated section on SOX-scoped infrastructure control effectiveness |

**SOX-specific governance constraint:** Agents operating in SOX-scoped infrastructure MUST be configured to produce `manual_review` governance mode as the maximum autonomy level. Autonomous execution (governance mode `auto_execute`) is prohibited in SOX-scoped contexts. This constraint MUST be enforced at the policy layer and MUST NOT be overridable by individual operators.

---

## 6. GDPR

Deployments that process network telemetry containing or capable of identifying natural persons within the European Union MUST implement the following ANIF constraints under Regulation (EU) 2016/679.

| GDPR Requirement | Article | ANIF Coverage | Additional Constraint |
|---|---|---|---|
| Data minimisation | Article 5(1)(c) | ANIF-714, ANIF-816 | Context window construction MUST exclude personal data not required for the specific intent being processed |
| Purpose limitation | Article 5(1)(b) | ANIF-806 | Agent episodic memory MUST NOT retain personal data beyond the lifetime of the intent for which it was collected |
| Data residency | Article 46 | ANIF-106 | Intent constraints MUST declare data residency requirements for deployments crossing jurisdictional boundaries |
| Right to explanation | Article 22 | ANIF-402 | AI-assisted decisions affecting individuals MUST be explainable; the explainability record MUST be retained and retrievable |
| Breach notification | Article 33 | ANIF-847 Level 4 | ANIF-847 Level 4 notification procedures MUST include GDPR data breach notification to the supervisory authority within 72 hours |
| Data Protection Impact Assessment | Article 35 | ANIF-836 | A DPIA MUST be completed before deploying ANIF to process personal data in network telemetry |
| Records of processing | Article 30 | ANIF-836 | Training data provenance records MUST be maintained as records of processing activities for GDPR compliance |

**GDPR-specific data governance:** The Data Protection Officer (ANIF-838 section 3.4) holds mandatory sign-off authority on all DPIA documents for GDPR-scoped deployments. DPO approval MUST be recorded in the audit trail before deployment proceeds.

---

## 7. ISO 27001:2022

ISO 27001 control mapping for AI agent deployments. This section complements the security-specific ISO 27001 mapping in ANIF-849 with operational and governance controls.

| ISO 27001 Control | ANIF Coverage | Additional Constraint |
|---|---|---|
| A.5.2 Information security roles | ANIF-838 | CAIO, AI Ethics Officer, and AI Risk Officer MUST be named in the ISO 27001 Statement of Applicability as role holders for AI-specific controls |
| A.5.30 ICT readiness for business continuity | ANIF-819, ANIF-405 | ANIF-819 degradation levels MUST be documented in the business continuity plan as AI-specific ICT resilience measures |
| A.6.3 Information security awareness | ANIF-838 | Governance role holders MUST receive ISO 27001-aligned security awareness training covering AI-specific threat scenarios |
| A.8.3 Information access restriction | ANIF-802, ANIF-843 | Agent permission declarations in ANIF-802 MUST align to the information classification scheme used in the ISO 27001 information asset register |
| A.8.16 Monitoring activities | ANIF-846 | SIEM integration and monitoring event types MUST be assessed against the ISO 27001 monitoring requirements and any gaps documented in the risk register |
| A.8.28 Secure coding | ANIF-820, ANIF-824 | Pre-deployment testing cadence from ANIF-820 MUST be integrated into the secure development lifecycle defined by the ISO 27001 programme |

---

## 8. NIST SP 800-53 Rev. 5

Control family mapping for deployments in US Federal Government contexts or deployments using NIST 800-53 as a security controls baseline.

| Control Family | Key Controls | ANIF Coverage |
|---|---|---|
| AC — Access Control | AC-2, AC-3, AC-6 | ANIF-802 (permissions), ANIF-843 (authentication), ANIF-838 (role definitions) |
| AU — Audit and Accountability | AU-2, AU-3, AU-9, AU-11 | ANIF-107, ANIF-724, ANIF-846 |
| CA — Assessment, Authorisation, Monitoring | CA-2, CA-7, CA-8 | ANIF-839, ANIF-846, ANIF-848 |
| CM — Configuration Management | CM-2, CM-6, CM-8 | ANIF-802, ANIF-807, ANIF-845 |
| IR — Incident Response | IR-1, IR-4, IR-5, IR-6 | ANIF-715, ANIF-847 |
| RA — Risk Assessment | RA-2, RA-3, RA-5 | ANIF-832, ANIF-841 |
| SA — System and Services Acquisition | SA-10, SA-11, SA-12 | ANIF-820, ANIF-824, ANIF-835 |
| SC — System and Communications Protection | SC-7, SC-8, SC-12 | ANIF-843, ANIF-844, ANIF-845 |
| SI — System and Information Integrity | SI-2, SI-3, SI-10 | ANIF-720–725, ANIF-842 |

**NIST 800-53 overlay:** Organisations using NIST 800-53 as a controls baseline SHOULD produce an ANIF-to-NIST controls overlay document as part of their System Security Plan (SSP), mapping each ANIF conformance requirement to the relevant NIST control and identifying residual organisational controls not covered by ANIF.

---

## 9. FedRAMP

Federal Risk and Authorisation Management Program requirements for deployments in or serving US Federal Government environments.

### 9.1 FedRAMP Impact Level Requirements

| FedRAMP Level | ANIF Conformance Requirement |
|---|---|
| FedRAMP Low | ANIF L3 minimum conformance |
| FedRAMP Moderate | ANIF L3 minimum conformance with full ANIF-840–849 security series implemented |
| FedRAMP High | ANIF L5 conformance required; autonomous execution (governance mode `auto_execute`) MUST NOT be enabled in federal networks without explicit AO authorisation |

### 9.2 FedRAMP-Specific Controls

| FedRAMP Requirement | ANIF Coverage | Additional Constraint |
|---|---|---|
| Continuous monitoring | ANIF-846, ANIF-839 | ConMon reporting cadence MUST align to FedRAMP continuous monitoring requirements; ANIF-846 monitoring events MUST be available to the AO on request |
| Penetration testing | ANIF-848 | FedRAMP penetration testing requirements supersede ANIF-848 where the FedRAMP requirement is more stringent |
| Incident reporting | ANIF-847 | US-CERT reporting obligations apply; ANIF-847 Level 4 notification procedures MUST include US-CERT notification within the required timeframe |
| Supply chain risk management | ANIF-824, ANIF-835 | FedRAMP supply chain risk management requirements MUST be applied to all AI model vendors; ICT supply chain security plan MUST reference ANIF-824 |

---

## 10. CCPA/CPRA

California Consumer Privacy Act and California Privacy Rights Act requirements for deployments that process personal information of California residents.

| CCPA/CPRA Right | ANIF Coverage | Additional Constraint |
|---|---|---|
| Right to know | CCPA §1798.100 | ANIF-836 training data provenance MUST identify whether California resident data is present in training sets; this record MUST be available for consumer request response |
| Right to delete | CCPA §1798.105 | Agent episodic memory and training data provenance records containing personal information of California residents MUST support deletion in response to verified consumer requests |
| Right to opt-out of sale | CCPA §1798.120 | Intent constraints MUST support a `data_sale_restricted: true` flag that prevents network telemetry involving that individual from being shared with third parties |
| Sensitive personal information limits | CPRA §1798.121 | Network telemetry classified as sensitive personal information under CPRA (e.g., precise geolocation) MUST be subject to ANIF-714 privacy-by-design constraints |
| Data minimisation | CPRA §1798.100(a)(3) | ANIF-714 and ANIF-816 context minimisation requirements satisfy the CPRA data minimisation requirement when correctly implemented |

---

## 11. Conformance Requirements

| ID | Requirement |
|---|---|
| CR-851-01 | Deployments in PCI-DSS scope MUST declare `pci_compliant: true` for intents operating in CDE-adjacent networks. |
| CR-851-02 | Deployments in HIPAA scope MUST declare `encryption: required` for agents handling ePHI-adjacent network operations. |
| CR-851-03 | Deployments in SOX scope MUST configure agents to produce `manual_review` as the maximum governance mode; `auto_execute` is prohibited. |
| CR-851-04 | Deployments in GDPR scope MUST complete a Data Protection Impact Assessment before deployment and retain the DPO approval in the audit trail. |
| CR-851-05 | Deployments targeting FedRAMP High MUST achieve ANIF L5 conformance before claiming FedRAMP High authorisation. |
| CR-851-06 | Organisations using NIST 800-53 as a baseline SHOULD produce an ANIF-to-NIST controls overlay as part of their System Security Plan. |

---

## 12. Security Considerations

Industry compliance requirements create a risk of compliance theatre — demonstrating control existence without control effectiveness. Organisations MUST ensure that ANIF compliance mappings are grounded in deployed, operational controls and not paper declarations. External audits (ANIF-839) MUST verify that compliance-specific constraints are operationally enforced, not merely documented.

---

## 13. Operational Considerations

Multiple compliance frameworks create overlapping control requirements. Organisations operating in regulated industries SHOULD implement a unified controls inventory that maps ANIF documents to all applicable framework controls simultaneously. This prevents duplicated assessment effort and ensures that a gap identified in one framework assessment is visible across all applicable frameworks.
