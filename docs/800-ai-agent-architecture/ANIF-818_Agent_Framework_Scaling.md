# ANIF-818: Agent Framework Scaling

| Field        | Value                                              |
|--------------|----------------------------------------------------|
| Doc ID       | ANIF-818                                           |
| Series       | AI Agent Architecture                              |
| Version      | 0.1.0                                              |
| Status       | Draft                                              |
| Authors      | ANIF Working Group                                 |
| Reviewers    | —                                                  |
| Approved by  | —                                                  |
| Created      | 2026-04-08                                         |
| Last updated | 2026-04-08                                         |
| Replaces     | N/A                                                |
| Related docs | ANIF-800, ANIF-809, ANIF-819, ANIF-803             |

---

## Abstract

This document defines the normative model for scaling an ANIF agent framework across three dimensions: agent instance scaling, pipeline scaling, and message bus scaling. Scaling operations MUST NOT deploy agents that have not completed build-time council review. Sudden scaling events — defined as an increase of more than 200% in agent instances within 10 minutes — MUST be logged as anomalies and reviewed. Scale-in operations MUST NOT reduce the instance count below the minimum required to maintain human override availability. Scaling is an operational capability that MUST remain within governance boundaries at all times.

---

## 1. Introduction

### 1.1 Purpose

As intent volumes grow, network scale increases, or deployment regions expand, the ANIF framework MUST scale to maintain performance while preserving governance integrity. This document specifies the dimensions of scale, the constraints that govern scaling operations, and the anomaly detection requirements that identify unexpected scaling behaviour.

### 1.2 Scope

This document covers:

- Three scaling dimensions: agent instances, pipeline parallelism, and message bus capacity
- The Agent Pool Controller role and its responsibilities
- Scaling constraints: council review and governance compliance
- Sudden scaling anomaly detection
- Minimum instance floors for human override availability

### 1.3 Out of Scope

This document does not cover:

- Agent lifecycle state transitions during scaling (see ANIF-803)
- Disaster recovery and degradation levels (see ANIF-819)
- Agent Coordination Model (see ANIF-809)
- Infrastructure capacity planning

### 1.4 Intended Audience

- Platform engineers designing agent deployment infrastructure
- Tier 0 agent developers implementing the Agent Pool Controller
- Governance officers reviewing scaling policies
- Conformance assessors evaluating scaling governance claims

---

## 2. Normative References

| Reference | Title |
|---|---|
| ANIF-800 | Agent Architecture Overview |
| ANIF-803 | Agent Lifecycle Management |
| ANIF-809 | Agent Coordination Model |
| ANIF-819 | Disaster Recovery and Resilience |
| ANIF-901 | AI Council Overview |
| RFC 2119 | Key words for use in RFCs to Indicate Requirement Levels |

---

## 3. Terms and Definitions

| Term | Definition |
|---|---|
| Agent Pool Controller | A Tier 0 agent responsible for monitoring queue depth and adjusting agent instance counts |
| Scale-out | Increasing the number of agent instances to handle higher load |
| Scale-in | Decreasing the number of agent instances during lower load periods |
| Minimum floor | The minimum number of instances for a given agent role that MUST be maintained at all times |
| Sudden scaling event | A scale-out event that increases agent instances by more than 200% within 10 minutes |
| Pipeline scaling | Increasing the number of concurrent intent processing pipelines |

---

## 4. Dimension 1 — Agent Instance Scaling

### 4.1 Agent Pool Controller

The Agent Pool Controller is a Tier 0 agent responsible for monitoring intent queue depth and active pipeline utilisation, and for adjusting the number of active agent instances in response to load changes.

The Agent Pool Controller MUST:

- Monitor queue depth per agent role at a minimum interval of 30 seconds
- Issue scale-out or scale-in signals when queue depth crosses declared thresholds
- Log all scaling decisions with: `agent_role`, `current_instances`, `new_instances`, `trigger_reason`, `timestamp`

### 4.2 Scale-Out Constraints

Scale-out MUST NOT deploy an agent instance if any of the following conditions apply:

- The agent type has not completed build-time council review (ANIF-901)
- The agent manifest has not been signed by the build-time council
- The agent type is in SUSPENDED or DEPRECATED lifecycle state (ANIF-803)

Attempting to scale out a non-council-reviewed agent type is a Severity 2 governance violation.

### 4.3 Scale-In Constraints

Scale-in MUST NOT reduce the active instance count below the declared minimum floor for any agent role. Minimum floors MUST be declared per agent role in the deployment configuration.

Scale-in MUST drain in-flight work before terminating an instance. Instance termination before in-flight work is completed is a conformance violation.

### 4.4 Minimum Floors

The following minimum floors apply by default and MUST NOT be reduced without governance committee approval:

| Agent Role Category | Minimum Floor |
|---|---|
| Intent Validation Agent | 2 |
| Policy Evaluation Agent | 2 |
| Decision Engine Agent | 2 |
| Execution Agent (Tier 3) | 1 |
| Human Override Handler | 2 |
| Intent Manager Agent (singleton) | 1 |

---

## 5. Dimension 2 — Pipeline Scaling

### 5.1 Concurrent Pipelines

Pipeline scaling allows multiple intent processing pipelines to operate concurrently, each handling a separate intent. The number of concurrent pipelines MUST be declared as `max_concurrent_pipelines` in the deployment configuration.

### 5.2 Pipeline Scaling Constraints

Increasing `max_concurrent_pipelines` MUST NOT result in more concurrent intents than the human override system can service. The maximum concurrent pipeline count MUST NOT exceed a value where the human-in-loop queue would be unable to meet its SLA (ANIF-404) under peak approval demand.

### 5.3 Pipeline Queue Management

The Agent Pool Controller MUST prioritise pipeline allocation by intent priority level. Intents with higher declared priority MUST be allocated pipeline capacity before lower-priority intents.

---

## 6. Dimension 3 — Message Bus Scaling

### 6.1 Bus Capacity

The message bus that carries agent-to-agent communications (ANIF-804) MUST be scaled to maintain message delivery latency below 500 milliseconds at the 99th percentile under peak load.

### 6.2 Bus Scaling Triggers

Bus capacity MUST be reviewed when:

- Measured message delivery latency exceeds 300 milliseconds at the 95th percentile
- Message queue depth on any bus topic exceeds 10,000 messages
- Agent instance count increases by more than 50% since last bus capacity review

---

## 7. Sudden Scaling Anomaly Detection

### 7.1 Threshold Definition

A sudden scaling event occurs when the total agent instance count across all roles increases by more than 200% within any 10-minute window.

### 7.2 Anomaly Response

When a sudden scaling event is detected:

1. The event MUST be logged immediately as a scaling anomaly with: `total_instances_before`, `total_instances_after`, `time_window_minutes`, `timestamp`.
2. The governance committee MUST be notified within 5 minutes.
3. The Agent Pool Controller MUST pause further scale-out actions until a human operator reviews and acknowledges the event.
4. The scaling pause MUST NOT affect scale-in operations — instances may still be reduced during a pause.

### 7.3 Anomaly Investigation

The governance committee MUST review the anomaly cause within 24 hours of notification and determine whether the scaling event was:

- Expected (e.g., due to a known large-scale event) — log as reviewed and resume scaling
- Unexpected (e.g., runaway queue growth, misconfiguration) — require remediation before resuming

---

## 8. Governance Compliance During Scaling

All scaling operations MUST be logged and available to the governance audit trail (ANIF-724). Scaling is not an administrative operation exempt from audit — the deployment of additional agent capacity is an action with governance implications.

The governance committee MUST receive a monthly scaling report including:

- Peak instance counts by agent role
- Scaling events and their triggers
- Any sudden scaling anomalies and their outcomes
- Human override system capacity utilisation at peak load

---

## 9. Conformance Requirements

| ID | Requirement |
|---|---|
| CR-818-01 | Scale-out MUST NOT deploy agent types that have not completed build-time council review. |
| CR-818-02 | Scale-in MUST NOT reduce agent instance counts below declared minimum floors. |
| CR-818-03 | Instance termination with in-flight work is a conformance violation. |
| CR-818-04 | Sudden scaling events (>200% instance increase in 10 minutes) MUST be logged as anomalies. |
| CR-818-05 | The governance committee MUST be notified of sudden scaling events within 5 minutes. |
| CR-818-06 | Further scale-out MUST be paused following a sudden scaling event until human review. |
| CR-818-07 | All scaling operations MUST be logged to the governance audit trail. |
| CR-818-08 | Message bus latency MUST be maintained below 500 milliseconds at the 99th percentile. |

---

## 10. Security Considerations

Scaling infrastructure is a potential attack surface: an attacker who can trigger scale-out may inflate operational costs without improving throughput (if the scale-out is not matched to genuine intent volume). The sudden scaling anomaly detection (section 7) is partly a security control. Scaling decisions by the Agent Pool Controller MUST be authenticated and authorised — the controller MUST NOT accept scaling signals from unauthenticated sources.

---

## 11. Operational Considerations

Minimum floor values MUST be reviewed as the deployment matures. A minimum floor of 2 for Intent Validation Agents is appropriate at initial deployment but may need to increase as intent volume grows. Operators SHOULD review minimum floors annually and after any significant change to deployment scale or criticality.

Scaling capacity SHOULD be pre-provisioned for known high-volume events (e.g., planned maintenance windows, end-of-quarter provisioning cycles). Reactive scaling is slower and more disruptive than proactive pre-scaling.
