# ANIF-307: Distributed Source of Truth

| Field        | Value                              |
|--------------|------------------------------------|
| Doc ID       | ANIF-307                           |
| Series       | Core                               |
| Version      | 0.1.0                              |
| Status       | Draft                              |
| Authors      | ANIF Working Group                 |
| Reviewers    | —                                  |
| Approved by  | —                                  |
| Created      | 2026-04-07                         |
| Last updated | 2026-04-07                         |
| Replaces     | N/A                                |
| Related docs | ANIF-200, ANIF-202, ANIF-308       |

---

## Abstract

This document is the normative specification for the ANIF Distributed Source of Truth (DSoT). Network state in a multi-vendor, multi-region infrastructure is inherently distributed across heterogeneous sources — NetBox, CMDBs, cloud provider APIs, and physical inventory systems. The DSoT defines how ANIF builds and maintains a canonical state model by federating these sources, applies source freshness scoring to guard against stale data, resolves source conflicts through a defined priority hierarchy, and handles partial outages gracefully without halting the pipeline. All pipeline components that consume network state MUST read from the canonical state model, not from individual sources directly.

---

## 1. Introduction

### 1.1 Purpose

To define the normative requirements for how ANIF collects, merges, versions, and maintains the authoritative view of network state that the policy engine, risk engine, and decision engine depend on for accurate, consistent decision-making.

### 1.2 Scope

This document covers:

- The challenge of distributed, multi-source network state and why a canonical model is required.
- The canonical state model definition and its mandatory fields.
- Source registry: the sources ANIF MUST support in its reference implementation.
- Source freshness scoring and its effect on risk score.
- Source priority hierarchy for conflict resolution.
- Reconciliation process when sources conflict.
- Failure handling when a source is unreachable.
- State versioning and how intents reference state versions.

### 1.3 Out of Scope

- The digital twin, which builds on the canonical state for simulation (see ANIF-308).
- Risk scoring that consumes freshness scores (see ANIF-304).
- Physical topology models (see ANIF-200 series).

### 1.4 Intended Audience

- Platform engineers implementing or integrating the DSoT layer.
- Network architects designing multi-source state federation.
- Risk engine implementers who consume canonical state.
- Operators maintaining source integrations.

---

## 2. Normative References

- ANIF-200: Network Architecture Overview
- ANIF-202: Topology Model Specification
- ANIF-304: Risk and Trust Quantification
- ANIF-308: Digital Twin and Change Validation
- RFC 2119: Key words for use in RFCs to indicate requirement levels

---

## 3. Terms and Definitions

**Canonical State**
The merged, authoritative view of the current network state produced by the DSoT layer. All pipeline components MUST consume canonical state, not raw source data.

**Source**
An external system that provides network state data. Examples: NetBox, CMDB, AWS API, GCP API, physical inventory.

**Source Snapshot**
A point-in-time extract of state data from a single source, captured at a specific timestamp.

**Freshness Score**
A numeric indicator (0–100) of how current a source's last snapshot is. A higher freshness score indicates more recent data; a lower score indicates stale data. Stale data MUST increase the risk score (ANIF-304, RF-005 fallback logic).

**Staleness**
The condition in which a source's last snapshot was captured more than the defined staleness threshold ago. A stale source MUST be flagged and its contribution to canonical state MUST be marked as potentially outdated.

**Source Priority**
The precedence order used when two sources provide conflicting values for the same network state field. Higher-priority sources MUST win.

**Conflict**
A condition in which two sources provide different, incompatible values for the same state field.

**Reconciliation**
The process of surfacing source conflicts to human operators for resolution. In the ANIF prototype, reconciliation does NOT involve automatic resolution; conflicts are flagged and escalated.

**State Version**
A monotonically increasing integer or UUID assigned to each canonical state snapshot. Intents MUST reference the state version they were evaluated against.

---

## 4. The Distributed State Challenge

Network infrastructure state in a modern enterprise is not stored in one place. A single network change may be reflected in:

- **NetBox:** Physical and virtual network inventory, rack diagrams, IP address management.
- **CMDB (Configuration Management Database):** Logical service-to-device mappings, change history.
- **Cloud provider APIs (AWS, GCP, Azure):** Real-time virtual network topology, security groups, routing tables.
- **Physical inventory systems:** Hardware asset tracking, firmware versions, port connectivity.
- **Monitoring/telemetry systems:** Live operational state (up/down status, interface utilisation, latency metrics).

Each source has different update frequencies, different data models, and different reliability characteristics. Without a canonical state layer, the ANIF pipeline would face:

- Inconsistent inputs producing non-deterministic decisions.
- Risk scores computed on stale data that does not reflect current network health.
- Policy evaluations that miss recently discovered compliance gaps.

The DSoT resolves this by providing a single, versioned, merged view that the pipeline depends on.

---

## 5. Canonical State Model

### 5.1 Required Fields

Every canonical state record MUST include the following fields.

```json
{
  "state_version": "<integer or UUID>",
  "captured_at": "<ISO 8601 timestamp>",
  "status": "normal | degraded | critical",
  "topology": {
    "segments": [],
    "links": [],
    "nodes": []
  },
  "source_metadata": [
    {
      "source_id": "netbox",
      "last_synced": "<ISO 8601>",
      "freshness_score": 95,
      "stale": false,
      "conflict_flags": []
    }
  ],
  "overall_freshness_score": 90,
  "conflicts": [],
  "region": "EU | US | APAC",
  "environment": "prod | staging | dev"
}
```

### 5.2 Status Field Derivation

The `status` field MUST be derived from the aggregate of source-reported operational states:

| Condition                                                    | Status    |
|--------------------------------------------------------------|-----------|
| All sources healthy; no degradation indicators               | `normal`  |
| One or more sources report degradation; no critical failures  | `degraded`|
| One or more sources report critical failure or are unreachable| `critical`|

When network status is `degraded` or `critical`, the risk engine MUST apply the appropriate risk factor (ANIF-304, RF-005).

### 5.3 Topology Sub-Model

The `topology` field MUST contain:

- `segments`: List of network segment identifiers with their current state.
- `links`: List of inter-segment links with status (up/down/degraded) and utilisation.
- `nodes`: List of network devices with their operational status.

Topology data MUST be sourced from the highest-priority available source for each element type.

---

## 6. Source Registry

The following sources MUST be supported in the ANIF reference implementation. Additional sources MAY be added via the plugin model (see ANIF-500 series, extensibility).

| Source ID       | Description                           | Update Frequency | Priority |
|-----------------|---------------------------------------|------------------|----------|
| prod_telemetry  | Live production telemetry             | Real-time (≤30s) | 1 (highest) |
| cloud_api       | Cloud provider API (AWS/GCP/Azure)    | Near-real-time (≤5m) | 2      |
| netbox          | Physical/virtual network inventory   | Periodic (≤15m)  | 3        |
| cmdb            | Configuration management database    | Periodic (≤30m)  | 4        |
| manual_entry    | Operator-entered state overrides      | On-demand        | 5 (lowest) |

---

## 7. Source Freshness Scoring

### 7.1 Freshness Score Calculation

Each source's freshness score MUST be calculated based on the elapsed time since the source's last successful snapshot, measured against the source's defined update frequency.

```
elapsed = current_time - source.last_synced (in seconds)
expected_interval = source.update_frequency (in seconds)
freshness_score = MAX(0, 100 - (elapsed / expected_interval) * 50)
```

This formula yields:
- Score 100 when data was just synced.
- Score 75 when data is at 50% of the expected interval age.
- Score 50 when data is at the expected interval age (on-time but not ahead).
- Score 0 when data is twice the expected interval age or older.

### 7.2 Staleness Threshold

A source MUST be flagged as `stale = true` when its freshness score falls below 50.

When a stale source contributes data to the canonical state:
- The affected canonical state fields MUST be marked with `stale: true` in the `source_metadata`.
- The `overall_freshness_score` MUST be the weighted average of all active sources' freshness scores, where weight equals source priority (higher priority = higher weight).

### 7.3 Freshness Impact on Risk Score

The `overall_freshness_score` of the canonical state MUST be provided to the risk engine as part of the network state input. The risk engine MUST apply the following additional risk contribution when state is stale:

| Overall Freshness Score | Additional Risk | Justification Entry          |
|-------------------------|-----------------|------------------------------|
| < 50                    | +10             | "canonical state: stale data"|
| < 25                    | +20             | "canonical state: very stale"|

This is supplementary to, not a replacement for, the network status risk factor (RF-005 in ANIF-304).

---

## 8. Source Priority and Conflict Resolution

### 8.1 Priority Hierarchy

When two sources provide different values for the same state field, the higher-priority source's value MUST be used in the canonical state. Priority order (highest to lowest):

1. `prod_telemetry` — live production telemetry
2. `cloud_api` — cloud provider API
3. `netbox` — network inventory
4. `cmdb` — configuration database
5. `manual_entry` — operator overrides

### 8.2 Conflict Detection

A conflict exists when two sources of different priority levels provide different values for the same state field, and the difference is materially significant (not merely a timestamp difference or minor precision difference in numeric values).

### 8.3 Conflict Handling in Prototype

In the ANIF prototype, source conflicts MUST NOT be automatically resolved by the DSoT layer. The following procedure applies:

1. The conflict MUST be detected and recorded in the `conflicts` array of the canonical state.
2. The higher-priority source's value MUST be used in the canonical state.
3. The conflict MUST be flagged for human review.
4. A conflict notification MUST be raised in the operator dashboard (or equivalent notification channel).
5. The canonical state MUST remain usable with the winning value; the conflict does NOT block the pipeline.

### 8.4 Conflict Record Schema

```json
{
  "conflict_id": "<UUID>",
  "field_path": "topology.segments[eu-west-1a].status",
  "source_a": "prod_telemetry",
  "value_a": "degraded",
  "source_b": "netbox",
  "value_b": "normal",
  "winner": "prod_telemetry",
  "winner_rationale": "prod_telemetry has higher priority (rank 1) than netbox (rank 3)",
  "detected_at": "<ISO 8601>",
  "resolved": false
}
```

---

## 9. Failure Handling

### 9.1 Unreachable Source

When a source cannot be reached (network timeout, API error, authentication failure):

1. The source MUST be marked as `unreachable` in `source_metadata`.
2. The last known snapshot from this source MUST be used as a fallback, with its age noted.
3. If no prior snapshot exists for this source, its contribution to canonical state MUST be omitted entirely.
4. The pipeline MUST continue using the remaining sources; an unreachable source MUST NOT halt the pipeline.
5. The canonical state MUST reflect the missing source in its metadata.
6. The risk engine MUST apply elevated risk per the staleness rules in Section 7.3 (or the network status fallback in ANIF-304, Section 6.6 if all sources are unreachable).

### 9.2 All Sources Unreachable

If all sources are simultaneously unreachable:

1. The last fully-assembled canonical state snapshot MUST be used.
2. `status` MUST be set to `degraded` at minimum.
3. The risk engine MUST apply the degraded network state risk factor (+20, RF-005).
4. A CRITICAL system alert MUST be raised.
5. The pipeline MAY continue but MUST NOT auto-execute any action; all decisions MUST be routed to `manual_review`.

### 9.3 Partial Source Availability

Partial source availability (some sources reachable, some not) is the expected operational state. The DSoT MUST continue to function with any subset of sources available, using cached data from unreachable sources with appropriate freshness score penalties.

---

## 10. State Versioning

### 10.1 State Version Assignment

Every canonical state snapshot MUST be assigned a unique state version identifier. The state version MUST be:

- A monotonically increasing integer, OR
- A UUID v4 with an associated creation timestamp.

The state version MUST change every time the canonical state is updated (i.e., on every sync cycle that produces a materially different state).

### 10.2 Intent-to-State Version Linkage

Every intent MUST reference the state version that was current at the time of:

- Risk scoring (the risk engine MUST record which state version it used).
- Decision making (the decision engine MUST record which state version it used).

This linkage ensures that audit records can reconstruct the exact network state under which a decision was made, even if the network state has subsequently changed.

### 10.3 State Version in Execution Records

Execution records MUST also reference the state version that was current at execution time. This allows post-execution analysis to compare the state assumed during decision making with the state at execution time, surfacing any drift.

---

## 11. Conformance Requirements

1. All pipeline components MUST read network state from the canonical state model, not from individual sources directly.
2. Source freshness scores MUST be calculated as defined in Section 7.1.
3. A source MUST be flagged as stale when its freshness score falls below 50.
4. The source priority hierarchy MUST be applied when resolving source conflicts.
5. Source conflicts MUST be recorded; they MUST NOT be auto-resolved in the prototype.
6. An unreachable source MUST NOT halt the pipeline; cached state MUST be used.
7. Every canonical state snapshot MUST carry a state version identifier.
8. Intents MUST be linked to the state version used during risk scoring and decision making.
9. If all sources are unreachable, all decisions MUST be routed to `manual_review`.

---

## 12. Security Considerations

- Source API credentials MUST be stored in a secrets management system and MUST NOT appear in canonical state records or audit logs.
- The canonical state is operationally sensitive; read access MUST be restricted to authorised pipeline components.
- Manual entry is the lowest-priority source precisely because it is the most easily manipulated. Operator-entered overrides MUST be accompanied by an audit record with the operator's identity and the reason for the override.

---

## 13. Operational Considerations

- Sync intervals SHOULD be tunable per source. Higher-priority sources SHOULD be synced more frequently.
- Source health dashboards SHOULD display freshness scores and staleness flags in real time.
- Teams SHOULD review recurring source conflicts as indicators of data model drift between systems.
- The DSoT layer SHOULD expose a `GET /state/current` endpoint for operator inspection of the current canonical state, and a `GET /state/{version}` endpoint for historical lookup.

---

## Appendix A: Examples

### A.1 Canonical State Record (Partial)

```json
{
  "state_version": 1042,
  "captured_at": "2026-04-07T10:00:00Z",
  "status": "degraded",
  "topology": {
    "segments": [
      {"id": "eu-west-1a", "status": "degraded", "utilisation_percent": 87},
      {"id": "eu-west-1b", "status": "normal", "utilisation_percent": 42}
    ],
    "links": [
      {"from": "eu-west-1a", "to": "eu-west-1b", "status": "up", "utilisation_percent": 65}
    ],
    "nodes": [
      {"id": "core-router-01", "status": "degraded", "platform": "cisco-ios-xe"}
    ]
  },
  "source_metadata": [
    {
      "source_id": "prod_telemetry",
      "last_synced": "2026-04-07T09:59:45Z",
      "freshness_score": 99,
      "stale": false,
      "conflict_flags": []
    },
    {
      "source_id": "netbox",
      "last_synced": "2026-04-07T09:45:00Z",
      "freshness_score": 68,
      "stale": false,
      "conflict_flags": ["eu-west-1a.status"]
    }
  ],
  "overall_freshness_score": 91,
  "conflicts": [
    {
      "conflict_id": "sc0001-aaaa-4abc-bbbb-cccc00000001",
      "field_path": "topology.segments[eu-west-1a].status",
      "source_a": "prod_telemetry",
      "value_a": "degraded",
      "source_b": "netbox",
      "value_b": "normal",
      "winner": "prod_telemetry",
      "winner_rationale": "prod_telemetry (rank 1) > netbox (rank 3)",
      "detected_at": "2026-04-07T10:00:00Z",
      "resolved": false
    }
  ],
  "region": "EU",
  "environment": "prod"
}
```

---

## Appendix B: Change History

| Version | Date       | Author             | Description   |
|---------|------------|--------------------|---------------|
| 0.1.0   | 2026-04-07 | ANIF Working Group | Initial draft |
