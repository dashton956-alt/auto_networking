# Autonomous Networking & Infrastructure Framework (ANIF)
## Master Structure, Naming Conventions & Document Index

**Version:** 0.1.0-draft  
**Status:** Working Draft  
**License:** Apache 2.0 (code) / CC-BY-4.0 (documentation)  
**Maintainer:** ANIF Working Group  
**Repository:** github.com/[org]/anif  

---

## Table of Contents

1. [Framework Overview](#1-framework-overview)
2. [Design Principles](#2-design-principles)
3. [Repository Structure](#3-repository-structure)
4. [Document Naming Conventions](#4-document-naming-conventions)
5. [Document Series Index](#5-document-series-index)
6. [Document Template](#6-document-template)
7. [Versioning & Lifecycle](#7-versioning--lifecycle)
8. [External Alignment Map](#8-external-alignment-map)
9. [Conformance Levels](#9-conformance-levels)
10. [Contribution Model](#10-contribution-model)

---

## 1. Framework Overview

ANIF is an open, multi-framework-aligned specification for autonomous networking, infrastructure, and cloud operations. It provides governance, architecture, policy, and operational standards for organisations building or adopting autonomous network management systems — from scripted automation through to Dark NOC partial autonomy.

### Scope

ANIF covers:
- Governance and policy for autonomous network/infra/cloud actions
- Intent-based networking architecture and standards
- Risk quantification, trust scoring, and decision frameworks
- Human-in-loop controls and audit requirements
- Observability, explainability, and closed-loop feedback
- Maturity progression model (Level 0 → Level 4)
- Vendor/cloud integration profiles and conformance criteria

ANIF does **not** cover:
- Physical layer hardware specifications
- Vendor-specific CLI or API implementations (delegated to profiles)
- General IT service management (deferred to ITIL)

### Positioning

| Framework | Relationship to ANIF |
|---|---|
| ETSI ZSM | ANIF extends ZSM intent concepts; cross-referenced in ANIF-2xx |
| TMForum Autonomous Networks | ANIF aligns to AN maturity levels; maps in ANIF-101 |
| NIST CSF | ANIF maps all governance controls to CSF functions in ANIF-102 |
| TOGAF ADM | ANIF architecture domains follow TOGAF; mapped in ANIF-200 |
| ITIL 4 | ANIF change and incident practices extend ITIL 4 practices |
| IETF ANIMA | ANIF intent schema designed for ANIMA compatibility |

---

## 2. Design Principles

These are the non-negotiable tenets of the framework. All documents, schemas, and implementations must comply.

| ID | Principle | Statement |
|---|---|---|
| P-01 | Reversibility | Every autonomous action must have a defined rollback path before execution is permitted. |
| P-02 | Auditability | No action may be taken without a complete, immutable, timestamped audit record. |
| P-03 | Determinism | Policy evaluation and risk scoring must produce identical outputs for identical inputs. |
| P-04 | Explainability | Every automated decision must be explainable in human-readable form on demand. |
| P-05 | Least privilege | Autonomous agents operate    What's missing and should be added to ANIF-841:
    - Session hijacking / token theft (stealing an agent's authenticated session)
    - Bus spoofing (an agent publishing to a bus it shouldn't have access to)
    - Replay attacks on the recommendation bus (already in ANIF-844 but not named in the threat model)

    Flag these for the ANIF-841 task when writing the threat catalogue.
with the minimum permissions required for each intent. |
| P-06 | Human override | A human operator must always be able to halt, override, or reverse any automated action. |
| P-07 | Fail safe | On uncertainty or system error, the default posture is to halt and escalate, not to proceed. |
| P-08 | Transparency | The reasoning chain for every decision must be captured and queryable. |
| P-09 | Vendor neutrality | The framework must not mandate any specific vendor implementation. |
| P-10 | Incremental adoption | Organisations must be able to adopt ANIF incrementally without full commitment upfront. |
| P-11 | Data residency | Data sovereignty and compliance constraints are first-class inputs to every decision. |
| P-12 | Continuous learning | The system must improve from outcomes, subject to human approval of policy changes. |

---

## 3. Repository Structure

```
anif/
│
├── README.md                          # Framework introduction and quickstart
├── CHANGELOG.md                       # Version history
├── CONTRIBUTING.md                    # Contribution guidelines
├── LICENSE                            # Apache 2.0
├── LICENSE-docs                       # CC-BY-4.0 for documentation
│
├── docs/
│   │
│   ├── 000-foundation/
│   │   ├── ANIF-001_Charter.md
│   │   ├── ANIF-002_Principles.md
│   │   ├── ANIF-003_Glossary.md
│   │   └── ANIF-004_RACI.md
│   │
│   ├── 100-governance/
│   │   ├── ANIF-100_Governance_Overview.md
│   │   ├── ANIF-101_Compliance_Mapping.md
│   │   ├── ANIF-102_NIST_CSF_Alignment.md
│   │   ├── ANIF-103_Autonomous_Action_Policy.md
│   │   ├── ANIF-104_Change_Management_Policy.md
│   │   ├── ANIF-105_Escalation_Exception_Policy.md
│   │   ├── ANIF-106_Data_Residency_Compliance_Policy.md
│   │   └── ANIF-107_Audit_Trail_Requirements.md
│   │
│   ├── 200-architecture/
│   │   ├── ANIF-200_Reference_Architecture.md
│   │   ├── ANIF-201_Business_Architecture.md
│   │   ├── ANIF-202_Data_Architecture.md
│   │   ├── ANIF-203_Application_Architecture.md
│   │   ├── ANIF-204_Technology_Architecture.md
│   │   └── ANIF-205_Security_Architecture.md
│   │
│   ├── 300-core/
│   │   ├── ANIF-300_Intent_Framework.md
│   │   ├── ANIF-301_Intent_Authoring_Standard.md
│   │   ├── ANIF-302_Policy_Engine_Specification.md
│   │   ├── ANIF-303_Policy_Conflict_Resolution.md
│   │   ├── ANIF-304_Risk_Trust_Quantification.md
│   │   ├── ANIF-305_Decision_Engine_Specification.md
│   │   ├── ANIF-306_Action_Execution_Standard.md
│   │   ├── ANIF-307_Distributed_Source_of_Truth.md
│   │   └── ANIF-308_Digital_Twin_Validation.md
│   │
│   ├── 400-operations/
│   │   ├── ANIF-400_Operations_Overview.md
│   │   ├── ANIF-401_Observability_Standard.md
│   │   ├── ANIF-402_Explainability_Requirements.md
│   │   ├── ANIF-403_Closed_Loop_Feedback.md
│   │   ├── ANIF-404_Human_in_Loop_Controls.md
│   │   ├── ANIF-405_Incident_Outage_Modeling.md
│   │   ├── ANIF-406_Governance_Controls.md
│   │   └── ANIF-407_Dark_NOC_Maturity_Model.md
│   │
│   ├── 500-conformance/
│   │   ├── ANIF-500_Conformance_Overview.md
│   │   ├── ANIF-501_Conformance_Level_Definitions.md
│   │   ├── ANIF-502_Certification_Process.md
│   │   ├── ANIF-503_Test_Case_Catalogue.md
│   │   ├── ANIF-504_Vendor_Profile_Template.md
│   │   ├── ANIF-505_Cloud_Profile_Template.md
│   │   └── ANIF-506_Telco_Profile_Template.md
│   │
│   └── 600-annexes/
│       ├── ANIF-600_Schema_Reference.md
│       ├── ANIF-601_Worked_Examples.md
│       ├── ANIF-602_Implementation_Guide.md
│       ├── ANIF-603_Glossary_Extensions.md
│       └── ANIF-604_Reference_Prototype_Guide.md
│
├── schemas/
│   ├── intent_schema.yml              # (existing — promote to v1.0)
│   ├── action_schema.yml              # (existing — promote to v1.0)
│   ├── policy_schema.yml              # (existing — promote to v1.0)
│   ├── risk_score_schema.yml          # (to create)
│   ├── audit_record_schema.yml        # (to create)
│   └── plugin_manifest_schema.yml     # (to create)
│
├── profiles/
│   ├── aws/
│   │   └── ANIF-PROFILE-AWS_v0.1.md
│   ├── azure/
│   │   └── ANIF-PROFILE-AZURE_v0.1.md
│   ├── gcp/
│   │   └── ANIF-PROFILE-GCP_v0.1.md
│   ├── cisco-aci/
│   │   └── ANIF-PROFILE-CISCO-ACI_v0.1.md
│   └── juniper-apstra/
│       └── ANIF-PROFILE-JUNIPER-APSTRA_v0.1.md
│
├── conformance/
│   ├── test-cases/
│   │   ├── TC-001_intent_validation.yml
│   │   ├── TC-002_policy_evaluation.yml
│   │   ├── TC-003_risk_scoring.yml
│   │   ├── TC-004_audit_trail.yml
│   │   └── TC-005_rollback_capability.yml
│   └── self-assessment/
│       └── ANIF_Self_Assessment_Checklist.md
│
├── prototype/
│   ├── README.md
│   └── src/                           # Reference implementation (separate README)
│
└── prompts/                           # (existing — keep as tooling aids)
    └── ...
```

---

## 4. Document Naming Conventions

### Core Document Files

```
ANIF-{series}{number}_{Title_With_Underscores}.md
```

**Examples:**
```
ANIF-001_Charter.md
ANIF-304_Risk_Trust_Quantification.md
ANIF-502_Certification_Process.md
```

**Rules:**
- Series prefix matches the folder number (`000`, `100`, `200`, etc.)
- Document number is 3 digits within the series
- Title uses Title_Case_With_Underscores (no spaces, no hyphens in title portion)
- Always `.md` extension for spec documents

### Profile Files

```
ANIF-PROFILE-{VENDOR-OR-PLATFORM}_{vX.Y}.md
```

**Examples:**
```
ANIF-PROFILE-AWS_v0.1.md
ANIF-PROFILE-CISCO-ACI_v1.0.md
```

### Schema Files

```
{subject}_schema.{yml|json}
```

**Examples:**
```
intent_schema.yml
audit_record_schema.yml
```

### Test Case Files

```
TC-{number}_{subject}.yml
```

**Examples:**
```
TC-001_intent_validation.yml
TC-023_policy_conflict_resolution.yml
```

### Conformance Checklist Files

```
ANIF_Self_Assessment_{scope}.md
ANIF_Certification_Report_{org}_{date}.md
```

### Versioned Release Archives

```
anif-v{MAJOR}.{MINOR}.{PATCH}.tar.gz
anif-v1.0.0.tar.gz
```

---

## 5. Document Series Index

### ANIF-000 Foundation

| Doc ID | Title | Status | Priority |
|---|---|---|---|
| ANIF-001 | Charter and Scope | To create | P0 |
| ANIF-002 | Principles | To create | P0 |
| ANIF-003 | Glossary | To create | P0 |
| ANIF-004 | Roles and RACI | To create | P1 |

### ANIF-100 Governance

| Doc ID | Title | Status | Priority |
|---|---|---|---|
| ANIF-100 | Governance Overview | To create | P0 |
| ANIF-101 | Compliance Mapping (TMForum, ETSI ZSM) | To create | P1 |
| ANIF-102 | NIST CSF Alignment | To create | P1 |
| ANIF-103 | Autonomous Action Policy | To create | P0 |
| ANIF-104 | Change Management Policy | To create | P0 |
| ANIF-105 | Escalation and Exception Policy | To create | P1 |
| ANIF-106 | Data Residency and Compliance Policy | To create | P1 |
| ANIF-107 | Audit Trail Requirements | To create | P0 |

### ANIF-200 Architecture

| Doc ID | Title | Status | Source |
|---|---|---|---|
| ANIF-200 | Reference Architecture | To create | New |
| ANIF-201 | Business Architecture (TOGAF Business Domain) | To create | New |
| ANIF-202 | Data Architecture (TOGAF Data Domain) | To create | New |
| ANIF-203 | Application Architecture (TOGAF Application Domain) | To create | New |
| ANIF-204 | Technology Architecture (TOGAF Technology Domain) | To create | New |
| ANIF-205 | Security Architecture | To create | New |

### ANIF-300 Core Framework

| Doc ID | Title | Status | Source |
|---|---|---|---|
| ANIF-300 | Intent Framework Overview | To create | New |
| ANIF-301 | Intent Authoring Standard | To create | New |
| ANIF-302 | Policy Engine Specification | To create | prompts/policy_engine.md |
| ANIF-303 | Policy Conflict Resolution and Precedence | Draft exists | docs/strategic/04 |
| ANIF-304 | Risk and Trust Quantification | Draft exists | prompts/01 |
| ANIF-305 | Decision Engine Specification | To create | prompts/Decision Engine Prompt |
| ANIF-306 | Action Execution Standard | To create | schemas/action_schema.yml |
| ANIF-307 | Distributed Source of Truth | Draft exists | docs/strategic/05 |
| ANIF-308 | Digital Twin and Change Validation | Draft exists | prompts/02 |

### ANIF-400 Operations

| Doc ID | Title | Status | Source |
|---|---|---|---|
| ANIF-400 | Operations Overview | To create | New |
| ANIF-401 | Observability Standard | Draft exists | docs/strategic/09 |
| ANIF-402 | Explainability Requirements | Draft exists | docs/strategic/09 |
| ANIF-403 | Closed Loop Feedback and Learning | Draft exists | docs/strategic/03 |
| ANIF-404 | Human-in-Loop Controls | Draft exists | docs/strategic/06 |
| ANIF-405 | Incident and Outage Modeling | Draft exists | docs/strategic/07 |
| ANIF-406 | Governance Controls | Draft exists | docs/strategic/06 |
| ANIF-407 | Dark NOC Maturity Model | Draft exists | docs/strategic/08 |

### ANIF-500 Conformance

| Doc ID | Title | Status | Priority |
|---|---|---|---|
| ANIF-500 | Conformance Overview | To create | P1 |
| ANIF-501 | Conformance Level Definitions | To create | P1 |
| ANIF-502 | Certification Process | To create | P2 |
| ANIF-503 | Test Case Catalogue | To create | P1 |
| ANIF-504 | Vendor Profile Template | To create | P2 |
| ANIF-505 | Cloud Profile Template | To create | P2 |
| ANIF-506 | Telco Profile Template | To create | P2 |

### ANIF-600 Annexes

| Doc ID | Title | Status | Source |
|---|---|---|---|
| ANIF-600 | Schema Reference | Draft exists | schemas/ |
| ANIF-601 | Worked Examples | To create | prompts/examples |
| ANIF-602 | Implementation Guide | To create | New |
| ANIF-603 | Glossary Extensions | To create | New |
| ANIF-604 | Reference Prototype Guide | To create | New |

---

## 6. Document Template

Every ANIF document must open with this frontmatter block and follow this structure.

```markdown
# ANIF-{NNN}: {Title}

| Field        | Value                                      |
|--------------|--------------------------------------------|
| Doc ID       | ANIF-{NNN}                                 |
| Series       | {Foundation / Governance / Architecture /  |
|              |  Core / Operations / Conformance / Annex}  |
| Version      | {X.Y.Z}                                    |
| Status       | {Draft / Review / Approved / Deprecated}   |
| Authors      | {Name(s)}                                  |
| Reviewers    | {Name(s)}                                  |
| Approved by  | {Name / Working Group}                     |
| Created      | {YYYY-MM-DD}                               |
| Last updated | {YYYY-MM-DD}                               |
| Replaces     | {ANIF-NNN or N/A}                          |
| Related docs | {ANIF-NNN, ANIF-NNN}                       |

---

## Abstract

{2–4 sentence summary of what this document defines and why it exists.}

---

## 1. Introduction

### 1.1 Purpose
### 1.2 Scope
### 1.3 Out of scope
### 1.4 Intended audience

---

## 2. Normative references

{List of external standards this document references normatively.}

- RFC 2119 — Key words for use in RFCs (MUST, SHOULD, MAY semantics)
- {Other references}

---

## 3. Terms and definitions

{Terms specific to this document not covered in ANIF-003.}

| Term | Definition |
|---|---|
| | |

---

## 4. {Core content sections — specific to each document}

{All normative requirements must use RFC 2119 keywords:
  MUST / MUST NOT — mandatory
  SHOULD / SHOULD NOT — recommended
  MAY — optional}

---

## 5. Conformance requirements

{What an implementation MUST do to conform to this document.}

---

## 6. Security considerations

---

## 7. Operational considerations

---

## Appendix A: Examples

## Appendix B: Change history

| Version | Date | Author | Changes |
|---|---|---|---|
| 0.1.0 | {date} | {author} | Initial draft |
```

---

## 7. Versioning & Lifecycle

### Semantic Versioning

ANIF uses semantic versioning: `MAJOR.MINOR.PATCH`

| Increment | Trigger |
|---|---|
| `MAJOR` | Breaking change to schemas, conformance criteria, or normative requirements |
| `MINOR` | New documents, new non-breaking requirements, new conformance levels |
| `PATCH` | Corrections, clarifications, editorial changes |

### Document Status Lifecycle

```
Draft → Review → Approved → Deprecated
              ↘ Rejected
```

| Status | Meaning |
|---|---|
| `Draft` | Work in progress; not for external use |
| `Review` | Open for community comment (issue tracker) |
| `Approved` | Normative; included in a versioned ANIF release |
| `Deprecated` | Superseded by a newer document; kept for reference |
| `Rejected` | Did not reach approval; archived only |

### Release Cadence

- **Patch releases:** as needed for corrections
- **Minor releases:** quarterly
- **Major releases:** annual, with 6-month deprecation notice for breaking changes

---

## 8. External Alignment Map

### NIST Cybersecurity Framework (CSF) Mapping

| CSF Function | ANIF Documents |
|---|---|
| Identify | ANIF-202, ANIF-307, ANIF-403 |
| Protect | ANIF-103, ANIF-205, ANIF-404 |
| Detect | ANIF-401, ANIF-403, ANIF-405 |
| Respond | ANIF-305, ANIF-405, ANIF-406 |
| Recover | ANIF-308, ANIF-405, ANIF-407 |

### ITIL 4 Practice Mapping

| ITIL Practice | ANIF Documents |
|---|---|
| Change enablement | ANIF-104, ANIF-305, ANIF-308 |
| Incident management | ANIF-405 |
| Problem management | ANIF-403, ANIF-405 |
| Service configuration management | ANIF-307 |
| Monitoring and event management | ANIF-401, ANIF-402 |
| Continual improvement | ANIF-403, ANIF-407 |

### TOGAF ADM Mapping

| TOGAF Domain | ANIF Documents |
|---|---|
| Preliminary (principles) | ANIF-001, ANIF-002 |
| Business Architecture | ANIF-201, ANIF-407 |
| Data Architecture | ANIF-202, ANIF-307 |
| Application Architecture | ANIF-203, ANIF-300–308 |
| Technology Architecture | ANIF-204, ANIF-600 |

### ETSI ZSM Cross-Reference

| ZSM Concept | ANIF Equivalent |
|---|---|
| Intent interface | ANIF-300, ANIF-301 |
| Closed-loop automation | ANIF-403 |
| Cross-domain orchestration | ANIF-200, ANIF-305 |
| Analytics service | ANIF-401, ANIF-402 |

---

## 9. Conformance Levels

Implementations declare conformance at one of four levels.

| Level | Name | Description | Key Requirements |
|---|---|---|---|
| L1 | Aware | Organisation has reviewed ANIF and mapped its current state | Self-assessment completed; gaps documented |
| L2 | Aligned | Core governance and policy documents implemented | ANIF-001–107 satisfied; audit trail in place |
| L3 | Conformant | All core framework domains implemented and tested | ANIF-300–407 satisfied; test cases TC-001–005 passed |
| L4 | Certified | Third-party verified conformance | ANIF-500–503 process completed; certification issued |

### Conformance Claims

A conforming implementation MUST:
- Declare which ANIF version it conforms to
- Declare its conformance level (L1–L4)
- Publish a completed self-assessment checklist (L2+)
- Pass all mandatory test cases for its declared level (L3+)
- Not claim a higher level than verified

---

## 10. Contribution Model

### How to Contribute

1. **Issues** — raise in the GitHub issue tracker for corrections, questions, or proposals
2. **Proposals** — open a `proposal:` issue with the ANIF document ID affected and a description
3. **Pull requests** — follow the template below; PRs require one working group review and one approval
4. **New documents** — submit a `new-doc:` issue first; documents are assigned an ID by the maintainer

### Working Group

ANIF is governed by the ANIF Working Group. Membership is open to anyone who:
- Has made at least one accepted contribution, or
- Represents an organisation that has declared ANIF conformance

### PR Checklist

- [ ] Document uses the standard template from Section 6
- [ ] Naming convention from Section 4 followed
- [ ] RFC 2119 keywords used correctly for all normative statements
- [ ] CHANGELOG.md updated
- [ ] Relevant cross-references added to related documents
- [ ] If schema change: backwards compatibility confirmed or MAJOR version bump noted

### Governance of This Framework

ANIF itself is governed by ANIF-001 (Charter). Changes to the Charter require a supermajority (2/3) of active working group members.

---

## Appendix A: Priority Build Order

Build documents in this order to get to a publishable v0.1 skeleton.

### Phase 1 — Foundation (weeks 1–2)
```
ANIF-001  Charter and Scope
ANIF-002  Principles
ANIF-003  Glossary
ANIF-103  Autonomous Action Policy
ANIF-107  Audit Trail Requirements
```

### Phase 2 — Architecture & Core (weeks 3–5)
```
ANIF-200  Reference Architecture
ANIF-300  Intent Framework Overview
ANIF-301  Intent Authoring Standard
ANIF-302  Policy Engine Specification
ANIF-304  Risk and Trust Quantification
ANIF-407  Dark NOC Maturity Model
```

### Phase 3 — Operations & Governance (weeks 6–8)
```
ANIF-100  Governance Overview
ANIF-102  NIST CSF Alignment
ANIF-104  Change Management Policy
ANIF-401  Observability Standard
ANIF-403  Closed Loop Feedback
ANIF-404  Human-in-Loop Controls
ANIF-405  Incident and Outage Modeling
```

### Phase 4 — Conformance & Annexes (weeks 9–12)
```
ANIF-500  Conformance Overview
ANIF-501  Conformance Level Definitions
ANIF-503  Test Case Catalogue
ANIF-600  Schema Reference
ANIF-602  Implementation Guide
```

---

## Appendix B: Existing Asset Migration Map

Map your current files to their ANIF home.

| Existing file | Target ANIF document |
|---|---|
| docs/strategic/03_Closed_Loop_Feedback_Learning.md | ANIF-403 |
| docs/strategic/04_Policy_Conflict_Resolution_Precedence.md | ANIF-303 |
| docs/strategic/05_Distributed_Source_of_Truth.md | ANIF-307 |
| docs/strategic/06_Governance_Human_in_Loop.md | ANIF-404, ANIF-406 |
| docs/strategic/07_Incident_Outage_Modeling.md | ANIF-405 |
| docs/strategic/08_Dark_NOC_Evolution_Plan.md | ANIF-407 |
| docs/strategic/09_Observability_Explainability_Artifacts.md | ANIF-401, ANIF-402 |
| docs/strategic/10_Extensibility_Plugin_Model.md | ANIF-203 (plugin section) |
| schemas/intent_schema.yml | ANIF-600 + schemas/intent_schema.yml v1.0 |
| schemas/action_schema.yml | ANIF-600 + schemas/action_schema.yml v1.0 |
| schemas/policy_schema.yml | ANIF-600 + schemas/policy_schema.yml v1.0 |
| prompts/01_Risk_Trust_Quantification_Framework_prompt.md | ANIF-304 (appendix) |
| prompts/02_Change_Validation_Digital_Twin_prompt.md | ANIF-308 (appendix) |
| prompts/policy_engine.md | ANIF-302 (appendix) |
| prompts/Intent_Vailidation_service_prompt.md | ANIF-301 (appendix) |

---

*ANIF is an open specification. Feedback, issues, and contributions are welcome via the project repository.*
