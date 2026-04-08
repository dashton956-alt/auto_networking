# ANIF-101: Compliance Mapping — TMForum and ETSI ZSM

| Field        | Value                                            |
|--------------|--------------------------------------------------|
| Doc ID       | ANIF-101                                         |
| Series       | Governance                                       |
| Version      | 0.1.0                                            |
| Status       | Draft                                            |
| Authors      | ANIF Working Group                               |
| Reviewers    | —                                                |
| Approved by  | —                                                |
| Created      | 2026-04-07                                       |
| Last updated | 2026-04-07                                       |
| Replaces     | N/A                                              |
| Related docs | ANIF-001, ANIF-102, ANIF-300, ANIF-403           |

---

## Abstract

This document maps the Autonomous Networking and Infrastructure Framework (ANIF) to the TMForum Autonomous Networks maturity model and the ETSI Zero-touch network and Service Management (ZSM) framework. It also documents alignment with IETF ANIMA for intent schema. The mapping enables operators and compliance officers to understand how ANIF conformance levels correspond to industry benchmarks, to identify gaps, and to plan adoption roadmaps.

---

## 1. Introduction

### 1.1 Purpose

Telecommunications operators and enterprises deploying ANIF operate within an ecosystem of industry frameworks and regulatory requirements. This document provides authoritative mappings between ANIF and two primary external frameworks — TMForum Autonomous Networks and ETSI ZSM — enabling:

- Evidence generation for conformance assessments.
- Gap analysis against industry benchmarks.
- Roadmap planning for incremental adoption (P-09).
- Communication with auditors and regulators using industry-standard terminology.

### 1.2 Scope

This document covers:

- TMForum Autonomous Networks maturity model (levels 0–5) mapped to ANIF conformance levels L1–L4.
- ETSI ZSM framework components mapped to specific ANIF documents and pipeline stages.
- IETF ANIMA intent schema alignment.
- Identified gaps and deliberate deviations with rationale.

### 1.3 Out of Scope

- Implementation guidance for achieving specific maturity levels.
- Vendor-specific TMForum or ETSI product certifications.
- Financial or SLA frameworks not directly related to autonomous networking governance.
- 3GPP network management standards (future document).

### 1.4 Intended Audience

| Audience               | Purpose                                                              |
|------------------------|----------------------------------------------------------------------|
| Compliance Officer     | Evidence generation and gap analysis                                 |
| Policy Administrator   | Understanding how ANIF policies map to ZSM closed-loop controls      |
| Senior Engineer        | Architecture alignment with industry standards                       |
| Automation Agent       | Reference for intent schema compatibility with IETF ANIMA            |

---

## 2. Normative References

| Reference             | Title                                                                      |
|-----------------------|----------------------------------------------------------------------------|
| ANIF-001              | ANIF Constitution and Guiding Principles                                   |
| ANIF-002              | ANIF Core Glossary                                                         |
| ANIF-100              | Governance Overview                                                        |
| ANIF-103              | Autonomous Action Policy                                                   |
| ANIF-300              | Intent Schema Specification                                                |
| ANIF-301              | Intent Validation                                                          |
| ANIF-305              | Orchestration and Cross-Domain                                             |
| ANIF-401              | Analytics Framework                                                        |
| ANIF-402              | Audit and Observability                                                    |
| ANIF-403              | Closed-Loop Automation                                                     |
| TMF-921               | Autonomous Networks Levels Technical Specification                         |
| ETSI GS ZSM 001       | ZSM Framework                                                              |
| ETSI GS ZSM 002       | ZSM Terminology                                                            |
| ETSI GS ZSM 006       | ZSM Proof of Concept Framework                                             |
| RFC 8993              | IETF ANIMA Reference Model                                                 |
| RFC 9315              | Intent-Based Networking — Concepts and Definitions                         |

---

## 3. Terms and Definitions

| Term                  | Definition                                                                                       |
|-----------------------|--------------------------------------------------------------------------------------------------|
| TMForum AN Level      | One of six maturity levels (0–5) in the TMForum Autonomous Networks specification (TMF-921).     |
| ZSM                   | ETSI Zero-touch network and Service Management — a framework for fully automated network management. |
| Closed-Loop           | An automated management cycle: monitor → analyse → decide → execute, with feedback.              |
| ANIMA                 | IETF Autonomic Networking Integrated Model and Approach; defines an intent schema standard.      |
| Intent Interface      | The northbound interface through which operators express desired network outcomes.                |
| Cross-Domain          | Operations spanning multiple network or management domains.                                      |

---

## 4. Compliance Mappings

### 4.1 TMForum Autonomous Networks Maturity Model

The TMForum Autonomous Networks Technical Specification (TMF-921) defines six maturity levels representing the degree of autonomy in network operations.

#### 4.1.1 TMForum Level Definitions

| TMF Level | Name                   | Description                                                                      |
|-----------|------------------------|----------------------------------------------------------------------------------|
| L0        | Manual                 | All operations performed manually; no automation.                                |
| L1        | Assisted               | System provides recommendations; humans execute all actions.                     |
| L2        | Partial Autonomy       | System executes routine tasks autonomously; humans handle exceptions.            |
| L3        | Conditional Autonomy   | System operates autonomously within defined conditions; human oversight retained.|
| L4        | High Autonomy          | System manages most operations autonomously; humans set policy only.             |
| L5        | Full Autonomy          | Fully autonomous; no human intervention required.                                |

#### 4.1.2 TMForum to ANIF Conformance Level Mapping

| TMF Level | ANIF Conformance Level | Mapping Rationale                                                                                                   |
|-----------|------------------------|---------------------------------------------------------------------------------------------------------------------|
| L0        | Pre-L1                 | No ANIF governance implemented; system is entirely manual.                                                          |
| L1        | L1 Aware               | Organisation is aware of ANIF principles; no formal implementation. System recommends but does not act.             |
| L2        | L1 Aware / L2 Aligned  | ANIF-103 and ANIF-107 implemented at basic level; system executes pre-approved low-risk actions autonomously.       |
| L3        | L2 Aligned / L3 Conformant | Full ANIF pipeline implemented; mode gate enforces `auto`/`manual_review`/`block`; all 100-series documents active. |
| L4        | L3 Conformant          | All governance domains active; exception and escalation policies fully operational; continuous learning (P-12) active.|
| L5        | L4 Certified           | Third-party validated ANIF conformance; full autonomous operation within certified policy envelope.                 |

**Note**: ANIF does not endorse TMF L5 (full autonomy without human override capability) as a target state. Principle P-06 (Human Override) requires that humans MUST retain the ability to halt or override any autonomous action at all conformance levels.

#### 4.1.3 ANIF Alignment with TMForum AN Dimensions

TMF-921 assesses autonomy across multiple dimensions. The following table maps ANIF components to each dimension:

| TMF Dimension              | ANIF Alignment                                                         | ANIF Document(s)        |
|----------------------------|------------------------------------------------------------------------|-------------------------|
| Self-configuration         | Intent-driven configuration via bounded action set                     | ANIF-103, ANIF-300      |
| Self-optimisation          | Closed-loop analytics and QoS tuning                                   | ANIF-401, ANIF-403      |
| Self-healing               | Automated segment isolation and rerouting on fault detection           | ANIF-103, ANIF-405      |
| Self-protection            | Risk scoring, policy enforcement, mode gate blocking                   | ANIF-103, ANIF-307      |
| Intent-based management    | Northbound intent interface with schema validation                     | ANIF-300, ANIF-301      |
| Closed-loop management     | Full monitor-analyse-decide-execute pipeline                           | ANIF-403                |
| Audit and accountability   | Mandatory audit trail at every pipeline stage                          | ANIF-107, ANIF-402      |

### 4.2 ETSI ZSM Framework Mapping

ETSI ZSM defines a reference architecture for zero-touch network management. The following sections map ZSM components to ANIF.

#### 4.2.1 ZSM Intent Interface → ANIF Intent Layer

ZSM defines an intent interface (ZSM-001 §8.3) as the northbound interface for expressing desired network outcomes without specifying how to achieve them.

| ZSM Component              | ANIF Mapping                      | Notes                                                         |
|----------------------------|-----------------------------------|---------------------------------------------------------------|
| Intent interface           | ANIF-300 (Intent Schema)          | ANIF intent schema is aligned with ZSM intent structure.      |
| Intent validation          | ANIF-301 (Intent Validation)      | ZSM validation requirements fully addressed.                  |
| Intent lifecycle           | ANIF-300, ANIF-301                | ANIF tracks intent through full pipeline lifecycle.           |
| Fulfilment reporting       | ANIF-107 (Audit Trail)            | Every execution outcome is audited and queryable.             |

#### 4.2.2 ZSM Closed-Loop → ANIF Closed-Loop Automation

ZSM closed-loop automation (ZSM-001 §9) is the core operational pattern. ANIF's pipeline implements a closed-loop with explicit governance gates.

| ZSM Closed-Loop Step       | ANIF Pipeline Stage               | ANIF Document(s)                |
|----------------------------|-----------------------------------|---------------------------------|
| Data collection            | Pre-pipeline telemetry            | ANIF-401, ANIF-402              |
| Analysis                   | Risk Score stage                  | ANIF-307, ANIF-403              |
| Decision                   | Decision stage                    | ANIF-103, ANIF-403              |
| Execution                  | Execute stage                     | ANIF-103, ANIF-306              |
| Feedback / verification    | Post-execution verification       | ANIF-104, ANIF-405              |
| Governance gate            | Mode Gate (ANIF addition)         | ANIF-103, ANIF-104, ANIF-105    |

**Deviation**: ZSM does not mandate a governance gate between decision and execution. ANIF's mode gate is a deliberate addition implementing P-06 (Human Override). This deviation is intentional and is considered a governance enhancement, not a non-conformance.

#### 4.2.3 ZSM Cross-Domain Orchestration → ANIF Orchestration

ZSM defines cross-domain management (ZSM-001 §10) for orchestration across multiple network domains.

| ZSM Cross-Domain Component | ANIF Mapping                      | ANIF Document(s)                |
|----------------------------|-----------------------------------|---------------------------------|
| E2E service management     | Cross-domain intent orchestration | ANIF-200, ANIF-305              |
| Domain service management  | Per-domain policy enforcement     | ANIF-103, ANIF-200              |
| Resource management        | Bandwidth and QoS management      | ANIF-103, ANIF-202              |
| Inter-domain coordination  | Multi-domain risk aggregation     | ANIF-305, ANIF-307              |

#### 4.2.4 ZSM Analytics → ANIF Analytics

ZSM defines analytics services (ZSM-001 §11) for data collection, processing, and insight generation.

| ZSM Analytics Component    | ANIF Mapping                      | ANIF Document(s)                |
|----------------------------|-----------------------------------|---------------------------------|
| Data collection services   | Telemetry ingestion               | ANIF-401                        |
| Analytics services         | Risk scoring and trend analysis   | ANIF-401, ANIF-402              |
| Insight generation         | Closed-loop decision support      | ANIF-403                        |
| Performance analytics      | Post-execution metrics            | ANIF-402, ANIF-405              |

### 4.3 IETF ANIMA Alignment

IETF ANIMA (RFC 8993) and intent-based networking concepts (RFC 9315) define a reference model for autonomic networking. ANIF's intent schema (ANIF-300) is designed for alignment with these standards.

#### 4.3.1 Intent Schema Alignment

| IETF ANIMA / IBN Concept   | ANIF Alignment                                                            |
|----------------------------|---------------------------------------------------------------------------|
| Intent as goal expression  | ANIF intents express desired outcomes, not low-level instructions         |
| Intent ambiguity resolution| ANIF-301 validation catches ambiguous or conflicting intents before execution |
| Fulfillment reporting      | ANIF-107 audit trail provides structured fulfillment evidence             |
| Intent lifecycle           | ANIF-300 defines: submitted → validated → executing → fulfilled/failed    |
| Refinement loop            | ANIF-403 closed-loop supports iterative intent refinement                 |

#### 4.3.2 ANIMA-Specific Deviations

ANIF makes the following deliberate deviations from IETF ANIMA:

| Deviation                          | Rationale                                                                         |
|------------------------------------|-----------------------------------------------------------------------------------|
| Bounded action set (4 action types)| ANIF constrains actions to a predefined set to enforce safety (P-03, P-07). ANIMA does not constrain action types. |
| Explicit governance gate           | ANIF adds a mandatory mode gate not present in ANIMA reference model.              |
| Audit-first requirement            | ANIF requires write-before-return audit records; ANIMA does not specify audit behaviour. |

---

## 5. Conformance Requirements

5.1 Implementations claiming TMForum L3 alignment MUST implement ANIF-103, ANIF-104, ANIF-107, and the full governance pipeline.

5.2 Implementations claiming ETSI ZSM alignment MUST implement the intent interface (ANIF-300, ANIF-301) and closed-loop automation (ANIF-403).

5.3 The ANIF Working Group MUST review this mapping document whenever TMForum or ETSI publish new major versions of their respective frameworks.

5.4 Gaps identified in Section 4 MUST be tracked in the ANIF gap register. Each gap entry MUST include: gap ID, affected framework, description, planned resolution, and target version.

5.5 Deliberate deviations from external frameworks documented in this document are normative. Implementations MUST NOT introduce additional undocumented deviations without Working Group approval.

---

## 6. Security Considerations

6.1 Cross-framework compliance mapping documents contain information about system capabilities and constraints. Access SHOULD be restricted to compliance officers and senior engineers.

6.2 When ANIF is assessed against external frameworks by third parties, the mapping tables in this document MUST be used as the authoritative reference to prevent misrepresentation.

6.3 Compliance evidence packages drawn from ANIF audit records (ANIF-107) MUST be cryptographically signed before submission to external auditors to ensure integrity.

---

## 7. Operational Considerations

7.1 Operators SHOULD perform an annual compliance gap review using the mapping tables in Section 4 to identify drift between their ANIF deployment and the target conformance level.

7.2 When TMForum or ETSI publish updated framework versions, the compliance officer MUST initiate a review of this document within 90 days of publication.

7.3 Operators targeting TMForum L4 or higher SHOULD prioritise implementation of ANIF-403 (closed-loop automation) and ANIF-401 (analytics) as these capabilities are central to high-autonomy operation.

---

## Appendix A: Examples

### A.1 TMForum Assessment Evidence Package

For a TMForum L3 autonomous networks assessment, the following ANIF documents and artefacts provide evidence:

| TMF L3 Requirement                    | ANIF Evidence                                           |
|---------------------------------------|---------------------------------------------------------|
| Autonomous execution of routine tasks | ANIF-103 action policy; audit records of `auto` mode executions |
| Human oversight for exceptions        | ANIF-105 escalation policy; approval ticket audit records |
| Intent-based northbound interface     | ANIF-300, ANIF-301; intent schema validation logs        |
| Audit trail for all autonomous actions| ANIF-107; `GET /audit/{intent_id}` query results         |

### A.2 ETSI ZSM Conformance Self-Assessment Checklist

| ZSM Requirement                       | ANIF Implementation                          | Status   |
|---------------------------------------|----------------------------------------------|----------|
| Intent interface implemented          | ANIF-300, ANIF-301                           | Covered  |
| Closed-loop automation implemented    | ANIF-403                                     | Covered  |
| Cross-domain orchestration supported  | ANIF-200, ANIF-305                           | Covered  |
| Analytics services implemented        | ANIF-401, ANIF-402                           | Covered  |
| Governance gate (ANIF addition)       | ANIF-103, ANIF-104, ANIF-105                 | Covered  |

---

## Appendix B: Change History

| Version | Date       | Author             | Description          |
|---------|------------|--------------------|----------------------|
| 0.1.0   | 2026-04-07 | ANIF Working Group | Initial draft        |
