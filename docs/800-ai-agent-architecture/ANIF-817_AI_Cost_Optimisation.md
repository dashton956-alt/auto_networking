# ANIF-817: AI Cost Optimisation and Governance

| Field        | Value                                              |
|--------------|----------------------------------------------------|
| Doc ID       | ANIF-817                                           |
| Series       | AI Agent Architecture                              |
| Version      | 0.1.0                                              |
| Status       | Draft                                              |
| Authors      | ANIF Working Group                                 |
| Reviewers    | —                                                  |
| Approved by  | —                                                  |
| Created      | 2026-04-08                                         |
| Last updated | 2026-04-08                                         |
| Replaces     | N/A                                                |
| Related docs | ANIF-807, ANIF-816, ANIF-834, ANIF-401             |

---

## Abstract

This document defines the normative requirements for governing the cost of AI operations in an ANIF-conformant implementation. The foundational principle is deterministic-first: LLM invocation occurs only where deterministic reasoning is genuinely insufficient. Seven cost controls MUST be implemented: response caching, deterministic-first checking, token budgets per intent, request batching, model tier selection, cost circuit breaking, and idle agent suspension. All cost data MUST flow to the observability layer and governance reporting. LLM inference is an operational cost that MUST be governed with the same rigour as any other infrastructure resource.

---

## 1. Introduction

### 1.1 Purpose

LLM API costs are variable, can scale rapidly with intent volume, and are difficult to attribute to specific operational outcomes if not tracked proactively. This document establishes the governance model for AI operational cost — ensuring that LLM invocations are justified, bounded, monitored, and reported.

### 1.2 Scope

This document covers:

- The deterministic-first principle and its application
- Seven cost control mechanisms and their requirements
- Model tier selection criteria
- Cost circuit breaker specification
- Cost data flow to observability and governance reporting

### 1.3 Out of Scope

This document does not cover:

- Context window management strategies (see ANIF-816)
- LLM agent manifest requirements (see ANIF-807)
- General observability metrics (see ANIF-401)
- AI governance reporting content (see ANIF-834)

### 1.4 Intended Audience

- Platform engineers implementing cost control mechanisms
- AI engineers selecting model tiers for agent roles
- Finance and governance officers reviewing AI cost reports
- Conformance assessors evaluating cost governance claims

---

## 2. Normative References

| Reference | Title |
|---|---|
| ANIF-401 | Observability Standard |
| ANIF-807 | LLM Agent Specification |
| ANIF-816 | Context Window Management |
| ANIF-834 | AI Governance Reporting |
| RFC 2119 | Key words for use in RFCs to Indicate Requirement Levels |

---

## 3. Terms and Definitions

| Term | Definition |
|---|---|
| Deterministic-first | The principle that every task is attempted by a deterministic component before an LLM is invoked |
| Model tier | A classification of LLM models by capability and cost: small, mid, and full |
| Cost circuit breaker | A control that halts LLM usage for a defined period when cumulative cost exceeds a declared budget threshold |
| Token budget | The maximum number of tokens an agent may consume processing a single intent |
| Idle agent suspension | The practice of suspending agents that have received no invocations within a defined idle window to eliminate standby cost |

---

## 4. The Deterministic-First Principle

### 4.1 Requirement

For every task assigned to an LLM agent, a deterministic component MUST first attempt the task. The LLM is invoked only when:

- The deterministic component returns a confidence score below the declared `confidence_threshold` for the task, or
- The deterministic component explicitly declares that the task requires reasoning beyond its rule set

This is not merely a cost optimisation — it is a correctness and governance requirement. Deterministic outputs are reproducible and auditable. LLM outputs are probabilistic. The deterministic-first principle ensures that probabilistic inference is applied only where it is genuinely necessary.

### 4.2 Pass-Through Condition

When the deterministic component returns a confidence score at or above the declared `confidence_threshold`, its output MUST be used directly without invoking the LLM. The decision to bypass LLM invocation MUST be logged as `deterministic_resolved: true` in the intent processing record.

---

## 5. Cost Control 1 — Response Caching

### 5.1 Requirement

Responses to structurally identical queries MUST be cached and served from cache rather than re-invoking the LLM.

### 5.2 Cache Key

The cache key MUST be computed from: the hash of the input prompt (post-compression and sanitisation) and the `llm_model_id`. Two invocations with the same hash and model MUST receive the same cached response.

### 5.3 Cache TTL

Cache entries MUST expire after the `cache_ttl_seconds` declared in the agent manifest. The default is 300 seconds (5 minutes) if not declared. Serving a cache entry beyond its TTL is a conformance violation.

### 5.4 Cache Invalidation

Cache entries MUST be invalidated when the canonical state data underlying the query changes. A response that was correct when cached may be incorrect if network state has changed.

---

## 6. Cost Control 2 — Deterministic-First Checking

The deterministic-first check (section 4) MUST be logged per invocation as part of the cost audit record. The log MUST record:

- Whether the deterministic component resolved the task (`deterministic_resolved: true/false`)
- The deterministic confidence score
- If LLM was invoked, the reason it was required

---

## 7. Cost Control 3 — Token Budget Per Intent

### 7.1 Requirement

Every intent MUST declare a `token_budget` in its manifest specifying the maximum tokens that may be consumed across all LLM invocations during its processing. If an intent does not declare a token budget, the system-wide default of 20,000 tokens applies.

### 7.2 Budget Tracking

The platform MUST track cumulative token consumption per intent across all pipeline stages. When cumulative consumption reaches 90% of the declared budget, the platform MUST emit a budget warning to the agent.

When cumulative consumption reaches 100% of the declared budget:

1. Further LLM invocations for this intent MUST be blocked.
2. The agent MUST apply its declared fallback behaviour.
3. A budget exhaustion event MUST be logged.

---

## 8. Cost Control 4 — Request Batching

Where intent processing latency permits, LLM requests for multiple low-priority intents SHOULD be batched into a single API call. Batching MUST NOT be applied where it would cause any intent to breach its declared TTL.

Batching is permitted only within the same agent role and model tier. Intents at different risk levels MUST NOT be batched together if the batch would mix intents requiring manual approval with intents eligible for auto-approval.

---

## 9. Cost Control 5 — Model Tier Selection

### 9.1 Three Tiers

| Tier | Description | Use Cases |
|---|---|---|
| Small | Lowest cost, limited reasoning depth | Intent classification, anomaly flagging, simple Q&A |
| Mid | Balanced cost and capability | Policy evaluation, risk summarisation, report drafting |
| Full | Highest capability, highest cost | Complex multi-domain analysis, council deliberation support, novel failure mode diagnosis |

### 9.2 Selection Requirement

Each agent MUST declare its model tier in the agent manifest. Model tier selection MUST be justified against the agent's task requirements. Agents using the Full tier for tasks achievable by the Small or Mid tier MUST be flagged in the monthly cost governance report (ANIF-834).

### 9.3 Dynamic Downgrade

For intents classified as low priority (priority level 1 or 2 out of 5), agents MAY dynamically downgrade to the Small tier if the intent content is within the Small tier's declared capability envelope. Dynamic downgrade MUST be logged.

---

## 10. Cost Control 6 — Cost Circuit Breaker

### 10.1 Requirement

Every deployment MUST configure a cost circuit breaker with a declared budget threshold per time window.

### 10.2 Trigger Condition

When cumulative LLM API cost within the declared time window exceeds the declared threshold, the circuit breaker MUST:

1. Halt all non-critical LLM invocations immediately.
2. Route affected intents to their declared fallback.
3. Notify the governance committee within 5 minutes with: current spend, threshold, time window, and the volume of intents affected.
4. Remain open (blocking LLM invocations) until a governance committee member explicitly resets it.

### 10.3 Critical Exemption

LLM invocations classified as supporting active P1 incident response MAY be exempted from circuit breaker blocking. The exemption MUST be logged with a justification.

### 10.4 Threshold Declaration

Budget thresholds MUST be declared in the deployment configuration, not in agent manifests. The governance committee is responsible for setting and reviewing thresholds.

---

## 11. Cost Control 7 — Idle Agent Suspension

### 11.1 Requirement

Agents that have received no invocations within their declared `idle_suspension_threshold_minutes` MUST be suspended. The default threshold is 30 minutes if not declared.

### 11.2 Suspension and Resumption

Suspension MUST release compute resources while preserving the agent's registered state. On receiving a new invocation, a suspended agent MUST resume within 5 seconds. Resumption latency MUST NOT cause intent TTL breaches.

### 11.3 Exemptions

The following agent roles are exempt from idle suspension:

- Intent Manager Agent (singleton, must be available for conflict resolution)
- Override-handling components (must be available with zero latency)

---

## 12. Cost Data and Reporting

### 12.1 Observability Integration

All LLM invocations MUST emit cost metrics to the observability layer (ANIF-401). Metrics MUST include: `agent_id`, `model_tier`, `tokens_consumed`, `estimated_cost`, `intent_id`, `timestamp`.

### 12.2 Governance Reporting

Monthly AI cost reports MUST be produced for the governance committee (ANIF-834). Reports MUST include:

- Total cost by model tier
- Cost by agent role
- Top 10 intents by token consumption
- Circuit breaker trigger events (if any)
- Agents flagged for inappropriate tier selection

---

## 13. Conformance Requirements

| ID | Requirement |
|---|---|
| CR-817-01 | The deterministic-first principle MUST be applied to every LLM agent invocation. |
| CR-817-02 | Deterministic-first bypass MUST be logged as `deterministic_resolved: true/false` per invocation. |
| CR-817-03 | Response cache entries MUST not be served beyond their declared TTL. |
| CR-817-04 | Every intent MUST have a declared or default token budget. |
| CR-817-05 | When an intent's token budget is exhausted, further LLM invocations for that intent MUST be blocked. |
| CR-817-06 | Every deployment MUST configure a cost circuit breaker with a declared budget threshold. |
| CR-817-07 | When the circuit breaker triggers, the governance committee MUST be notified within 5 minutes. |
| CR-817-08 | Idle agents exceeding their suspension threshold MUST be suspended. |
| CR-817-09 | Suspended agents MUST resume within 5 seconds of receiving an invocation. |
| CR-817-10 | LLM cost metrics MUST flow to the observability layer per the fields in section 12.1. |

---

## 14. Security Considerations

Cost circuit breaker triggering is itself a potential attack vector — an attacker who can flood the system with LLM-invoking intents may intentionally trigger the circuit breaker to degrade autonomous operation. Rate limiting at the intent submission layer (ANIF-813) is the primary countermeasure. Unusual patterns of cost growth SHOULD be investigated for both accidental and deliberate causes.

---

## 15. Operational Considerations

Cost thresholds MUST be reviewed regularly as deployment scale grows. A threshold appropriate at initial deployment may trigger false positives within six months as intent volume grows. Governance committees SHOULD review cost thresholds quarterly and update them before sustained volume growth causes operational disruption.
