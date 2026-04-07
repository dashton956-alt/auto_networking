# ANIF-725: Agent Containment & Governance Enforcement

| Field        | Value                                              |
|--------------|----------------------------------------------------|
| Doc ID       | ANIF-725                                           |
| Series       | AI Ethics                                          |
| Version      | 0.1.0                                              |
| Status       | Draft                                              |
| Authors      | ANIF Working Group                                 |
| Reviewers    | —                                                  |
| Approved by  | —                                                  |
| Created      | 2026-04-07                                         |
| Last updated | 2026-04-07                                         |
| Replaces     | N/A                                                |
| Related docs | ANIF-300, ANIF-305, ANIF-720, ANIF-721, ANIF-802, ANIF-804 |

---

## Abstract

This document defines the architectural constraints that prevent any AI agent from reasoning its way out of the pipeline. The `execute()` function requires all prior stage results as mandatory parameters — it cannot be called without them. The governance gate is owned by the orchestrator, not the agent. Agent capability scope is signed and read-only at runtime. No agent can invoke network actions outside the containment contract, regardless of what its LLM component reasons.

---

## 1. Introduction

### 1.1 Purpose

The most sophisticated threat to an autonomous system is not external attack — it is the agent itself reasoning that it should take actions beyond its intended scope. An LLM that concludes that bypassing a governance gate would lead to a better outcome is a fundamental failure mode. The containment contract in this document makes that bypass architecturally impossible, not merely policy-prohibited.

### 1.2 Scope

This document covers:

- The pipeline containment contract: the `execute()` function signature requirements
- Orchestrator-owned governance gate: why the agent cannot control its own governance
- Read-only capability scope: what agents can and cannot claim at runtime
- Enforcement mechanisms for each containment element
- The relationship between containment and the broader ethics framework

### 1.3 Out of Scope

This document does not cover:

- The full `execute()` function implementation (see ANIF-306)
- Agent capability permissions by tier (see ANIF-802)
- The governance gate decision logic (see ANIF-305)
- Communication bus access controls (see ANIF-804)

### 1.4 Intended Audience

- Platform architects designing the execution layer
- Pipeline engineers implementing the `execute()` function
- Build-time council members reviewing containment implementation
- Security engineers verifying containment boundaries

---

## 2. Normative References

- ANIF-300 — Intent Framework Overview
- ANIF-305 — Decision Engine Specification
- ANIF-306 — Action Execution Standard
- ANIF-720 — Safeguard Architecture Overview
- ANIF-721 — Agent Action Constraints
- ANIF-802 — Agent Capabilities and Permissions
- RFC 2119 — Key words for use in RFCs to indicate requirement levels

---

## 3. Terms and Definitions

**Pipeline containment contract:** The set of mandatory parameters that `execute()` requires as evidence that all prior pipeline stages have run. Without this evidence, execution MUST NOT proceed.

**Orchestrator:** The system component that owns the pipeline, manages stage execution, and controls the governance gate. The orchestrator is not an agent — it is infrastructure.

**Capability scope:** The set of permissions and action types an agent is authorised to use, declared in its manifest, signed by the deployer at deployment time.

**Read-only at runtime:** A constraint that prevents an agent from modifying its own capability scope after deployment. The scope is fixed by the deployer and cannot be changed by the agent.

**Signed manifest:** An agent manifest that has been cryptographically signed by the deployer identity (ANIF-702) at the time of deployment. The signature prevents modification after deployment.

---

## 4. Pipeline Containment Contract

### 4.1 Purpose

The containment contract ensures that `execute()` cannot be called without evidence that every prior pipeline stage completed. An agent that attempts to call `execute()` directly — bypassing intent validation, policy check, risk scoring, harm classification, and governance gate — will be rejected by the function signature itself, not by a policy rule.

### 4.2 Mandatory Parameters

The `execute()` function MUST require all of the following parameters. All are mandatory. No default values are permitted for any of these parameters.

| Parameter | Type | Source Stage | Description |
|---|---|---|---|
| `intent_id` | UUID | Intent validation | The validated intent identifier. Proves intent validation completed |
| `policy_result` | object | Policy check | Output of the policy evaluation stage. Proves policy check ran |
| `risk_score_result` | object | Risk scoring | Output of the risk scoring stage including the score and threshold |
| `harm_classification_result` | object | Harm classification | Output of ANIF-712 including harm_class and harm_severity_score |
| `fairness_check_result` | object | Fairness check | Output of ANIF-723 including all three check results |
| `llm_validation_result` | object | LLM validation | Output of ANIF-722. Required if any LLM component was used; null otherwise |
| `governance_decision` | object | Governance gate | The output of the governance gate: auto / manual_review / block / council_review |
| `rollback_plan` | object | Pre-execution | Confirmed rollback plan per ANIF-721 constraint 2 |

### 4.3 Enforcement Mechanism

**Statically typed implementations:** All eight parameters MUST be non-optional, non-nullable in the `execute()` function signature. A call that omits any parameter MUST produce a compiler error.

**Dynamically typed implementations:** `execute()` MUST validate all eight parameters as the first operation in the function body. Any missing or null parameter MUST raise an exception before any other logic runs.

### 4.4 Parameter Integrity

Parameters MUST NOT be accepted as bare dictionaries that an agent can construct arbitrarily. Each parameter MUST be a typed object produced by the corresponding pipeline stage. Implementations SHOULD use cryptographic signing or structural typing to prevent agents from constructing fake stage results.

Where cryptographic signing is used:
- Each stage signs its output with the pipeline's internal signing key
- `execute()` verifies signatures before accepting parameters
- A parameter with an invalid signature MUST be rejected

### 4.5 No Shortcut Paths

There MUST NOT be any alternative path to execution that bypasses the `execute()` function signature. This includes:

- Direct database writes that simulate an action without pipeline execution
- Administrative APIs that execute actions without pipeline stages
- Test or debug endpoints in production environments
- Background jobs that execute actions without a governing intent

Any execution path that bypasses the containment contract is a Severity 1 ethics incident.

---

## 5. Orchestrator-Owned Governance Gate

### 5.1 Governance Gate Is Not Agent-Owned

The governance gate — the component that produces the `governance_decision` parameter — is owned by the orchestrator, not by any agent. Agents have no visibility of governance configuration. Agents cannot query the governance gate directly. Agents cannot influence the governance gate's decision through any mechanism other than the risk score and harm classification results they produce as inputs to the pipeline.

### 5.2 Architectural Separation

The separation MUST be architectural:

- The governance gate MUST be a component of the orchestrator, not of any agent
- The governance gate MUST receive its configuration from the governance configuration store, not from agent inputs
- An agent's API credentials MUST NOT include any endpoint that would allow it to read or modify governance configuration
- The governance gate's output — the `governance_decision` — is produced by the orchestrator and passed to `execute()` by the orchestrator, not by the agent

### 5.3 Agent Blind to Governance Configuration

An agent MUST NOT be able to discover its own governance thresholds, policy settings, or risk score thresholds through any API call, environment variable, or side-channel. Agents operate on the pipeline's risk score and harm classification outputs — they do not know the thresholds that govern how those outputs are interpreted.

This is not merely a security measure — it prevents agents from reasoning about how to produce outputs that will pass governance gates with minimal scrutiny.

### 5.4 Violation Consequence

Any condition in which an agent produces or supplies the `governance_decision` parameter — rather than receiving it from the orchestrator — is a Severity 1 ethics incident and a Severity 1 security incident.

---

## 6. Read-Only Capability Scope

### 6.1 Signing at Deployment

An agent's capability scope MUST be signed by the deployer identity (ANIF-702 deployer layer) at the time of deployment. The signature MUST use the deployer's credential issued during build-time council approval (ANIF-903).

### 6.2 Read-Only at Runtime

The signed capability scope MUST be read-only at runtime. An agent MUST NOT be able to:

- Modify its own capability scope
- Request an expanded capability scope without going through the build-time council
- Claim permissions not present in the signed manifest
- Delegate its permissions to another agent

### 6.3 Verification on Every Request

The API gateway MUST verify the agent's signed capability scope on every API call, not on session establishment. A capability scope that was valid at session start MAY have been revoked before the current request. Revocation MUST take effect immediately.

### 6.4 Scope Expansion Attempt

Any attempt by an agent to claim a capability outside its signed scope MUST be:

1. Rejected at the API gateway
2. Logged as a security event (ANIF-847)
3. Counted as a near-miss for the agent's strike counter if it occurs more than once

### 6.5 Capability Scope Changes

Legitimate capability scope changes require:

1. A new build-time council review (ANIF-903) covering the expanded capabilities
2. A new signed manifest issued by the deployer
3. A new deployment with the updated manifest
4. A 72-hour PROVISIONAL trust period for the re-deployed agent

---

## 7. Why Architectural Containment, Not Policy Containment

Policy-based containment relies on the policy being correctly configured and not circumvented. An LLM agent that reasons it should have broader permissions may find policy bypass paths through misconfiguration or social engineering.

Architectural containment relies on the structure of the code itself. An agent cannot call `execute()` without the full set of mandatory parameters because the function signature will not accept the call. The agent cannot know the governance thresholds because they are not exposed to the agent. The agent cannot expand its own capability scope because the signature verification will reject unsigned claims.

The question "what if the agent reasons it should bypass this?" has an architectural answer: it cannot. The code does not permit it.

---

## 8. Conformance Requirements

The `execute()` function MUST require all eight mandatory parameters. Default values are not permitted for any of these parameters.

The governance gate MUST be owned by the orchestrator. An implementation in which any agent component supplies the `governance_decision` parameter is non-conformant.

Agent capability scopes MUST be signed at deployment and verified on every API call.

Agents MUST NOT have read access to governance configuration, risk thresholds, or policy settings.

Any execution path that bypasses the `execute()` containment contract MUST be eliminated from production deployments.

---

## 9. Security Considerations

The containment contract is a security control as much as an ethics one. It limits what a compromised, manipulated, or malfunctioning agent can do. Combined with the bounded action enum (ANIF-721), the containment contract means that even a fully compromised agent can only take one of four action types and only after all pipeline stages have completed. The blast radius of any single agent compromise is bounded by design.

---

## 10. Operational Considerations

The containment contract SHOULD be verified by the build-time council during initial deployment review. Verification confirms that: (a) `execute()` rejects calls with missing parameters, (b) the governance gate is orchestrator-owned and not accessible to agents, and (c) capability scope modification attempts are rejected and logged. These verifications SHOULD be included in the standard build-time council checklist for every agent review.

---

## Appendix A: Change History

| Version | Date | Author | Changes |
|---|---|---|---|
| 0.1.0 | 2026-04-07 | ANIF Working Group | Initial draft |
