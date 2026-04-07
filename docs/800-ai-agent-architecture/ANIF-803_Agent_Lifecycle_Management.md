# ANIF-803: Agent Lifecycle Management

| Field        | Value                                              |
|--------------|----------------------------------------------------|
| Doc ID       | ANIF-803                                           |
| Series       | AI Agent Architecture                              |
| Version      | 0.1.0                                              |
| Status       | Draft                                              |
| Authors      | ANIF Working Group                                 |
| Reviewers    | —                                                  |
| Approved by  | —                                                  |
| Created      | 2026-04-07                                         |
| Last updated | 2026-04-07                                         |
| Replaces     | N/A                                                |
| Related docs | ANIF-800, ANIF-802, ANIF-716, ANIF-843, ANIF-903  |

---

## Abstract

This document defines the complete lifecycle for every AI agent from initial proposal through decommissioning. Five lifecycle states are defined: PROPOSED, PROVISIONAL, ACTIVE, DEGRADED, and DECOMMISSIONED. No agent may skip a state. The build-time council review is mandatory before any agent reaches ACTIVE. Decommissioning is permanent — a decommissioned agent identity MUST NOT be reused.

---

## 1. Introduction

### 1.1 Purpose

Lifecycle management ensures that every deployed agent has a known state, a known history, and a known path to any other state. An agent without a defined lifecycle has an undefined accountability chain — it is unclear who approved it, what state it is in, and whether it can be trusted. The lifecycle model in this document is the operational expression of the accountability principles in ANIF-702.

### 1.2 Scope

This document covers:

- The five lifecycle states and their definitions
- The permitted transitions between states
- The conditions and approvals required for each transition
- The 72-hour PROVISIONAL trust period
- Decommissioning as a permanent terminal state

### 1.3 Out of Scope

This document does not cover:

- The build-time council review process (see ANIF-903)
- The progressive intervention model that drives state transitions (see ANIF-716)
- The signed manifest format (see ANIF-843)
- The permission changes associated with state transitions (see ANIF-802)

### 1.4 Intended Audience

- Platform engineers managing agent deployments
- Build-time council members conducting reviews
- AI engineers understanding what their agents go through before production
- Governance committee members monitoring agent state

---

## 2. Normative References

- ANIF-700 — Ethics Framework Overview
- ANIF-702 — Accountability Chain Model
- ANIF-716 — Progressive Intervention Model
- ANIF-802 — Agent Capabilities and Permissions
- ANIF-843 — Agent Zero Trust and Authentication
- ANIF-903 — Build-Time Council Review Process
- RFC 2119 — Key words for use in RFCs to indicate requirement levels

---

## 3. Terms and Definitions

**Lifecycle state:** One of five defined states (PROPOSED, PROVISIONAL, ACTIVE, DEGRADED, DECOMMISSIONED) that an agent occupies at any point in time. Exactly one state is current at all times.

**State transition:** A change from one lifecycle state to another. Every transition has a defined trigger, a defined approval requirement, and a defined set of actions that MUST occur during the transition.

**PROVISIONAL trust period:** A 72-hour period following initial deployment during which an agent is subject to enhanced monitoring and has reduced operational scope. All new agents begin in PROVISIONAL.

**Terminal state:** A state from which no further transitions are possible. DECOMMISSIONED is the only terminal state.

---

## 4. Lifecycle States

### 4.1 PROPOSED

An agent that has been proposed for deployment but has not yet passed build-time council review. The agent MUST NOT be deployed in any environment — including development or test environments that share infrastructure with production.

**Properties:**
- No agent identity issued
- No credentials provisioned
- No API access of any kind
- Exists as a specification document only

### 4.2 PROVISIONAL

An agent that has passed build-time council review and has been deployed for the first time, or has been re-deployed after a capability scope change. PROVISIONAL is a trust-limited operational state.

**Properties:**
- Agent identity issued and signed manifest active
- Full permission set as declared in manifest is active
- All actions subject to mandatory post-execution audit review within 24 hours
- A human counterpart MUST actively monitor the agent's outputs during this period
- Duration: 72 hours from initial deployment

**Why PROVISIONAL exists:**

A newly deployed agent has a signed manifest that the council has reviewed, but the agent's behaviour in production has not yet been observed. PROVISIONAL creates an observation window during which anomalous behaviour can be caught before the agent's actions are treated as routine.

### 4.3 ACTIVE

An agent that has completed the PROVISIONAL period without adverse observations. This is the normal operational state.

**Properties:**
- Full permission set active
- Standard audit and monitoring applies
- Normal escalation paths apply
- Progressive intervention model (ANIF-716) is the primary governance mechanism

### 4.4 DEGRADED

An agent that has received a Strike 2 event under the progressive intervention model (ANIF-716), or that has been placed in DEGRADED by a human operator due to observed anomalous behaviour.

**Properties:**
- Trust level set to PROVISIONAL (not the deployment PROVISIONAL — a runtime trust level)
- All actions require human approval before execution
- Enhanced logging: full prompt and output capture enabled
- The agent's human counterpart MUST be notified of the DEGRADED state

DEGRADED is a recoverable state. Recovery to ACTIVE requires human clearance from the AI Ethics Officer or the governance committee (ANIF-716 section 4).

### 4.5 DECOMMISSIONED

A permanently terminated agent. No further actions are permitted. The agent's identity is retired and MUST NOT be reused.

**Properties:**
- All credentials revoked
- All API access removed
- Agent identity recorded in the decommissioned identity register
- Identity MUST NOT be reissued or reused for any future agent
- A decommission record MUST be written to the audit trail identifying the reason, the date, and the approving authority

DECOMMISSIONED is terminal. There is no path from DECOMMISSIONED to any other state.

---

## 5. State Transitions

### 5.1 Permitted Transitions

| From | To | Trigger | Approver |
|---|---|---|---|
| PROPOSED | PROVISIONAL | Build-time council approval (ANIF-903) | Council majority |
| PROVISIONAL | ACTIVE | 72-hour period completed without adverse observations | Automatic (human audit confirms) |
| PROVISIONAL | DEGRADED | Adverse observation during PROVISIONAL period | AI Ethics Officer |
| PROVISIONAL | DECOMMISSIONED | Severity 1 incident during PROVISIONAL period | Governance committee |
| ACTIVE | DEGRADED | Strike 2 (ANIF-716) or human operator decision | Progressive intervention (auto) or AI Ethics Officer |
| ACTIVE | DECOMMISSIONED | Strike 4 (ANIF-716) or governance committee decision | Progressive intervention (auto) or governance committee |
| DEGRADED | ACTIVE | Human clearance after investigation | AI Ethics Officer or governance committee |
| DEGRADED | DECOMMISSIONED | Strike 3 escalation to Strike 4, or governance committee decision | Progressive intervention (auto) or governance committee |

### 5.2 Prohibited Transitions

The following transitions MUST NOT occur:

| Prohibited Transition | Reason |
|---|---|
| PROPOSED → ACTIVE | Skips build-time council review and PROVISIONAL period |
| PROPOSED → DECOMMISSIONED (without record) | Decommissioning requires a decommission record even for undeployed agents |
| DECOMMISSIONED → any state | Terminal state — no reactivation |
| ACTIVE → PROPOSED | An agent cannot be un-deployed back to proposal state |

### 5.3 Transition Logging

Every state transition MUST be recorded in the agent's lifecycle record. The record MUST include:

- The previous state
- The new state
- The timestamp of the transition
- The trigger (system event or human decision)
- The identity of the approving authority
- A free-text reason (MUST NOT be empty for transitions to DEGRADED or DECOMMISSIONED)

---

## 6. Capability Scope Changes

### 6.1 Scope Expansion

Any expansion of an agent's declared capability scope — even a minor addition — requires:

1. A new PROPOSED state entry for the updated agent specification
2. A full build-time council review (ANIF-903) of the expanded capabilities
3. A new signed manifest issued by the deployer
4. A new PROVISIONAL trust period (72 hours) following re-deployment

The 72-hour PROVISIONAL period is non-negotiable for scope expansions, regardless of the agent's prior operational history.

### 6.2 Scope Reduction

A reduction in capability scope does not require a new council review. The deployer MAY issue a new signed manifest with reduced capabilities without triggering a PROVISIONAL period.

### 6.3 Version Updates Without Scope Change

A software update that does not change the capability scope declared in the manifest does not require a new council review. The deployer SHOULD issue a new signed manifest with the updated version identifier. The updated agent resumes in ACTIVE state if the previous agent was ACTIVE.

---

## 7. Decommissioned Identity Register

The platform MUST maintain a register of all decommissioned agent identities. The register MUST be append-only. The register MUST contain:

- The decommissioned agent's UUID
- The decommissioned agent's role and tier
- The date and timestamp of decommissioning
- The reason for decommissioning
- The identity of the approving authority

When a new agent is proposed, the build-time council review MUST check the decommissioned identity register to ensure the proposed agent's identity does not conflict with a retired identity.

---

## 8. Conformance Requirements

Every deployed agent MUST have a current lifecycle state declared in the agent state registry.

No agent MUST transition directly from PROPOSED to ACTIVE. The PROVISIONAL period is mandatory.

The PROVISIONAL trust period MUST be a minimum of 72 hours. It MUST NOT be shortened by configuration or exception.

DECOMMISSIONED is a terminal state. No transition out of DECOMMISSIONED is permitted.

Every state transition MUST be logged with the fields defined in section 5.3.

---

## 9. Security Considerations

The decommissioned identity register prevents identity recycling — an attacker cannot re-register a decommissioned agent identity to gain its historical trust level. The PROVISIONAL period ensures that a compromised agent cannot operate unchecked from the moment of deployment; anomalous behaviour during PROVISIONAL will trigger human review before the agent is trusted as routine.

---

## 10. Operational Considerations

The AI Ethics Officer SHOULD review the state distribution of the agent pool on a regular basis — at a minimum monthly. A pool with a high proportion of DEGRADED agents indicates systemic problems that may require investigation beyond the individual progressive intervention model. A pool where no agent has ever been DEGRADED may indicate that governance thresholds are set too loosely.

---

## Appendix A: Change History

| Version | Date | Author | Changes |
|---|---|---|---|
| 0.1.0 | 2026-04-07 | ANIF Working Group | Initial draft |
