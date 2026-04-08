# ANIF-903: Build-Time Council

| Field        | Value                                              |
|--------------|----------------------------------------------------|
| Doc ID       | ANIF-903                                           |
| Series       | AI Council                                         |
| Version      | 0.1.0                                              |
| Status       | Draft                                              |
| Authors      | ANIF Working Group                                 |
| Reviewers    | —                                                  |
| Approved by  | —                                                  |
| Created      | 2026-04-08                                         |
| Last updated | 2026-04-08                                         |
| Replaces     | N/A                                                |
| Related docs | ANIF-803, ANIF-820, ANIF-824, ANIF-900, ANIF-901, ANIF-906 |

---

## Abstract

This document defines the Build-Time Council: its trigger conditions, required inputs, deliberation requirements, decision types, and conditional approval provisions. The Build-Time Council MUST convene before any new agent type is deployed to production, before any model version change, and before any capability expansion. Consensus from all veto seats is required — a single veto from the Ethics Chair, Security Chair, or Governance Chair blocks deployment. Conditional approval is permitted, and conditions MUST be documented, tracked to completion, and verified before the agent reaches VERIFIED trust status. The Build-Time Council extends and formalises the GARTH-COUNCIL-001 pre-deployment governance pattern for autonomous network infrastructure.

---

## 1. Introduction

### 1.1 Purpose

An agent deployed without structured human review of its capabilities, test results, and supply chain provenance introduces unquantified risk into the operational environment. The Build-Time Council is the governance gate through which every new agent capability must pass before it is allowed to operate on the network.

### 1.2 Scope

Build-Time Council trigger conditions, required inputs, deliberation model, decision types, conditional approval provisions, and build artefact retention requirements.

### 1.3 Out of Scope

Council composition and quorum requirements (see ANIF-901), mode selection logic (see ANIF-902), Runtime Council procedures (see ANIF-904), Review Council procedures (see ANIF-905), deliberation time limits (see ANIF-906).

### 1.4 Intended Audience

- Build engineers preparing agent deployment packages
- Council seat holders reviewing deployment requests
- Security engineers assessing supply chain provenance
- Conformance assessors verifying build governance

---

## 2. Normative References

| Reference | Title |
|---|---|
| ANIF-803 | Agent Lifecycle Management |
| ANIF-805 | Agent Trust Model |
| ANIF-807 | LLM Agent Specification |
| ANIF-820 | AI Agent Testing and Red-Team Standards |
| ANIF-824 | Agent Supply Chain Security |
| ANIF-900 | AI Council Overview |
| ANIF-901 | AI Council Composition and Roles |
| ANIF-902 | Council Mode Selector |
| ANIF-906 | Council Deliberation Standards |
| ANIF-907 | Council Audit and Accountability |
| RFC 2119 | Key words for use in RFCs to Indicate Requirement Levels |

---

## 3. Trigger Conditions

The Build-Time Council MUST convene before any of the following actions:

| Trigger | Definition |
|---|---|
| New agent deployment | Any new agent type being deployed to the production environment for the first time |
| Model version change | Any change to the LLM model version identifier declared in an agent manifest (ANIF-807) |
| Capability expansion | Any change to an agent's capability manifest that adds new permitted actions, expands tier access, or increases permission scope |
| Trust level reinstatement | Any reinstatement of an agent from DEGRADED or UNTRUSTED trust status following a security incident |

A deployment that proceeds without a Build-Time Council review under any of these trigger conditions is a conformance violation and MUST be reported to the governance committee within 5 business days of discovery.

---

## 4. Required Inputs

The submitting team MUST provide the following artefacts to the council before the review begins. The council MUST NOT begin deliberation with incomplete inputs.

| Input | Description | ANIF Source |
|---|---|---|
| Agent manifest | Complete capability manifest including all declared permissions, tier assignment, and trust model fields | ANIF-802 |
| Capability scope document | Description of what the agent does, what it cannot do, and the boundaries of its operation | ANIF-802 |
| Test results | Completed results from all ANIF-820 mandatory test types, signed by the test lead | ANIF-820 |
| Supply chain provenance | Model hash, training data provenance record, dependency scan results | ANIF-824 |
| Red-team findings | Red-team report where available; if not available, documented rationale for absence | ANIF-820, ANIF-848 |
| Ethics assessment | Assessment of the agent's ethics constraint implementation against ANIF-720–725 | ANIF-720 |
| Prior council decisions | Any prior Build-Time Council decisions on this agent type or model | ANIF-907 |

---

## 5. Deliberation Model

The Build-Time Council uses the consensus deliberation model (ANIF-906) for all deployment decisions. Consensus from all veto seats — Ethics Chair, Security Chair, and Governance Chair — is required. No deployment proceeds without consensus from all three veto-holding seats.

Non-veto seats (Operations Chair, Architecture Chair, Learning Chair, Human Advocate) contribute to deliberation and their positions are recorded, but their disagreement does not block a deployment where all three veto seats agree.

---

## 6. Decision Types

| Decision | Definition | Effect |
|---|---|---|
| Approved | Council reaches consensus to approve deployment | Agent transitions to ACTIVE lifecycle state with PROVISIONAL trust for minimum 72 hours (ANIF-805) |
| Blocked | One or more veto seats exercise their veto | Agent MUST NOT be deployed; submitting team MUST address cited deficiencies before resubmission |
| Conditional | Council approves deployment subject to stated conditions | Agent transitions to ACTIVE with PROVISIONAL trust; conditions MUST be met before VERIFIED status is granted |
| Deferred | Council requires additional information before deciding | Deployment is held; submitting team MUST provide requested information within the stated window |

### 6.1 Blocked Decision Requirements

A blocked decision MUST include:
- The specific ANIF requirement(s) that were not satisfied
- The specific deficiency in the submitted artefacts
- The minimum remediation required before resubmission is permitted

### 6.2 Conditional Approval Requirements

A conditional approval MUST include:
- Each condition stated precisely and independently verifiable
- The deadline for meeting each condition
- The council member responsible for verifying each condition
- The consequence of failing to meet a condition within the deadline (typically: reversion to DEGRADED trust status)

Conditions MUST be tracked in the council record (ANIF-907). An agent with outstanding unmet conditions MUST NOT be granted VERIFIED trust status.

---

## 7. Build Artefact Retention

All artefacts submitted to the Build-Time Council MUST be retained in the build artefact store for the duration of the agent's operational lifetime plus 3 years. Artefacts MUST be accessible to the governance committee, Review Council, and external auditors. Deletion of build artefacts during the retention period requires governance committee approval.

---

## 8. Conformance Requirements

| ID | Requirement |
|---|---|
| CR-903-01 | The Build-Time Council MUST convene before any new agent deployment, model version change, capability expansion, or trust reinstatement. |
| CR-903-02 | Council deliberation MUST NOT begin with incomplete required inputs. |
| CR-903-03 | Consensus from all three veto seats (Ethics Chair, Security Chair, Governance Chair) is REQUIRED for a deployment to proceed. |
| CR-903-04 | A blocked decision MUST state the specific ANIF requirement(s) not satisfied. |
| CR-903-05 | A conditional approval MUST list each condition as a precisely stated, independently verifiable requirement. |
| CR-903-06 | Agents with outstanding unmet conditions MUST NOT be granted VERIFIED trust status. |
| CR-903-07 | Build artefacts MUST be retained for the agent's operational lifetime plus 3 years. |

---

## 9. Security Considerations

The Build-Time Council is the organisation's primary defence against malicious or misconfigured agents entering production. The supply chain provenance artefact (ANIF-824) is the most critical input — a model with a tampered supply chain that passes all other tests represents an undetected compromise. The Security Chair MUST specifically review the supply chain provenance artefact and the model hash against the approved registry before indicating consensus.

---

## 10. Operational Considerations

Build-Time Council reviews are predictable events that can be scheduled. Submitting teams SHOULD notify council seat holders at least 5 business days before the intended review date and provide all artefacts at least 2 business days in advance of the council session. Last-minute submission of artefacts is a common cause of Build-Time Council deferrals and deployment delays.
