# ANIF-810: Process Agent Integration

| Field        | Value                                              |
|--------------|----------------------------------------------------|
| Doc ID       | ANIF-810                                           |
| Series       | AI Agent Architecture                              |
| Version      | 0.1.0                                              |
| Status       | Draft                                              |
| Authors      | ANIF Working Group                                 |
| Reviewers    | —                                                  |
| Approved by  | —                                                  |
| Created      | 2026-04-08                                         |
| Last updated | 2026-04-08                                         |
| Replaces     | N/A                                                |
| Related docs | ANIF-801, ANIF-814, ANIF-725, ANIF-104             |

---

## Abstract

This document defines the normative requirements for integrating ANIF management agents with external process systems — IT service management (ITSM) platforms, project management tools, and configuration management databases (CMDBs). All integrations MUST follow the adapter pattern defined in this document and MUST comply with the agent containment requirements of ANIF-725. Each adapter declares precisely what data it reads, what data it writes, and what actions it is prohibited from taking. Integration failures MUST degrade gracefully to human process and MUST NOT cause silent data loss or unacknowledged state divergence.

---

## 1. Introduction

### 1.1 Purpose

Management agents (as defined in ANIF-801) operate within a broader operational ecosystem that includes ITSM platforms, project management tools, and configuration databases. This document defines how those integrations are implemented, bounded, and governed. The adapter pattern ensures that every integration is explicitly declared, auditable, and reversibly disconnectable without disrupting the core ANIF pipeline.

### 1.2 Scope

This document covers:

- The adapter pattern for process system integration
- Per-system adapter specifications: ITSM, project management, CMDB
- Read, write, and prohibition boundaries for each adapter
- Integration failure handling and graceful degradation
- Audit logging requirements for all integration actions

### 1.3 Out of Scope

This document does not cover:

- Agent-to-agent communication (see ANIF-804)
- Agent tool integration for network execution tools (see ANIF-814)
- Data architecture and canonical state model (see ANIF-202)
- Change management policy (see ANIF-104)

### 1.4 Intended Audience

- Platform engineers implementing process system adapters
- ITSM administrators governing agent integration access
- AI engineers building management agents
- Governance officers auditing process integration records

---

## 2. Normative References

| Reference | Title |
|---|---|
| ANIF-104 | Change Management Policy |
| ANIF-202 | Data Architecture |
| ANIF-725 | Agent Containment and Governance Enforcement |
| ANIF-801 | Agent Types, Roles and Human Counterparts |
| ANIF-814 | Agent Tool Integration |
| RFC 2119 | Key words for use in RFCs to Indicate Requirement Levels |

---

## 3. Terms and Definitions

| Term | Definition |
|---|---|
| Adapter | A bounded integration component that mediates all data exchange between an ANIF agent and an external process system |
| ITSM | IT Service Management platform (e.g., ServiceNow, Jira Service Management) |
| CMDB | Configuration Management Database — the authoritative record of infrastructure components and their relationships |
| Graceful degradation | The ability of a system to continue operating in a reduced-function mode when an integration is unavailable, without loss of auditability or human oversight |
| Integration boundary | The explicit declaration of what an adapter may read, write, and must not do |

---

## 4. The Adapter Pattern

### 4.1 Principle

Every integration between an ANIF management agent and an external process system MUST be implemented as a named adapter. Direct API calls from agents to external systems, bypassing the adapter layer, are a conformance violation.

### 4.2 Adapter Registration

Every adapter MUST be registered in the agent capability manifest (ANIF-802) of the management agent that uses it. The manifest entry MUST declare:

| Field | Description |
|---|---|
| `adapter_id` | Unique identifier for the adapter |
| `target_system` | The external system being integrated (e.g., `servicenow`, `jira`, `netbox`) |
| `target_system_version` | The version of the external system API being used |
| `reads` | List of data types the adapter may read from the external system |
| `writes` | List of data types the adapter may write to the external system |
| `prohibited` | List of actions the adapter is explicitly prohibited from performing |

### 4.3 Containment Compliance

All adapters MUST comply with the containment requirements of ANIF-725. An adapter MUST NOT grant a management agent capabilities beyond what is declared in its registered boundary. An adapter that exposes undeclared capabilities is a Severity 2 governance violation.

---

## 5. ITSM Adapter Specification

### 5.1 Permitted Reads

| Data Type | Purpose |
|---|---|
| Incident records | Correlate network events with open incidents |
| Problem records | Cross-reference root cause analysis |
| Change requests | Validate intent against approved change windows |
| Configuration item (CI) records | Confirm CMDB state before action |
| SLA definitions | Apply SLA-bearing service prioritisation |

### 5.2 Permitted Writes

| Data Type | Condition |
|---|---|
| Incident notes | Automated diagnostic information appended to existing incidents |
| Incident status updates | Only from `In Progress` to `Resolved` — never direct-close |
| Change request evidence | Attach execution evidence to an approved change request |
| Work notes | Non-status informational annotations |

### 5.3 Prohibited Actions

The ITSM adapter MUST NOT:

- Create, delete, or close incident records
- Create, approve, or reject change requests
- Modify SLA definitions or priority levels
- Access user account or personnel records
- Read or write financial data

---

## 6. Project Management Adapter Specification

### 6.1 Permitted Reads

| Data Type | Purpose |
|---|---|
| Project task status | Determine if infrastructure changes are scheduled |
| Resource allocation | Understand planned maintenance windows |
| Milestone dates | Avoid conflicting changes near critical milestones |

### 6.2 Permitted Writes

| Data Type | Condition |
|---|---|
| Task progress notes | Automated status updates on infrastructure work items |
| Completion markers | Mark infrastructure tasks complete after successful execution |

### 6.3 Prohibited Actions

The project management adapter MUST NOT:

- Create, delete, or reassign project tasks
- Modify milestone dates or project timelines
- Access budget or cost data
- Read personnel performance records

---

## 7. CMDB Adapter Specification

### 7.1 Permitted Reads

| Data Type | Purpose |
|---|---|
| CI records (network devices) | Confirm device inventory before action |
| Relationship records | Understand topology dependencies |
| Configuration baseline | Verify intended state before change |

### 7.2 Permitted Writes

| Data Type | Condition |
|---|---|
| CI attribute updates | Post-execution only, for attributes changed by an executed intent |
| Relationship additions | When new topology elements are created by an executed intent |

### 7.3 Prohibited Actions

The CMDB adapter MUST NOT:

- Delete CI records or relationships
- Create new CI records (provisioning is a human-initiated process)
- Modify CI classification or ownership fields
- Write to CI records while a related change request is not in `Approved` state

---

## 8. Integration Failure Handling

### 8.1 Failure Detection

An adapter MUST treat any of the following as an integration failure:

- No response from the external system within 15 seconds
- An HTTP 5xx response from the external system API
- Authentication or authorisation failure
- Schema mismatch between returned data and expected format

### 8.2 Graceful Degradation

When an integration failure is detected:

1. The adapter MUST log the failure event with: `adapter_id`, `target_system`, `failure_reason`, `timestamp`, `intent_id`.
2. The agent MUST continue processing using the last known good data from the canonical state (ANIF-307), clearly flagged as `integration_degraded: true`.
3. The agent MUST NOT silently substitute stale data without flagging the degraded state.
4. The integration failure MUST be reported to the observability layer (ANIF-401) within 60 seconds.

### 8.3 Prolonged Unavailability

If an integration remains unavailable for more than 15 minutes, the agent MUST escalate to the human-in-loop queue (ANIF-404) for any actions that would normally have relied on the unavailable integration data. Human operators MUST make the final decision in the absence of current integration data.

---

## 9. Audit Logging

Every adapter action — read, write, or failure — MUST be logged to the audit trail (ANIF-724) with the following fields:

| Field | Type | Description |
|---|---|---|
| `adapter_event_id` | UUID v4 | Unique event identifier |
| `adapter_id` | string | The adapter that performed the action |
| `action_type` | enum | One of: `read`, `write`, `failure` |
| `target_system` | string | The external system involved |
| `data_type` | string | The type of data read or written |
| `intent_id` | UUID v4 | The associated intent |
| `outcome` | enum | One of: `success`, `failure`, `degraded` |
| `timestamp` | ISO 8601 | Time of the action |

---

## 10. Conformance Requirements

| ID | Requirement |
|---|---|
| CR-810-01 | All process system integrations MUST be implemented via registered adapters. Direct API calls from agents to external systems are a conformance violation. |
| CR-810-02 | Every adapter MUST declare `reads`, `writes`, and `prohibited` in the capability manifest. |
| CR-810-03 | All adapters MUST comply with ANIF-725 containment requirements. |
| CR-810-04 | ITSM adapters MUST NOT create, delete, or close incident records. |
| CR-810-05 | CMDB adapters MUST NOT delete CI records or create new CI records. |
| CR-810-06 | Integration failures MUST be logged within the agent's processing cycle. |
| CR-810-07 | Agents using degraded integration data MUST flag all affected outputs as `integration_degraded: true`. |
| CR-810-08 | Integrations unavailable for more than 15 minutes MUST result in human-in-loop escalation for affected actions. |
| CR-810-09 | All adapter actions MUST be logged with the fields defined in section 9. |

---

## 11. Security Considerations

Process system adapters connect ANIF agents to enterprise platforms that hold sensitive operational and organisational data. Adapter credentials MUST be stored in a secrets management system, not in agent manifests or environment variables. Adapter credentials MUST be rotated on a schedule no longer than 90 days. Read access to personnel or financial data MUST NOT be granted to any adapter regardless of operational justification.

---

## 12. Operational Considerations

Adapter availability directly affects the quality of management agent decisions. Operators SHOULD monitor adapter health separately from agent health, as ITSM or CMDB platform outages may not be visible in agent health metrics. Integration degradation events SHOULD trigger notification to the relevant platform team, not just the ANIF operations team.
