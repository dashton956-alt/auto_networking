# ANIF-814: Agent Tool Integration

| Field        | Value                                              |
|--------------|----------------------------------------------------|
| Doc ID       | ANIF-814                                           |
| Series       | AI Agent Architecture                              |
| Version      | 0.1.0                                              |
| Status       | Draft                                              |
| Authors      | ANIF Working Group                                 |
| Reviewers    | —                                                  |
| Approved by  | —                                                  |
| Created      | 2026-04-08                                         |
| Last updated | 2026-04-08                                         |
| Replaces     | N/A                                                |
| Related docs | ANIF-802, ANIF-810, ANIF-725, ANIF-845             |

---

## Abstract

This document defines the normative requirements for integrating ANIF agents with external tools — network management APIs, automation platforms, and data sources accessed via structured tool-call protocols. Every tool used by an agent MUST be declared in the agent capability manifest. All tool invocations MUST be logged to the audit trail with sanitised inputs and summarised outputs. Tool versions MUST be pinned to ensure reproducible behaviour. Agents MUST NOT silently fail when a tool is unavailable — a declared fallback MUST be invoked and the degradation MUST be recorded. Tool call rate limits per agent prevent runaway tool usage.

---

## 1. Introduction

### 1.1 Purpose

Agents operate by reasoning over data and acting through tools. The tool integration layer is where agent authority becomes real-world consequence — an agent that calls a network configuration API can change traffic flows, and an agent that calls a provisioning API can create or delete infrastructure. This document establishes the normative requirements that ensure every tool call is declared, authorised, logged, and bounded.

### 1.2 Scope

This document covers:

- Tool declaration requirements in agent capability manifests
- Tool call logging standards
- Tool version pinning and upgrade governance
- Graceful failure and declared fallback requirements
- Tool call rate limits

### 1.3 Out of Scope

This document does not cover:

- Process system adapters (ITSM, CMDB, project management tools) (see ANIF-810)
- Agent capability boundaries and permission enforcement (see ANIF-802)
- Agent containment requirements (see ANIF-725)
- Supply chain security for tool dependencies (see ANIF-845)

### 1.4 Intended Audience

- AI engineers implementing tool-using agents
- Platform engineers maintaining tool registries
- Security teams auditing tool call records
- Conformance assessors evaluating tool governance claims

---

## 2. Normative References

| Reference | Title |
|---|---|
| ANIF-725 | Agent Containment and Governance Enforcement |
| ANIF-802 | Agent Capabilities and Permissions |
| ANIF-810 | Process Agent Integration |
| ANIF-845 | Agent Supply Chain Security — Tool Dependencies |
| RFC 2119 | Key words for use in RFCs to Indicate Requirement Levels |

---

## 3. Terms and Definitions

| Term | Definition |
|---|---|
| Tool | An external function, API, or service that an agent invokes to retrieve data or perform an action |
| Tool call | A single invocation of a tool by an agent, including inputs, outputs, and outcome |
| Tool registry | The authoritative list of registered tools available in the deployment, with version and permission metadata |
| Tool version pinning | The practice of binding a tool invocation to a specific API version rather than a floating version alias |
| Graceful failure | Handling of tool unavailability without silent error propagation — the fallback action MUST be declared and the failure MUST be logged |
| Rate limit | The maximum number of tool calls an agent is permitted to make within a defined time window |

---

## 4. Tool Declaration in Agent Manifests

### 4.1 Mandatory Declaration

Every tool an agent uses MUST be declared in the agent's capability manifest (ANIF-802) before the agent transitions to ACTIVE state. An agent that invokes a tool not declared in its manifest is committing a containment violation (ANIF-725).

### 4.2 Tool Declaration Schema

Each tool entry in the manifest MUST include:

| Field | Type | Description |
|---|---|---|
| `tool_id` | string | Registered tool identifier from the tool registry |
| `tool_version` | string | Pinned version of the tool (MUST NOT be a floating alias) |
| `purpose` | string | Brief description of why this agent uses this tool |
| `access_type` | enum | One of: `read_only`, `read_write`, `write_only` |
| `fallback` | enum | One of: `block`, `use_cache`, `skip_stage` |
| `rate_limit` | object | `max_calls` per `window_seconds` |

### 4.3 Tool Registry

The tool registry is the authoritative source for tool availability. Before registering an agent manifest, the platform MUST verify that every declared `tool_id` exists in the tool registry and that the declared `tool_version` is a currently supported version. Manifests referencing unregistered tools or unsupported versions MUST be rejected.

---

## 5. Tool Call Logging

Every tool call MUST be logged to the audit trail (ANIF-724). The log entry MUST contain:

| Field | Type | Description |
|---|---|---|
| `tool_call_id` | UUID v4 | Unique identifier for this invocation |
| `agent_id` | string | The invoking agent |
| `tool_id` | string | The tool invoked |
| `tool_version` | string | The version invoked |
| `intent_id` | UUID v4 | The intent this tool call serves |
| `inputs_sanitised` | object | Tool inputs with all sensitive values redacted |
| `outputs_summary` | string | A human-readable summary of the output (not full raw output) |
| `duration_ms` | integer | Wall-clock time for the tool call in milliseconds |
| `outcome` | enum | One of: `success`, `failure`, `timeout` |
| `failure_reason` | string | Populated when outcome is `failure` or `timeout` |
| `timestamp` | ISO 8601 | Start time of the tool call |

### 5.1 Input Sanitisation

The `inputs_sanitised` field MUST have all values that match these patterns redacted and replaced with `[REDACTED]`:

- IP addresses in private ranges
- Credentials, tokens, or keys
- Values declared as `sensitive` in the tool's registry entry

Sanitisation is required to protect operational security while preserving auditability of tool call intent.

### 5.2 Output Summarisation

Full raw tool outputs MUST NOT be stored in the audit trail. The `outputs_summary` MUST capture the operational meaning of the output (e.g., "BGP peer state returned: established for 3 of 4 peers") without reproducing raw API response bodies.

---

## 6. Tool Version Management

### 6.1 Version Pinning

Tool versions MUST be pinned to exact API versions in the agent manifest. Floating version references (e.g., `latest`, `v2`, `stable`) are not permitted. Manifests using floating references MUST be rejected at registration.

### 6.2 Tool Version Upgrade Process

Upgrading a tool version in an agent manifest requires:

1. The new tool version MUST be tested against the agent's test suite before deployment (ANIF-820).
2. The manifest MUST be updated and re-signed.
3. The change MUST be reviewed by the build-time council (ANIF-901) if the tool has `access_type: read_write` or `write_only`.
4. The tool registry entry for the old version MUST be retained until all agents using it have been upgraded.

### 6.3 Deprecated Tool Versions

When a tool version is deprecated in the tool registry, all agents using that version MUST be notified. Agents using a deprecated tool version MUST complete upgrade before the version reaches end-of-life. Operating an agent with an end-of-life tool version is a conformance violation.

---

## 7. Graceful Failure and Fallback

### 7.1 Failure Detection

An agent MUST treat any of the following as a tool failure:

- No response within the tool's declared timeout (default: 10 seconds)
- An error response from the tool
- A response that fails schema validation

### 7.2 Fallback Behaviour

When a tool failure is detected, the agent MUST invoke the fallback declared in its manifest for that tool:

| Fallback Value | Behaviour |
|---|---|
| `block` | The agent MUST halt the current pipeline stage, log the failure, and escalate to the human-in-loop queue |
| `use_cache` | The agent MUST use the most recent cached output for this tool, clearly labelled `tool_degraded: true` in all downstream outputs |
| `skip_stage` | The agent MUST skip the pipeline stage that depends on this tool and log the skip as a degradation event |

### 7.3 Silent Failure Prohibition

An agent MUST NOT continue processing as if a tool call succeeded when it failed. All three fallback options require logging the failure and flagging the degraded state. Silent continuation is a conformance violation.

---

## 8. Tool Call Rate Limits

Every tool declaration in the agent manifest MUST specify a `rate_limit` with `max_calls` and `window_seconds`. The platform MUST enforce these limits at the tool invocation layer.

When an agent reaches its rate limit for a tool:

1. Further calls to that tool MUST be blocked for the remainder of the rate window.
2. The rate limit breach MUST be logged as a governance event.
3. The agent MUST apply the declared fallback for the tool for the duration of the block.
4. Rate limit breaches occurring more than three times within any 7-day window for the same agent and tool MUST trigger a manifest review.

---

## 9. Conformance Requirements

| ID | Requirement |
|---|---|
| CR-814-01 | Every tool used by an agent MUST be declared in the agent capability manifest before the agent transitions to ACTIVE state. |
| CR-814-02 | Agents invoking undeclared tools MUST be treated as committing a containment violation. |
| CR-814-03 | Tool version references MUST be pinned. Floating version references MUST be rejected at registration. |
| CR-814-04 | Every tool call MUST be logged with all fields defined in section 5. |
| CR-814-05 | Tool call inputs MUST be sanitised before logging. |
| CR-814-06 | Full raw tool outputs MUST NOT be stored in the audit trail. |
| CR-814-07 | Tool failures MUST invoke the declared fallback. Silent failure is a conformance violation. |
| CR-814-08 | Tool call rate limits MUST be enforced by the platform. |
| CR-814-09 | Three or more rate limit breaches within 7 days for the same agent and tool MUST trigger a manifest review. |
| CR-814-10 | Operating an agent with an end-of-life tool version is a conformance violation. |

---

## 10. Security Considerations

Tool calls are the primary means by which agents affect real infrastructure. Tool call logs are therefore a primary source of evidence in security investigations. The sanitisation requirement (section 5.1) must be carefully balanced: over-sanitisation that removes operationally relevant data undermines investigation capability. The declared sensitive fields in each tool's registry entry SHOULD be reviewed regularly to ensure they reflect current sensitivity classifications.

Access to the tool registry itself MUST be restricted — an attacker who can register a malicious tool or elevate a tool's access type can expand agent capabilities without touching agent manifests.

---

## 11. Operational Considerations

Tool call duration metrics (from the `duration_ms` field) are useful for detecting tool degradation before it causes failures. Operators SHOULD alert on tool call durations that exceed twice the historical mean for a given tool, as this often precedes timeout failures.

Tool call logs accumulate rapidly in active deployments. Operators MUST implement a log retention policy that satisfies the audit retention requirements of ANIF-107 while managing storage growth. Summarised outputs (section 5.2) significantly reduce storage requirements compared to retaining full raw API responses.
