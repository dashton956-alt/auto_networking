# ANIF-102: NIST Cybersecurity Framework Alignment

| Field        | Value                                            |
|--------------|--------------------------------------------------|
| Doc ID       | ANIF-102                                         |
| Series       | Governance                                       |
| Version      | 0.1.0                                            |
| Status       | Draft                                            |
| Authors      | ANIF Working Group                               |
| Reviewers    | —                                                |
| Approved by  | —                                                |
| Created      | 2026-04-07                                       |
| Last updated | 2026-04-07                                       |
| Replaces     | N/A                                              |
| Related docs | ANIF-001, ANIF-101, ANIF-103                     |

---

## Abstract

This document maps the Autonomous Networking and Infrastructure Framework (ANIF) to the NIST Cybersecurity Framework (CSF) version 2.0. For each of the six CSF functions — Govern, Identify, Protect, Detect, Respond, and Recover — it identifies the ANIF documents and controls that satisfy the function's requirements. The document also maps ANIF to relevant ITIL 4 practices. Together these mappings enable compliance officers to use ANIF as evidence of cybersecurity posture and support integration with enterprise risk management programmes.

---

## 1. Introduction

### 1.1 Purpose

The NIST Cybersecurity Framework is widely adopted as the baseline for organisational cybersecurity governance. ANIF, as an autonomous network operations framework, introduces novel risks — autonomous decision-making, automated action execution, AI-generated reasoning — that must be addressed within an existing CSF programme. This document:

- Maps every ANIF governance document and control to the relevant CSF 2.0 function and category.
- Identifies CSF categories where ANIF provides direct evidence of control implementation.
- Highlights gaps where additional organisational controls are needed outside ANIF.
- Maps ANIF to ITIL 4 practices for service management alignment.

### 1.2 Scope

This document covers:

- NIST CSF 2.0 mapping across all six functions: GV (Govern), ID (Identify), PR (Protect), DE (Detect), RS (Respond), RC (Recover).
- ITIL 4 practice mapping for: change enablement, incident management, problem management, service configuration management, monitoring and event management, continual improvement.
- ANIF-specific security controls introduced by autonomous operations.

### 1.3 Out of Scope

- NIST SP 800-53 control mapping (future document).
- ISO 27001 mapping (future document).
- Network-layer security controls not related to autonomous operations governance.
- Penetration testing or red team procedures.

### 1.4 Intended Audience

| Audience               | Purpose                                                                       |
|------------------------|-------------------------------------------------------------------------------|
| Compliance Officer     | Evidence generation for CSF assessments; gap identification                   |
| Policy Administrator   | Understanding how ANIF policies satisfy CSF Protect and Govern requirements   |
| Senior Engineer        | Architecture alignment with CSF Detect, Respond, and Recover                 |
| Network Engineer       | Understanding security obligations under ANIF operations                      |

---

## 2. Normative References

| Reference             | Title                                                                      |
|-----------------------|----------------------------------------------------------------------------|
| ANIF-001              | ANIF Constitution and Guiding Principles                                   |
| ANIF-100              | Governance Overview                                                        |
| ANIF-103              | Autonomous Action Policy                                                   |
| ANIF-104              | Change Management Policy                                                   |
| ANIF-105              | Escalation and Exception Policy                                            |
| ANIF-106              | Data Residency and Compliance Policy                                       |
| ANIF-107              | Audit Trail Requirements                                                   |
| ANIF-202              | Asset Registry                                                             |
| ANIF-205              | Access Control and Identity                                                |
| ANIF-307              | Risk Scoring Engine                                                        |
| ANIF-308              | Recovery Procedures                                                        |
| ANIF-401              | Analytics Framework                                                        |
| ANIF-402              | Audit and Observability                                                    |
| ANIF-403              | Closed-Loop Automation                                                     |
| ANIF-404              | Operational Security Controls                                              |
| ANIF-405              | Incident Management                                                        |
| ANIF-406              | Incident Response                                                          |
| ANIF-407              | Recovery Planning                                                          |
| NIST CSF 2.0          | NIST Cybersecurity Framework Version 2.0 (NIST CSWP 29)                   |
| ITIL 4                | ITIL 4 Foundation                                                          |

---

## 3. Terms and Definitions

| Term            | Definition                                                                                            |
|-----------------|-------------------------------------------------------------------------------------------------------|
| CSF Function    | One of six top-level NIST CSF categories: Govern, Identify, Protect, Detect, Respond, Recover.        |
| CSF Category    | A subdivision of a CSF function representing a specific security outcome.                             |
| CSF Subcategory | A specific, measurable security outcome within a CSF category.                                        |
| ITIL 4 Practice | A set of organisational resources designed for performing work or accomplishing an objective (ITIL 4).|
| Control         | A measure that modifies risk; may be preventive, detective, or corrective.                            |

---

## 4. NIST CSF 2.0 Alignment

### 4.1 CSF Function: Govern (GV)

The Govern function establishes the organisational context, strategy, and accountability structures for cybersecurity risk management. ANIF's governance framework directly addresses this function.

| CSF Category                          | CSF Subcategory (Selected)                          | ANIF Controls and Documents                                  |
|---------------------------------------|-----------------------------------------------------|--------------------------------------------------------------|
| GV.OC: Organisational Context         | Mission and risk tolerance defined                  | ANIF-001 (Principles P-01 to P-12); ANIF-100 (Governance Overview) |
| GV.RM: Risk Management Strategy       | Risk tolerance thresholds documented                | ANIF-103 (Action Policy risk thresholds); ANIF-307           |
| GV.RR: Roles and Responsibilities     | Accountability for cybersecurity defined            | ANIF-100 §4.7 (Role definitions); ANIF-103 (Authorisation matrix) |
| GV.PO: Policy                         | Policies established and communicated               | ANIF-103, ANIF-104, ANIF-105, ANIF-106, ANIF-107            |
| GV.OV: Oversight                      | Governance oversight of cybersecurity strategy      | ANIF-100 §4.3 (Governance hierarchy); ANIF-104              |
| GV.SC: Supply Chain Risk Management   | Third-party risk managed                            | ANIF-001 (P-08 Vendor Neutrality); ANIF-106                 |

**Summary**: ANIF fully addresses GV.OC, GV.RM, GV.RR, and GV.PO. GV.SC is partially addressed; operators MUST supplement with organisational vendor risk management procedures.

### 4.2 CSF Function: Identify (ID)

The Identify function develops organisational understanding of cybersecurity risks to systems, people, assets, data, and capabilities.

| CSF Category                          | CSF Subcategory (Selected)                          | ANIF Controls and Documents                                  |
|---------------------------------------|-----------------------------------------------------|--------------------------------------------------------------|
| ID.AM: Asset Management               | Software assets inventoried                         | ANIF-202 (Asset Registry)                                    |
| ID.AM: Asset Management               | Network topology documented                         | ANIF-202; ANIF-307 (Risk Scoring — asset context)           |
| ID.RA: Risk Assessment                | Threat intelligence gathered and analysed           | ANIF-307 (Risk Scoring Engine); ANIF-401 (Analytics)        |
| ID.RA: Risk Assessment                | Risk responses documented                           | ANIF-103 (thresholds); ANIF-105 (escalation triggers)        |
| ID.IM: Improvement                    | Lessons learned captured                            | ANIF-403 (closed-loop feedback); ANIF-405 (incident reviews) |

**Key ANIF Controls for Identify**:
- ANIF-202 MUST maintain an up-to-date registry of all network assets within the autonomous operations envelope.
- ANIF-307 risk scoring MUST incorporate asset criticality data from ANIF-202.
- ANIF-403 closed-loop feedback MUST feed back into ANIF-307 risk model calibration (P-12 Continuous Learning).

### 4.3 CSF Function: Protect (PR)

The Protect function develops and implements safeguards to ensure delivery of critical services.

| CSF Category                              | CSF Subcategory (Selected)                          | ANIF Controls and Documents                                   |
|-------------------------------------------|-----------------------------------------------------|---------------------------------------------------------------|
| PR.AA: Identity Management and Auth       | Identities and credentials managed                  | ANIF-205 (Access Control and Identity); ANIF-103 (role matrix)|
| PR.AA: Identity Management and Auth       | Least privilege enforced                            | ANIF-001 (P-05); ANIF-103 §4.2 (Authorisation matrix)        |
| PR.AT: Awareness and Training             | Personnel trained on cybersecurity responsibilities | Organisational responsibility; ANIF-100 §4.7 documents roles  |
| PR.DS: Data Security                      | Data at rest and in transit protected               | ANIF-106 (encryption requirements); ANIF-404                 |
| PR.DS: Data Security                      | Data residency requirements enforced                | ANIF-106 (Data Residency Policy); ANIF-302                   |
| PR.IR: Technology Infrastructure Resil.  | Networks protected against unauthorised access      | ANIF-103 (action authorisation); ANIF-205; ANIF-404          |
| PR.PS: Platform Security                  | Configuration managed securely                      | ANIF-104 (Change Management); ANIF-404                       |

**Key ANIF Controls for Protect**:
- ANIF-103 MUST enforce role-based authorisation for all autonomous actions.
- ANIF-205 MUST implement least-privilege access for all roles (P-05).
- ANIF-106 MUST enforce encryption requirements for pci_compliant and EU-region workloads.
- ANIF-404 MUST define technical controls for securing the ANIF pipeline components.

### 4.4 CSF Function: Detect (DE)

The Detect function develops and implements activities to identify cybersecurity events.

| CSF Category                          | CSF Subcategory (Selected)                          | ANIF Controls and Documents                                   |
|---------------------------------------|-----------------------------------------------------|---------------------------------------------------------------|
| DE.AE: Adverse Event Analysis         | Anomalous activity detected                         | ANIF-401 (Analytics); ANIF-403 (Closed-Loop)                 |
| DE.AE: Adverse Event Analysis         | Event data correlated from multiple sources         | ANIF-401; ANIF-402 (Audit and Observability)                 |
| DE.AE: Adverse Event Analysis         | Estimated impact of adverse events understood       | ANIF-307 (Risk Scoring); ANIF-403                            |
| DE.CM: Continuous Monitoring          | Networks monitored for anomalies                    | ANIF-403; ANIF-405 (Incident Management)                     |
| DE.CM: Continuous Monitoring          | Personnel activity monitored                        | ANIF-107 (Audit Trail — operator_id field); ANIF-402         |

**Key ANIF Controls for Detect**:
- ANIF-401 MUST provide real-time analytics capable of detecting anomalies in network behaviour.
- ANIF-403 closed-loop MUST include a monitoring phase that feeds detected anomalies into the pipeline.
- ANIF-107 audit records with `operator_id` and `reasoning_chain` fields provide personnel activity monitoring for autonomous agent actions.
- ANIF-405 MUST define detection thresholds that trigger incident management workflows.

### 4.5 CSF Function: Respond (RS)

The Respond function develops and implements activities to take action regarding detected cybersecurity incidents.

| CSF Category                          | CSF Subcategory (Selected)                          | ANIF Controls and Documents                                   |
|---------------------------------------|-----------------------------------------------------|---------------------------------------------------------------|
| RS.MA: Incident Management            | Incident response plan executed                     | ANIF-405 (Incident Management); ANIF-406 (Incident Response) |
| RS.MA: Incident Management            | Incidents categorised and prioritised               | ANIF-105 (Escalation Policy — P0/P1 classification)          |
| RS.AN: Incident Analysis              | Root causes of incidents investigated               | ANIF-107 (audit trail); ANIF-402; ANIF-405                  |
| RS.AN: Incident Analysis              | Impact of incidents determined                      | ANIF-307 (risk scoring); ANIF-405                            |
| RS.CO: Incident Response Reporting    | Incidents reported to internal stakeholders         | ANIF-105 (escalation notifications); ANIF-406               |
| RS.MI: Incident Mitigation            | Incidents contained                                 | ANIF-103 (`isolate_segment` action); ANIF-305                |

**Key ANIF Controls for Respond**:
- ANIF-105 MUST define escalation triggers that automatically initiate incident response for P0 and P1 events.
- ANIF-406 MUST document the incident response playbook for autonomous operation failures.
- ANIF-305 cross-domain orchestration MUST support coordinated containment actions.
- ANIF-107 audit trail provides the forensic record required for incident analysis (P-02 Auditability).

### 4.6 CSF Function: Recover (RC)

The Recover function develops and implements activities to maintain plans for resilience and restore capabilities.

| CSF Category                          | CSF Subcategory (Selected)                          | ANIF Controls and Documents                                   |
|---------------------------------------|-----------------------------------------------------|---------------------------------------------------------------|
| RC.RP: Incident Recovery Plan Exec.   | Recovery plans executed and updated                 | ANIF-308 (Recovery Procedures); ANIF-405                    |
| RC.RP: Incident Recovery Plan Exec.   | Recovery activities coordinated with stakeholders   | ANIF-105; ANIF-405; ANIF-407 (Recovery Planning)            |
| RC.CO: Incident Recovery Comms        | Restoration activities communicated                 | ANIF-405; ANIF-406                                          |

**Key ANIF Controls for Recover**:
- ANIF-103 rollback requirements ensure every autonomous action has a defined recovery path (P-01 Reversibility).
- ANIF-308 MUST define recovery procedures for each action type and environment.
- ANIF-407 MUST define recovery time objectives (RTOs) and recovery point objectives (RPOs) for autonomous operations.
- Rollback MUST be independently callable per ANIF-103 — this is the primary recovery mechanism for autonomous action failures.

### 4.7 CSF Full Mapping Summary

| CSF Function | Primary ANIF Documents                              | Coverage Level |
|--------------|-----------------------------------------------------|----------------|
| GV Govern    | ANIF-001, ANIF-100, ANIF-103, ANIF-104             | High           |
| ID Identify  | ANIF-202, ANIF-307, ANIF-403                        | Medium-High    |
| PR Protect   | ANIF-103, ANIF-205, ANIF-404                        | High           |
| DE Detect    | ANIF-401, ANIF-403, ANIF-405                        | Medium-High    |
| RS Respond   | ANIF-305, ANIF-405, ANIF-406                        | Medium         |
| RC Recover   | ANIF-308, ANIF-405, ANIF-407                        | Medium         |

**Coverage levels**: High = direct controls in ANIF; Medium-High = ANIF controls with supplemental organisational procedures; Medium = ANIF provides foundation but significant organisational supplementation required.

---

### 4.8 ITIL 4 Practice Mapping

ITIL 4 provides a service management framework widely used in telecommunications and enterprise IT. The following table maps ANIF to relevant ITIL 4 practices:

| ITIL 4 Practice                    | ANIF Alignment                                                                   | ANIF Document(s)                |
|------------------------------------|----------------------------------------------------------------------------------|--------------------------------|
| Change Enablement                  | All autonomous changes follow the intent-to-execution pipeline with governance gate. Pre-authorised standard changes defined. | ANIF-104, ANIF-103            |
| Incident Management                | Escalation triggers, P0/P1 classification, and war-room procedures defined.      | ANIF-105, ANIF-405, ANIF-406  |
| Problem Management                 | Closed-loop feedback and continuous learning support root cause analysis.        | ANIF-403, ANIF-405            |
| Service Configuration Management  | Asset registry and bounded action set constrain the configuration space.         | ANIF-202, ANIF-103            |
| Monitoring and Event Management    | Continuous monitoring pipeline feeds anomaly detection and escalation.           | ANIF-401, ANIF-403, ANIF-402  |
| Continual Improvement              | P-12 Continuous Learning embedded in pipeline design; governance review cadence. | ANIF-001 (P-12), ANIF-403     |

#### 4.8.1 ITIL Change Types vs ANIF Change Classification

| ITIL Change Type   | ANIF Equivalent           | Governance Path                                    |
|--------------------|---------------------------|----------------------------------------------------|
| Standard change    | Pre-authorised pattern    | `auto` mode; no manual_review required             |
| Normal change      | Risk-scored intent        | `manual_review` if risk_score ≥ threshold          |
| Emergency change   | P0/P1 incident action     | War-room path per ANIF-105; post-hoc review required |

---

## 5. Conformance Requirements

5.1 Implementations claiming NIST CSF alignment at Tier 3 or higher MUST implement all governance documents referenced in the Govern (GV) row of the summary table (Section 4.7).

5.2 Implementations MUST supplement ANIF controls with organisational procedures for CSF categories rated Medium in Section 4.7.

5.3 The compliance officer MUST perform an annual CSF alignment review using this mapping document and MUST document any gaps in the organisational risk register.

5.4 ANIF audit records (ANIF-107) MUST be treated as primary evidence artefacts for CSF DE and RS function assessments.

5.5 When NIST publishes a new major version of the CSF, the ANIF Working Group MUST update this document within 180 days.

---

## 6. Security Considerations

6.1 This mapping document contains a description of the organisation's security control landscape. It MUST be classified as internal-confidential and access restricted to compliance officers and senior engineers.

6.2 Gaps identified in the CSF mapping (Section 4.7) represent real security risk. Identified gaps MUST be tracked in a remediation register with assigned owners and target dates.

6.3 The CSF alignment does not constitute a certification. Formal NIST CSF assessment MUST be conducted by a qualified assessor.

6.4 Autonomous network operations introduce AI-specific risks not fully addressed by current CSF categories. The ANIF Working Group SHOULD monitor NIST AI Risk Management Framework (AI RMF) guidance and incorporate relevant controls in a future revision.

---

## 7. Operational Considerations

7.1 Operators SHOULD integrate ANIF audit records into their SIEM platform to support continuous CSF monitoring.

7.2 The incident management workflow (ANIF-105, ANIF-405) SHOULD be tested annually through tabletop exercises simulating P0 autonomous operation failures.

7.3 The change enablement mapping (Section 4.8.1) SHOULD be reviewed whenever new intent patterns are added to the pre-authorised standard change catalogue.

7.4 ITIL continual improvement practices require a governance review cadence; the ANIF Working Group SHOULD conduct quarterly reviews of escalation rate, exception rate, and policy violation trends.

---

## Appendix A: Examples

### A.1 CSF Assessment Evidence Package

For a CSF Tier 3 assessment of an ANIF deployment, the following artefacts constitute evidence:

| CSF Function | Evidence Artefact                                                    |
|--------------|----------------------------------------------------------------------|
| GV           | ANIF-001, ANIF-100, ANIF-103, role assignment records                |
| ID           | ANIF-202 asset registry export, ANIF-307 risk model documentation    |
| PR           | ANIF-205 access control policy, ANIF-106 encryption requirements     |
| DE           | ANIF-401 monitoring configuration, ANIF-107 audit records            |
| RS           | ANIF-105 escalation playbook, ANIF-406 incident response records     |
| RC           | ANIF-308 recovery procedures, rollback execution audit records       |

### A.2 ITIL Change Enablement Integration Example

Standard change scenario: `scale_bandwidth` intent for a known traffic pattern in non-production.

1. Intent submitted with `environment: staging`, `action: scale_bandwidth`.
2. Policy Check: matches pre-authorised standard change pattern (ANIF-104).
3. Risk Score: 25 (below warn threshold of 60 for non-prod).
4. Mode Gate: `auto`.
5. Execute: action executes without manual_review.
6. Audit: record written; ITSM ticket auto-created as closed/completed.
7. ITIL: recorded as standard change; no CAB review required.

---

## Appendix B: Change History

| Version | Date       | Author             | Description          |
|---------|------------|--------------------|----------------------|
| 0.1.0   | 2026-04-07 | ANIF Working Group | Initial draft        |
