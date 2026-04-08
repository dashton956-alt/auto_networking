# ANIF-502: Certification Process

| Field        | Value                                        |
|--------------|----------------------------------------------|
| Doc ID       | ANIF-502                                     |
| Series       | Conformance                                  |
| Version      | 0.1.0                                        |
| Status       | Draft                                        |
| Authors      | ANIF Working Group                           |
| Reviewers    | —                                            |
| Approved by  | —                                            |
| Created      | 2026-04-07                                   |
| Last updated | 2026-04-07                                   |
| Replaces     | N/A                                          |
| Related docs | ANIF-500, ANIF-501, ANIF-503                 |

---

## Abstract

This document defines the normative process for achieving ANIF L4 Certified status. It specifies the prerequisites for entering the certification process, the qualifications required of certification bodies, the scope of a certification assessment, the six-step certification process, the artefacts produced, the validity period and suspension conditions of a certificate, and the annual renewal process.

---

## 1. Introduction

### 1.1 Purpose

ANIF L4 certification provides an independent, third-party-verified assurance that an implementation satisfies all ANIF L3 requirements. This document defines the process that governing bodies, certification organisations, and implementing organisations MUST follow to conduct a valid ANIF certification.

### 1.2 Scope

This document applies to:

- Implementing organisations seeking L4 certification
- Third-party certification bodies conducting ANIF assessments
- The ANIF Working Group in its role overseeing the certification programme

### 1.3 Out of Scope

This document does not:

- Define the test cases executed during technical assessment (see ANIF-503)
- Define the conformance levels themselves (see ANIF-501)
- Define vendor, cloud, or telco profile templates (see ANIF-504–506)

### 1.4 Intended Audience

Governance leads and compliance officers at implementing organisations, technical architects preparing for L4 assessment, and personnel at certification bodies conducting ANIF assessments.

---

## 2. Normative References

| Document  | Title                                    |
|-----------|------------------------------------------|
| ANIF-001  | Framework Charter                        |
| ANIF-500  | Conformance Overview                     |
| ANIF-501  | Conformance Level Definitions            |
| ANIF-503  | Test Case Catalogue                      |
| RFC 2119  | Key words for use in RFCs to indicate requirement levels |

---

## 3. Terms and Definitions

**Certification body**: An independent organisation or individual qualified to conduct ANIF L4 certification assessments.

**Assessee**: The organisation seeking L4 certification.

**Pre-assessment**: The preparatory phase in which the assessee submits evidence and the certification body evaluates readiness.

**Findings report**: The formal output of the certification assessment, documenting all test case results, document review findings, and any required remediations.

**Certificate document**: The formal instrument issued by the certification body confirming L4 conformance, including scope, version, issuance date, and expiry date.

**Critical finding**: A finding that indicates failure to satisfy a mandatory requirement. All critical findings MUST be resolved before a certificate is issued.

**Advisory finding**: A finding that indicates a recommended requirement is not satisfied. Advisory findings do not block certificate issuance but MUST be documented in the findings report.

**Certificate suspension**: The temporary removal of L4 status pending investigation or remediation of a P0 violation.

---

## 4. Certification Body Requirements

### 4.1 Eligibility

A certification body MUST meet all of the following criteria to conduct ANIF L4 assessments:

| Criterion | Requirement                                                                                     |
|-----------|-------------------------------------------------------------------------------------------------|
| Independence | The certification body MUST be independent of the assessee; it MUST NOT have a financial interest in the outcome |
| Technical competence | The certification body MUST demonstrate knowledge of the ANIF framework, autonomous networking, and the test cases in ANIF-503 |
| Audit capability | The certification body MUST have personnel experienced in IT or infrastructure audit |
| Conflict of interest | The certification body MUST disclose any prior consulting or advisory relationship with the assessee |
| ANIF registration | The certification body SHOULD be registered with the ANIF Working Group as a recognised certification partner |

### 4.2 Certifier Qualifications

Individual assessors conducting the technical assessment MUST:

- Have reviewed and understood ANIF-001 through ANIF-503
- Have experience executing the test cases defined in ANIF-503, or have completed an equivalent familiarisation programme
- Be able to interpret test results and identify deviations from expected behaviour

### 4.3 Recognised Certification Partners

The ANIF Working Group maintains a register of recognised certification partners. Assessees SHOULD select a certification body from this register. Use of a non-registered body is permitted but MUST be justified and documented.

---

## 5. Prerequisites

Before entering the certification process, the assessee MUST:

| Prerequisite | Requirement                                                                                              |
|--------------|----------------------------------------------------------------------------------------------------------|
| L3 self-assessment | A completed L3 self-assessment checklist MUST be produced and available for submission              |
| Test evidence | Logs from a self-conducted run of TC-001 through TC-005 MUST be available                              |
| Evidence package | The full L3 evidence package as defined in ANIF-501 Section 4.3.4 MUST be assembled                 |
| Stable implementation | The implementation MUST be at a stable, versioned state; changes MUST NOT be made during the certification process without notifying the certifier |
| Named ANIF lead | A named individual MUST be designated as the primary contact for the certification process             |

---

## 6. Certification Process

The ANIF L4 certification process consists of six steps executed in sequence. The certifier and assessee MUST agree on timelines for each step before the process begins.

### 6.1 Step 1 — Pre-Assessment

**Objective**: Confirm that the assessee is ready for certification and that the evidence package is complete.

**Assessee actions:**
- Submit the pre-assessment package to the certification body. The package MUST include:
  - Completed L3 self-assessment checklist
  - Self-conducted test run logs for TC-001 through TC-005
  - Implementation architecture documentation
  - Pipeline configuration records
  - Audit log exports from a representative operating period

**Certifier actions:**
- Review the pre-assessment package for completeness
- Identify any material gaps that MUST be resolved before proceeding
- Issue a pre-assessment readiness determination: Ready / Ready with conditions / Not ready

**Outcome**: Written pre-assessment readiness determination. If "Not ready," the assessee MUST address identified gaps before resubmitting.

**Typical duration**: 5–10 business days

---

### 6.2 Step 2 — Document Review

**Objective**: Verify that the assessee's implementation documentation satisfies the normative requirements of the ANIF document series in scope.

**Certifier actions:**
- Review each ANIF document (ANIF-001 through ANIF-407) against the assessee's evidence package
- For each normative requirement, record: Satisfied / Partially satisfied / Not satisfied
- Identify any critical or advisory findings

**Scope of document review:**

| ANIF Series   | Focus areas                                                  |
|---------------|--------------------------------------------------------------|
| 000 Foundation | Charter, principles, and framework intent                   |
| 100 Governance | Policy schema, intent lifecycle, audit, roles, risk, data residency |
| 200 Architecture | System design and integration points                       |
| 300 Core       | Pipeline implementation, intent validation, decision logic  |
| 400 Operations | Runbooks, monitoring, incident response, change management  |

**Outcome**: Preliminary document review findings recorded in the draft findings report.

**Typical duration**: 10–15 business days

---

### 6.3 Step 3 — Technical Assessment

**Objective**: Execute test cases TC-001 through TC-005 against the live implementation to verify behavioural conformance.

**Environment requirements:**
- The assessment MUST be conducted against the same implementation version submitted in the pre-assessment package
- The certifier MUST have direct access to the implementation or may execute tests under supervision with the assessee present
- The environment MUST be representative of the production configuration

**Test execution:**

| Test Case | Title                | Certifier action                                      |
|-----------|----------------------|-------------------------------------------------------|
| TC-001    | Intent Validation    | Execute all test steps; compare results against ANIF-503 expected values |
| TC-002    | Policy Evaluation    | Execute all test steps including determinism check    |
| TC-003    | Risk Scoring         | Execute all test steps; verify exact score calculations |
| TC-004    | Audit Trail          | Execute all test steps; verify append-only behaviour  |
| TC-005    | Rollback Capability  | Execute all test steps for all four action types      |

The certifier MUST:

- Record all test inputs, outputs, and timestamps
- Note any deviation from expected results defined in ANIF-503
- Classify each deviation as: Critical (blocks certification) or Advisory

**Outcome**: Technical assessment test run logs with pass/fail determination for each test case.

**Typical duration**: 3–5 business days

---

### 6.4 Step 4 — Findings Report

**Objective**: Consolidate all document review and technical assessment findings into a formal report.

The findings report MUST contain:

| Section                    | Content                                                                |
|----------------------------|------------------------------------------------------------------------|
| Executive summary          | Overall determination (Pass / Fail / Conditional)                     |
| Scope statement            | Components and domains assessed                                        |
| Document review findings   | Per-requirement results with evidence references                       |
| Test case results          | Per-test-case pass/fail with log references                            |
| Critical findings          | Enumerated list with specific requirement references                   |
| Advisory findings          | Enumerated list with recommendations                                   |
| Remediation requirements   | For each critical finding: required action, suggested timeline         |
| Certifier declaration      | Signed statement from lead assessor                                    |

The assessee MUST receive the draft findings report and MAY submit a written response within 5 business days. The certifier MUST consider the response before finalising the report.

**Outcome**: Final findings report delivered to assessee.

**Typical duration**: 5 business days (draft); 5 business days for assessee response; 3 business days for final

---

### 6.5 Step 5 — Certification Issuance

**Objective**: Issue the certificate of conformance following resolution of all critical findings.

**Pre-conditions for issuance:**

- All critical findings MUST be remediated and verified by the certifier
- The final findings report MUST be signed by the lead assessor
- The assessee MUST confirm acceptance of the findings report

**Certificate document MUST include:**

| Field                  | Content                                                      |
|------------------------|--------------------------------------------------------------|
| Certificate ID         | Unique identifier assigned by the certification body         |
| Assessee name          | Legal name of the certified organisation                     |
| Product/system name    | Name and version of the certified implementation             |
| ANIF version           | Version of the ANIF specification assessed against           |
| Conformance level      | L4 — Certified                                               |
| Certification scope    | Specific components, domains, and action types in scope      |
| Issuance date          | Date the certificate is issued                               |
| Expiry date            | Exactly 12 months from issuance date                         |
| Certification body     | Name and contact details of the certification body           |
| Lead assessor          | Name of the lead assessor                                    |
| Certificate status     | Active / Suspended / Expired                                 |

**Typical duration**: 3–5 business days after all critical findings are resolved

---

### 6.6 Step 6 — Annual Renewal

**Objective**: Maintain L4 certification through annual re-certification.

An L4 certificate expires 12 months from its issuance date. To maintain L4 status, the organisation MUST:

1. Initiate the renewal process no later than 60 days before expiry
2. Submit an updated evidence package covering changes since the last certification
3. Complete a delta assessment covering: any changed components, any new test case versions, and any open findings from the previous certification
4. Receive a renewed certificate before the expiry date

If a renewed certificate is not issued before the expiry date, the organisation MUST downgrade its conformance claim per the conditions in ANIF-501 Section 6.

---

## 7. Certification Artefacts

The following artefacts are produced by a successful certification engagement and MUST be retained by both the certifier and the assessee:

| Artefact                        | Produced by  | Retention period |
|---------------------------------|--------------|------------------|
| Pre-assessment package          | Assessee     | 3 years          |
| Pre-assessment readiness determination | Certifier | 3 years         |
| Document review findings        | Certifier    | 3 years          |
| Technical assessment test run logs | Certifier  | 3 years          |
| Draft findings report           | Certifier    | 3 years          |
| Assessee response to draft      | Assessee     | 3 years          |
| Final findings report           | Certifier    | 3 years          |
| Remediation evidence            | Assessee     | 3 years          |
| Certificate document            | Certifier    | 3 years (or until superseded) |

---

## 8. Certificate Validity and Suspension

### 8.1 Validity Period

A certificate is valid for 12 months from its issuance date. An expired certificate MUST NOT be represented as active.

### 8.2 Suspension Conditions

A certificate MUST be suspended immediately upon:

- Confirmation of a P0 principle violation (as defined in ANIF-501 Section 6.3)
- Discovery that material information was withheld from the certification assessment
- A significant implementation change that removes a previously certified capability

### 8.3 Suspension Process

Upon suspension:

1. The organisation MUST immediately notify the certification body
2. The certification body MUST update the certificate status to "Suspended"
3. The organisation MUST NOT make active L4 claims during suspension
4. The organisation MUST conduct a root cause analysis and remediation
5. Restoration requires a targeted re-assessment by the certification body covering the affected areas

---

## Appendix A: Certification Process Timeline Summary

| Step | Activity                    | Typical duration     | Key output                          |
|------|-----------------------------|----------------------|-------------------------------------|
| 1    | Pre-assessment              | 5–10 business days   | Readiness determination             |
| 2    | Document review             | 10–15 business days  | Preliminary findings                |
| 3    | Technical assessment        | 3–5 business days    | Test run logs                       |
| 4    | Findings report             | 13 business days     | Final findings report               |
| 5    | Certification issuance      | 3–5 business days    | Certificate document                |
| 6    | Annual renewal              | Ongoing (60 days before expiry) | Renewed certificate       |

Total end-to-end duration (first certification): approximately 7–9 weeks, excluding remediation time.

---

## Appendix B: Change History

| Version | Date       | Author             | Description   |
|---------|------------|--------------------|---------------|
| 0.1.0   | 2026-04-07 | ANIF Working Group | Initial draft |
