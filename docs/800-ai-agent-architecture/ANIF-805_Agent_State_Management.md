# ANIF-805: Agent State Management

| Field        | Value                                              |
|--------------|----------------------------------------------------|
| Doc ID       | ANIF-805                                           |
| Series       | AI Agent Architecture                              |
| Version      | 0.1.0                                              |
| Status       | Draft                                              |
| Authors      | ANIF Working Group                                 |
| Reviewers    | —                                                  |
| Approved by  | —                                                  |
| Created      | 2026-04-07                                         |
| Last updated | 2026-04-07                                         |
| Replaces     | N/A                                                |
| Related docs | ANIF-800, ANIF-803, ANIF-716, ANIF-724             |

---

## Abstract

This document defines what agent state is, what agents are permitted to persist, and how state is governed at runtime. Agents are stateless by design — they MUST NOT accumulate memory across intents. An agent's working context for any intent MUST be cleared when that intent completes. Persistent state is limited to agent identity, lifecycle state, and the strike counter. LLM agents MUST NOT retain conversation history across unrelated intents.

---

## 1. Introduction

### 1.1 Purpose

Stateful agents accumulate context. Accumulated context introduces two risks: an agent may act on stale or manipulated prior context, and an agent that retains cross-intent memory may develop emergent behaviours that were not present during build-time council review. The stateless-by-design principle in this document prevents both risks.

Stateless design does not mean agents cannot have memory within an intent — it means agents MUST NOT carry memory across intents that are not explicitly related.

### 1.2 Scope

This document covers:

- The stateless design principle and its rationale
- What agents MUST NOT persist across intents
- What agents MAY retain and for how long
- The agent state registry
- LLM-specific state constraints

### 1.3 Out of Scope

This document does not cover:

- The canonical state store (that is network state, not agent state)
- The ethics audit record (see ANIF-724)
- The strike counter store (see ANIF-716)
- Agent lifecycle states (see ANIF-803)

### 1.4 Intended Audience

- AI engineers implementing agent memory and context management
- Platform engineers designing the agent runtime environment
- Build-time council members reviewing agent state claims
- Security engineers auditing agent state retention

---

## 2. Normative References

- ANIF-700 — Ethics Framework Overview
- ANIF-703 — Bias and Fairness Principles
- ANIF-716 — Progressive Intervention Model
- ANIF-724 — Ethics Audit Trail Requirements
- ANIF-803 — Agent Lifecycle Management
- RFC 2119 — Key words for use in RFCs to indicate requirement levels

---

## 3. Terms and Definitions

**Intent scope:** The bounded context of a single intent from receipt to completion (or failure). Agent working state within an intent scope is transient.

**Cross-intent memory:** Any state that an agent retains from one intent and applies to a subsequent unrelated intent. Cross-intent memory is prohibited unless explicitly sanctioned by an intent chain relationship.

**Intent chain:** A declared relationship between intents where a subsequent intent is explicitly a continuation of a prior intent. Intent chains are declared at the pipeline level, not by the agent.

**Working context:** The set of data an agent holds in memory while processing a single intent. Working context MUST be cleared at intent completion.

**Persistent state:** State that survives agent restart, redeployment, or version update. Only identity, lifecycle state, and the strike counter are permitted as persistent state.

---

## 4. Stateless Design Principle

### 4.1 The Principle

Agents MUST be designed so that their behaviour for any given intent depends only on:

- The content of that intent
- The current canonical state (as retrieved within that intent's execution)
- The agent's signed manifest (capabilities and configuration)

An agent's behaviour MUST NOT depend on what intents it has previously processed, what recommendations it has previously made, or what operators it has previously interacted with.

### 4.2 Rationale

An agent that accumulates context may develop working patterns that diverge from the behaviour observed during build-time council review. The council reviewed the agent's behaviour given clean inputs. If the agent's behaviour drifts over time as it accumulates context, the council's review is no longer a valid representation of what the agent does.

Context accumulation also introduces a manipulation surface: if an agent retains cross-intent memory, an adversary can craft a sequence of seemingly benign intents that prime the agent's context for a later malicious intent.

### 4.3 Intent Chain Exception

Where an intent is explicitly a continuation of a prior intent — for example, a rollback intent that references the original change intent — the agent MAY retain relevant context from the prior intent within the declared intent chain. The intent chain relationship MUST be declared in the pipeline and MUST be traceable in the audit record. This exception does not permit the accumulation of general operational memory.

---

## 5. Prohibited State

The following MUST NOT be persisted by any agent beyond the completion of the intent in which they were generated:

- LLM conversation history or prior prompt-response pairs
- Operator identity from prior intents
- Prior risk scores or harm classifications
- Prior policy evaluation results
- Any derived model of an operator's preferences or patterns
- Any derived model of network behaviour patterns beyond what is present in current canonical state
- Intermediate reasoning steps from prior intents

An agent that retains any of the above across intent boundaries has an undeclared memory that was not reviewed by the build-time council. This is a Severity 2 ethics condition.

---

## 6. Permitted Persistent State

The following state MUST persist across agent restarts and redeployments:

| State element | Owner | Format |
|---|---|---|
| Agent UUID | Platform / identity service | Immutable after issuance |
| Signed manifest | Deployer | Replaced only by new council-reviewed manifest |
| Lifecycle state | Agent state registry | Managed by the orchestrator per ANIF-803 |
| Strike counter | Append-only strike store | Managed per ANIF-716 |

These four elements are the complete set of permitted persistent state. An agent that persists anything beyond this set MUST NOT be approved by the build-time council.

---

## 7. Working Context Lifecycle

### 7.1 Acquisition

Working context for an intent MUST be acquired fresh at the start of intent processing. An agent MUST NOT reuse working context from a prior intent.

### 7.2 Retention

Working context MUST be held only for the duration of intent processing. The agent MAY retain context across internal reasoning steps within a single intent.

### 7.3 Clearing

Working context MUST be cleared when the intent completes — regardless of whether the intent succeeded, failed, or was rolled back. Clearing MUST occur before the agent begins processing any subsequent intent.

### 7.4 Verification

The agent runtime MUST log the intent ID at working context creation and at working context clearing. If a subsequent intent begins before the prior intent's context has been confirmed cleared, the platform MUST block the new intent and log an anomaly.

---

## 8. LLM-Specific State Constraints

### 8.1 Conversation History

LLM agents MUST NOT retain conversation history across unrelated intents. Each intent MUST begin a new LLM context window with no prior turns.

### 8.2 In-Context Learning

In-context learning — including few-shot examples — is permitted within a single intent's LLM call. The examples MUST be sourced from the agent's static configuration or the current intent's data. Examples from prior intents MUST NOT be included.

### 8.3 Fine-Tuning State

Fine-tuning updates to an LLM component MUST be treated as a manifest change — they alter the agent's behaviour and require a new build-time council review before production deployment.

### 8.4 Context Window Flushing

At the completion of every intent, the LLM component's context window MUST be explicitly flushed. The runtime MUST confirm the flush before accepting the next intent.

---

## 9. Agent State Registry

The agent state registry is an orchestrator-managed record of the current state of all deployed agents. It MUST contain:

- Agent UUID
- Agent role (ANIF-801)
- Agent tier
- Current lifecycle state (ANIF-803)
- Current trust level
- Strike counter value
- Last intent processed (intent ID and timestamp)
- Current working context status (clear / active)

The agent state registry is read by Tier 0 coordination agents. It MUST NOT be writable by any agent. Only the orchestrator infrastructure MAY write to the agent state registry.

---

## 10. Conformance Requirements

Agents MUST be stateless across intents. Working context MUST be cleared at intent completion.

LLM agents MUST NOT retain conversation history across unrelated intents.

The agent runtime MUST confirm working context clearing before accepting a subsequent intent.

Fine-tuning changes to LLM components MUST trigger a new build-time council review.

---

## 11. Security Considerations

Stateless agents are harder to manipulate through context poisoning. An adversary who successfully primes an agent's context in one intent cannot rely on that priming persisting to a future intent. Context clearing is a security control as much as a governance one. LLM context flushing eliminates the jailbreak persistence pattern — where a successful jailbreak in one session is exploited in subsequent sessions.

---

## 12. Operational Considerations

Organisations SHOULD verify working context clearing as part of build-time council review by running test sequences designed to detect context leakage between intents. A test sequence that produces different results for an identical second intent than for the first identical intent — in an agent that should be stateless — indicates context leakage.

---

## Appendix A: Change History

| Version | Date | Author | Changes |
|---|---|---|---|
| 0.1.0 | 2026-04-07 | ANIF Working Group | Initial draft |
