# ANIF-816: Context Window Management

| Field        | Value                                              |
|--------------|----------------------------------------------------|
| Doc ID       | ANIF-816                                           |
| Series       | AI Agent Architecture                              |
| Version      | 0.1.0                                              |
| Status       | Draft                                              |
| Authors      | ANIF Working Group                                 |
| Reviewers    | —                                                  |
| Approved by  | —                                                  |
| Created      | 2026-04-08                                         |
| Last updated | 2026-04-08                                         |
| Replaces     | N/A                                                |
| Related docs | ANIF-806, ANIF-807, ANIF-817, ANIF-812             |

---

## Abstract

This document defines the six normative strategies for managing the context window of LLM-backed agents within an ANIF-conformant implementation. Unmanaged context growth degrades LLM output quality, increases cost, and introduces stale data risks. The six strategies — intent isolation, context budgets, prompt compression and caching, selective retrieval, summarisation checkpoints, and role-scoped context delivery — MUST be applied in combination to ensure agents receive precisely the data their role requires and no more. Context overflow events MUST be logged and treated as design signals for manifest review rather than silent truncation events.

---

## 1. Introduction

### 1.1 Purpose

LLM agents have finite context windows. Without disciplined context management, agents accumulate stale or irrelevant data, produce degraded outputs, and incur unnecessary cost. This document specifies the normative strategies that implementers MUST apply to keep agent context focused, current, and role-appropriate.

### 1.2 Scope

This document covers:

- The six context management strategies and their requirements
- Context budget declaration in agent manifests
- Context overflow detection and handling
- The relationship between context management and cost optimisation

### 1.3 Out of Scope

This document does not cover:

- LLM agent manifest requirements beyond context fields (see ANIF-807)
- AI cost optimisation strategies beyond context management (see ANIF-817)
- Knowledge package content and distribution (see ANIF-812)
- Agent observability and health metrics (see ANIF-806)

### 1.4 Intended Audience

- AI engineers implementing LLM-backed agents
- Platform architects designing multi-stage pipelines
- Cost governance officers reviewing context budgets
- Conformance assessors evaluating LLM deployment practices

---

## 2. Normative References

| Reference | Title |
|---|---|
| ANIF-307 | Distributed Source of Truth |
| ANIF-807 | LLM Agent Specification |
| ANIF-812 | Learning Agent and Network Intelligence |
| ANIF-817 | AI Cost Optimisation and Governance |
| RFC 2119 | Key words for use in RFCs to Indicate Requirement Levels |

---

## 3. Terms and Definitions

| Term | Definition |
|---|---|
| Context window | The maximum number of tokens (input plus output) that an LLM can process in a single invocation |
| Context budget | The maximum token allocation declared for an agent role in its capability manifest |
| Context overflow | A condition where the data required for an agent's task exceeds its declared context budget |
| Intent isolation | The practice of providing a fresh context for each intent, with no carry-over from previous intents |
| RAG | Retrieval-Augmented Generation — a technique where relevant data is retrieved and inserted into context rather than providing the full data store |
| Summarisation checkpoint | A pipeline stage that compresses the outputs of prior stages into a summary before passing to subsequent stages |

---

## 4. Strategy 1 — Intent Isolation

### 4.1 Requirement

Each intent MUST be processed with a fresh context. LLM agents MUST NOT retain context from one intent invocation to the next.

### 4.2 Rationale

Context carry-over between intents introduces cross-intent contamination — reasoning about one intent can be influenced by the data from a previous, unrelated intent. Intent isolation eliminates this class of error. The cost of reconstructing context per intent is addressed by the caching strategy (section 6).

### 4.3 Session Boundary

The context boundary coincides with the intent lifecycle boundary. When an intent moves to a terminal state, all context accumulated during that intent's processing MUST be discarded.

---

## 5. Strategy 2 — Context Budgets

### 5.1 Declaration Requirement

Every LLM agent MUST declare a `context_budget_tokens` field in its capability manifest specifying the maximum token allocation for a single invocation. This value MUST NOT exceed 80% of the LLM model's documented context window limit, reserving 20% for output generation.

### 5.2 Budget Enforcement

The platform MUST enforce context budgets at the point of LLM invocation. If the assembled context for an invocation exceeds the declared budget, the overflow MUST be handled per section 10 — the context MUST NOT be silently truncated.

### 5.3 Budget Values

Context budgets MUST be declared by agent role category. Example reference values:

| Agent Role Category | Reference Budget |
|---|---|
| Intent classification agents | 4,000 tokens |
| Policy evaluation agents | 8,000 tokens |
| Risk scoring agents | 6,000 tokens |
| Anomaly analysis agents | 12,000 tokens |
| Report generation agents | 16,000 tokens |

These are reference values only. Deployments MUST declare budgets based on observed operational requirements and MUST update manifest values when requirements change.

---

## 6. Strategy 3 — Prompt Compression and Caching

### 6.1 Canonical Pattern Caching

Prompts that are structurally identical across multiple invocations — system prompts, role descriptions, standard policy summaries — MUST be cached at the platform level. Cached prompt components MUST be referenced by hash rather than re-transmitted in full on each invocation.

### 6.2 Prompt Compression

Before assembling the final context for an LLM invocation, the platform SHOULD apply lossless compression to repetitive structures in the prompt (repeated key-value patterns, redundant header text, duplicate policy clauses).

### 6.3 Cache Invalidation

Cached prompt components MUST be invalidated and regenerated when the underlying source data changes. Stale cached components that misrepresent current policy or state are a conformance violation. Cache invalidation MUST occur within 60 seconds of the source data change.

---

## 7. Strategy 4 — Selective Retrieval (RAG)

### 7.1 Requirement

LLM agents MUST NOT receive the full canonical network state or topology in their context. Agents MUST receive only the subset of canonical state relevant to the current intent, retrieved via selective retrieval.

### 7.2 Retrieval Scope

The retrieval scope for each agent role MUST be declared in the agent manifest as `retrieval_scope`. Retrieval MUST be limited to the declared scope. Common scope definitions:

| Agent Role | Retrieval Scope |
|---|---|
| Intent classification | Intent content only |
| Policy evaluation | Applicable policies for the intent's domain |
| Risk scoring | Historical risk records for affected components |
| Anomaly analysis | Metrics for the flagged component ± 2 topological hops |

### 7.3 Scope Violations

An agent that retrieves data outside its declared `retrieval_scope` is committing a containment violation (ANIF-725). Retrieval operations MUST be logged to verify scope compliance.

---

## 8. Strategy 5 — Summarisation Checkpoints

### 8.1 Requirement

In multi-stage pipelines, each pipeline stage MUST receive a structured summary of prior stage outputs rather than raw data. Pipeline stages MUST NOT pass full raw outputs forward.

### 8.2 Summary Format

Summaries MUST include:

- Stage name and completion status
- Key findings or outputs in structured form
- Any flags or escalation conditions raised
- The intent_id and stage_id for traceability

### 8.3 Summary Retention

Stage summaries MUST be retained in the audit trail (ANIF-724) as part of the intent processing record. They serve as the compressed representation of pipeline execution history for audit and query purposes.

---

## 9. Strategy 6 — Role-Scoped Context Delivery

### 9.1 Requirement

Each agent MUST receive only the data that its declared role requires. Context assembly MUST be role-aware — the platform MUST NOT deliver undifferentiated context to all agents.

### 9.2 Scope Enforcement

Role-scoped delivery is enforced through the combination of:

- `retrieval_scope` in the agent manifest (section 7.2)
- Role-scoped knowledge package distribution (ANIF-812)
- Pipeline stage summarisation (section 8)

An agent whose context contains data outside its declared scope MUST NOT be permitted to invoke the LLM until the out-of-scope data is removed.

---

## 10. Context Overflow Handling

### 10.1 Overflow Detection

Context overflow occurs when the assembled context exceeds the agent's declared `context_budget_tokens`. Overflow MUST be detected before the LLM is invoked.

### 10.2 Overflow Response

When overflow is detected:

1. The LLM invocation MUST NOT proceed with truncated context.
2. An overflow event MUST be logged with: `agent_id`, `intent_id`, `budget_tokens`, `actual_tokens`, `overflow_tokens`, `timestamp`.
3. The overflow event MUST be forwarded to the Learning Agent (ANIF-812) as a design signal.
4. The agent MUST apply its declared fallback behaviour (`block`, `use_cache`, or `skip_stage` per ANIF-807).

### 10.3 Overflow as Design Signal

Repeated overflow events for the same agent MUST be treated as evidence that the agent's `context_budget_tokens` or `retrieval_scope` requires review. Three or more overflow events for the same agent within any 7-day window MUST trigger a manifest review.

---

## 11. Conformance Requirements

| ID | Requirement |
|---|---|
| CR-816-01 | Each intent MUST be processed with a fresh context. Context carry-over between intents is prohibited. |
| CR-816-02 | Every LLM agent MUST declare `context_budget_tokens` in its manifest. |
| CR-816-03 | `context_budget_tokens` MUST NOT exceed 80% of the model's documented context window limit. |
| CR-816-04 | Context exceeding the declared budget MUST NOT be silently truncated. |
| CR-816-05 | Stale cached prompt components that misrepresent current state are a conformance violation. |
| CR-816-06 | Agents MUST NOT receive the full canonical state. Retrieval MUST be scoped to the declared `retrieval_scope`. |
| CR-816-07 | Multi-stage pipelines MUST pass stage summaries forward, not raw outputs. |
| CR-816-08 | Context overflow events MUST be logged and forwarded to the Learning Agent. |
| CR-816-09 | Three or more overflow events for the same agent within 7 days MUST trigger a manifest review. |

---

## 12. Security Considerations

Context injection is a prompt injection vector. Data retrieved from external sources — ITSM records, monitoring alerts, CMDB entries — MUST be sanitised before insertion into context to prevent injected instructions from influencing agent behaviour. Retrieval scope limits (section 7) reduce the attack surface by limiting the quantity of external data that enters agent context.

---

## 13. Operational Considerations

Context budget values declared at deployment will require periodic review as network scale, intent complexity, and agent capabilities evolve. Operators SHOULD treat context overflow events as a backlog item rather than an alert — a single overflow event is a design signal; a pattern of overflows is an operational problem requiring manifest updates.
