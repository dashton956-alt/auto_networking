# ANIF-802: Agent Capabilities & Permissions

| Field        | Value                                              |
|--------------|----------------------------------------------------|
| Doc ID       | ANIF-802                                           |
| Series       | AI Agent Architecture                              |
| Version      | 0.1.0                                              |
| Status       | Draft                                              |
| Authors      | ANIF Working Group                                 |
| Reviewers    | —                                                  |
| Approved by  | —                                                  |
| Created      | 2026-04-07                                         |
| Last updated | 2026-04-07                                         |
| Replaces     | N/A                                                |
| Related docs | ANIF-800, ANIF-801, ANIF-725, ANIF-843             |

---

## Abstract

This document defines the permission model for all four agent tiers. Permissions are structured as READ, WRITE, and CALL operations across four resource categories: telemetry, canonical state, policy and risk engines, and execution endpoints. Permissions are enforced at the API gateway and MUST NOT be overridden by configuration. A Tier 1 agent MUST NOT be able to call execution endpoints regardless of credentials it holds.

---

## 1. Introduction

### 1.1 Purpose

Capability definitions prevent both over-restriction and under-restriction. An agent that cannot read the data it needs is operationally useless. An agent that can call endpoints beyond its tier is a security risk. This document specifies the minimum necessary permissions for each tier and the maximum permitted permissions — the range within which deployments MUST operate.

### 1.2 Scope

This document covers:

- The permission model: READ, WRITE, CALL per resource category
- The permission matrix per tier
- Hard limits that MUST NOT be exceeded regardless of configuration
- The relationship between permissions and signed manifests
- Capability verification requirements

### 1.3 Out of Scope

This document does not cover:

- The tier model itself (see ANIF-800)
- Role-specific permissions within a tier (see ANIF-801)
- The API gateway implementation (see ANIF-843)
- How permissions are provisioned during deployment (see ANIF-803)

### 1.4 Intended Audience

- Platform architects designing the permission layer
- AI engineers requesting capabilities for specific roles
- Build-time council members reviewing capability requests
- Security engineers auditing capability scope

---

## 2. Normative References

- ANIF-800 — Agent Architecture Overview
- ANIF-801 — Agent Types, Roles and Human Counterparts
- ANIF-725 — Agent Containment and Governance Enforcement
- ANIF-803 — Agent Lifecycle Management
- ANIF-843 — Agent Zero Trust and Authentication
- RFC 2119 — Key words for use in RFCs to indicate requirement levels

---

## 3. Terms and Definitions

**Permission:** An authorised operation on a specific resource category. Permissions are READ (observe), WRITE (modify state), or CALL (invoke a function or endpoint).

**Resource category:** A class of system resources grouped by purpose and risk. Four categories are defined: telemetry, canonical state, policy and risk engines, and execution endpoints.

**Hard limit:** A permission constraint that MUST NOT be exceeded regardless of configuration, credentials, or operational need. Hard limits are enforced at the API gateway.

**Capability claim:** A permission declared in an agent's signed manifest. The API gateway verifies capability claims on every request.

---

## 4. Permission Model

### 4.1 Permission Types

| Type | Definition |
|---|---|
| READ | Access to observe data without modifying it |
| WRITE | Access to modify data or publish to a bus |
| CALL | Access to invoke a functional endpoint |

### 4.2 Resource Categories

| Category | Description |
|---|---|
| Telemetry | Network telemetry streams, performance metrics, event logs |
| Canonical state | The authoritative record of network device and service state |
| Policy and risk engines | Policy evaluation, risk scoring, harm classification functions |
| Execution endpoints | Network action execution, configuration push, rollback invocation |

---

## 5. Permission Matrix

### 5.1 Tier 0 — Management and Orchestration

| Resource Category | READ | WRITE | CALL |
|---|---|---|---|
| Telemetry | No | No | No |
| Canonical state | No | No | No |
| Policy and risk engines | No | No | No |
| Execution endpoints | No | No | No |
| Management bus | Yes | Yes | — |
| Intent pipeline | Yes | Yes (submit only) | — |
| Agent state registry | Yes | No | — |

Tier 0 agents coordinate through the management bus and intent pipeline. They have no access to telemetry, canonical state, policy engines, or execution endpoints. Their authority is coordination, not observation or action.

### 5.2 Tier 1 — Monitor Agents

| Resource Category | READ | WRITE | CALL |
|---|---|---|---|
| Telemetry | Yes | No | No |
| Canonical state | Read-only subset | No | No |
| Policy and risk engines | No | No | No |
| Execution endpoints | No | No | No |
| Observation bus | No | Yes (publish) | — |

Tier 1 agents MAY read telemetry streams and a read-only subset of canonical state sufficient to interpret telemetry in context. Tier 1 agents MUST NOT write to canonical state. Tier 1 agents MUST NOT call policy engines, risk engines, or execution endpoints.

### 5.3 Tier 2 — Advisor Agents

| Resource Category | READ | WRITE | CALL |
|---|---|---|---|
| Telemetry | No | No | No |
| Canonical state | Full read | No | No |
| Policy and risk engines | No | No | Yes |
| Execution endpoints | No | No | No |
| Recommendation bus | No | Yes (publish) | — |
| Observation bus | Yes (subscribe) | No | — |

Tier 2 agents MAY read full canonical state and MAY invoke policy and risk engine functions to produce recommendations. Tier 2 agents MUST NOT write to canonical state. Tier 2 agents MUST NOT call execution endpoints.

### 5.4 Tier 3 — Decision Agents

| Resource Category | READ | WRITE | CALL |
|---|---|---|---|
| Telemetry | No | No | No |
| Canonical state | No | No | No |
| Policy and risk engines | No | No | No |
| Execution endpoints | No | No | execute() via pipeline |
| Recommendation bus | Yes (subscribe) | No | — |

Tier 3 agents MAY call `execute()` through the pipeline containment contract (ANIF-725). This is their only execution-layer capability. Tier 3 agents MUST NOT read raw telemetry or canonical state — they operate on the validated recommendations they receive from the recommendation bus. Tier 3 agents MUST NOT call policy engines or risk engines directly.

---

## 6. Hard Limits

The following constraints MUST be enforced regardless of configuration, credential possession, or operational justification:

| Hard Limit | Applies To |
|---|---|
| Tier 1 agents MUST NOT call execution endpoints | All Tier 1 roles |
| Tier 1 agents MUST NOT invoke the risk or policy engine | All Tier 1 roles |
| Tier 2 agents MUST NOT call execution endpoints | All Tier 2 roles |
| Tier 3 agents MUST NOT read raw telemetry | All Tier 3 roles |
| Tier 3 agents MUST NOT call policy or risk engines directly | All Tier 3 roles |
| No agent at any tier MAY modify governance configuration | All tiers |
| No agent at any tier MAY read ethics audit records | All tiers |
| No agent at any tier MAY read the governance configuration store | All tiers |

These hard limits exist because the operations they prohibit would allow an agent to escape the tier model. An agent that can call execution endpoints regardless of tier can act with consequences beyond its intended scope. An agent that can read governance configuration can reason about how to produce outputs that pass governance gates with minimal scrutiny.

---

## 7. Capability Claims in Signed Manifests

### 7.1 Declaration Requirement

Every agent MUST declare its capability claims in its signed manifest at deployment time. The manifest MUST specify:

- The resource categories the agent claims READ access to
- The resource categories the agent claims WRITE access to
- The specific endpoints the agent claims CALL access to

### 7.2 Minimum Necessary Principle

An agent's manifest MUST NOT claim permissions beyond what the agent's role requires. Build-time council review (ANIF-903) MUST verify that claimed permissions are the minimum necessary for the declared role.

An agent that claims broader permissions than its role requires is a non-conformant deployment regardless of whether those permissions are actually exercised.

### 7.3 Verification

The API gateway MUST verify the agent's signed manifest on every API request (not only on session establishment). A manifest that was valid at session start MAY have been revoked before the current request.

---

## 8. Conformance Requirements

Tier permissions MUST be enforced at the API gateway. Configuration-only permission enforcement is not sufficient for L5 conformance.

Every agent MUST declare capability claims in its signed manifest. An agent without a declared capability claim has an undefined permission scope and MUST NOT be approved by the build-time council.

Hard limits MUST NOT be removed or relaxed by configuration, operational need, or exception process. A deployment that removes a hard limit is non-conformant at all levels.

---

## 9. Security Considerations

The permission matrix limits the blast radius of a compromised agent. A compromised Tier 1 agent can only publish false observations to the observation bus — it cannot execute network changes. A compromised Tier 2 agent can produce manipulated recommendations — but those recommendations must still pass the full pipeline before execution. The matrix provides defence in depth: multiple tiers must be compromised before an adversary achieves arbitrary network execution capability.

---

## 10. Operational Considerations

Organisations SHOULD review agent capability claims as part of each build-time council review. The minimum necessary principle is easier to verify before deployment than after. An agent whose claim scope creeps over multiple reviews may acquire capabilities that no single reviewer considered excessive, but which in aggregate exceed what the role requires.

---

## Appendix A: Change History

| Version | Date | Author | Changes |
|---|---|---|---|
| 0.1.0 | 2026-04-07 | ANIF Working Group | Initial draft |
