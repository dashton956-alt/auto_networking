# ANIF-003: Terms and Definitions

| Field        | Value                                    |
|--------------|------------------------------------------|
| Doc ID       | ANIF-003                                 |
| Series       | Foundation                               |
| Version      | 0.1.0                                    |
| Status       | Draft                                    |
| Authors      | ANIF Working Group                       |
| Reviewers    | —                                        |
| Approved by  | —                                        |
| Created      | 2026-04-07                               |
| Last updated | 2026-04-07                               |
| Replaces     | N/A                                      |
| Related docs | All ANIF documents                       |

---

## Abstract

This document defines the authoritative vocabulary for the Autonomous Networking & Infrastructure Framework (ANIF). All ANIF documents MUST use terms consistently with the definitions provided here. Where a term appears in a normative ANIF document without qualification, the definition in this glossary applies. Terms sourced from external standards are noted with their origin; where ANIF refines an external definition, the ANIF definition takes precedence within the ANIF context.

---

## 1. Introduction

### 1.1 Purpose

Precise, shared vocabulary is essential for a multi-stakeholder framework. Ambiguous terminology leads to inconsistent implementations, failed conformance tests, and misaligned expectations between vendors, operators, and standards bodies. This glossary provides the single authoritative source for all ANIF terminology.

### 1.2 Scope

This document covers all terms that appear in normative ANIF documents (series 000–500). Informative terms that appear only in series 600 annexes are noted as informative.

### 1.3 Out of Scope

- General networking or IT infrastructure terminology not specific to ANIF
- Terms whose ANIF usage is identical to the standard industry definition (these are referenced, not redefined)
- Product or vendor-specific terminology

### 1.4 Intended Audience

All ANIF document authors, implementers, conformance testers, operators, and reviewers.

---

## 2. Normative References

- RFC 2119 — Key words for use in RFCs to indicate requirement levels
- ETSI GS ZSM 001 — Zero-touch network & Service Management; Reference Architecture
- TMForum IG1218 — Autonomous Networks Reference Architecture
- NIST SP 800-53 Rev. 5 — Security and Privacy Controls
- IETF RFC 8993 — A Reference Model for Autonomic Networking

---

## 3. Terms and Definitions

Terms are listed alphabetically. For each term, the following fields are provided where applicable:
- **Definition**: The normative ANIF definition.
- **Context**: Where the term is principally used within the ANIF pipeline.
- **See also**: Related terms within this glossary.
- **Source**: External standard or document from which the term is derived or adapted (if applicable).

---

### 3.1 Core Pipeline Terms

| Term | Definition | Context | See also |
|---|---|---|---|
| **Intent** | A structured, declarative expression of a desired end-state for network or infrastructure configuration, submitted to the ANIF pipeline for evaluation and execution. An intent describes *what* should be achieved, not *how* to achieve it. An intent MUST conform to the ANIF Intent Schema. | Intent submission, validation | Action, Policy, Intent Validation |
| **Intent Validation** | The pipeline stage that verifies a submitted intent conforms to the ANIF Intent Schema, is internally consistent, and contains all mandatory fields before it is passed to policy evaluation. Intent validation MUST be the first stage in the ANIF pipeline. | Stage 1 of the pipeline | Intent, Policy Evaluation, Schema |
| **Policy** | A named, versioned set of rules that governs what actions are permitted, under what conditions, and with what constraints. Policies are evaluated deterministically by the Policy Engine against each intent. | Policy evaluation | Policy Evaluation, Policy Set, Governance Gate |
| **Policy Evaluation** | The pipeline stage in which the Policy Engine applies all active policies to a validated intent and produces a policy result. The policy result includes any conditions, restrictions, or blocks that apply to the intent. | Stage 2 of the pipeline | Policy, Policy Engine, Governance Gate |
| **Policy Set** | A versioned, named collection of policies that is atomically applied during policy evaluation. A policy set has a unique identifier and version number. Changes to a policy set MUST produce a new version. | Policy management | Policy, Policy Administrator |
| **Risk Score** | A numeric value, on a defined scale (0.0–1.0 by default), that quantifies the estimated risk associated with executing a specific action derived from an intent. Risk scores are produced by the Risk Scoring Engine and are one input to the Decision Engine. | Stage 3 of the pipeline | Risk Scoring Engine, Trust Score, Decision Engine |
| **Trust Score** | A numeric value, on a defined scale (0.0–1.0 by default), that represents the assessed trustworthiness of an automation agent or human operator submitting intents. Trust scores are maintained by the governance system and are one input to policy evaluation. | Policy evaluation | Risk Score, Automation Agent, Least Privilege |
| **Safety Decision** | The output of the Decision Engine for a specific intent, comprising a governance mode (`auto`, `manual_review`, or `block`), a risk score, a reasoning chain, and applicable conditions. A safety decision is a first-class ANIF object with its own identity and audit record. | Stage 4 of the pipeline | Decision Engine, Governance Mode, Reasoning Chain |
| **Action** | A specific, concrete operation to be executed on network or infrastructure — derived from a validated, policy-checked, and risk-scored intent. An action MUST conform to the ANIF Action Schema and MUST include a `rollback_spec`. An action is more specific than an intent: one intent may produce one or more actions. | Stage 5 of the pipeline | Intent, Action Executor, Rollback |
| **Rollback** | A defined, tested mechanism that reverses a previously executed action and restores the affected system to its pre-action state. Every action MUST have a rollback mechanism defined in its `rollback_spec` before execution is permitted. | Post-action recovery | Action, Reversibility (P-01), Rollback Spec |
| **Rollback Spec** | The structured specification, carried in every Action object, that defines: the rollback mechanism type, the scope of rollback, the expected post-rollback state, and the rollback window (time within which rollback is guaranteed). | Action schema | Rollback, Action |
| **Audit Record** | An immutable, append-only, timestamped, structured record of an event in the ANIF pipeline. Audit records MUST be produced for every pipeline stage and MUST NOT be mutated or deleted after creation. | Throughout the pipeline | Audit Store, Immutable Log, Auditability (P-02) |
| **Reasoning Chain** | An ordered, human-readable list of steps that explains how the Decision Engine reached a specific Safety Decision. Each step identifies the rule or factor evaluated, the input values, and the intermediate conclusion. The reasoning chain MUST be generated at decision time and stored with the Safety Decision. | Decision explanation | Safety Decision, Explainability (P-04), /why API |
| **Governance Gate** | The decision point in the ANIF pipeline, evaluated by the Policy Engine and Decision Engine, that classifies an intent as `auto`, `manual_review`, or `block`. The governance gate is mandatory and MUST NOT be bypassed. | Stage 4 of the pipeline | Governance Mode, Policy Evaluation, Human Override (P-06) |
| **Governance Mode** | One of three possible classifications produced by the Governance Gate: `auto` (action may proceed without human review), `manual_review` (action is queued for human approval before proceeding), or `block` (action is permanently rejected). | Decision output | Governance Gate, Governance Ticket, Human Override |
| **Governance Ticket** | A work item created in the governance queue when an intent receives a `manual_review` governance mode. The ticket contains the intent, safety decision, reasoning chain, and risk score. A human operator MUST review and either approve or reject the ticket before the action proceeds. | Manual review workflow | Governance Mode, Human Override, Escalation |

---

### 3.2 System Components

| Term | Definition | Context | See also |
|---|---|---|---|
| **Decision Engine** | The ANIF pipeline component that receives the outputs of policy evaluation and risk scoring and produces a Safety Decision, including a governance mode and reasoning chain. The Decision Engine MUST be deterministic and MUST NOT contain non-deterministic logic. | Core engine | Policy Engine, Risk Scoring Engine, Safety Decision |
| **Policy Engine** | The ANIF pipeline component that evaluates all active policies in a Policy Set against a validated intent and produces a policy result. The Policy Engine MUST be a pure function: identical inputs MUST always produce identical outputs. | Core engine | Policy, Policy Evaluation, Determinism (P-03) |
| **Risk Scoring Engine** | The ANIF pipeline component that computes a Risk Score for an intent by evaluating a defined set of risk factors and their weights. The Risk Scoring Engine MUST be a pure function. | Core engine | Risk Score, Decision Engine, Determinism (P-03) |
| **Action Executor** | The ANIF pipeline component responsible for carrying out an approved Action on the target network or infrastructure. An Action Executor MUST implement a `rollback()` handler. Action Executors MUST NOT have capabilities beyond those declared in their capability manifest. | Stage 5 of the pipeline | Action, Rollback, Adapter, Least Privilege (P-05) |
| **Adapter** | A software plugin that translates between the ANIF abstract model and a specific vendor's or cloud provider's native API or configuration format. Adapters are the only ANIF components that MAY contain vendor-specific code. Adapters MUST implement the ANIF Adapter Interface (ANIF-401). | Integration layer | Plugin, Vendor Neutrality (P-08), Action Executor |
| **Plugin** | Synonym for Adapter in the ANIF context. Used interchangeably. | Integration layer | Adapter |
| **Audit Store** | The persistent, append-only data store in which all Audit Records are written. The Audit Store MUST enforce append-only semantics at the storage layer. | Audit component | Audit Record, Immutable Log |
| **Intent Validator** | The ANIF pipeline component responsible for schema validation, internal consistency checking, and pre-flight verification of submitted intents. | Stage 1 of the pipeline | Intent, Intent Validation |

---

### 3.3 Concepts and Properties

| Term | Definition | Context | See also |
|---|---|---|---|
| **Closed Loop** | An automation pattern in which the system observes an outcome, compares it to the intended state, and automatically initiates corrective action if a deviation is detected — without requiring human intervention for each cycle. ANIF governs closed-loop automation by requiring every loop iteration to pass through the full pipeline. | Architecture concept | Intent, Safety Decision, Governance Gate |
| **Dark NOC** | An operational mode in which the network operations centre operates without active human monitoring, relying entirely on autonomous systems to detect and respond to events. Dark NOC operation requires ANIF Level 4 maturity and full compliance with all twelve ANIF principles. | Maturity model | Maturity Level, Autonomous Action |
| **Determinism** | The property of a function or system whereby identical inputs always produce identical outputs, with no dependence on time, randomness, or external non-deterministic state. Determinism is required by P-03 for all policy evaluation and risk scoring functions. | Principle | P-03 Determinism, Policy Engine, Risk Scoring Engine |
| **Digital Twin** | A real-time or near-real-time virtual representation of a network or infrastructure topology and state, used as a simulation environment for validating intents and testing actions before they are executed on production infrastructure. A Digital Twin MAY be used to pre-validate intents but MUST NOT replace the full ANIF pipeline. | Pre-execution simulation | Intent Validation, Action |
| **Escalation** | The process of routing a halted, blocked, or uncertain pipeline event to a human operator for review and action. Escalations MUST produce a governance ticket and MUST trigger operator notification. | Human oversight | Governance Ticket, Fail Safe (P-07), Human Override (P-06) |
| **Explainability** | The property of a decision-making system whereby every decision it produces can be explained in human-readable terms that a domain expert can evaluate without access to system source code. Required by P-04. | Principle | P-04 Explainability, Reasoning Chain |
| **Fail Safe** | The operational posture of defaulting to halt and escalate when encountering uncertainty, error, or missing data, rather than proceeding with best-effort or silent failure. Required by P-07. | Principle | P-07 Fail Safe, Escalation |
| **Immutable Log** | An audit log whose records, once written, cannot be modified or deleted by any application operation. Immutability MAY be enforced at the storage layer, the application layer, or both. Required by P-02. | Audit | Audit Store, Audit Record, Auditability (P-02) |
| **Incremental Adoption** | The property of a framework or system that allows organisations to adopt individual components independently, gaining value from each stage before adding the next. Required by P-09. | Principle | P-09 Incremental Adoption |
| **Least Privilege** | The security principle that any actor (human or automated) should operate with only the minimum permissions required to perform its defined function. Required by P-05 for all automation agents and human operators. | Principle | P-05 Least Privilege, Capability Manifest |
| **Vendor Neutrality** | The property of a system or framework whereby its core logic and schemas do not depend on any specific vendor's API, SDK, or proprietary format. Required by P-08. | Principle | P-08 Vendor Neutrality, Adapter |

---

### 3.4 Roles and Actors

| Term | Definition | Context | See also |
|---|---|---|---|
| **Operator** | A human individual who interacts with the ANIF system in an operational capacity — submitting intents, reviewing governance tickets, invoking overrides, or monitoring system health. Operators are assigned one or more ANIF roles. | Human actor | Network Engineer, Senior Engineer, System Operator, ANIF-004 |
| **Automation Agent** | A non-human principal (software process, pipeline, or bot) that submits intents to the ANIF pipeline programmatically. An Automation Agent MUST be authenticated, MUST have an assigned role (at minimum `automation_agent`), and MUST have a capability manifest defining its permitted action types. | Automated actor | Intent, Capability Manifest, Least Privilege (P-05) |
| **Network Engineer** | An ANIF role assigned to human operators who submit intents, review `manual_review` escalations, and approve governance tickets within their authority level. The Network Engineer role does not have authority to approve high-risk actions — those require the Senior Engineer role. | Role | ANIF-004, Governance Ticket |
| **Senior Engineer** | An ANIF role with final approval authority for high-risk actions and the ability to override governance decisions. The Senior Engineer role MUST be assigned only to qualified individuals with appropriate authority and accountability. | Role | ANIF-004, Human Override (P-06) |
| **Policy Administrator** | An ANIF role responsible for managing policy sets, reviewing policy conflict resolution outcomes, and approving or rejecting policy change proposals from the learning feedback loop. | Role | Policy Set, Continuous Learning (P-12), ANIF-004 |
| **Compliance Officer** | An ANIF role with read access to audit logs and the ability to query `/audit` and `/audit/{id}/why` endpoints. The Compliance Officer role does not have action submission or approval authority. | Role | Audit Record, ANIF-004 |
| **System Operator** | An ANIF role responsible for monitoring system health, managing adapter configurations, and escalating incidents. The System Operator role has access to system health APIs and incident management workflows. | Role | Adapter, Escalation, ANIF-004 |
| **ANIF Working Group** | The governing body responsible for maintaining ANIF framework documents, assigning document IDs, and approving specification changes. The WG operates according to the governance rules in ANIF-001. | Governance | ANIF-001 |

---

### 3.5 Governance and Compliance Terms

| Term | Definition | Context | See also |
|---|---|---|---|
| **Capability Manifest** | A versioned, policy-store-managed document that explicitly lists all action types a specific automation agent or action executor is permitted to perform. The capability manifest is evaluated by the Policy Engine as part of the P-05 (Least Privilege) check. | Policy | Least Privilege (P-05), Automation Agent, Action Executor |
| **Conformance Level** | One of four graduated levels indicating the degree to which an ANIF implementation satisfies the framework's requirements. Levels are: L1 Aware, L2 Aligned, L3 Conformant, L4 Certified. Each level has defined requirements in the ANIF-500 series. | Conformance | ANIF-500, Conformance Test |
| **Conformance Test** | A defined, repeatable test procedure that verifies a specific normative requirement of the ANIF framework. Conformance tests are specified in the ANIF-500 series and are the basis for conformance level certification. | Conformance | Conformance Level, ANIF-500 |
| **Data Residency** | The constraint that data or configuration may only be processed within specified geographic jurisdictions or cloud regions. Data residency constraints are first-class policy inputs per P-11. | Compliance | P-11 Data Residency, Policy |
| **Governance Queue** | The ordered list of governance tickets awaiting human review. Tickets in the governance queue are visible to operators with the Network Engineer or Senior Engineer role, subject to their authority level. | Manual review workflow | Governance Ticket, Governance Mode |
| **Maturity Level** | One of five levels (Level 0 through Level 4) describing the degree of autonomous operations capability an organisation has achieved. Level 0 is fully manual; Level 4 is fully autonomous (Dark NOC). The ANIF maturity model is defined in the ANIF-100 series. | Maturity model | Dark NOC, ANIF-100 |

---

### 3.6 Technical and API Terms

| Term | Definition | Context | See also |
|---|---|---|---|
| **/why API** | The ANIF API endpoint (`/audit/{id}/why`) that returns the reasoning chain for a specific decision, identified by its audit record ID. The /why API MUST be implemented for all Safety Decisions and MUST be responsive within the audit record retention period. | API | Reasoning Chain, Explainability (P-04), Audit Record |
| **Autonomous Action** | Any configuration change, operational command, or infrastructure modification initiated by the ANIF system without direct human input at the moment of execution. Autonomous actions MUST pass through the full ANIF pipeline before execution. | Core concept | Action, Intent, Pipeline |
| **Pipeline** | The ordered sequence of processing stages through which every intent passes in the ANIF system: Intent → Validate → Policy Check → Risk Score → Decision → Action → Audit. The pipeline is the central architectural concept of ANIF. | Architecture | Intent, Action, Safety Decision, Audit Record |
| **Trace ID** | A unique identifier assigned to an intent at the point of submission and propagated through every subsequent pipeline stage, audit record, and log entry associated with that intent's processing. Trace IDs MUST be included in all API responses and audit records. | Observability | Audit Record, Pipeline |
| **Dry Run** | An execution mode in which a pipeline component evaluates its inputs and produces outputs as normal, but does not commit any side effects (configuration changes, state modifications). Dry run mode is used for testing and pre-validation. SHOULD be supported by all pipeline components. | Testing | Incremental Adoption (P-09) |
| **Schema** | A formal, machine-readable specification of the structure, field types, and validation rules for an ANIF data object (intent, action, policy, audit record, etc.). ANIF schemas MUST be expressed in JSON Schema or equivalent open format. | Data model | Vendor Neutrality (P-08), Intent, Action |
| **Rollback Window** | The time period after an action executes within which the rollback mechanism is guaranteed to be available and operable. After the rollback window closes, rollback may no longer be possible. The rollback window MUST be specified in the action's `rollback_spec`. | Post-action | Rollback, Rollback Spec |
| **Retention Period** | The length of time for which audit records are retained and queryable. The retention period MUST be configurable and MUST satisfy applicable regulatory requirements. After the retention period, records MAY be archived or purged in accordance with applicable data governance policies. | Audit | Audit Record, Audit Store |

---

### 3.7 Learning and Feedback Terms

| Term | Definition | Context | See also |
|---|---|---|---|
| **Continuous Learning** | The ANIF principle (P-12) that the system should improve from operational outcomes over time. Learning-derived policy changes MUST be subject to human approval before taking effect. | Principle | P-12 Continuous Learning, Feedback Loop |
| **Feedback Loop** | A system component that observes the outcomes of executed actions, compares them to expected outcomes, and generates structured proposals for policy or scoring adjustments. Feedback loop proposals MUST be submitted as governance tickets, not applied directly to production policy. | Learning component | Continuous Learning (P-12), Governance Ticket |
| **Policy Proposal** | A structured suggestion, generated by the feedback loop, that a specific policy rule or risk factor weight should be modified. Policy proposals are submitted as governance tickets and MUST be reviewed and approved by a Policy Administrator before taking effect. | Learning output | Feedback Loop, Policy Administrator, Governance Ticket |

---

## 4. Abbreviations and Acronyms

| Abbreviation | Expansion |
|---|---|
| ANIF | Autonomous Networking & Infrastructure Framework |
| ANIMA | Autonomic Networking Integrated Model and Approach (IETF) |
| CSF | Cybersecurity Framework (NIST) |
| ETSI | European Telecommunications Standards Institute |
| IETF | Internet Engineering Task Force |
| ITIL | IT Infrastructure Library |
| NOC | Network Operations Centre |
| NIST | National Institute of Standards and Technology |
| RFC | Request for Comments |
| RACI | Responsible, Accountable, Consulted, Informed |
| SLA | Service Level Agreement |
| TMForum | TeleManagement Forum |
| TOGAF | The Open Group Architecture Framework |
| ZSM | Zero-touch network and Service Management (ETSI) |
| WG | Working Group |
| API | Application Programming Interface |
| YAML | YAML Ain't Markup Language |
| JSON | JavaScript Object Notation |
| CI/CD | Continuous Integration / Continuous Delivery |
| PII | Personally Identifiable Information |
| GDPR | General Data Protection Regulation |

---

## 5. Conformance Requirements

- All ANIF documents (series 000–500) MUST use terms consistently with the definitions in this glossary.
- When a term in a normative document has a definition that differs from common industry usage, the ANIF definition in this glossary takes precedence.
- Implementers MUST use the ANIF definitions when interpreting normative requirements in any ANIF document.
- New terms introduced in ANIF documents MUST be submitted for inclusion in this glossary as part of the document review process.

---

## 6. Security Considerations

This document is definitional and does not introduce technical security controls. However:

- Terms such as "Audit Record", "Immutable Log", "Least Privilege", and "Capability Manifest" have direct security implications. Implementations MUST treat these as security-relevant concepts, not merely operational ones.
- The definitions of "Automation Agent" and "Operator" establish the subject identities for ANIF access control. Identity and authentication requirements for these actors are specified in ANIF-100.

---

## 7. Operational Considerations

- This glossary is a living document. Terms MUST be updated when new ANIF documents are published.
- Editors of new ANIF documents are responsible for submitting new terms to the ANIF-003 editor for inclusion.
- Terms MUST NOT be redefined in individual ANIF documents. If a document requires a term with a different meaning, the ANIF-003 editor MUST be consulted and the global definition updated if appropriate.

---

## Appendix A: Index of Terms by ANIF Document

The following table maps each term to the primary ANIF documents in which it appears normatively. This index is informative.

| Term | Primary Documents |
|---|---|
| Intent | ANIF-003, ANIF-200, ANIF-300 |
| Policy | ANIF-003, ANIF-100, ANIF-300 |
| Risk Score | ANIF-003, ANIF-300 |
| Trust Score | ANIF-003, ANIF-100 |
| Safety Decision | ANIF-003, ANIF-300 |
| Action | ANIF-003, ANIF-200, ANIF-400 |
| Rollback | ANIF-003, ANIF-002, ANIF-400 |
| Audit Record | ANIF-003, ANIF-002, ANIF-400 |
| Reasoning Chain | ANIF-003, ANIF-002, ANIF-300 |
| Governance Gate | ANIF-003, ANIF-100, ANIF-300 |
| Governance Mode | ANIF-003, ANIF-100 |
| Digital Twin | ANIF-003, ANIF-200 |
| Closed Loop | ANIF-003, ANIF-200 |
| Dark NOC | ANIF-003, ANIF-100 |
| Conformance Level | ANIF-003, ANIF-500 |
| Intent Validation | ANIF-003, ANIF-300 |
| Policy Evaluation | ANIF-003, ANIF-300 |
| Decision Engine | ANIF-003, ANIF-300 |
| Action Executor | ANIF-003, ANIF-400 |
| Adapter | ANIF-003, ANIF-400 |
| Operator | ANIF-003, ANIF-004 |
| Automation Agent | ANIF-003, ANIF-004, ANIF-100 |
| Escalation | ANIF-003, ANIF-100, ANIF-400 |
| Immutable Log | ANIF-003, ANIF-002, ANIF-400 |
| Determinism | ANIF-003, ANIF-002 |
| Explainability | ANIF-003, ANIF-002 |
| Least Privilege | ANIF-003, ANIF-002 |
| Fail Safe | ANIF-003, ANIF-002 |
| Vendor Neutrality | ANIF-003, ANIF-002 |
| Incremental Adoption | ANIF-003, ANIF-002 |
| Data Residency | ANIF-003, ANIF-002 |
| Continuous Learning | ANIF-003, ANIF-002 |

---

## Appendix B: Change History

| Version | Date | Author | Changes |
|---|---|---|---|
| 0.1.0 | 2026-04-07 | ANIF Working Group | Initial draft |
