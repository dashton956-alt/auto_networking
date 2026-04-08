# ANIF-504: Vendor Profile Template

| Field        | Value                                              |
|--------------|----------------------------------------------------|
| Doc ID       | ANIF-504                                           |
| Series       | Conformance                                        |
| Version      | 0.1.0                                              |
| Status       | Draft                                              |
| Authors      | ANIF Working Group                                 |
| Reviewers    | —                                                  |
| Approved by  | —                                                  |
| Created      | 2026-04-07                                         |
| Last updated | 2026-04-07                                         |
| Replaces     | N/A                                                |
| Related docs | ANIF-500, ANIF-501, ANIF-505, ANIF-506             |

---

## Abstract

This document defines the standard template that vendors use to declare their ANIF conformance profile. A completed vendor profile documents the vendor's product capabilities, declared conformance level, action type support, intent schema compatibility, any deliberate deviations from ANIF normative requirements, and certification status. Completed profiles enable procurement teams, integrators, and operators to make informed decisions about ANIF-conformant vendor products.

---

## 1. Introduction

### 1.1 Purpose

Vendors implementing ANIF capabilities in their products MUST produce a completed vendor profile using the template defined in this document. The profile enables consumers of vendor products to understand the precise scope of ANIF support, any deviations, and the level at which conformance has been claimed.

### 1.2 Scope

This document applies to:

- Networking equipment vendors implementing ANIF capabilities
- Software vendors building network automation platforms, orchestrators, or controllers
- Any vendor producing a product that claims ANIF conformance

Cloud providers and telecommunications operators SHOULD use the specialised templates defined in ANIF-505 and ANIF-506, which extend this base template.

### 1.3 Out of Scope

This document does not define:

- The certification process for achieving L4 (see ANIF-502)
- Cloud-provider-specific capability mappings (see ANIF-505)
- Telco-specific network domain coverage (see ANIF-506)

### 1.4 Intended Audience

Vendor product managers and technical architects preparing conformance profiles; procurement teams evaluating vendor products; integration engineers planning ANIF deployments.

---

## 2. Normative References

| Document  | Title                                    |
|-----------|------------------------------------------|
| ANIF-101  | Policy Schema                            |
| ANIF-300  | Core Framework Overview                  |
| ANIF-500  | Conformance Overview                     |
| ANIF-501  | Conformance Level Definitions            |
| ANIF-502  | Certification Process                    |
| RFC 2119  | Key words for use in RFCs to indicate requirement levels |

---

## 3. Terms and Definitions

**Native support**: An action type or schema field is natively supported when the product implements it without requiring any external adapter, custom scripting, or manual operator intervention.

**Custom adapter**: An extension module, plugin, or scripted integration that a customer or partner must build or configure to enable support for a capability not natively provided by the product.

**Deviation**: A deliberate, documented departure from a ANIF normative (MUST-level) requirement. Deviations MUST be declared; undeclared deviations that are later discovered may result in downgrade or certification suspension.

**Profile version**: The version of the vendor profile document, which MUST be updated whenever the product version, conformance level, or capability declarations change.

---

## 4. Profile Requirements

### 4.1 Profile Maintenance

A vendor MUST:

- Produce a vendor profile for each product version that claims ANIF conformance
- Update the profile within 30 days of any change that affects a declared capability, deviation, or conformance level
- Make the profile available to customers and integration partners upon request
- Retain superseded profile versions for a minimum of 24 months

### 4.2 Deviation Declarations

Any deviation from a ANIF MUST-level requirement MUST be declared in the profile. For each deviation:

- The specific ANIF requirement MUST be identified by document ID and section
- The nature of the deviation MUST be described precisely
- A rationale MUST be provided
- A roadmap for resolving the deviation SHOULD be included

### 4.3 Certification Claims

A vendor MUST NOT claim L4 certification in a profile unless a valid, unexpired certificate has been issued by a qualified certification body per ANIF-502. Self-declared conformance at L1, L2, or L3 MUST be clearly labelled as self-declared.

---

## 5. Vendor Profile Template

The following is the normative template. Vendors MUST copy this template and complete all fields. Fields marked [REQUIRED] must not be left blank. Fields marked [IF APPLICABLE] may be omitted only when they genuinely do not apply, with a brief explanation.

---

```markdown
# ANIF Vendor Conformance Profile

## Profile Header

| Field                     | Value                                                        |
|---------------------------|--------------------------------------------------------------|
| Profile version           | [REQUIRED: e.g., 1.0.0]                                     |
| Vendor name               | [REQUIRED: Legal entity name]                               |
| Product name              | [REQUIRED: Product/platform name]                           |
| Product version           | [REQUIRED: Version string]                                  |
| ANIF version              | [REQUIRED: e.g., 0.1.0]                                     |
| Declared conformance level | [REQUIRED: L1 / L2 / L3 / L4]                             |
| Verification method       | [REQUIRED: Self-declaration / Self-assessment / Third-party certified] |
| Profile date              | [REQUIRED: ISO 8601 date]                                   |
| Profile author            | [REQUIRED: Name and role]                                   |
| Contact email             | [REQUIRED]                                                  |

---

## Capability Declarations

### Action Type Support

| Action Type       | Support level  | Notes                                              |
|-------------------|----------------|----------------------------------------------------|
| reroute_traffic   | [Native / Custom adapter / Not supported] | [Brief description of implementation] |
| apply_qos         | [Native / Custom adapter / Not supported] | [Brief description of implementation] |
| scale_bandwidth   | [Native / Custom adapter / Not supported] | [Brief description of implementation] |
| isolate_segment   | [Native / Custom adapter / Not supported] | [Brief description of implementation] |

### Governance Mode Support

| Governance mode  | Supported | Notes                              |
|------------------|-----------|------------------------------------|
| auto             | [Yes / No] | [Any conditions or limitations]   |
| manual_review    | [Yes / No] | [Any conditions or limitations]   |
| block            | [Yes / No] | [Any conditions or limitations]   |

### Pipeline Stage Support

| Pipeline stage     | Implemented | Notes                              |
|--------------------|-------------|------------------------------------|
| Intent validation  | [Yes / No / Partial] | [Description]              |
| Policy check       | [Yes / No / Partial] | [Description]              |
| Risk scoring       | [Yes / No / Partial] | [Description]              |
| Decision           | [Yes / No / Partial] | [Description]              |
| Governance gate    | [Yes / No / Partial] | [Description]              |
| Action execution   | [Yes / No / Partial] | [Description]              |
| Audit log          | [Yes / No / Partial] | [Description]              |
| Rollback           | [Yes / No / Partial] | [Description]              |

---

## Schema Compatibility

### Intent Schema Field Support

| Field                        | Supported | Notes / Vendor-specific behaviour  |
|------------------------------|-----------|------------------------------------|
| action                       | [Yes / No / Extended] | [Description]          |
| target                       | [Yes / No / Extended] | [Description]          |
| environment                  | [Yes / No / Extended] | [Description]          |
| priority                     | [Yes / No / Extended] | [Description]          |
| constraints.encryption       | [Yes / No / Extended] | [Description]          |
| constraints.allowed_zones    | [Yes / No / Extended] | [Description]          |
| constraints.availability     | [Yes / No / Extended] | [Description]          |
| constraints.latency_ms       | [Yes / No / Extended] | [Description]          |
| constraints.pci_compliant    | [Yes / No / Extended] | [Description]          |

### Vendor-Specific Schema Extensions

[IF APPLICABLE: List any vendor-specific intent fields added beyond the ANIF standard schema. For each field:]

| Extension field       | Type    | Purpose                               | Impact on interoperability  |
|-----------------------|---------|---------------------------------------|-----------------------------|
| [field name]          | [type]  | [description]                         | [None / Limited / Requires adapter] |

Extensions MUST NOT conflict with existing ANIF schema fields. Extension field names MUST use a vendor-specific prefix (e.g., `acme_`).

---

## Deviations

[IF APPLICABLE: List all deliberate deviations from ANIF MUST-level requirements. If there are no deviations, state "None".]

### Deviation 1

| Field           | Value                                                        |
|-----------------|--------------------------------------------------------------|
| Deviation ID    | DEV-001                                                      |
| ANIF requirement | [Document ID, section, and requirement text]               |
| Nature of deviation | [Precise description of how the implementation differs] |
| Rationale       | [Business, technical, or regulatory reason for the deviation] |
| Impact          | [Effect on interoperability, safety, or governance]         |
| Remediation plan | [Target date and approach for resolving the deviation, or "No current plan" with justification] |

---

## Principle Implementation

| Principle | Status | Notes                                  |
|-----------|--------|----------------------------------------|
| P-01 Reversibility        | [Implemented / Partial / Not implemented] | [Description] |
| P-02 Auditability         | [Implemented / Partial / Not implemented] | [Description] |
| P-03 Determinism          | [Implemented / Partial / Not implemented] | [Description] |
| P-04 Explainability       | [Implemented / Partial / Not implemented] | [Description] |
| P-05 Least Privilege      | [Implemented / Partial / Not implemented] | [Description] |
| P-06 Human Override       | [Implemented / Partial / Not implemented] | [Description] |
| P-07 Fail Safe            | [Implemented / Partial / Not implemented] | [Description] |
| P-08 Vendor Neutrality    | [Implemented / Partial / Not implemented] | [Description] |
| P-09 Incremental Adoption | [Implemented / Partial / Not implemented] | [Description] |
| P-10 Test-First           | [Implemented / Partial / Not implemented] | [Description] |
| P-11 Data Residency       | [Implemented / Partial / Not implemented] | [Description] |
| P-12 Continuous Learning  | [Implemented / Partial / Not implemented] | [Description] |

---

## Certification Status

| Field                          | Value                                                       |
|--------------------------------|-------------------------------------------------------------|
| Certification status           | [Self-declared / Self-assessed / Third-party certified]     |
| Certification body             | [IF L4: Name of certification body]                         |
| Certificate ID                 | [IF L4: Certificate identifier]                             |
| Certificate issuance date      | [IF L4: ISO 8601 date]                                      |
| Certificate expiry date        | [IF L4: ISO 8601 date]                                      |
| Self-assessment date           | [IF L2/L3: Date of most recent self-assessment]             |
| Test cases passed              | [IF L3/L4: TC-001, TC-002, TC-003, TC-004, TC-005 — list which passed] |
| Evidence package location      | [Reference to where evidence package is held]              |

---

## Known Limitations

[IF APPLICABLE: Describe any known limitations that affect the product's ANIF implementation but are not formal deviations (e.g., maximum intent throughput, unsupported environment types, platform-specific constraints).]

---

## Support and Contact

| Field                     | Value                                  |
|---------------------------|----------------------------------------|
| Technical support contact | [Email or URL]                         |
| Documentation URL         | [URL to product ANIF documentation]    |
| Issue tracking            | [URL or contact for reporting ANIF-related defects] |
| Profile update notification | [Mechanism by which customers are notified of profile updates] |

---

## Profile Attestation

I, [NAME], [ROLE] at [VENDOR NAME], attest that the information in this profile is accurate and complete to the best of my knowledge as of [DATE]. I acknowledge that misrepresentation of conformance status may result in downgrade, certification suspension, or removal from the ANIF Working Group partner registry.

Signed: ___________________________
Date: ___________________________
```

---

## 6. Security Considerations

Vendor profiles MUST NOT include:

- Authentication credentials or API keys
- Internal system hostnames or IP addresses
- Security vulnerability information (this should be disclosed through coordinated vulnerability disclosure channels)

Vendors SHOULD consider whether profile information could reveal details about their implementation that could be exploited by adversaries.

---

## 7. Operational Considerations

- Profiles SHOULD be published in a machine-readable format (JSON or YAML equivalent) in addition to the Markdown format defined here
- Profiles SHOULD be signed with the vendor's code signing certificate where the implementing organisation has one
- When a profile is superseded by a newer version, the older version MUST be retained and marked as superseded with a reference to the current version

---

## Appendix A: Example Completed Profile (Abbreviated)

The following abbreviated example illustrates a completed profile for a hypothetical vendor.

```markdown
# ANIF Vendor Conformance Profile

## Profile Header

| Field                     | Value                        |
|---------------------------|------------------------------|
| Profile version           | 1.2.0                        |
| Vendor name               | Acme Networks Ltd            |
| Product name              | NetOrchestrator              |
| Product version           | 4.1.2                        |
| ANIF version              | 0.1.0                        |
| Declared conformance level | L3 — Conformant             |
| Verification method       | Self-assessment              |
| Profile date              | 2026-04-07                   |

## Action Type Support

| Action Type     | Support level | Notes                              |
|-----------------|---------------|------------------------------------|
| reroute_traffic | Native        | Implemented via BGP policy updates |
| apply_qos       | Native        | Uses DSCP marking pipeline         |
| scale_bandwidth | Custom adapter | Requires acme-bw-adapter v2+      |
| isolate_segment | Native        | VLAN and ACL-based isolation       |

## Deviations

| Deviation ID | ANIF requirement | Nature | Rationale |
|---|---|---|---|
| DEV-001 | ANIF-103 §4.2 append-only audit | Audit records older than 90 days are archived to cold storage with reduced query performance | Storage cost constraints; archive is still queryable |

## Certification Status

| Field | Value |
|---|---|
| Certification status | Self-assessed |
| Self-assessment date | 2026-03-15 |
| Test cases passed | TC-001, TC-002, TC-003, TC-004, TC-005 |
```

---

## Appendix B: Change History

| Version | Date       | Author             | Description   |
|---------|------------|--------------------|---------------|
| 0.1.0   | 2026-04-07 | ANIF Working Group | Initial draft |
