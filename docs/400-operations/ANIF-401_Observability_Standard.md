# ANIF-401: Observability Standard

| Field        | Value                              |
|--------------|------------------------------------|
| Doc ID       | ANIF-401                           |
| Series       | Operations                         |
| Version      | 0.1.0                              |
| Status       | Draft                              |
| Authors      | ANIF Working Group                 |
| Reviewers    | —                                  |
| Approved by  | —                                  |
| Created      | 2026-04-07                         |
| Last updated | 2026-04-07                         |
| Replaces     | N/A                                |
| Related docs | ANIF-400, ANIF-402, ANIF-107       |

---

## Abstract

This document defines the observability requirements for ANIF-conformant deployments. It specifies what MUST be observable within the intent execution pipeline, the mandatory metric set, the structured log format, trace correlation requirements, dashboard requirements for operational use, alert thresholds, and the health check endpoint specification. Observability is the foundational operational capability upon which explainability (ANIF-402), feedback analysis (ANIF-403), and governance audit (ANIF-406) all depend.

---

## 1. Introduction

### 1.1 Purpose

This document establishes normative requirements for observability within ANIF deployments. Observability in this context means the ability of operators and automated systems to understand, at any point in time, the internal state of the ANIF pipeline by examining its external outputs: metrics, logs, and traces.

### 1.2 Scope

This document covers:

- Observable pipeline stages and the events they MUST emit.
- The mandatory metric set and how metrics MUST be captured.
- The structured log record format.
- Trace correlation requirements across pipeline stages.
- Dashboard content requirements for operational use.
- Alert thresholds that MUST trigger operator notifications.
- The health check endpoint (`GET /health`) specification.

### 1.3 Out of Scope

- The internal implementation of the observability storage layer (e.g., choice of time-series database, log aggregation platform).
- Visualisation tooling selection.
- Long-term archival and retention policy (covered in ANIF-107).
- Explainability of individual decisions (covered in ANIF-402).

### 1.4 Intended Audience

| Audience                     | Usage                                                            |
|------------------------------|------------------------------------------------------------------|
| Platform/SRE Engineers       | Implementing and operating the observability infrastructure      |
| Network Operations Engineers | Using dashboards and responding to alerts                        |
| Compliance and Audit         | Verifying completeness of log records                            |
| Architecture Teams           | Designing pipeline components to emit correct telemetry          |

---

## 2. Normative References

- ANIF-107: Audit and Immutable Logging Standard
- ANIF-400: Operations Overview
- ANIF-402: Explainability Requirements
- ANIF-305: Intent Execution Pipeline
- RFC 2119: Key words for use in RFCs to Indicate Requirement Levels

---

## 3. Terms and Definitions

| Term              | Definition                                                                                              |
|-------------------|---------------------------------------------------------------------------------------------------------|
| Pipeline Stage    | A discrete processing step within the intent execution pipeline (e.g., parse, policy, risk, govern, execute). |
| Trace ID          | A globally unique identifier (UUID v4) assigned at pipeline entry and carried through all stages.       |
| Intent ID         | A globally unique identifier for a specific intent submission; stable across retries.                   |
| Metric            | A numeric measurement captured at a point in time or over a time window.                               |
| Structured Log    | A log record serialised as JSON with a defined schema.                                                  |
| Dashboard         | A real-time or near-real-time visual display of operational metrics and pipeline state.                 |
| Alert             | An automated notification triggered when a metric breaches a defined threshold.                         |

---

## 4. Observability Requirements

### 4.1 Observable Scope

Every component that participates in the ANIF intent execution pipeline MUST be observable. Specifically:

1. **Every pipeline stage** MUST emit a telemetry event upon entry and upon exit.
2. **Every automated decision** (policy evaluation, risk scoring, governance mode selection) MUST be captured in the audit log before the response is returned to the caller.
3. **Every execution action** (network configuration change, rollback, no-op) MUST generate a log record that includes the action type, target resource, operator or agent identity, and outcome.
4. **Every rollback** MUST generate a distinct log record flagged with `event_type: rollback`, linked to the original execution record via `intent_id` and `trace_id`.
5. **Every error or exception** within pipeline processing MUST be logged with full context; errors MUST NOT be silently swallowed.

### 4.2 Mandatory Metric Set

An ANIF deployment MUST capture and expose the following metrics. All metrics MUST be labelled with `environment` (e.g., prod, staging) and `pipeline_stage` where applicable.

| Metric Name                          | Type      | Labels                              | Description                                                             |
|--------------------------------------|-----------|-------------------------------------|-------------------------------------------------------------------------|
| `anif_requests_total`                | Counter   | endpoint, method, status_code       | Total HTTP requests received per endpoint                               |
| `anif_request_latency_ms`            | Histogram | endpoint, stage                     | Request latency in milliseconds, per endpoint and per pipeline stage    |
| `anif_risk_score_distribution`       | Histogram | environment                         | Distribution of risk scores assigned to processed intents               |
| `anif_escalation_rate`               | Gauge     | environment                         | Rolling % of executions elevated to manual_review or block (24h window) |
| `anif_execution_success_total`       | Counter   | environment, action_type            | Total executions that completed with outcome=success                    |
| `anif_execution_failure_total`       | Counter   | environment, action_type            | Total executions that completed with outcome=failure                    |
| `anif_rollback_total`                | Counter   | environment, action_type            | Total rollback events triggered                                         |
| `anif_policy_evaluation_total`       | Counter   | policy_id, result                   | Total policy evaluations, by policy and result (pass/fail/error)        |
| `anif_governance_mode_total`         | Counter   | mode, environment                   | Total governance mode gate decisions (auto/manual_review/block)         |
| `anif_approval_ticket_total`         | Counter   | status, environment                 | Total approval tickets by final status (approved/rejected/expired)      |
| `anif_false_positive_rate`           | Gauge     | environment                         | Rolling % of escalations approved without change (24h window)           |
| `anif_audit_record_total`            | Counter   | stage, environment                  | Total audit records written, by pipeline stage                          |

### 4.3 Metric Retention

- Raw metric data points MUST be retained for a minimum of 90 days.
- Aggregated (hourly and daily) metric summaries MUST be retained for a minimum of 2 years.
- Retention policy MUST be documented in the deployment's operational runbook.

### 4.4 Structured Log Record Format

Every log record emitted by an ANIF pipeline component MUST be serialised as JSON and MUST include the following fields:

```json
{
  "timestamp":    "<ISO 8601 datetime with millisecond precision and UTC timezone>",
  "trace_id":     "<UUID v4 — assigned at pipeline entry; same value for all records in one request>",
  "intent_id":    "<UUID v4 — the identifier of the intent being processed>",
  "stage":        "<string — the pipeline stage emitting this record>",
  "event_type":   "<string — one of: request, decision, execution, rollback, error, audit>",
  "operator_id":  "<string — the authenticated identity of the requesting operator or agent>",
  "outcome":      "<string — one of: success, failure, pending, skipped, error>",
  "duration_ms":  "<integer — elapsed processing time in milliseconds for this stage>",
  "environment":  "<string — e.g. prod, staging, dev>",
  "payload":      { "<stage-specific structured fields>" }
}
```

#### 4.4.1 Field Requirements

- `timestamp`: MUST be in ISO 8601 format with millisecond precision, expressed in UTC (e.g., `2026-04-07T14:23:01.452Z`).
- `trace_id`: MUST be identical for every log record generated within the same HTTP request lifecycle. MUST be a UUID v4.
- `intent_id`: MUST be present for all records associated with an intent; MUST be `null` for infrastructure-level health records.
- `stage`: MUST be one of the registered pipeline stage names: `ingestion`, `parse`, `policy`, `risk`, `governance`, `approval`, `execution`, `rollback`, `feedback`, `audit`.
- `operator_id`: MUST be the authenticated principal; MUST NOT be omitted or anonymised in operational logs.
- `outcome`: MUST reflect the actual result of the stage at the time of writing; a record MUST NOT be written with `outcome: success` before the operation has completed.
- `duration_ms`: MUST be measured from stage entry to log write; MUST be a non-negative integer.

#### 4.4.2 Log Immutability

- Log records MUST be written to an append-only store.
- Existing records MUST NOT be modified or deleted after writing.
- Log immutability requirements are further specified in ANIF-107.

### 4.5 Trace Correlation

- A `trace_id` MUST be generated at the point of pipeline entry (first HTTP handler invocation) for every request.
- The `trace_id` MUST be included in every log record generated within the same request lifecycle, regardless of pipeline stage.
- The `trace_id` MUST be included in every HTTP response from an ANIF API endpoint, returned in the `X-Trace-Id` response header.
- The `trace_id` MUST be propagated to any downstream service calls made within the same request context.
- Operators MUST be able to retrieve all log records for a single request by querying the audit log using `trace_id`.

### 4.6 Stage Telemetry Events

Each pipeline stage MUST emit the following events:

| Stage        | Entry Event  | Exit Events (success path) | Exit Events (error path) |
|--------------|--------------|----------------------------|--------------------------|
| ingestion    | request      | decision                   | error                    |
| parse        | request      | decision                   | error                    |
| policy       | request      | decision (per policy)      | error                    |
| risk         | request      | decision                   | error                    |
| governance   | request      | decision, audit             | error, audit             |
| approval     | request      | decision, audit             | error, audit             |
| execution    | request      | execution, audit            | error, rollback, audit   |
| rollback     | request      | rollback, audit             | error, audit             |
| feedback     | request      | audit                       | error, audit             |

---

## 5. Dashboard Requirements

### 5.1 Mandatory Dashboard Views

An ANIF deployment MUST provide operator-accessible dashboards containing at minimum the following views:

#### 5.1.1 Live Pipeline State Dashboard

Displays the real-time state of all active and recently completed pipeline executions. MUST include:

- Active executions: count by stage.
- Pending approval tickets: count, oldest ticket age.
- Pipeline throughput: requests per minute (RPM) over last 60 minutes.
- Per-stage latency (p50, p95, p99) over last 60 minutes.
- Current system health status (from `GET /health`).

#### 5.1.2 Decision Heat Map

Displays the distribution of governance decisions over time. MUST include:

- Governance mode distribution (auto / manual_review / block) as percentage and absolute count over configurable time window.
- Risk score heatmap: distribution of risk scores by hour of day and day of week.
- Top policies by failure frequency (last 24 hours).
- Escalation rate trend over the last 7 days.

#### 5.1.3 Alert and Incident Rate Dashboard

MUST include:

- Escalation rate (current 24h, 7-day trend).
- Execution failure rate (current 24h, 7-day trend).
- Rollback rate (current 24h, 7-day trend).
- False positive rate (current 24h, 7-day trend).
- Active alerts with acknowledged/unacknowledged status.

### 5.2 Dashboard Refresh Rate

- Live Pipeline State Dashboard MUST refresh at a maximum interval of 30 seconds.
- Decision Heat Map MUST refresh at a maximum interval of 5 minutes.
- Alert and Incident Rate Dashboard MUST refresh at a maximum interval of 60 seconds.

---

## 6. Alert Thresholds

The following thresholds MUST trigger an automated alert. Alerts MUST be routed to the on-call operational team.

| Metric                   | Threshold             | Severity | Alert Description                                             |
|--------------------------|-----------------------|----------|---------------------------------------------------------------|
| Escalation Rate          | > 20% (24h window)    | Warning  | More than 1 in 5 executions requiring human review            |
| Escalation Rate          | > 35% (24h window)    | Critical | Automation effectiveness severely degraded                    |
| Execution Failure Rate   | > 10% (24h window)    | Warning  | Execution pipeline reliability below acceptable threshold     |
| Execution Failure Rate   | > 20% (24h window)    | Critical | Severe execution failure; consider reverting maturity level   |
| Rollback Rate            | > 5% (24h window)     | Warning  | Elevated rollback activity; review execution policies         |
| Rollback Rate            | > 10% (24h window)    | Critical | Rollback rate unsustainable; immediate review required        |
| False Positive Rate      | > 30% (24h window)    | Warning  | Over-escalation detected; review risk thresholds              |
| Audit Record Gap         | Any stage with 0 records in 15 min during active hours | Warning | Possible observability failure |
| Health Check Failure     | /health returns non-200 for > 60s | Critical | ANIF system health degraded                     |
| Pipeline Latency p99     | > 5000 ms (any stage, 15-min window) | Warning | Stage latency exceeding acceptable threshold     |

### 6.1 Alert Routing

- Warning alerts MUST be routed to the operations team via the configured notification channel.
- Critical alerts MUST be routed to both the operations team and the on-call senior_engineer.
- All alerts MUST generate an audit record with `event_type: audit` and `stage: alerting`.

---

## 7. Health Check Endpoint

### 7.1 Specification

`GET /health`

Returns the operational health status of the ANIF system.

**Response (healthy):**
```json
{
  "status": "healthy",
  "timestamp": "2026-04-07T14:23:01.452Z",
  "version": "0.1.0",
  "components": {
    "pipeline": "healthy",
    "audit_log": "healthy",
    "policy_engine": "healthy",
    "risk_engine": "healthy",
    "governance_engine": "healthy",
    "feedback_engine": "healthy"
  },
  "uptime_seconds": 86400
}
```

**Response (degraded):**
```json
{
  "status": "degraded",
  "timestamp": "2026-04-07T14:23:01.452Z",
  "version": "0.1.0",
  "components": {
    "pipeline": "healthy",
    "audit_log": "degraded",
    "policy_engine": "healthy",
    "risk_engine": "healthy",
    "governance_engine": "healthy",
    "feedback_engine": "unhealthy"
  },
  "uptime_seconds": 86400
}
```

**HTTP Status Codes:**

| Condition             | HTTP Status |
|-----------------------|-------------|
| All components healthy | 200         |
| One or more degraded  | 200 (with status: degraded in body) |
| One or more unhealthy | 503         |

- `GET /health` MUST NOT require authentication.
- `GET /health` MUST respond within 500 ms.
- `GET /health` MUST NOT perform any write operations.
- `GET /health` results MUST NOT be logged to the primary audit log to avoid log pollution; they SHOULD be logged to a separate health log.

---

## 8. Operational Considerations

- The observability infrastructure MUST be treated as a critical dependency; pipeline processing SHOULD NOT proceed if the audit log is unreachable, to avoid ungoverned execution.
- Log ingestion latency SHOULD be monitored; records SHOULD appear in the queryable log store within 10 seconds of emission.
- Operators SHOULD validate trace correlation by querying `GET /audit/{intent_id}` after test executions to confirm all expected log records are present.
- When upgrading ANIF components, the log schema version SHOULD be incremented and the consumer (dashboard, explainability service) MUST be updated to handle the new schema before the producer is deployed.

---

## Appendix A: Examples

### A.1 Sample Structured Log Record — Governance Stage

```json
{
  "timestamp": "2026-04-07T14:23:01.452Z",
  "trace_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "intent_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "stage": "governance",
  "event_type": "decision",
  "operator_id": "user@example.com",
  "outcome": "pending",
  "duration_ms": 42,
  "environment": "prod",
  "payload": {
    "mode": "manual_review",
    "risk_score": 72,
    "trigger_rule": "risk_score_threshold",
    "ticket_id": "GOV-20260407-001"
  }
}
```

### A.2 Sample Structured Log Record — Execution Stage (Rollback)

```json
{
  "timestamp": "2026-04-07T14:25:44.812Z",
  "trace_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "intent_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "stage": "rollback",
  "event_type": "rollback",
  "operator_id": "automation_agent@anif.internal",
  "outcome": "success",
  "duration_ms": 1203,
  "environment": "prod",
  "payload": {
    "action_type": "route_update",
    "target_resource": "segment-42",
    "rollback_reason": "post_execution_verification_failed",
    "original_execution_record": "audit-record-id-abc123"
  }
}
```

---

## Appendix B: Change History

| Version | Date       | Author             | Change                    |
|---------|------------|--------------------|---------------------------|
| 0.1.0   | 2026-04-07 | ANIF Working Group | Initial draft             |
