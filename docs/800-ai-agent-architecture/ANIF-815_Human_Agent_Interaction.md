# ANIF-815: Human-Agent Interaction Model

| Field        | Value                                              |
|--------------|----------------------------------------------------|
| Doc ID       | ANIF-815                                           |
| Series       | AI Agent Architecture                              |
| Version      | 0.1.0                                              |
| Status       | Draft                                              |
| Authors      | ANIF Working Group                                 |
| Reviewers    | —                                                  |
| Approved by  | —                                                  |
| Created      | 2026-04-08                                         |
| Last updated | 2026-04-08                                         |
| Replaces     | N/A                                                |
| Related docs | ANIF-808, ANIF-404, ANIF-402, ANIF-809             |

---

## Abstract

This document defines the four normative interaction modes through which human operators communicate with ANIF agents: directive, approval, override, and query. Each interaction mode has defined behaviour requirements, latency bounds, and audit obligations. Query responses MUST be generated from audit log data and canonical state — LLM inference is prohibited in query responses because it introduces hallucination risk at the human-facing layer where accuracy is most critical. Override actions MUST take effect within 5 seconds of submission and MUST be acknowledged to the operator.

---

## 1. Introduction

### 1.1 Purpose

Human operators interact with ANIF agents in four distinct modes, each serving a different governance function. This document defines the normative requirements for each mode — what the operator can submit, what the system MUST do in response, and what guarantees the system MUST provide regarding latency, accuracy, and auditability.

### 1.2 Scope

This document covers:

- The four human-agent interaction modes and their behavioural requirements
- Latency requirements for override and approval interactions
- The prohibition on LLM inference in query responses
- Audit logging requirements for all interaction events
- Interaction interface availability requirements

### 1.3 Out of Scope

This document does not cover:

- Human authority boundaries by role (see ANIF-808)
- Human-in-loop approval workflow details (see ANIF-404)
- Explainability API specification (see ANIF-402)
- Agent coordination responses to override signals (see ANIF-809)

### 1.4 Intended Audience

- Platform engineers implementing human-agent interaction interfaces
- UX designers building operator-facing dashboards
- AI engineers implementing query response systems
- Conformance assessors evaluating human override guarantees

---

## 2. Normative References

| Reference | Title |
|---|---|
| ANIF-307 | Distributed Source of Truth |
| ANIF-402 | Explainability Requirements |
| ANIF-404 | Human-in-Loop Controls |
| ANIF-724 | Ethics Audit Trail Requirements |
| ANIF-808 | Human-Agent Collaboration Model |
| RFC 2119 | Key words for use in RFCs to Indicate Requirement Levels |

---

## 3. Terms and Definitions

| Term | Definition |
|---|---|
| Directive interaction | An interaction mode where the human instructs an agent to take a specific action or adopt a specific configuration |
| Approval interaction | An interaction mode where the human reviews an agent recommendation and approves or rejects it |
| Override interaction | An interaction mode where the human halts or reverses an action that an agent is taking or has taken |
| Query interaction | An interaction mode where the human asks an agent about the current state of the system or the reasoning behind a past decision |
| Audit-grounded response | A query response generated exclusively from records in the audit trail and canonical state, with no inference or extrapolation |

---

## 4. Interaction Mode: Directive

### 4.1 Definition

In directive mode, a human operator submits an explicit instruction to an agent. The instruction may direct the agent to take a specific action, change its operating parameters, or transition to a specific state.

### 4.2 Requirements

- The directive MUST be submitted as a structured intent (ANIF-301) or as a signed agent control message.
- The agent MUST acknowledge receipt of the directive within 2 seconds.
- The directive MUST be processed through the full intent lifecycle (ANIF-811) including policy evaluation and risk scoring — directives do not bypass pipeline stages.
- If the directive conflicts with a standing policy, the conflict MUST be escalated rather than silently resolved.

### 4.3 Audit Requirements

Every directive interaction MUST be logged with: `operator_id`, `agent_id`, `directive_content` (sanitised), `acknowledgement_timestamp`, `outcome`.

---

## 5. Interaction Mode: Approval

### 5.1 Definition

In approval mode, an agent presents a recommendation to a human operator and the operator accepts or rejects it. The agent MUST NOT proceed with the recommended action until approval is received.

### 5.2 Requirements

- The approval request MUST present the agent's full recommendation, including the risk score, confidence score, affected scope, and the `/why` explanation generated per ANIF-402.
- The operator MUST be able to approve, reject, or request modification.
- Approval requests MUST expire according to the intent TTL defined in ANIF-811.
- Approval MUST be recorded with the operator's identity. Approval without an authenticated identity MUST be rejected.

### 5.3 SLA

Approval queue items MUST be surfaced to the operator within 60 seconds of entering PENDING_APPROVAL state. Items not actioned within the SLA defined in ANIF-404 MUST be escalated.

### 5.4 Audit Requirements

Every approval interaction MUST be logged with: `operator_id`, `intent_id`, `decision` (approved/rejected/modified), `decision_timestamp`, `modification_details` (if applicable).

---

## 6. Interaction Mode: Override

### 6.1 Definition

In override mode, a human operator halts an action that is in progress or reverses an action that has been executed. Override is the most time-sensitive interaction mode.

### 6.2 Requirements

- Override MUST take effect within 5 seconds of operator submission.
- The override signal MUST propagate to all agents involved in executing the affected intent within 5 seconds.
- If the intent is in EXECUTING state, override MUST trigger an immediate halt and rollback procedure as defined in ANIF-306.
- Override MUST be unconditional — no agent may delay, dispute, or defer an override signal.
- The operator MUST receive explicit acknowledgement that the override has taken effect, including confirmation of halt and rollback initiation.

### 6.3 Override Latency Verification

Implementations MUST log the elapsed time between override submission timestamp and override effect confirmation timestamp. If the elapsed time exceeds 5 seconds, the event MUST be logged as a latency violation and reported to the governance committee.

### 6.4 Audit Requirements

Every override interaction MUST be logged per ANIF-808 override logging requirements, plus: `override_effect_timestamp`, `elapsed_ms`, `rollback_initiated` (boolean).

---

## 7. Interaction Mode: Query

### 7.1 Definition

In query mode, a human operator asks the system a question about current state or about the reasoning behind a past decision. Examples:

- "What is the current state of intent 2f4a...?"
- "Why did the pipeline recommend scaling the MPLS path at 14:32?"
- "Which agents were active during the P1 incident yesterday?"

### 7.2 Audit-Grounded Responses

Query responses MUST be generated exclusively from:

- Records in the audit trail (ANIF-724)
- Current canonical state data (ANIF-307)
- Agent observability data (ANIF-806)

LLM inference MUST NOT be used to generate or supplement query responses. The prohibition is absolute: even where an LLM might produce a more natural-sounding or comprehensive response, the risk of hallucination at the human-facing layer — where operators make consequential decisions — outweighs the benefit.

### 7.3 Response Accuracy Requirement

Query responses MUST accurately reflect the records they are derived from. If the records required to answer a query are unavailable (e.g., the relevant audit window has been archived), the system MUST return an explicit statement that the information is unavailable, not an approximation.

### 7.4 Response Latency

Query responses MUST be returned within 10 seconds for queries covering the last 24 hours of audit data. Queries covering longer time ranges MAY return within 60 seconds. Queries that will exceed 60 seconds MUST return an asynchronous acknowledgement and deliver results when available.

### 7.5 Audit Requirements

Every query interaction MUST be logged with: `operator_id`, `query_text`, `data_sources_consulted`, `response_timestamp`, `response_summary`.

---

## 8. Interface Availability

The human-agent interaction interface MUST maintain 99.9% availability. During periods of reduced availability:

- Approval queue items MUST be preserved and remain actionable when the interface recovers.
- Override capability MUST be maintained even if other interaction modes are degraded. Override is the highest-priority interaction mode — its availability MUST be prioritised above all others.

---

## 9. Conformance Requirements

| ID | Requirement |
|---|---|
| CR-815-01 | Directive interactions MUST be acknowledged within 2 seconds. |
| CR-815-02 | Directives MUST pass through the full intent lifecycle including policy and risk evaluation. |
| CR-815-03 | Approval requests MUST present the full recommendation including risk score, confidence, scope, and `/why` explanation. |
| CR-815-04 | Approval MUST be recorded with authenticated operator identity. Unauthenticated approvals MUST be rejected. |
| CR-815-05 | Override MUST take effect within 5 seconds of operator submission. |
| CR-815-06 | Override latency violations (> 5 seconds) MUST be logged and reported to the governance committee. |
| CR-815-07 | Query responses MUST be generated exclusively from audit log and canonical state data. LLM inference in query responses is prohibited. |
| CR-815-08 | Query responses covering the last 24 hours MUST be returned within 10 seconds. |
| CR-815-09 | Override interface availability MUST be prioritised above all other interaction modes during degraded conditions. |

---

## 10. Security Considerations

The interaction interface is a privileged access surface. All interaction submissions MUST require authenticated sessions with multi-factor authentication for override and approval modes. Session tokens MUST expire after 8 hours of inactivity. Interaction logs MUST be treated as security-sensitive records — they record the identity and decisions of human operators and MUST be protected against tampering.

---

## 11. Operational Considerations

Operators relying on query responses for incident triage MUST be aware that query responses reflect the state of records at query time. If an audit event has not yet been written (due to processing lag), it will not appear in query results. Operators SHOULD account for a propagation lag of up to 30 seconds between an event occurring and it appearing in query results.
