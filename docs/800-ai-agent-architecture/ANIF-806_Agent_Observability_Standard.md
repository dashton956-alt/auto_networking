# ANIF-806: Agent Observability Standard

| Field        | Value                                              |
|--------------|----------------------------------------------------|
| Doc ID       | ANIF-806                                           |
| Series       | AI Agent Architecture                              |
| Version      | 0.1.0                                              |
| Status       | Draft                                              |
| Authors      | ANIF Working Group                                 |
| Reviewers    | —                                                  |
| Approved by  | —                                                  |
| Created      | 2026-04-07                                         |
| Last updated | 2026-04-07                                         |
| Replaces     | N/A                                                |
| Related docs | ANIF-401, ANIF-724, ANIF-800, ANIF-716             |

---

## Abstract

This document defines the mandatory observability requirements for all ANIF agents across all tiers. Every agent MUST emit a structured health signal at a maximum interval of 60 seconds. Every agent MUST expose a standard set of metrics via the agent metrics endpoint. Tier 3 agents MUST emit a pre-execution signal before calling `execute()`. Observability is a governance obligation, not an operational nicety — an agent that cannot be observed cannot be governed.

---

## 1. Introduction

### 1.1 Purpose

Governance requires visibility. The ethics framework (ANIF-700 series) defines what agents MUST and MUST NOT do. The progressive intervention model (ANIF-716) defines how violations are handled. Neither can function without observability — the ability to detect what an agent is doing before and after it acts. This document specifies the minimum observability requirements that make governance possible.

### 1.2 Scope

This document covers:

- Mandatory health signals: format, fields, and emission interval
- Standard agent metrics
- The pre-execution signal for Tier 3 agents
- Observability failure handling
- The relationship between agent observability and the ethics audit trail

### 1.3 Out of Scope

This document does not cover:

- Network observability (see ANIF-401)
- Ethics audit trail record schema (see ANIF-724)
- Monitoring infrastructure implementation
- Alerting thresholds and escalation paths (see ANIF-835)

### 1.4 Intended Audience

- Platform engineers implementing agent monitoring infrastructure
- AI engineers building observable agents
- Operations teams responsible for agent health monitoring
- Build-time council members verifying observability implementation

---

## 2. Normative References

- ANIF-401 — Observability Standard
- ANIF-716 — Progressive Intervention Model
- ANIF-724 — Ethics Audit Trail Requirements
- ANIF-800 — Agent Architecture Overview
- ANIF-835 — Agent Monitoring and Alerting
- RFC 2119 — Key words for use in RFCs to indicate requirement levels

---

## 3. Terms and Definitions

**Health signal:** A structured message emitted by an agent at regular intervals indicating its current operational state, resource usage, and recent activity summary.

**Pre-execution signal:** A structured message emitted by a Tier 3 agent immediately before calling `execute()`. The pre-execution signal creates a before-snapshot for change tracking.

**Agent metrics endpoint:** A standardised endpoint exposed by every agent providing current metric values in a machine-readable format compatible with common monitoring systems.

**Observability failure:** A condition in which a deployed agent fails to emit health signals or fails to expose its metrics endpoint. An observability failure is a governance concern, not merely an operational one.

---

## 4. Health Signal

### 4.1 Requirement

Every deployed agent MUST emit a health signal at a maximum interval of 60 seconds. The health signal interval MAY be shorter but MUST NOT exceed 60 seconds under any operational condition.

### 4.2 Health Signal Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `agent_id` | UUID | MUST | Agent identity |
| `agent_tier` | enum: 0/1/2/3 | MUST | Current tier |
| `lifecycle_state` | enum | MUST | Current lifecycle state per ANIF-803 |
| `trust_level` | enum | MUST | SYSTEM / VERIFIED / PROVISIONAL / UNTRUSTED |
| `signal_timestamp` | ISO 8601 | MUST | Timestamp of signal emission |
| `intents_processed_1m` | integer | MUST | Intents completed in the last 60 seconds |
| `intents_failed_1m` | integer | MUST | Intent failures in the last 60 seconds |
| `llm_invocations_1m` | integer | MUST if LLM capable | LLM calls in the last 60 seconds |
| `llm_suppressions_1m` | integer | MUST if LLM capable | LLM outputs suppressed in the last 60 seconds |
| `governance_gates_triggered_1m` | integer | MUST | Governance gate events in the last 60 seconds |
| `working_context_status` | enum: clear/active | MUST | Whether working context is currently held |
| `strike_count` | integer | MUST | Current strike count from ANIF-716 |
| `uptime_seconds` | integer | MUST | Seconds since last restart |

### 4.3 Health Signal Destination

Health signals MUST be published to the management bus. Tier 0 agents and the orchestrator infrastructure MUST subscribe to health signals from all agents.

### 4.4 Missed Health Signals

If a deployed agent fails to emit a health signal within 120 seconds (two signal intervals), the orchestrator MUST:

1. Classify the agent as health-signal-absent
2. Log the absence as a Severity 3 condition
3. Notify the agent's human counterpart
4. Escalate to Severity 2 if the agent remains absent for a further 5 minutes

An agent that has been health-signal-absent for more than 30 minutes without a known scheduled maintenance window MUST be treated as a Severity 1 operational incident.

---

## 5. Standard Agent Metrics

### 5.1 Metrics Endpoint

Every deployed agent MUST expose a metrics endpoint accessible to the monitoring infrastructure. The endpoint MUST respond within 2 seconds.

### 5.2 Required Metrics

| Metric | Unit | Description |
|---|---|---|
| `agent_intents_total` | counter | Total intents processed since deployment |
| `agent_intents_failed_total` | counter | Total intent failures since deployment |
| `agent_intent_duration_seconds` | histogram | Intent processing duration distribution |
| `agent_llm_invocations_total` | counter | Total LLM calls (0 if non-LLM agent) |
| `agent_llm_suppressions_total` | counter | Total LLM outputs suppressed |
| `agent_governance_triggers_total` | counter | Total governance gate triggers |
| `agent_strike_count` | gauge | Current strike count |
| `agent_lifecycle_state` | gauge (enum encoded) | Current lifecycle state |
| `agent_working_context_active` | gauge (0/1) | Whether working context is currently held |
| `agent_bus_publish_total` | counter | Total messages published to buses |
| `agent_bus_publish_failed_total` | counter | Bus publish failures |

### 5.3 Label Requirements

All metrics MUST carry the following labels:

- `agent_id`: UUID of the agent
- `agent_tier`: tier number (0, 1, 2, or 3)
- `agent_role`: role name from ANIF-801

---

## 6. Pre-Execution Signal (Tier 3)

### 6.1 Requirement

Every Tier 3 agent MUST emit a pre-execution signal immediately before calling `execute()`. The pre-execution signal MUST be confirmed as delivered before `execute()` is called.

If the pre-execution signal cannot be delivered and confirmed within 5 seconds, the `execute()` call MUST be blocked and the intent routed to `manual_review`.

### 6.2 Pre-Execution Signal Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `agent_id` | UUID | MUST | Agent identity |
| `intent_id` | UUID | MUST | Intent being executed |
| `action_type` | enum | MUST | One of the four bounded action types (ANIF-721) |
| `action_target` | string | MUST | The network resource targeted by the action |
| `risk_score` | integer | MUST | Risk score from pipeline |
| `harm_class` | enum | MUST | Harm class from ANIF-712 |
| `governance_decision` | enum | MUST | auto / manual_review / block |
| `rollback_plan_id` | UUID | MUST | Rollback plan identifier |
| `pre_execution_timestamp` | ISO 8601 | MUST | Timestamp of this signal |

### 6.3 Purpose

The pre-execution signal creates a durable record that execution was about to occur, with all relevant governance context, before any network change happens. In the event of an execution failure or incomplete action, the pre-execution signal provides evidence of intent and governance context at the precise moment before the change.

---

## 7. Observability Failure Handling

### 7.1 Classification

An observability failure occurs when:

- A deployed agent fails to emit health signals for more than 120 seconds
- A deployed agent's metrics endpoint fails to respond for more than 5 minutes
- A Tier 3 agent fails to emit a pre-execution signal before calling `execute()`

### 7.2 Governance Status

An observability failure is a governance condition, not merely an operational one. An agent that cannot be observed cannot be verified as operating within its declared constraints. An unobservable agent MUST be treated as operating outside confirmed governance bounds.

A Tier 3 agent that cannot emit pre-execution signals MUST NOT call `execute()`. This is a hard block — not a configurable threshold.

### 7.3 Restoration

An agent whose observability has been restored — after a health signal gap of more than 30 minutes — MUST restart the PROVISIONAL trust period (72 hours) before resuming ACTIVE status. The observability gap introduces uncertainty about what the agent did during the unobserved period.

---

## 8. Conformance Requirements

Every deployed agent MUST emit health signals at a maximum interval of 60 seconds.

Every deployed agent MUST expose a standard metrics endpoint.

Tier 3 agents MUST emit a pre-execution signal before calling `execute()`. A Tier 3 agent that cannot deliver and confirm the pre-execution signal MUST NOT call `execute()`.

An agent that has been health-signal-absent for more than 30 minutes without a known maintenance window MUST trigger a Severity 1 operational incident.

---

## 9. Security Considerations

Health signals and pre-execution signals are observability artefacts that could reveal information about intended network changes. The management bus access controls (ANIF-804) ensure only authorised subscribers receive these signals. Health signal integrity is protected by the signed message envelope. A fabricated health signal indicating a healthy state for a compromised agent would carry an invalid signature and be rejected.

---

## 10. Operational Considerations

Monitoring dashboards SHOULD display the health signal stream for all deployed agents in a single view. Operators SHOULD be able to see at a glance how many agents are in each lifecycle state, how many governance gate triggers are occurring, and whether any agents are in health-signal-absent status. This view is the primary instrument panel for AI governance at the operational level.

---

## Appendix A: Change History

| Version | Date | Author | Changes |
|---|---|---|---|
| 0.1.0 | 2026-04-07 | ANIF Working Group | Initial draft |
