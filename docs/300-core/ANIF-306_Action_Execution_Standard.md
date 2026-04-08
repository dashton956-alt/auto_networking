# ANIF-306: Action Execution Standard

| Field        | Value                              |
|--------------|------------------------------------|
| Doc ID       | ANIF-306                           |
| Series       | Core                               |
| Version      | 0.1.0                              |
| Status       | Draft                              |
| Authors      | ANIF Working Group                 |
| Reviewers    | —                                  |
| Approved by  | —                                  |
| Created      | 2026-04-07                         |
| Last updated | 2026-04-07                         |
| Replaces     | N/A                                |
| Related docs | ANIF-103, ANIF-305, ANIF-404       |

---

## Abstract

This document is the normative specification for autonomous action execution within the ANIF framework. It defines the four action types and their operational characteristics, the governance preconditions that MUST be satisfied before any action executes, the executor interface contract (including the mandatory rollback implementation), the execution response schema, failure handling obligations, and the mock adapter behaviour used in the ANIF prototype. All execution events MUST be written to the audit log.

---

## 1. Introduction

### 1.1 Purpose

To define the normative requirements for action executors and adapter implementations so that all network-affecting actions in the ANIF pipeline are executed predictably, reversibly, and with complete audit coverage.

### 1.2 Scope

This document covers:

- The four action types and their operational characteristics (risk, success rates, parameter requirements).
- Governance preconditions that MUST be satisfied before execution.
- The executor interface: `execute()` and `rollback()` contract.
- The execution response schema.
- Automatic rollback on failure.
- The adapter layer architecture.
- Mock adapter behaviour specification for prototype environments.
- Audit obligations for all execution events.

### 1.3 Out of Scope

- Decision engine logic that selects the action type (see ANIF-305).
- Governance approval workflow mechanics (see ANIF-100 series).
- Digital twin simulation consulted before execution (see ANIF-308).
- Production adapter implementations for specific vendors.

### 1.4 Intended Audience

- Implementers of the `/execute` and `/rollback/{intent_id}` endpoints.
- Adapter authors integrating vendor-specific network platforms.
- Governance and compliance reviewers verifying execution controls.
- Platform architects designing the execution tier.

---

## 2. Normative References

- ANIF-103: Framework Operational Procedures
- ANIF-305: Decision Engine Specification
- ANIF-307: Distributed Source of Truth
- ANIF-404: Audit Log Specification
- RFC 2119: Key words for use in RFCs to indicate requirement levels

---

## 3. Terms and Definitions

**Executor**
The component responsible for receiving an approved decision and orchestrating action delivery via an adapter.

**Adapter**
A vendor-specific or platform-specific implementation that translates abstract action commands into API calls, CLI commands, or configuration payloads for a target system.

**Abstract Adapter Interface**
The language-agnostic interface definition that all adapters MUST implement. The core executor MUST call only the abstract interface; it MUST NOT depend on adapter internals.

**Execution Record**
The durable record produced on completion (success or failure) of an execute or rollback call.

**Rollback**
The operation that reverses the effect of a previously executed action. Rollback MUST be independently callable without requiring the original execute call context.

**Governance Clearance**
The state produced when the governance gate has determined that an action may proceed: either `mode = auto` with no manual review required, or an approved ticket for `mode = manual_review` intents.

---

## 4. Action Types and Characteristics

### 4.1 reroute_traffic

| Property         | Value                                              |
|------------------|----------------------------------------------------|
| Risk level       | medium                                             |
| Mock success rate| 90%                                                |
| Required parameters | `source_segment`, `target_segment`, `routing_protocol` |
| Governance       | Auto-executable when `mode = auto`                 |
| Rollback type    | Restore previous routing state                     |

**Description:** Redirects traffic flows from one path or node to another. Typically used when the primary path is degraded or when availability objectives require load distribution across multiple paths.

**Parameter requirements:**
- `source_segment` (string): Identifier of the segment from which traffic is being redirected.
- `target_segment` (string): Identifier of the destination segment.
- `routing_protocol` (string): The routing protocol to use (e.g., `BGP`, `OSPF`, `static`).

### 4.2 apply_qos

| Property         | Value                                              |
|------------------|----------------------------------------------------|
| Risk level       | low                                                |
| Mock success rate| 95%                                                |
| Required parameters | `policy_name`, `traffic_class`, `bandwidth_guarantee_mbps` |
| Governance       | Auto-executable when `mode = auto`                 |
| Rollback type    | Remove applied QoS policy and restore default class|

**Description:** Applies a quality-of-service policy to a traffic flow to enforce latency, bandwidth, or priority guarantees. The lowest-risk action type; appropriate when the primary concern is latency or traffic prioritisation.

**Parameter requirements:**
- `policy_name` (string): Name of the QoS policy profile to apply.
- `traffic_class` (string): Traffic classification marker (e.g., `DSCP_EF`, `DSCP_AF41`).
- `bandwidth_guarantee_mbps` (number): Minimum bandwidth guarantee in Mbps.

### 4.3 scale_bandwidth

| Property         | Value                                              |
|------------------|----------------------------------------------------|
| Risk level       | low                                                |
| Mock success rate| 85%                                                |
| Required parameters | `segment_id`, `target_bandwidth_mbps`, `direction` |
| Governance       | Auto-executable when `mode = auto`                 |
| Rollback type    | Restore previous bandwidth allocation              |

**Description:** Increases or decreases the allocated bandwidth for a network segment. Appropriate when throughput objectives cannot be met with current capacity.

**Parameter requirements:**
- `segment_id` (string): Identifier of the segment to scale.
- `target_bandwidth_mbps` (number): Target bandwidth in Mbps.
- `direction` (enum): `up` (increase) or `down` (decrease).

### 4.4 isolate_segment

| Property         | Value                                                         |
|------------------|---------------------------------------------------------------|
| Risk level       | high                                                          |
| Mock success rate| 80%                                                           |
| Required parameters | `segment_id`, `isolation_reason`, `blast_radius_assessment` |
| Governance       | ALWAYS requires pre-approved ticket; NEVER auto-executable    |
| Rollback type    | Re-integrate the isolated segment                             |

**Description:** Isolates a network segment by blocking all inbound and outbound traffic to contain a fault or security incident. This is the highest-risk action type. It MUST NEVER proceed without an approved governance ticket, regardless of the risk score or safety decision.

**Parameter requirements:**
- `segment_id` (string): Identifier of the segment to isolate.
- `isolation_reason` (string): Human-readable justification for the isolation.
- `blast_radius_assessment` (string): Description of services and users affected by the isolation.

---

## 5. Governance Preconditions (Normative)

Execution MUST NOT proceed unless at least one of the following preconditions is satisfied:

**Precondition A (Auto mode):**
- `governance_result.mode = auto`
- The decision engine produced `mode = auto` for this intent.
- No manual review ticket was created.

**Precondition B (Approved ticket):**
- `governance_result.mode = manual_review`
- A governance ticket with `status = approved` exists for this intent's `decision_id`.
- The ticket was approved via `POST /governance/approve/{ticket_id}`.

**Additional precondition for isolate_segment:**
- `recommended_action.action_type = isolate_segment` ALWAYS requires Precondition B (approved ticket), regardless of mode.
- An `isolate_segment` action MUST NOT be executed under Precondition A only.

**If neither precondition is satisfied:**
- The executor MUST return an error response.
- The executor MUST write a `PRECONDITION_FAILED` audit event.
- No network change MUST be made.

---

## 6. Executor Interface Contract

Every executor MUST implement the following two operations. Both operations MUST be independently callable.

### 6.1 execute(decision, governance_clearance) → execution_record

- MUST verify governance preconditions (Section 5) before calling the adapter.
- MUST call the abstract adapter interface (Section 7), NOT the adapter implementation directly.
- MUST record the start time and end time of the execution.
- MUST record the full adapter response.
- MUST set `rollback_available = true` if the adapter confirms the action was applied and a rollback path exists.
- On success: MUST write a `EXECUTION_SUCCESS` audit event.
- On failure: MUST attempt automatic rollback (Section 8.1).

### 6.2 rollback(intent_id) → rollback_record

- MUST be callable using only the `intent_id` as input.
- MUST NOT require the caller to supply decision parameters.
- MUST retrieve the rollback plan from the execution record stored for this `intent_id`.
- MUST call the abstract adapter interface with the rollback action.
- MUST record the rollback outcome.
- On success: MUST write a `ROLLBACK_SUCCESS` audit event.
- On failure: MUST write a `ROLLBACK_FAILED` audit event.
- A `ROLLBACK_FAILED` outcome MUST trigger a human escalation alert.

---

## 7. Adapter Layer Architecture

### 7.1 Separation of Concerns

Vendor-specific integration logic MUST live exclusively in the adapter layer. The core executor MUST call only the abstract adapter interface. This ensures:

- The executor is portable across vendors.
- Adapters can be tested and mocked independently.
- Vendor API credentials and connection details are isolated in the adapter layer.

### 7.2 Abstract Adapter Interface

Every adapter MUST implement the following interface:

```
interface NetworkAdapter:
    execute(action_type: string, parameters: object) → AdapterResponse
    rollback(action_type: string, rollback_parameters: object) → AdapterResponse
    health_check() → AdapterHealthStatus
```

**AdapterResponse schema:**
```json
{
  "success": true,
  "adapter_status_code": 200,
  "adapter_message": "Action applied successfully",
  "applied_changes": [],
  "rollback_reference": "<adapter-internal rollback token>"
}
```

**AdapterHealthStatus schema:**
```json
{
  "healthy": true,
  "adapter_name": "mock",
  "last_checked": "<ISO 8601>",
  "error": null
}
```

### 7.3 Adapter Selection

The executor MUST select the adapter based on the `target_segment` or `segment_id` parameter, resolved against the canonical state (ANIF-307) to determine the target platform. The executor MUST NOT hardcode adapter selection logic; it MUST use the canonical state's platform mapping.

---

## 8. Failure Handling

### 8.1 Automatic Rollback on Failure

If `execute()` returns a failure response from the adapter:

1. The executor MUST immediately attempt `rollback()` using the rollback plan from the decision record.
2. The rollback attempt MUST NOT be skipped, even if the failure reason suggests a partial application.
3. The executor MUST record the rollback outcome.
4. If rollback succeeds: the execution record MUST reflect `status = failed` and `rollback_status = success`.
5. If rollback also fails: the execution record MUST reflect `status = failed` and `rollback_status = failed`; a human escalation alert MUST be raised.

### 8.2 Partial Success

If the adapter reports a partial application (some changes applied, some failed):

- The execution status MUST be `partial`.
- Rollback MUST be attempted automatically.
- The execution record MUST include the adapter's list of applied and unapplied changes.

### 8.3 Timeout Handling

If the adapter does not respond within the configured timeout:

- The execution status MUST be `failed` (not `partial`).
- Rollback MUST be attempted.
- The adapter's health SHOULD be checked after a timeout failure.

---

## 9. Execution Response Schema

The `/execute` endpoint MUST return a response conforming to the following structure.

```json
{
  "execution_id": "<UUID>",
  "intent_id": "<UUID>",
  "decision_id": "<UUID>",
  "action_type": "reroute_traffic | apply_qos | scale_bandwidth | isolate_segment",
  "status": "success | failed | partial",
  "adapter_response": {
    "success": true,
    "adapter_status_code": 200,
    "adapter_message": "Action applied successfully",
    "applied_changes": [],
    "rollback_reference": "<token>"
  },
  "duration_ms": 143,
  "rollback_available": true,
  "rollback_status": null,
  "executed_at": "<ISO 8601 timestamp>",
  "completed_at": "<ISO 8601 timestamp>"
}
```

**Field requirements:**

| Field             | Required | Notes                                                         |
|-------------------|----------|---------------------------------------------------------------|
| execution_id      | Always   | UUID v4 assigned by executor.                                 |
| intent_id         | Always   | The intent that drove this execution.                         |
| decision_id       | Always   | The decision record that authorised this execution.           |
| action_type       | Always   | The action type that was executed.                            |
| status            | Always   | `success`, `failed`, or `partial`.                            |
| adapter_response  | Always   | Full adapter response, even on failure.                       |
| duration_ms       | Always   | Wall-clock time from execute start to adapter response.       |
| rollback_available| Always   | `true` if a valid rollback path was confirmed.               |
| rollback_status   | Conditional | `success`, `failed`, or `null` (if no rollback was attempted).|
| executed_at       | Always   | ISO 8601 timestamp of execution start.                        |
| completed_at      | Always   | ISO 8601 timestamp of execution completion.                   |

---

## 10. Mock Adapter Behaviour Specification

The ANIF prototype uses a mock adapter that simulates action execution without making real network changes. Mock adapter behaviour MUST be deterministic within a test run.

### 10.1 Mock Success Rates

| Action Type       | Mock Success Rate | Behaviour on Failure Simulation         |
|-------------------|-------------------|-----------------------------------------|
| reroute_traffic   | 90%               | Returns `success: false` with adapter error code 503 |
| apply_qos         | 95%               | Returns `success: false` with adapter error code 422 |
| scale_bandwidth   | 85%               | Returns `success: false` with adapter error code 503 |
| isolate_segment   | 80%               | Returns `success: false` with adapter error code 500 |

### 10.2 Mock Adapter Response on Success

```json
{
  "success": true,
  "adapter_status_code": 200,
  "adapter_message": "Mock action applied: {action_type}",
  "applied_changes": [
    "Simulated change: {action_type} on segment {segment_id}"
  ],
  "rollback_reference": "mock-rollback-{execution_id}"
}
```

### 10.3 Mock Adapter Response on Failure

```json
{
  "success": false,
  "adapter_status_code": 503,
  "adapter_message": "Mock adapter simulated failure for action: {action_type}",
  "applied_changes": [],
  "rollback_reference": null
}
```

### 10.4 Mock Rollback Behaviour

- Mock rollback succeeds 100% of the time if the `rollback_reference` is non-null.
- If `rollback_reference` is null (because the original action failed before any changes were applied), rollback MUST return a success response indicating no changes to reverse.

---

## 11. Audit Requirements

All execution events MUST be written to the audit log (ANIF-404). The following events MUST each produce a separate audit record:

| Event                  | Trigger                                           |
|------------------------|---------------------------------------------------|
| `EXECUTION_START`      | Immediately before the adapter is called          |
| `EXECUTION_SUCCESS`    | On successful adapter response                    |
| `EXECUTION_FAILED`     | On failed adapter response                        |
| `EXECUTION_PARTIAL`    | On partial adapter response                       |
| `ROLLBACK_START`       | Immediately before a rollback adapter call        |
| `ROLLBACK_SUCCESS`     | On successful rollback adapter response           |
| `ROLLBACK_FAILED`      | On failed rollback adapter response               |
| `PRECONDITION_FAILED`  | When governance preconditions are not satisfied   |

Each audit event MUST include the `execution_id`, `intent_id`, `decision_id`, `action_type`, event timestamp, and relevant payload.

---

## 12. Conformance Requirements

1. Execution MUST NOT proceed unless governance preconditions (Section 5) are satisfied.
2. `isolate_segment` MUST ALWAYS require an approved governance ticket; auto-execution is PROHIBITED.
3. Every adapter MUST implement the abstract adapter interface defined in Section 7.2.
4. Vendor-specific logic MUST be confined to the adapter layer.
5. Automatic rollback MUST be attempted on every execution failure.
6. Rollback MUST be independently callable via `POST /rollback/{intent_id}`.
7. Every execution event (start, success, failure, rollback) MUST be written to the audit log.
8. The execution response MUST include all fields defined in Section 9.
9. A `ROLLBACK_FAILED` outcome MUST trigger a human escalation alert.

---

## 13. Security Considerations

- The `/execute` endpoint MUST require elevated privileges beyond those required for intent submission.
- Adapter credentials MUST be stored in a secrets management system and MUST NOT appear in execution records, audit logs, or adapter responses.
- Execution records are forensically sensitive; they MUST be append-only and tamper-evident.
- The `isolate_segment` action, as the highest-impact action type, SHOULD have additional approval controls (e.g., two-person authorisation) in production environments.

---

## 14. Operational Considerations

- Execution timeout values SHOULD be configured per action type, as `isolate_segment` and `reroute_traffic` may take longer than `apply_qos`.
- Operators SHOULD monitor `rollback_available = false` records as they indicate executions from which recovery is not possible through the standard pipeline rollback path.
- Mock adapter failure simulation rates SHOULD be adjusted during load testing to verify that automatic rollback paths function correctly under realistic failure scenarios.

---

## Appendix A: Examples

### A.1 Successful Execute Response

```json
{
  "execution_id": "e1a2b3c4-0001-4abc-9000-111122223333",
  "intent_id": "f3a9b2c1-4d7e-4f88-9012-abcdef012345",
  "decision_id": "d9e8f7a6-0001-4abc-b000-ccccdddd0001",
  "action_type": "reroute_traffic",
  "status": "success",
  "adapter_response": {
    "success": true,
    "adapter_status_code": 200,
    "adapter_message": "Mock action applied: reroute_traffic",
    "applied_changes": ["Simulated change: reroute_traffic on segment eu-west-1a"],
    "rollback_reference": "mock-rollback-e1a2b3c4-0001-4abc-9000-111122223333"
  },
  "duration_ms": 143,
  "rollback_available": true,
  "rollback_status": null,
  "executed_at": "2026-04-07T10:00:05Z",
  "completed_at": "2026-04-07T10:00:05.143Z"
}
```

### A.2 Failed Execute With Automatic Rollback

```json
{
  "execution_id": "e1a2b3c4-0002-4abc-9000-444455556666",
  "intent_id": "aabbccdd-1111-4abc-8000-000011112222",
  "decision_id": "d9e8f7a6-0002-4abc-b000-ccccdddd0002",
  "action_type": "scale_bandwidth",
  "status": "failed",
  "adapter_response": {
    "success": false,
    "adapter_status_code": 503,
    "adapter_message": "Mock adapter simulated failure for action: scale_bandwidth",
    "applied_changes": [],
    "rollback_reference": null
  },
  "duration_ms": 88,
  "rollback_available": false,
  "rollback_status": "success",
  "executed_at": "2026-04-07T10:01:00Z",
  "completed_at": "2026-04-07T10:01:00.088Z"
}
```

---

## Appendix B: Change History

| Version | Date       | Author             | Description   |
|---------|------------|--------------------|---------------|
| 0.1.0   | 2026-04-07 | ANIF Working Group | Initial draft |
