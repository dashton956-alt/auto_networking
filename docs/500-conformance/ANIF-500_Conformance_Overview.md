# ANIF-500: Conformance Overview

| Field        | Value                                   |
|--------------|-----------------------------------------|
| Doc ID       | ANIF-500                                |
| Series       | Conformance                             |
| Version      | 0.1.0                                   |
| Status       | Draft                                   |
| Authors      | ANIF Working Group                      |
| Reviewers    | —                                       |
| Approved by  | —                                       |
| Created      | 2026-04-07                              |
| Last updated | 2026-04-07                              |
| Replaces     | N/A                                     |
| Related docs | ANIF-501, ANIF-503                      |

---

## Abstract

This document provides the entry point for the ANIF Conformance series. It defines the purpose of ANIF conformance, distinguishes conformance from regulatory compliance, describes the scope of normative requirements at each conformance level, and explains how organisations progress through the four-level conformance model. It also describes the relationship between conformance and the ANIF prototype implementation.

---

## 1. Introduction

### 1.1 Purpose

The ANIF Conformance series establishes a structured, verifiable basis for claiming that an implementation of the Autonomous Networking and Infrastructure Framework (ANIF) meets its stated design goals: interoperability, safety, governance consistency, and auditability. This document serves as the authoritative entry point for that series, orienting readers toward the appropriate documents for their conformance objectives.

### 1.2 Scope

This document applies to:

- Organisations deploying ANIF-based autonomous networking systems
- Vendors building products or platforms that implement ANIF capabilities
- Cloud providers and telcos declaring ANIF support
- Third-party auditors conducting L4 certification assessments

### 1.3 Out of Scope

This document does not:

- Define the detailed requirements for individual conformance levels (see ANIF-501)
- Specify the certification process (see ANIF-502)
- Enumerate test cases (see ANIF-503)
- Provide vendor, cloud, or telco profile templates (see ANIF-504 through ANIF-506)
- Define regulatory compliance obligations, which remain the responsibility of the implementing organisation

### 1.4 Intended Audience

This document is intended for:

- Technical architects planning an ANIF implementation
- Project leads overseeing an ANIF adoption programme
- Procurement teams evaluating ANIF-conformant vendor products
- Auditors seeking orientation before engaging with the detailed conformance series

---

## 2. Normative References

The following documents are normative for the interpretation of this document:

| Document  | Title                                    |
|-----------|------------------------------------------|
| ANIF-001  | Framework Charter                        |
| ANIF-100  | Governance Overview                      |
| ANIF-101  | Policy Schema                            |
| ANIF-300  | Core Framework Overview                  |
| ANIF-501  | Conformance Level Definitions            |
| ANIF-502  | Certification Process                    |
| ANIF-503  | Test Case Catalogue                      |
| RFC 2119  | Key words for use in RFCs to indicate requirement levels |

---

## 3. Terms and Definitions

**Conformance**: The state in which an implementation satisfies all mandatory requirements of the ANIF specification at a declared level.

**Compliance**: Adherence to external regulations, laws, or standards (e.g., GDPR, PCI-DSS, SOC 2). Compliance is distinct from ANIF conformance and is the responsibility of the implementing organisation.

**Conformance Level**: One of four levels (L1 through L4) that characterise the degree of ANIF implementation completeness and verifiability.

**Normative Requirement**: A requirement expressed using RFC 2119 keywords (MUST, MUST NOT, SHOULD, SHOULD NOT, MAY) that an implementation MUST satisfy to claim a given conformance level.

**Self-Assessment**: An evaluation conducted by the implementing organisation itself, without independent third-party verification.

**Certification**: A conformance determination made by a qualified, independent third-party auditor following the process defined in ANIF-502.

**Evidence Package**: The collection of artefacts (documents, test logs, configuration records, audit trails) that substantiate a conformance claim.

**Downgrade**: The reduction of a declared conformance level due to failure to maintain requirements, as defined in ANIF-501.

---

## 4. Conformance and the ANIF Framework

### 4.1 Why Conformance Matters

Autonomous networking systems make decisions that affect live infrastructure. Without a structured conformance model, different implementations of ANIF may diverge in safety posture, audit capability, or policy enforcement behaviour — reducing interoperability and increasing governance risk. ANIF conformance provides a shared vocabulary and verifiable baseline that procurement, operations, and audit teams can rely on.

Conformance serves three primary goals:

| Goal                      | Description                                                                                 |
|---------------------------|---------------------------------------------------------------------------------------------|
| Interoperability          | Conformant implementations share a common intent schema, policy model, and audit interface  |
| Safety                    | Conformance requires that core safety principles (P-01 through P-12) are implemented        |
| Governance consistency    | Conformance ensures that governance gates, audit trails, and rollback capability are present |

### 4.2 Conformance vs Compliance

These terms are frequently confused. ANIF draws a clear distinction:

| Dimension        | Conformance                                       | Compliance                                     |
|------------------|---------------------------------------------------|------------------------------------------------|
| Reference        | ANIF specification documents                      | External regulations and standards             |
| Determined by    | ANIF Working Group or ANIF-authorised auditors    | Regulatory bodies, internal legal/compliance   |
| Scope            | Technical implementation of ANIF requirements    | Organisational obligations under law or contract |
| Relationship     | An ANIF-conformant system MAY also be compliant   | Compliance does not imply ANIF conformance     |

An organisation MUST NOT represent ANIF conformance as equivalent to regulatory compliance. Conversely, achieving regulatory compliance does not satisfy ANIF conformance requirements unless the implementation independently meets ANIF normative requirements.

### 4.3 Normative Document Scope by Level

The following table identifies which ANIF document series are normative for each conformance level. An implementation MUST satisfy all normative documents for its declared level.

| Conformance Level | Normative Document Series                                        |
|-------------------|------------------------------------------------------------------|
| L1 Aware          | ANIF-001 (Charter); self-assessment checklist only              |
| L2 Aligned        | ANIF-001 through ANIF-107 (Foundation + Governance)             |
| L3 Conformant     | ANIF-001 through ANIF-407 (all series through Operations); TC-001–TC-005 passed |
| L4 Certified      | All of L3; ANIF-500–503 process completed; third-party verified |

---

## 5. The Four-Level Conformance Model

### 5.1 Model Overview

ANIF defines four conformance levels that represent a progressive maturity journey from initial awareness through full third-party certification. Each level builds on the previous; an organisation cannot claim level N without satisfying all requirements of levels 1 through N−1.

| Level | Name        | Verification       | Key Characteristic                                     |
|-------|-------------|--------------------|--------------------------------------------------------|
| L1    | Aware        | Self-declaration  | Organisation has reviewed ANIF and documented its gap analysis |
| L2    | Aligned      | Self-assessment   | Core governance and policy documents are implemented   |
| L3    | Conformant   | Self-assessment + test cases | Full framework implemented and tested       |
| L4    | Certified    | Third-party audit | Independent verification of L3 conformance             |

### 5.2 L1 — Aware

An L1-Aware organisation has engaged with the ANIF framework at a foundational level. It has reviewed the framework documentation, assessed its current state against ANIF requirements, and documented the resulting gap analysis. L1 does not require any implementation work; it establishes an informed baseline for the adoption roadmap.

### 5.3 L2 — Aligned

An L2-Aligned organisation has implemented the governance and policy foundations of ANIF. This means that the documents covering governance structure, policy schema, intent lifecycle, and audit requirements (ANIF-001 through ANIF-107) are satisfied. An L2 organisation maintains an audit trail and a completed self-assessment checklist that can be shared with stakeholders.

### 5.4 L3 — Conformant

An L3-Conformant organisation has implemented the full ANIF framework across all core domains — architecture, core pipeline, and operations — and has demonstrated this through passing the mandatory test cases TC-001 through TC-005 defined in ANIF-503. L3 is self-assessed but requires documented test evidence.

### 5.5 L4 — Certified

An L4-Certified organisation has had its L3 conformance independently verified by a qualified third-party auditor following the process defined in ANIF-502. Certification is time-limited to 12 months and may be suspended in the event of a P0 principle violation.

---

## 6. Progressing Through Conformance Levels

### 6.1 Typical Adoption Pathway

Organisations are not required to progress through all four levels. However, the following pathway represents the intended adoption arc:

1. **Initiate (L1)**: Review ANIF documentation, assign an ANIF lead, complete the gap analysis and self-assessment checklist.
2. **Govern (L2)**: Implement governance structure, policy schema, intent lifecycle management, and audit logging. Complete the L2 self-assessment.
3. **Implement (L3)**: Deploy the full pipeline (Intent → Validate → Policy Check → Risk Score → Decision → Governance Gate → Action → Audit). Pass test cases TC-001 through TC-005.
4. **Certify (L4)**: Engage a qualified certification body, submit the evidence package, pass the technical assessment, receive the certificate.

### 6.2 Partial Conformance

An organisation MAY declare partial conformance when it has fully satisfied one level for a subset of domains while working toward the next level overall. For example, an organisation MAY declare "L2-Aligned for Governance, working toward L3 for Core." Partial conformance declarations MUST clearly identify the scope to which each level applies.

### 6.3 Maintaining Conformance

Conformance is not a one-time determination. An organisation MUST continue to satisfy all requirements for its declared level. Changes to the implementation that remove or degrade previously satisfied requirements MUST trigger a re-assessment. Failure to maintain requirements results in downgrade as defined in ANIF-501.

---

## 7. Conformance and the Prototype Implementation

The ANIF prototype implementation (see ANIF-300 series) serves as the reference implementation against which conformance test cases are developed. The prototype demonstrates the pipeline defined in the ANIF framework and is the subject of test cases TC-001 through TC-005 in ANIF-503.

The prototype MUST be understood as a reference, not a production requirement. An implementation:

- MUST satisfy the normative behavioural requirements of ANIF (schema, pipeline stages, audit trail, rollback)
- SHOULD use the prototype as a reference for expected inputs, outputs, and API shapes
- MAY differ from the prototype in architecture, technology stack, and internal design, provided that observable behaviour satisfies the normative requirements

---

## Appendix A: Examples

### A.1 Example Conformance Declaration

The following example illustrates a well-formed ANIF conformance declaration:

```
Organisation: Acme Networks Ltd
Product: NetOrchestrator v3.2
ANIF Version: 0.1.0
Conformance Level: L3 — Conformant
Verification method: Self-assessment
Self-assessment date: 2026-04-07
Test cases passed: TC-001, TC-002, TC-003, TC-004, TC-005
Evidence package location: [internal document management system reference]
Scope: Production intent pipeline; excludes optical transport domain
```

### A.2 Conformance Level Selection Guide

| Organisation situation                                     | Recommended initial target |
|------------------------------------------------------------|----------------------------|
| Early-stage evaluation, no implementation begun           | L1                         |
| Governance and policy work in progress                    | L2                         |
| Full pipeline implemented, testing underway               | L3                         |
| Customer or procurement requirement for third-party proof | L4                         |

---

## Appendix B: Change History

| Version | Date       | Author             | Description     |
|---------|------------|--------------------|-----------------|
| 0.1.0   | 2026-04-07 | ANIF Working Group | Initial draft   |
