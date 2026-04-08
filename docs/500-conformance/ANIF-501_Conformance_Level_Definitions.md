# ANIF-501: Conformance Level Definitions

| Field        | Value                                        |
|--------------|----------------------------------------------|
| Doc ID       | ANIF-501                                     |
| Series       | Conformance                                  |
| Version      | 0.1.0                                        |
| Status       | Draft                                        |
| Authors      | ANIF Working Group                           |
| Reviewers    | —                                            |
| Approved by  | —                                            |
| Created      | 2026-04-07                                   |
| Last updated | 2026-04-07                                   |
| Replaces     | N/A                                          |
| Related docs | ANIF-500, ANIF-502, ANIF-503                 |

---

## Abstract

This document provides the normative definitions of the four ANIF conformance levels: L1 Aware, L2 Aligned, L3 Conformant, and L4 Certified. For each level it specifies mandatory and recommended requirements, the evidence required to substantiate a claim, the ANIF document series that must be satisfied, and the verification method applicable to the level. It also defines downgrade conditions, partial conformance rules, and the process for declaring a conformance level.

---

## 1. Introduction

### 1.1 Purpose

This document is the normative authority for determining whether an implementation qualifies for a given ANIF conformance level. All conformance claims MUST be evaluated against the requirements defined herein.

### 1.2 Scope

This document covers all four conformance levels (L1–L4) and applies to:

- Implementing organisations conducting self-assessments
- Vendors preparing conformance profiles (ANIF-504 through ANIF-506)
- Third-party auditors performing L4 certification assessments (ANIF-502)

### 1.3 Out of Scope

This document does not define:

- The test cases required for L3 (see ANIF-503)
- The certification body selection criteria or process (see ANIF-502)
- Vendor, cloud, or telco-specific profile templates (see ANIF-504–506)

### 1.4 Intended Audience

Technical architects, governance leads, compliance officers, and third-party auditors.

---

## 2. Normative References

| Document  | Title                                    |
|-----------|------------------------------------------|
| ANIF-001  | Framework Charter                        |
| ANIF-100  | Governance Overview                      |
| ANIF-101  | Policy Schema                            |
| ANIF-102  | Intent Lifecycle                         |
| ANIF-103  | Audit Requirements                       |
| ANIF-104  | Role and Permission Model                |
| ANIF-105  | Risk Scoring Model                       |
| ANIF-106  | Data Residency Policy                    |
| ANIF-107  | Change Management                        |
| ANIF-300  | Core Framework Overview                  |
| ANIF-500  | Conformance Overview                     |
| ANIF-503  | Test Case Catalogue                      |
| RFC 2119  | Key words for use in RFCs to indicate requirement levels |

---

## 3. Terms and Definitions

**Mandatory requirement**: A requirement expressed with the keyword MUST or MUST NOT. Failure to satisfy any mandatory requirement means the level cannot be claimed.

**Recommended requirement**: A requirement expressed with the keyword SHOULD or SHOULD NOT. Non-conformance with a recommended requirement is permitted only where a documented rationale exists.

**Evidence**: Artefacts — documents, configuration records, test run logs, audit exports — that demonstrate satisfaction of a requirement.

**Self-declaration**: A public statement by the implementing organisation, without supporting evidence package, asserting a conformance level. Applicable only at L1.

**Self-assessment**: A documented evaluation by the implementing organisation using the ANIF checklist and, at L3, test case evidence. Applicable at L2 and L3.

**Third-party certification**: An independent determination of conformance by a qualified certification body. Required for L4.

---

## 4. Conformance Level Definitions

### 4.1 L1 — Aware

#### 4.1.1 Description

L1 Aware is the entry-level conformance state. An L1 organisation has studied the ANIF framework, assessed its current state against ANIF requirements, and documented the resulting gap analysis. L1 does not require any implementation work; it establishes a credible, informed baseline for a structured ANIF adoption programme.

#### 4.1.2 Mandatory Requirements

| ID      | Requirement                                                                                           |
|---------|-------------------------------------------------------------------------------------------------------|
| L1-M-01 | The organisation MUST have reviewed ANIF-001 (Framework Charter) and ANIF-500 (Conformance Overview)  |
| L1-M-02 | The organisation MUST have documented its current networking automation state                         |
| L1-M-03 | The organisation MUST have completed a gap analysis mapping current state to ANIF requirements        |
| L1-M-04 | The organisation MUST have assigned a named ANIF lead responsible for the adoption programme         |
| L1-M-05 | The organisation MUST NOT claim a level higher than L1 on the basis of L1 activities alone           |

#### 4.1.3 Recommended Requirements

| ID      | Requirement                                                                                    |
|---------|------------------------------------------------------------------------------------------------|
| L1-S-01 | The organisation SHOULD complete the ANIF-500 self-assessment checklist                        |
| L1-S-02 | The organisation SHOULD publish its L1 declaration internally to relevant stakeholders         |
| L1-S-03 | The organisation SHOULD define a target date for progressing to L2                             |

#### 4.1.4 Evidence Required

| Artefact                        | Required |
|---------------------------------|----------|
| Gap analysis document           | MUST     |
| Named ANIF lead designation     | MUST     |
| L1 self-declaration statement   | MUST     |
| Completed self-assessment checklist | SHOULD |

#### 4.1.5 Verification Method

L1 is self-declared. No independent review is required. The organisation MUST retain evidence for a minimum of 12 months.

---

### 4.2 L2 — Aligned

#### 4.2.1 Description

L2 Aligned means that the governance and policy foundations of ANIF have been implemented and are operational. The documents covering governance structure, policy schema, intent lifecycle management, role and permission model, audit logging, data residency, and change management (ANIF-001 through ANIF-107) are satisfied. A completed self-assessment checklist is required.

#### 4.2.2 Mandatory Requirements

| ID      | Requirement                                                                                                        |
|---------|--------------------------------------------------------------------------------------------------------------------|
| L2-M-01 | The organisation MUST satisfy all L1 requirements                                                                  |
| L2-M-02 | The organisation MUST have implemented a governance structure conformant with ANIF-100                             |
| L2-M-03 | The organisation MUST have deployed a policy schema conformant with ANIF-101                                       |
| L2-M-04 | The organisation MUST have implemented an intent lifecycle management process conformant with ANIF-102             |
| L2-M-05 | The organisation MUST have implemented audit logging conformant with ANIF-103                                      |
| L2-M-06 | The organisation MUST have defined roles and permissions conformant with ANIF-104                                  |
| L2-M-07 | The organisation MUST have implemented a risk scoring model conformant with ANIF-105                               |
| L2-M-08 | The organisation MUST have implemented a data residency policy conformant with ANIF-106                           |
| L2-M-09 | The organisation MUST have implemented a change management process conformant with ANIF-107                        |
| L2-M-10 | The organisation MUST have produced a completed L2 self-assessment checklist                                      |
| L2-M-11 | The self-assessment checklist MUST cover all ANIF-001 through ANIF-107 requirements                               |
| L2-M-12 | Any gaps identified in the self-assessment MUST be documented with a remediation plan and target date             |

#### 4.2.3 Recommended Requirements

| ID      | Requirement                                                                                              |
|---------|----------------------------------------------------------------------------------------------------------|
| L2-S-01 | The organisation SHOULD have implemented monitoring for audit log integrity                              |
| L2-S-02 | The organisation SHOULD have performed a tabletop test of the governance gate decision process           |
| L2-S-03 | The organisation SHOULD have trained relevant personnel on ANIF principles P-01 through P-12            |
| L2-S-04 | The organisation SHOULD maintain its self-assessment checklist under version control                     |

#### 4.2.4 Evidence Required

| Artefact                              | Required |
|---------------------------------------|----------|
| L1 evidence package                   | MUST     |
| Governance structure documentation    | MUST     |
| Implemented policy schema instance    | MUST     |
| Intent lifecycle process document     | MUST     |
| Audit log implementation evidence     | MUST     |
| Role and permission model document    | MUST     |
| Completed L2 self-assessment checklist | MUST    |
| Remediation plan for identified gaps  | MUST (if gaps exist) |

#### 4.2.5 ANIF Document Series That MUST Be Satisfied

ANIF-001, ANIF-100, ANIF-101, ANIF-102, ANIF-103, ANIF-104, ANIF-105, ANIF-106, ANIF-107

#### 4.2.6 Verification Method

L2 is self-assessed. The implementing organisation conducts the assessment using the ANIF self-assessment checklist. No third-party review is mandatory, but SHOULD be considered for high-risk environments.

---

### 4.3 L3 — Conformant

#### 4.3.1 Description

L3 Conformant means that the full ANIF framework has been implemented across all core domains — foundation, governance, architecture, core pipeline, and operations — and that this has been demonstrated through passing the mandatory test cases TC-001 through TC-005. L3 is the minimum level for production deployment of an autonomous networking system under the ANIF framework.

#### 4.3.2 Mandatory Requirements

| ID      | Requirement                                                                                                         |
|---------|---------------------------------------------------------------------------------------------------------------------|
| L3-M-01 | The organisation MUST satisfy all L2 requirements                                                                   |
| L3-M-02 | The organisation MUST have implemented the full ANIF pipeline: Intent → Validate → Policy Check → Risk Score → Decision → Governance Gate → Action → Audit |
| L3-M-03 | The implementation MUST satisfy all ANIF-200 series (Architecture) documents                                       |
| L3-M-04 | The implementation MUST satisfy all ANIF-300 series (Core) documents                                               |
| L3-M-05 | The implementation MUST satisfy all ANIF-400 series (Operations) documents                                         |
| L3-M-06 | The implementation MUST pass test case TC-001 (Intent Validation) as defined in ANIF-503                           |
| L3-M-07 | The implementation MUST pass test case TC-002 (Policy Evaluation) as defined in ANIF-503                           |
| L3-M-08 | The implementation MUST pass test case TC-003 (Risk Scoring) as defined in ANIF-503                                |
| L3-M-09 | The implementation MUST pass test case TC-004 (Audit Trail) as defined in ANIF-503                                 |
| L3-M-10 | The implementation MUST pass test case TC-005 (Rollback Capability) as defined in ANIF-503                         |
| L3-M-11 | All five test cases MUST be executed against the same implementation version                                       |
| L3-M-12 | Test run logs MUST be retained as part of the evidence package                                                     |
| L3-M-13 | The implementation MUST support all four action types: reroute_traffic, apply_qos, scale_bandwidth, isolate_segment |
| L3-M-14 | The implementation MUST support all three governance modes: auto, manual_review, block                             |
| L3-M-15 | The implementation MUST implement all twelve principles P-01 through P-12                                          |

#### 4.3.3 Recommended Requirements

| ID      | Requirement                                                                                                    |
|---------|----------------------------------------------------------------------------------------------------------------|
| L3-S-01 | The organisation SHOULD execute test cases in an environment representative of production                      |
| L3-S-02 | The organisation SHOULD have a documented incident response plan for autonomous action failures                 |
| L3-S-03 | The implementation SHOULD achieve determinism scores as specified in TC-002 and TC-003                         |
| L3-S-04 | The organisation SHOULD conduct L3 self-assessment annually and after significant implementation changes       |

#### 4.3.4 Evidence Required

| Artefact                                        | Required |
|-------------------------------------------------|----------|
| L2 evidence package                             | MUST     |
| Completed L3 self-assessment checklist          | MUST     |
| Test run logs for TC-001 through TC-005         | MUST     |
| Implementation architecture documentation       | MUST     |
| Pipeline configuration records                  | MUST     |
| Rollback capability demonstration logs          | MUST     |
| Principle implementation mapping (P-01–P-12)    | MUST     |

#### 4.3.5 ANIF Document Series That MUST Be Satisfied

All of L2 plus: ANIF-200 series, ANIF-300 series, ANIF-400 series

#### 4.3.6 Test Cases That MUST Pass

TC-001, TC-002, TC-003, TC-004, TC-005 (see ANIF-503 for full definitions)

#### 4.3.7 Verification Method

L3 is self-assessed with documented test evidence. The implementing organisation runs all five test cases and retains the results. Although third-party review is not mandatory for L3, it is a prerequisite for L4 certification.

---

### 4.4 L4 — Certified

#### 4.4.1 Description

L4 Certified means that an independent, qualified third-party auditor has verified that the implementation satisfies all L3 requirements and has issued a certificate of conformance. L4 is the highest ANIF conformance level and is the appropriate target for environments where procurement requirements, regulatory context, or contractual obligations demand independent assurance.

#### 4.4.2 Mandatory Requirements

| ID      | Requirement                                                                                                              |
|---------|--------------------------------------------------------------------------------------------------------------------------|
| L4-M-01 | The organisation MUST satisfy all L3 requirements                                                                        |
| L4-M-02 | The organisation MUST engage a certification body that meets the criteria in ANIF-502                                   |
| L4-M-03 | The organisation MUST complete the pre-assessment submission as defined in ANIF-502                                      |
| L4-M-04 | The certifier MUST review all ANIF document implementations in scope                                                     |
| L4-M-05 | The certifier MUST execute all five test cases TC-001 through TC-005 against the live implementation                     |
| L4-M-06 | The certifier MUST issue a findings report identifying any pass/fail items and required remediations                     |
| L4-M-07 | All critical findings MUST be remediated before the certificate is issued                                                |
| L4-M-08 | The organisation MUST not claim L4 status before the certificate document has been issued by the certifier              |
| L4-M-09 | The organisation MUST re-certify annually                                                                                |
| L4-M-10 | The organisation MUST suspend its L4 claim immediately upon any confirmed P0 principle violation                        |

#### 4.4.3 Recommended Requirements

| ID      | Requirement                                                                                            |
|---------|--------------------------------------------------------------------------------------------------------|
| L4-S-01 | The organisation SHOULD maintain a public conformance register entry for its L4 certificate            |
| L4-S-02 | The organisation SHOULD engage the same certification body for annual renewals to enable continuity    |
| L4-S-03 | The organisation SHOULD conduct internal re-assessment at six-month intervals between certifications   |

#### 4.4.4 Evidence Required

| Artefact                                           | Required |
|----------------------------------------------------|----------|
| L3 evidence package                                | MUST     |
| Pre-assessment submission package                  | MUST     |
| Certifier's document review report                 | MUST     |
| Certifier's test run logs (TC-001–TC-005)          | MUST     |
| Certifier's findings report                        | MUST     |
| Remediation evidence for any critical findings     | MUST (if applicable) |
| Issued certificate document                        | MUST     |

#### 4.4.5 ANIF Document Series That MUST Be Satisfied

All of L3 plus: ANIF-500, ANIF-501, ANIF-502, ANIF-503

#### 4.4.6 Verification Method

Third-party certification per ANIF-502. The certifier must be independent of the implementing organisation and must meet the qualification criteria defined in ANIF-502 Section 4.

---

## 5. Conformance Requirements — Summary Table

| Requirement                        | L1 | L2 | L3 | L4 |
|------------------------------------|----|----|----|----|
| Gap analysis documented            | M  | M  | M  | M  |
| ANIF-001–107 satisfied             | —  | M  | M  | M  |
| ANIF-200–407 satisfied             | —  | —  | M  | M  |
| TC-001 through TC-005 passed       | —  | —  | M  | M  |
| Self-assessment checklist complete | S  | M  | M  | M  |
| Audit trail operational            | —  | M  | M  | M  |
| Test run logs retained             | —  | —  | M  | M  |
| Third-party certification          | —  | —  | —  | M  |
| Annual re-certification            | —  | —  | —  | M  |

M = MUST satisfy; S = SHOULD satisfy; — = not applicable at this level

---

## 6. Downgrade Conditions

### 6.1 Triggers for Downgrade

An organisation's claimed conformance level MUST be downgraded when any of the following conditions are met:

| Trigger                                                                 | Resulting downgrade              |
|-------------------------------------------------------------------------|----------------------------------|
| Implementation change removes a previously satisfied MUST requirement   | To the highest level still satisfied |
| L4 certificate expires without renewal                                  | From L4 to L3 (if L3 still satisfied) |
| Confirmed P0 principle violation (any principle in P-01–P-12)           | Immediate suspension pending review |
| Failure to retain required evidence artefacts                           | To the highest evidenced level   |
| Self-assessment reveals material gap in a previously satisfied requirement | To the highest fully satisfied level |

### 6.2 Downgrade Process

When a downgrade trigger is identified, the organisation MUST:

1. Suspend any public claims of the affected level within 5 business days
2. Document the trigger and root cause
3. Develop a remediation plan with a target restoration date
4. Re-assess once remediation is complete before restoring the level claim

### 6.3 P0 Violations

A P0 violation is defined as a confirmed breach of any of the twelve ANIF core principles (P-01 through P-12) that results in an uncontrolled autonomous action, a loss of audit trail integrity, or a suppression of the human override capability. P0 violations MUST be escalated to the ANIF Working Group if the implementing organisation holds L4 certification.

---

## 7. Partial Conformance

### 7.1 Partial Conformance Declaration

An organisation MAY declare partial conformance where it has fully satisfied the requirements of one level for a defined subset of its ANIF implementation scope, while working toward a higher level for the overall scope. Partial conformance declarations:

- MUST clearly identify the domain or component scope to which each level applies
- MUST NOT imply full-scope conformance at the higher level
- SHOULD include a roadmap for achieving full-scope conformance at the target level

### 7.2 Partial Conformance Example

```
Organisation: Acme Networks Ltd
Full scope: Governance (L2), Core Pipeline (working toward L3)
Partial claim: L2-Aligned for Governance domain (ANIF-100–107 satisfied)
Target: L3-Conformant for full scope by Q3 2026
```

---

## Appendix A: Self-Assessment Checklist Structure

The L2 and L3 self-assessment checklists MUST be structured as follows:

| Column        | Content                                                        |
|---------------|----------------------------------------------------------------|
| Requirement ID | ANIF document section and requirement identifier             |
| Requirement   | Full text of the normative requirement                         |
| Status        | Satisfied / Partially satisfied / Not satisfied / Not applicable |
| Evidence      | Reference to evidence artefact(s)                             |
| Notes         | Any relevant context or qualification                         |
| Remediation   | Required action and target date (if not satisfied)            |

---

## Appendix B: Change History

| Version | Date       | Author             | Description   |
|---------|------------|--------------------|---------------|
| 0.1.0   | 2026-04-07 | ANIF Working Group | Initial draft |
