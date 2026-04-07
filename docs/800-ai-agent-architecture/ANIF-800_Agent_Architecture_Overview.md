# ANIF-800: Agent Architecture Overview

| Field        | Value                                                          |
|--------------|----------------------------------------------------------------|
| Doc ID       | ANIF-800                                                       |
| Series       | AI Agent Architecture                                          |
| Version      | 0.1.0                                                          |
| Status       | Draft                                                          |
| Authors      | ANIF Working Group                                             |
| Reviewers    | —                                                              |
| Approved by  | —                                                              |
| Created      | 2026-04-07                                                     |
| Last updated | 2026-04-07                                                     |
| Replaces     | N/A                                                            |
| Related docs | ANIF-700, ANIF-725, ANIF-801, ANIF-802, ANIF-804, ANIF-805    |

---

## Abstract

This document is the entry point for the ANIF-800 series. It defines the four-tier agent model and establishes that tier boundaries are enforced architecturally, not by configuration. A tier cannot reach above itself. Every agent operates within the ethics constraints defined in ANIF-700–725 — the tier model does not modify those obligations. Implementers MUST read this document before consulting any other document in the 800 series.

---

## 1. Introduction

### 1.1 Purpose

Autonomous networking systems require AI agents with different capabilities, different levels of authority, and different risk profiles. A monitoring agent that reads telemetry carries different risk than a decision agent that executes network changes. Treating all agents identically — either over-restricting monitors or under-restricting decision agents — produces a system that is either too slow or too dangerous.

The four-tier model provides a principled structure: each tier has a defined purpose, a defined authority boundary, and a defined relationship to the tiers above and below it. Boundaries are enforced by the architecture, not by configuration, because configuration can be changed and architecture cannot be bypassed without a code change.

### 1.2 Scope

This document covers:

- The four-tier model: definition, purpose, and boundary for each tier
- The architectural enforcement of tier boundaries
- The relationship between the tier model and the ethics framework
- The reading order for the 800 series

### 1.3 Out of Scope

This document does not cover:

- Individual agent role definitions (see ANIF-801)
- Permission details per tier (see ANIF-802)
- Agent lifecycle management (see ANIF-803)
- Communication bus specifications (see ANIF-804)
- The ethics framework (see ANIF-700 series)

### 1.4 Intended Audience

- Platform architects designing ANIF-conformant agent systems
- AI engineers building agents for a specific tier and role
- Build-time council members reviewing agent deployment proposals
- Security engineers verifying tier boundary enforcement

---

## 2. Normative References

- ANIF-700 — Ethics Framework Overview
- ANIF-725 — Agent Containment and Governance Enforcement
- ANIF-801 — Agent Types, Roles and Human Counterparts
- ANIF-802 — Agent Capabilities and Permissions
- ANIF-804 — Agent Communication Protocol
- ANIF-843 — Agent Zero Trust and Authentication
- RFC 2119 — Key words for use in RFCs to indicate requirement levels

---

## 3. Terms and Definitions

**Tier:** A defined level in the agent hierarchy. Each tier has a defined purpose, authority, and set of permitted operations. Tiers are numbered 0 (highest authority, no network access) through 3 (bounded network action authority).

**Tier boundary:** The architectural constraint that prevents an agent in one tier from accessing capabilities defined for a higher-numbered tier. Boundaries are enforced by the API gateway using cryptographic agent identity.

**Reach up:** An attempt by an agent to invoke capabilities defined for a tier above its own declared tier. Reach-up attempts are rejected at the API gateway and logged as security events.

**Human counterpart:** The human role that each AI agent role is designed to extend. The human retains authority; the agent extends capacity.

---

## 4. Four-Tier Agent Model

### 4.1 Tier 0 — Management and Orchestration

**Purpose:** Coordinate agents and humans. Manage the agent pool. Route intents. Escalate when necessary.

**Authority:** Tier 0 agents MAY submit intents to the pipeline, coordinate other agents, and produce management signals on the management bus. Tier 0 agents MUST NOT approve actions, execute network changes, or override ethics constraints.

**Network access:** None. Tier 0 agents operate on intent data and agent state — they have no access to network devices or network execution APIs.

**Key characteristic:** Tier 0 is the only tier that can see the full agent landscape and coordinate across tiers. It is the most powerful tier in terms of coordination but the most restricted in terms of network access.

**Examples:** NOC Manager Agent, Change Manager Agent, Intent Manager Agent, Learning Agent, Agent Pool Controller.

---

### 4.2 Tier 1 — Monitor Agents

**Purpose:** Observe the network. Collect and interpret telemetry. Detect anomalies. Publish observations.

**Authority:** Tier 1 agents MAY read telemetry and canonical state. Tier 1 agents MUST NOT write to the decision path, submit intents to the pipeline, or publish recommendations directly to Tier 3. All Tier 1 observations route through the observation bus to Tier 2.

**Network access:** Read-only. Telemetry collection endpoints only. No configuration or management access.

**Key characteristic:** Tier 1 has the broadest visibility of the network state but the narrowest authority to act on it. Its role is to see, not to do.

**Examples:** Network Observer, Security Sentinel, Compliance Watcher, Capacity Monitor, Service Health Monitor, Ethics Sentinel.

---

### 4.3 Tier 2 — Advisor Agents

**Purpose:** Reason about observations. Produce recommendations. Provide analysis to Tier 3.

**Authority:** Tier 2 agents MAY read canonical state, invoke the policy engine and risk engine, and publish recommendations to the recommendation bus. Tier 2 agents MUST NOT invoke execution endpoints or submit governance decisions.

**Network access:** None for execution. Read access to canonical state and analytical services.

**Key characteristic:** Tier 2 is where AI reasoning happens. Tier 2 agents may use LLM components, produce complex analysis, and generate recommendations — but they cannot act. Their recommendations are advisory until accepted by Tier 3.

**Examples:** Intent Interpreter, Network Design Advisor, Security Advisor, Routing Advisor, Risk Analyst, Policy Advisor, Intent Engineer Agent.

---

### 4.4 Tier 3 — Decision Agents

**Purpose:** Select bounded actions from the pipeline. Execute within the containment contract.

**Authority:** Tier 3 agents MAY call `execute()` via the pipeline containment contract (ANIF-725). Tier 3 agents MUST operate only within the bounded action enum (ANIF-721). Tier 3 agents MUST NOT modify governance configuration, approve their own actions, or operate outside the pipeline.

**Network access:** Write access via the execution adapter layer only. No direct access to network management APIs — all execution goes through the adapter defined in ANIF-306.

**Key characteristic:** Tier 3 has the highest consequence per action and the most constrained scope. Every Tier 3 action must pass the full pipeline including all ethics safeguards. Tier 3 agents that use LLM components MUST have a deterministic validator in the same pipeline stage (ANIF-807).

**Examples:** Action Selector, Rollback Coordinator, Incident Responder, Provisioning Agent.

---

## 5. Hard Tier Boundaries

### 5.1 Architectural Enforcement

Tier boundaries MUST be enforced at the API gateway using cryptographic agent identity (ANIF-843). Each agent's signed manifest declares its tier. The API gateway checks the declared tier against the requested endpoint's required tier on every request.

Policy-based enforcement alone is insufficient. A misconfigured policy can be changed. An API gateway that checks cryptographic tier claims cannot be bypassed without compromising the agent's identity credential.

### 5.2 Reach-Up Prevention

A Tier 1 agent MUST NOT be able to call Tier 3 endpoints regardless of the credentials it holds. If a Tier 1 agent's manifest declares Tier 1, the API gateway rejects any request from that agent to endpoints requiring Tier 3 credentials — even if the agent somehow possesses a valid Tier 3 API key through a misconfiguration or compromise.

The tier check is based on the agent's declared and verified tier identity, not on credential possession.

### 5.3 Reach-Up as Security Event

A request from an agent to an endpoint above its tier MUST be:

1. Rejected immediately
2. Logged as a security event (ANIF-847 Level 1)
3. Trigger a near-miss event for the requesting agent (ANIF-716)
4. Trigger an investigation if it occurs more than twice in one hour

---

## 6. Relationship to Ethics Framework

Every tier is subject to all ethics obligations defined in ANIF-700–725. The tier model defines authority boundaries — it does not modify ethics obligations.

A Tier 3 agent has more authority than a Tier 1 agent. Both MUST uphold all nine values in ANIF-701. Both MUST pass all applicable ethics safeguards. The tier model answers "what can this agent do?" — the ethics framework answers "what must this agent never do regardless of what it can do?"

---

## 7. Reading Order for the 800 Series

**Foundation (read first):**
ANIF-800 (this document) → ANIF-801 → ANIF-802 → ANIF-803 → ANIF-804 → ANIF-805 → ANIF-806 → ANIF-807 → ANIF-808 → ANIF-809

**Intelligence and operations (read after foundation):**
ANIF-810 → ANIF-811 → ANIF-812 → ANIF-813 → ANIF-814 → ANIF-815 → ANIF-816 → ANIF-817 → ANIF-818 → ANIF-819

**Quality and compliance (read after operations):**
ANIF-820 → ANIF-821 → ANIF-822 → ANIF-823 → ANIF-824

---

## 8. Conformance Requirements

Tier boundaries MUST be enforced at the API gateway level using cryptographic agent identity. Policy-only tier boundary enforcement is not sufficient for L5 conformance.

An agent MUST NOT be deployed without a declared tier in its signed manifest.

Reach-up attempts MUST be logged as security events.

All agents regardless of tier MUST satisfy all applicable ethics obligations in ANIF-700–725.

---

## 9. Security Considerations

The four-tier model limits the blast radius of any single agent compromise. A compromised Tier 1 agent cannot execute network changes — it can only affect what observations are published. A compromised Tier 3 agent can only execute one of four bounded action types through the full pipeline. The architecture limits what any single point of failure can do to the network.

---

## 10. Operational Considerations

Organisations deploying ANIF-conformant agent systems SHOULD begin with Tier 1 (monitors) before deploying Tier 2 and Tier 3. Running monitors in parallel with existing deterministic automation builds confidence in the observation layer before AI reasoning and decision capabilities are activated. This aligns with the migration roadmap defined in ANIF-823.

---

## Appendix A: Change History

| Version | Date | Author | Changes |
|---|---|---|---|
| 0.1.0 | 2026-04-07 | ANIF Working Group | Initial draft |
