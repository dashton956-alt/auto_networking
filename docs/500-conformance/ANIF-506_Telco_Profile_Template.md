# ANIF-506: Telco Profile Template

| Field        | Value                                              |
|--------------|----------------------------------------------------|
| Doc ID       | ANIF-506                                           |
| Series       | Conformance                                        |
| Version      | 0.1.0                                              |
| Status       | Draft                                              |
| Authors      | ANIF Working Group                                 |
| Reviewers    | —                                                  |
| Approved by  | —                                                  |
| Created      | 2026-04-07                                         |
| Last updated | 2026-04-07                                         |
| Replaces     | N/A                                                |
| Related docs | ANIF-504, ANIF-505, ANIF-101, ANIF-500             |

---

## Abstract

This document defines the standard profile template for telecommunications providers declaring ANIF conformance. It extends the generic vendor profile (ANIF-504) with telco-specific declarations covering network domain scope, control protocol support, ETSI ZSM and TMForum AN alignment, 3GPP references, and carrier-grade availability requirements. Completed telco profiles enable operators and integrators to assess ANIF support across RAN, Core, Transport, IP, and Optical domains.

---

## 1. Introduction

### 1.1 Purpose

Telecommunications providers implementing ANIF capabilities across their network domains MUST produce a completed telco profile using the template defined in this document. The profile extends the base vendor profile with declarations specific to telco network architecture, standards alignment, and operational requirements.

### 1.2 Scope

This template applies to any organisation that:

- Operates telecommunications network infrastructure (RAN, Core, Transport, IP, Optical)
- Declares ANIF conformance for one or more network domains
- Claims alignment to ETSI ZSM, TMForum Autonomous Networks, or 3GPP specifications

### 1.3 Out of scope

- IT/enterprise network deployments (use ANIF-504 vendor profile)
- Cloud-native infrastructure without telco domain coverage (use ANIF-505 cloud profile)
- Hardware specifications or physical layer standards

### 1.4 Intended audience

Network architects, standards teams, procurement officers, and system integrators evaluating telco ANIF implementations.

---

## 2. Normative references

- RFC 2119 — Key words for use in RFCs to indicate requirement levels
- ANIF-504 — Vendor Profile Template (base template extended by this document)
- ANIF-101 — Compliance Mapping (TMForum, ETSI ZSM)
- ETSI GS ZSM 002 — Zero-touch network and Service Management; Reference Architecture
- TMForum IG1218 — Autonomous Networks Technical Architecture
- 3GPP TS 28.312 — Intent driven management services for mobile networks
- RFC 8969 — A Framework for Automating Service and Network Management with YANG

---

## 3. Terms and definitions

| Term | Definition |
|---|---|
| RAN | Radio Access Network — the part of a mobile network connecting end devices to the core |
| Core Network | The central part of a telecommunications network providing control, routing, and service functions |
| Transport Network | The network layer carrying traffic between RAN, Core, and Data Centres (IP/MPLS, Optical) |
| Network Slice | A logical end-to-end network with specific performance characteristics, isolated from other slices |
| VNF | Virtualised Network Function — a software implementation of a network function running on a VM |
| CNF | Cloud-native Network Function — a network function implemented as containerised microservices |
| NFVI | Network Function Virtualisation Infrastructure — the compute, storage, and network resources for VNFs |
| gNMI | gRPC Network Management Interface — a streaming telemetry and configuration protocol |
| NETCONF | Network Configuration Protocol (RFC 6241) — XML-based network configuration protocol |
| RESTCONF | HTTP-based protocol providing a programmatic interface over NETCONF datastores (RFC 8040) |
| OpenConfig | Vendor-neutral, model-driven configuration and telemetry standard |
| 5G NR | 5G New Radio — the air interface standard for 5G networks |
| NSSF | Network Slice Selection Function — 5G Core function for selecting appropriate network slices |

---

## 4. Telco Profile Template

### 4.1 Base Profile Header

Complete the vendor profile header from ANIF-504 first, then add the telco-specific sections below.

```
Organisation:          [Legal name of the telecommunications provider]
Network domains:       [List: RAN / Core / Transport / IP / Optical — check all that apply]
Standards body membership: [3GPP / ETSI / TMForum / IETF — list active memberships]
ANIF version:          [e.g., 0.1.0]
Conformance level:     [L1 / L2 / L3 / L4]
Profile version:       [e.g., 1.0.0]
Profile date:          [YYYY-MM-DD]
Profile contact:       [team email or URL]
```

---

### 4.2 Network Domain Coverage

Declare which network domains are within scope of the ANIF conformance claim. A separate profile MAY be submitted per domain.

| Domain | In Scope | Notes |
|---|---|---|
| RAN (4G LTE) | Yes / No | |
| RAN (5G NR) | Yes / No | |
| 5G Core (5GC) | Yes / No | Include SA / NSA distinction |
| EPC (4G Core) | Yes / No | |
| IP/MPLS Transport | Yes / No | |
| Optical Transport | Yes / No | |
| SD-WAN | Yes / No | |
| Enterprise Edge | Yes / No | |

**Domain scope narrative:** [Describe the boundaries of what is and is not covered within each in-scope domain.]

---

### 4.3 Action Type Support by Domain

For each in-scope domain, declare support for ANIF action types.

| Action Type | RAN | Core | Transport | IP | Optical | Notes |
|---|---|---|---|---|---|---|
| reroute_traffic | | | | | | |
| apply_qos | | | | | | |
| scale_bandwidth | | | | | | |
| isolate_segment | | | | | | |

Values: `Native` (direct support), `Adapter` (via custom adapter), `Partial` (subset of parameters), `Not Supported`

**Native implementation notes:** [Describe how each supported action type maps to actual network operations in each domain.]

---

### 4.4 Control Protocol Support

Declare which management and telemetry protocols the ANIF adapter layer uses.

| Protocol | Supported | Domains | Version | Notes |
|---|---|---|---|---|
| NETCONF | Yes / No | | RFC 6241 | |
| RESTCONF | Yes / No | | RFC 8040 | |
| gNMI | Yes / No | | v0.7+ | |
| OpenConfig | Yes / No | | | |
| SNMP | Yes / No | | v2c / v3 | Legacy only |
| CLI/SSH | Yes / No | | | Not recommended |
| Vendor proprietary API | Yes / No | | | Must document |

**Protocol implementation notes:** [Describe how protocols map to the ANIF adapter interface.]

---

### 4.5 ETSI ZSM Alignment

Declare alignment to ETSI Zero-touch network and Service Management.

| ZSM Concept | ANIF Equivalent | Implementation Status | Notes |
|---|---|---|---|
| Intent interface | ANIF-300, ANIF-301 | | |
| Closed-loop automation | ANIF-403 | | |
| Cross-domain orchestration | ANIF-200, ANIF-305 | | |
| Analytics service | ANIF-401, ANIF-402 | | |
| ZSM management domain | ANIF-203 module boundary | | |
| E2E service management | ANIF-305 orchestration | | |

**ZSM implementation summary:** [Describe which ZSM reference architecture components are implemented and how they integrate with ANIF.]

---

### 4.6 TMForum Autonomous Networks Alignment

Declare the declared TMForum Autonomous Networks maturity level and its mapping to ANIF.

| TMForum AN Level | Level Name | ANIF Equivalent | Claimed | Evidence |
|---|---|---|---|---|
| Level 0 | Manual | ANIF L1 (Aware) | Yes / No | |
| Level 1 | Assisted Automation | ANIF L2 (Aligned) | Yes / No | |
| Level 2 | Partial Automation | ANIF L2/L3 | Yes / No | |
| Level 3 | Conditional Automation | ANIF L3 (Conformant) | Yes / No | |
| Level 4 | High Automation | ANIF L3/L4 | Yes / No | |
| Level 5 | Full Automation | ANIF L4 (Certified) | Yes / No | |

**Declared TMForum AN level:** [Level number and justification]

---

### 4.7 3GPP Alignment

For implementations covering 5G or 4G domains, declare alignment to relevant 3GPP specifications.

| 3GPP Specification | Title | Relevance | Compliance Status |
|---|---|---|---|
| TS 28.312 | Intent driven management services | Intent authoring (ANIF-301) | |
| TS 28.313 | Self-Organizing Networks (SON) | Closed-loop (ANIF-403) | |
| TS 28.532 | Management services for communication networks | Audit trail (ANIF-107) | |
| TS 28.554 | 5G end-to-end KPI | Observability (ANIF-401) | |
| TS 33.501 | Security architecture and procedures for 5G | Security arch (ANIF-205) | |

**3GPP implementation notes:** [Describe how 3GPP management interfaces are exposed through or alongside the ANIF API layer.]

---

### 4.8 Carrier-Grade Availability Requirements

Telecommunications providers MUST declare their availability commitments and how these interact with ANIF governance controls.

**Service availability targets:**

| Network Domain | Availability Target | SLA Class | Impact on ANIF Risk Scoring |
|---|---|---|---|
| | | | |

**High-availability considerations for ANIF:**

- `availability_percent` objectives in intents referencing carrier-grade SLAs MUST be honoured by risk scoring
- Actions affecting domains with five-nines (99.999%) availability targets MUST always trigger `manual_review` regardless of risk score
- Rollback SLA for carrier-grade domains: rollback MUST complete within [specify] seconds

**Change window requirements:**

| Domain | Change Window | Frequency | Exclusion Periods |
|---|---|---|---|
| | | | |

---

### 4.9 Network Slice Support

For operators supporting 5G network slicing, declare ANIF intent handling for sliced networks.

- Network slice identifier (S-NSSAI) support in intent constraints: Yes / No
- Slice-specific policy sets: Yes / No
- Cross-slice isolation via `isolate_segment` action: Yes / No
- NSSF integration for slice selection: Yes / No

---

### 4.10 Compliance Certifications

List relevant compliance certifications held that affect ANIF data residency and security requirements.

| Certification | Issuing Body | Scope | Expiry | Relevant to ANIF |
|---|---|---|---|---|
| ISO 27001 | | | | Security architecture (ANIF-205) |
| SOC 2 Type II | | | | Audit trail (ANIF-107) |
| PCI-DSS | | | | Data residency (ANIF-106) |
| GDPR DPA registration | | | | EU data handling (ANIF-106) |
| NIS2 compliance | | | | Governance (ANIF-100) |
| Carrier-grade certification | | | | Availability commitments |

---

### 4.11 Deviations from ANIF Normative Requirements

Any deviation from ANIF normative requirements (MUST/MUST NOT) MUST be declared here. Undeclared deviations invalidate the conformance claim.

| ANIF Requirement | Doc Reference | Deviation Description | Justification | Remediation Plan |
|---|---|---|---|---|
| | | | | |

---

### 4.12 Known Limitations

| Limitation | Affected Domains | Workaround | Resolution Target |
|---|---|---|---|
| | | | |

---

## 5. Conformance Requirements

An ANIF telco profile MUST:

- Complete all sections of this template fully; sections marked "Yes / No" MUST have a definitive answer
- Not leave mandatory fields blank or marked "TBD" in a published profile
- Declare all deviations in section 4.11; deviations not declared here invalidate the conformance claim
- Base the telco profile on a completed ANIF-504 vendor profile header
- Declare a TMForum AN level in section 4.6 if TMForum AN alignment is claimed
- Declare all 3GPP specifications in section 4.7 that the implementation references normatively
- Republish the profile within 90 days of any change that affects the accuracy of any declared field

An ANIF telco profile SHOULD:

- Include evidence artefacts (test logs, third-party assessments) for each conformance claim
- Provide domain-specific sub-profiles when network domain scope is large
- Reference the specific product version to which the profile applies

---

## 6. Security Considerations

Telco profiles that disclose specific protocol versions, topology details, or slice configurations SHOULD be treated as sensitive documents. Operators MUST review whether profile content reveals information that could be exploited by adversaries before publishing externally.

---

## 7. Operational Considerations

Telco profiles SHOULD be reviewed and revalidated annually. Significant network architecture changes (new domain onboarding, protocol migrations, slice architecture changes) MUST trigger an out-of-cycle profile update within 90 days of the change.

---

## Appendix A: Example Telco Profile (Illustrative)

```
Organisation:          Example Telco plc
Network domains:       RAN (5G NR), 5G Core, IP/MPLS Transport
Standards body membership: 3GPP, ETSI, TMForum
ANIF version:          0.1.0
Conformance level:     L3 (Conformant — self-assessed)
Profile version:       1.0.0
Profile date:          2026-04-07

Action type support:
  reroute_traffic:     Native (IP/MPLS), Adapter (RAN via SON)
  apply_qos:           Native (all domains)
  scale_bandwidth:     Native (IP/MPLS), Partial (RAN — limited to pre-defined profiles)
  isolate_segment:     Adapter (5G Core — network slice isolation via NSSF)

Control protocols:     gNMI (RAN telemetry), NETCONF (IP/MPLS), RESTCONF (5G Core)
TMForum AN level:      Level 3 (Conditional Automation)
3GPP alignment:        TS 28.312 (intent), TS 28.313 (SON closed-loop)
Availability target:   99.999% (Core), 99.99% (RAN)

Deviations: None declared.
```

---

## Appendix B: Change History

| Version | Date | Author | Changes |
|---|---|---|---|
| 0.1.0 | 2026-04-07 | ANIF Working Group | Initial draft |
