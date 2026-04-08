# ANIF-001: Charter and Scope

| Field        | Value                                    |
|--------------|------------------------------------------|
| Doc ID       | ANIF-001                                 |
| Series       | Foundation                               |
| Version      | 0.1.0                                    |
| Status       | Draft                                    |
| Authors      | ANIF Working Group                       |
| Reviewers    | —                                        |
| Approved by  | —                                        |
| Created      | 2026-04-07                               |
| Last updated | 2026-04-07                               |
| Replaces     | N/A                                      |
| Related docs | ANIF-002, ANIF-003, ANIF-100             |

---

## Abstract

The Autonomous Networking & Infrastructure Framework (ANIF) is a vendor-neutral, open governance framework for the specification, implementation, and operation of autonomous network and infrastructure management systems. This charter establishes the purpose, scope, governance structure, and guiding principles under which ANIF is developed and maintained. It defines what ANIF covers, what it intentionally excludes, and how ANIF relates to adjacent industry standards and frameworks. All ANIF documents derive their authority from this charter.

---

## 1. Introduction

### 1.1 Purpose

Autonomous networking and infrastructure management capabilities are advancing rapidly. Network functions virtualisation, intent-based networking, AIOps, and closed-loop automation are moving from research into production deployments. However, the industry lacks a coherent, vendor-neutral governance framework that:

- Defines safety, auditability, and reversibility requirements for autonomous actions
- Specifies the decision pipeline from intent intake to action execution and audit
- Establishes conformance levels that allow organisations to assess and compare implementations
- Provides a common vocabulary and set of normative requirements that interoperate across vendor boundaries

ANIF exists to fill this gap. Its purpose is to provide the normative foundation — principles, architecture, APIs, and conformance criteria — upon which production-grade autonomous network and infrastructure management systems can be built with confidence.

ANIF does not build products. ANIF specifies what conformant products must do.

### 1.2 Scope

ANIF covers:

1. **Governance and policy**: The specification of policy models, policy evaluation engines, governance gates, and human-in-the-loop controls for autonomous network and infrastructure actions.
2. **Intent-based networking architecture**: The definition of the intent lifecycle — from submission through validation, policy evaluation, risk scoring, decision, and execution.
3. **Risk quantification and trust scoring**: Normative requirements for risk assessment models and trust scoring of automation agents operating within the framework.
4. **Human-in-the-loop controls**: The specification of override, halt, and reversal mechanisms that human operators MUST be able to invoke at all times.
5. **Observability and explainability**: Requirements for audit records, reasoning chains, and the `/why` API contract.
6. **Maturity progression**: A five-level maturity model (Level 0 through Level 4) for organisations adopting autonomous operations.
7. **Adapter and plugin interfaces**: Abstract interface specifications for vendor and cloud provider integrations, without prescribing any specific implementation.
8. **Conformance**: Four conformance levels (L1 Aware through L4 Certified) with associated test criteria.

### 1.3 Out of Scope

ANIF explicitly does not cover:

| Out-of-scope area | Rationale |
|---|---|
| Physical layer hardware management (optics, transceivers, physical cabling) | Below the network abstraction boundary ANIF targets |
| Vendor-specific CLI syntax or proprietary management APIs | Vendor-specific detail belongs in adapter documentation, not the core framework |
| General ITSM processes not related to autonomous actions (incident ticketing, asset management, CMDB) | Covered by ITIL 4 and related frameworks; ANIF defers to those |
| AI/ML model training, selection, or validation methodology | ANIF specifies behavioural requirements of AI components, not how models are built |
| Human resource management, organisational change management | Outside technical scope |
| Pricing, procurement, or commercial licensing of network equipment | Commercial, not technical |
| Regulatory compliance specifics for individual jurisdictions | ANIF provides a compliance-friendly framework; jurisdiction-specific requirements are an organisational concern |

### 1.4 Intended Audience

- Network architects and engineers evaluating or implementing autonomous networking systems
- Platform engineers building automation tooling for network and infrastructure
- Security and compliance officers assessing autonomous systems
- Vendors developing products they wish to certify as ANIF-conformant
- Standards body participants seeking to align ANIF with adjacent specifications
- ANIF Working Group members contributing to framework documents

---

## 2. Normative References

- RFC 2119 — Key words for use in RFCs to indicate requirement levels
- RFC 8174 — Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words
- ETSI GS ZSM 001 — Zero-touch network & Service Management; Reference Architecture
- ETSI GS ZSM 002 — Zero-touch network & Service Management; Concepts, use cases and requirements
- TMForum IG1218 — Autonomous Networks Reference Architecture
- NIST SP 800-53 Rev. 5 — Security and Privacy Controls for Information Systems and Organizations
- NIST CSF 2.0 — Cybersecurity Framework
- TOGAF Standard (10th Edition) — Architecture Development Method
- ITIL 4 — IT Service Management framework
- IETF RFC 8993 — A Reference Model for Autonomic Networking (ANIMA)
- ISO/IEC 27001:2022 — Information Security Management Systems

---

## 3. Terms and Definitions

See ANIF-003 for the full ANIF glossary. Key terms used in this document:

| Term | Definition |
|---|---|
| Autonomous action | Any configuration change, operational command, or infrastructure modification initiated without direct human input at the moment of execution |
| Framework | The complete set of ANIF normative documents, schemas, APIs, and conformance criteria |
| Working Group | The body responsible for maintaining and governing ANIF documents |
| Conformance level | One of four graduated levels (L1–L4) indicating the degree to which an implementation satisfies ANIF requirements |
| Adapter | A software component that translates between the ANIF abstract model and a specific vendor or cloud provider API |

---

## 4. Framework Positioning and Alignment

### 4.1 Relationship to Adjacent Standards

ANIF is designed to be complementary to, not a replacement for, existing industry standards and frameworks. The following table describes how ANIF aligns with each:

| Framework / Standard | Domain | ANIF Relationship |
|---|---|---|
| ETSI ZSM | Telecom network automation, zero-touch management | ANIF aligns its closed-loop architecture with ZSM's management domain concept. ANIF governance gates map to ZSM decision points. ANIF does not replicate ZSM but extends it with normative safety and auditability requirements. |
| TMForum Autonomous Networks | Telecom autonomous operations maturity model | ANIF's Level 0–4 maturity model is informed by and compatible with TMForum's AN levels. ANIF provides the normative content (principles, APIs, conformance tests) that TMForum's maturity model assumes but does not fully specify. |
| NIST CSF 2.0 | Cybersecurity framework (Identify, Protect, Detect, Respond, Recover) | ANIF's security considerations and governance gate requirements map to NIST CSF functions. ANIF's audit requirements satisfy NIST CSF Detect and Respond requirements. Organisations using NIST CSF MAY map ANIF conformance to CSF profile outcomes. |
| TOGAF ADM | Enterprise architecture methodology | ANIF architecture documents are structured to be consumable as TOGAF Architecture Building Blocks (ABBs). Organisations using TOGAF MAY incorporate ANIF specifications directly into their Architecture Repository. |
| ITIL 4 | IT service management | ANIF's governance gate and escalation model integrates with ITIL 4 change management practices. ANIF intents map to ITIL change requests. The ANIF audit record supports ITIL post-implementation review. |
| IETF ANIMA / RFC 8993 | Autonomic networking reference model | ANIF adopts ANIMA's reference model for autonomic functions and aligns its agent trust model with ANIMA's autonomic service agent concept. ANIF extends ANIMA with explicit human oversight and governance requirements. |
| NIST SP 800-53 Rev. 5 | Security controls catalogue | ANIF's audit (P-02), least privilege (P-05), and fail-safe (P-07) requirements map directly to relevant NIST 800-53 control families (AU, AC, SI). |

### 4.2 ANIF Document Series

ANIF documents are organised into series, each with a numeric prefix:

| Series | Prefix | Purpose |
|---|---|---|
| Foundation | 000 | Charter, principles, glossary, roles — the normative base |
| Governance | 100 | Policy model, governance gate, conformance levels |
| Architecture | 200 | System architecture, component interfaces, deployment models |
| Core Engines | 300 | Intent validation, risk scoring, decision engine specifications |
| Operations | 400 | Action execution, rollback, audit, observability, adapters |
| Conformance | 500 | Conformance test suites, certification process |
| Annexes | 600 | Implementation guides, worked examples, migration patterns |

### 4.3 Normative vs Informative Documents

All documents with series 000–500 are normative unless explicitly marked informative. Series 600 documents are informative unless explicitly marked normative.

---

## 5. Governance

### 5.1 Working Group Structure

The ANIF Working Group (WG) is the governing body for all ANIF specifications. The WG operates according to the following structure:

**Chairs (2):** Elected by active WG members for 12-month terms. Responsible for meeting facilitation, agenda management, and representing the WG externally.

**Editors:** One editor per document series, responsible for maintaining consistency, accepting contributions, and driving documents to publication-ready state.

**Contributors:** Any individual or organisation that contributes to ANIF documents, reference implementations, or test suites. Contributors MUST sign the ANIF Contributor Licence Agreement (CLA) prior to contribution.

**Observers:** Individuals or organisations that participate in WG discussions without contribution rights.

### 5.2 Decision-Making

The WG MUST use the following decision-making process:

1. **Rough consensus**: For editorial and minor technical decisions, the Chairs determine rough consensus from WG discussion. A formal vote is not required.
2. **Simple majority**: For technical decisions affecting normative content, a simple majority (>50%) of active WG members present at a scheduled meeting is required.
3. **Supermajority**: Charter amendments, new document series, and conformance level changes require a supermajority (≥ 2/3) of all active WG members. Active membership is defined as participation in at least 2 of the last 4 scheduled WG meetings.
4. **Objection process**: Any WG member MAY raise a formal objection. Objections MUST be documented with a written rationale. The Chairs MUST attempt to resolve objections through discussion within 30 days. Unresolved objections are escalated to a full WG vote.

### 5.3 Document Lifecycle

ANIF documents progress through the following states:

| State | Description | Entry Criteria |
|---|---|---|
| Proposal | Initial idea submitted for WG consideration | Any contributor may submit |
| Draft | Active development under editor control | WG approval of proposal |
| Candidate | Feature-complete, under WG review | Editor declares draft ready |
| Final | Published normative specification | Simple majority WG vote |
| Deprecated | Superseded by a newer document | WG vote; replacement document identified |

Draft documents MAY be implemented. Implementations against Draft documents are not eligible for L4 Certified conformance.

### 5.4 Intellectual Property Policy

- **Code and schemas**: Licensed under Apache License 2.0. All code contributions to the ANIF reference implementation and schema files MUST be made under Apache 2.0.
- **Documentation**: Licensed under Creative Commons Attribution 4.0 International (CC-BY-4.0). All documentation contributions MUST be made under CC-BY-4.0.
- **Patents**: Contributors MUST disclose any known patent claims that would be necessarily infringed by implementing ANIF specifications. The WG operates under a royalty-free patent licensing commitment for essential claims.

### 5.5 Charter Amendment Process

Amendments to this charter MUST satisfy all of the following conditions:

1. A written amendment proposal MUST be submitted to the WG mailing list at least 21 calendar days before the vote.
2. The proposal MUST include a rationale, the specific text to be changed, and an assessment of impact on existing conformant implementations.
3. The amendment MUST be approved by a supermajority (≥ 2/3) of all active WG members in a recorded vote.
4. Approved amendments MUST be reflected in a new version of this document within 30 calendar days of the vote.
5. Backward-incompatible charter amendments MUST increment the major version number of this document.

---

## 5. Conformance Requirements

Implementations claiming ANIF conformance MUST:

1. Reference the specific ANIF document series and version against which conformance is claimed.
2. Comply with all normative requirements (MUST / MUST NOT statements) in the claimed series.
3. Implement all 12 framework design principles as specified in ANIF-002.
4. Maintain the full decision pipeline: Intent → Validate → Policy Check → Risk Score → Decision → Action → Audit.
5. Provide evidence of conformance through test reports generated against ANIF-500 series test suites.

Conformance levels (L1–L4) are defined in the ANIF-100 series.

---

## 6. Security Considerations

This document is a governance charter and does not define technical security controls directly. However, the following security considerations apply to the governance process itself:

- WG communications channels MUST be authenticated. Unauthenticated submissions to normative document repositories MUST NOT be accepted.
- The document change history MUST be maintained in an immutable version control system (e.g., git with signed commits) to ensure document integrity.
- The CLA signing process MUST produce a verifiable record linking a legal entity to their contributions.
- Vulnerability disclosures related to ANIF specifications MUST be handled through a documented responsible disclosure process maintained by the WG Chairs.

---

## 7. Operational Considerations

- ANIF documents are maintained in a public git repository under the governance of the WG.
- Document IDs (e.g., ANIF-001) are permanent. A document ID MUST NOT be reused once assigned, even if the original document is deprecated.
- Editors MUST maintain a change history (Appendix B) in each document.
- The WG SHOULD meet at minimum monthly during active development phases and at minimum quarterly during maintenance phases.
- WG meeting minutes MUST be published within 14 calendar days of each meeting.

---

## Appendix A: Examples

### A.1 Charter Amendment Example

**Scenario**: The WG wishes to add a new conformance level (L5) to the framework.

**Process**:
1. A contributor submits a written proposal to the WG mailing list on Day 0, including rationale, proposed new text for ANIF-001 Section 4.2 and ANIF-500, and impact assessment.
2. The WG discusses the proposal over the following 21 days.
3. On Day 22 or later, a recorded vote is held. 18 of 24 active WG members vote in favour (75%, exceeding the 2/3 threshold).
4. The amendment is approved. The editor updates ANIF-001 to version 0.2.0 within 30 days, reflecting the change.

### A.2 Scope Boundary Example

**Scenario**: A contributor proposes adding ANIF requirements for DWDM optical transponder tuning.

**Ruling**: Out of scope under Section 1.3 ("Physical layer hardware management"). The contributor is advised to develop an ANIF-600 series informative annex if they wish to document integration patterns, but normative requirements for physical layer operations are not within ANIF scope.

---

## Appendix B: Change History

| Version | Date | Author | Changes |
|---|---|---|---|
| 0.1.0 | 2026-04-07 | ANIF Working Group | Initial draft |
