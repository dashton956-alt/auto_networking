# ANIF-308: Digital Twin and Change Validation

| Field        | Value                              |
|--------------|------------------------------------|
| Doc ID       | ANIF-308                           |
| Series       | Core                               |
| Version      | 0.1.0                              |
| Status       | Draft                              |
| Authors      | ANIF Working Group                 |
| Reviewers    | —                                  |
| Approved by  | —                                  |
| Created      | 2026-04-07                         |
| Last updated | 2026-04-07                         |
| Replaces     | N/A                                |
| Related docs | ANIF-200, ANIF-307, ANIF-305       |

---

## Abstract

This document is the normative specification for the ANIF Digital Twin and pre-execution change validation layer. Before any autonomous network action is executed, the ANIF framework SHOULD simulate the candidate action against a digital twin — a virtual representation of the current network topology — to assess impact, identify unsafe conditions, and confirm rollback feasibility. This document defines the digital twin model, the simulation workflow, the simulation output schema, and how simulation verdicts feed into governance mode determination. For the ANIF prototype, the digital twin is a mock topology object and simulation uses rule-based impact estimation.

---

## 1. Introduction

### 1.1 Purpose

To define the normative requirements for pre-execution simulation so that the ANIF pipeline can identify unsafe or high-impact changes before they are applied to production infrastructure, providing a safety net beyond risk scoring and policy evaluation.

### 1.2 Scope

This document covers:

- The definition and properties of the ANIF digital twin.
- The change validation workflow: when simulation runs and how it integrates with the pipeline.
- Simulation input and output schemas.
- Verdict definitions and their pipeline effects.
- Determinism requirements for simulation.
- Rollback feasibility assessment.
- Prototype implementation specification (mock topology + rule-based estimation).

### 1.3 Out of Scope

- The canonical state model that the digital twin is built from (see ANIF-307).
- The decision engine that determines the candidate action (see ANIF-305).
- Full physics-based or ML-based network simulation (future work).

### 1.4 Intended Audience

- Implementers of the digital twin and simulation subsystem.
- Platform architects integrating simulation into the execution pipeline.
- Governance and compliance reviewers assessing simulation's role in change safety.
- Network engineers contributing to the mock topology model.

---

## 2. Normative References

- ANIF-200: Network Architecture Overview
- ANIF-305: Decision Engine Specification
- ANIF-307: Distributed Source of Truth
- RFC 2119: Key words for use in RFCs to indicate requirement levels

---

## 3. Terms and Definitions

**Digital Twin**
A virtual representation of the network topology derived from the canonical state, used to simulate the effects of a candidate action without modifying production infrastructure.

**Simulation**
The process of applying a candidate action to the digital twin and evaluating the resulting state change to assess impact and safety.

**Verdict**
The simulation output's binary-plus classification of the candidate action's safety: one of `safe`, `unsafe`, or `uncertain`.

**Impact Metrics**
Quantitative estimates of the change's effect on the network: latency delta, number of paths affected, reachability status, and affected service count.

**Mitigation**
A suggested modification to the candidate action or its parameters that would reduce the simulated impact to a safe level.

**Rollback Feasibility**
The simulation's assessment of whether the candidate action can be reversed, and how long reversal would take.

**Mock Topology**
A simplified, hardcoded representation of a network topology used in the ANIF prototype when a live digital twin is not available.

---

## 4. The Digital Twin

### 4.1 Definition

The digital twin is a stateful virtual model that mirrors the current canonical network state at the time simulation is requested. It MUST be derived from the canonical state (ANIF-307) at the moment of the simulation request and MUST NOT be updated during a simulation run.

The digital twin is READ-ONLY during simulation. The simulation engine modifies a copy of the twin state to assess impact; the original twin state MUST remain unchanged after simulation.

### 4.2 Digital Twin Construction

The digital twin MUST be constructed from the following canonical state elements:

- Segment list with current status and utilisation.
- Link list with status, utilisation, and capacity.
- Node list with operational status.
- Routing table (derived or explicit).
- Service-to-segment mapping (from CMDB or topology model).

### 4.3 State Version Binding

The digital twin MUST record the canonical state version it was constructed from. The simulation result MUST reference this state version so that the audit record can identify the exact state against which the simulation was run.

### 4.4 Prototype: Mock Topology

In the ANIF prototype, the digital twin is a mock topology object with a predefined set of segments, links, and nodes. The mock topology MUST support at minimum:

- 4 network segments (representing availability zones).
- 6 inter-segment links (representing peered connections).
- At least one degraded segment to exercise degraded-state simulation rules.
- A routing table with at least 2 alternative paths per segment.

The mock topology MAY be defined as a static JSON or YAML file loaded at startup.

---

## 5. Change Validation Workflow

### 5.1 When Simulation Runs

Change validation SHOULD run after the decision engine has produced a recommended action and before the governance gate. The pipeline position is:

```
Decision Engine (ANIF-305) → recommended action
        ↓
Digital Twin Simulation (this document)
        ↓
Governance Gate (ANIF-100 series)
        ↓
Action Executor (ANIF-306)
```

Simulation is a SHOULD requirement, not MUST, because in the prototype implementation the digital twin may not be available for all intent types. However, if a simulation capability is present, it MUST be invoked for all non-null recommended actions.

### 5.2 Simulation Is Non-Destructive

Simulation MUST NOT modify the canonical state or production infrastructure. All changes MUST be applied to a copy of the twin state in memory. The original digital twin state MUST be restored to its pre-simulation condition after each simulation run.

### 5.3 Simulation Inputs

```json
{
  "intent_id": "<UUID>",
  "decision_id": "<UUID>",
  "candidate_action": {
    "action_type": "reroute_traffic | apply_qos | scale_bandwidth | isolate_segment",
    "parameters": {}
  },
  "state_version": 1042
}
```

### 5.4 Simulation Algorithm — Prototype (Rule-Based)

The prototype simulation engine uses rule-based impact estimation applied to the mock topology. The following rules MUST be implemented:

**Rule SIM-001: Segment Isolation Impact**
- Condition: `action_type = isolate_segment` AND `segment.status = normal` (segment was previously contributing to service)
- Impact: All services mapped to the isolated segment are marked unreachable. Latency delta for services depending on this segment increases by 50–200ms estimate. `failed_paths` count = number of routes transiting the segment.

**Rule SIM-002: Traffic Reroute — Path Availability**
- Condition: `action_type = reroute_traffic`
- Impact: Estimate new path latency based on target segment's current utilisation. If target segment utilisation > 80%, estimate latency delta +20ms and flag as potentially unsafe.
- If no alternative path exists: verdict MUST be `unsafe`.

**Rule SIM-003: QoS Application — Low Impact**
- Condition: `action_type = apply_qos`
- Impact: Estimate latency improvement of 10–30% on the affected traffic class. No path failures expected. Verdict defaults to `safe` unless the traffic class already has a conflicting policy applied.

**Rule SIM-004: Bandwidth Scale — Capacity Check**
- Condition: `action_type = scale_bandwidth` AND `direction = up`
- Impact: If requested `target_bandwidth_mbps` exceeds link capacity by more than 20%, verdict MUST be `unsafe`.
- If within capacity: estimate utilisation change; flag as `safe`.

**Rule SIM-005: Degraded Network — Elevated Uncertainty**
- Condition: `network_state.status = degraded`
- Effect: For any action type, if the target segment or any segment in the action's path is already degraded, verdict is elevated to `uncertain` unless a simulation rule has already returned `unsafe`.

---

## 6. Simulation Output Schema

The simulation engine MUST return a response conforming to the following structure.

```json
{
  "simulation_id": "<UUID>",
  "intent_id": "<UUID>",
  "decision_id": "<UUID>",
  "state_version": 1042,
  "verdict": "safe | unsafe | uncertain",
  "impact_metrics": {
    "latency_delta_ms": 0,
    "failed_paths": 0,
    "reachability_change": "none | partial_loss | full_loss",
    "affected_services": [],
    "utilisation_delta_percent": 0
  },
  "mitigations": [
    {
      "description": "<human-readable mitigation suggestion>",
      "action_modification": {}
    }
  ],
  "rollback_feasibility": {
    "feasible": true,
    "estimated_rollback_duration_ms": 5000,
    "rollback_complexity": "low | medium | high",
    "notes": null
  },
  "simulation_rules_applied": ["SIM-001", "SIM-005"],
  "simulated_at": "<ISO 8601 timestamp>"
}
```

**Field requirements:**

| Field                    | Required | Notes                                                                  |
|--------------------------|----------|------------------------------------------------------------------------|
| simulation_id            | Always   | UUID v4 assigned by simulation engine.                                 |
| verdict                  | Always   | One of `safe`, `unsafe`, `uncertain`.                                  |
| impact_metrics           | Always   | All sub-fields MUST be present; zero or null if not applicable.        |
| mitigations              | Conditional | MUST be non-empty if verdict is `unsafe` or `uncertain` and mitigations are available. MAY be empty if no mitigations are known. |
| rollback_feasibility     | Always   | MUST assess feasibility for all non-null actions.                      |
| simulation_rules_applied | Always   | MUST list all rules that were evaluated and contributed to the verdict. |

---

## 7. Verdict Definitions and Pipeline Effects

### 7.1 safe

**Definition:** The simulation indicates that the candidate action is expected to achieve the intent's objectives without causing unacceptable side effects. No unsafe conditions were identified.

**Pipeline effect:** No additional governance restriction is imposed by the simulation verdict. Mode remains as determined by the decision engine.

### 7.2 unsafe

**Definition:** The simulation has identified specific conditions under which the candidate action would cause harm (e.g., unreachable services, path failures exceeding policy thresholds, capacity overflow).

**Pipeline effect:**
- An `unsafe` verdict MUST block autonomous execution.
- `mode` MUST be elevated to `manual_review` or `block`, depending on the severity of the identified conditions.
- A human operator MUST review the simulation report before any execution can proceed.
- The simulation MUST include at least an attempt to provide mitigations in the `mitigations` field.

### 7.3 uncertain

**Definition:** The simulation could not determine with sufficient confidence whether the action is safe. Typically produced when the network state is degraded, when the digital twin lacks sufficient detail for the requested action type, or when simulation rules produce conflicting signals.

**Pipeline effect:**
- An `uncertain` verdict SHOULD trigger `manual_review`.
- The pipeline MAY proceed to autonomous execution only if the governance configuration explicitly permits `uncertain` verdicts to pass (not recommended for production).
- The `uncertain` condition SHOULD be logged as a warning in the audit record.

---

## 8. Rollback Feasibility Assessment

The simulation MUST assess rollback feasibility as part of every simulation run. The rollback feasibility assessment MUST:

1. Determine whether the candidate action can be reversed (e.g., if the action replaces a unique routing path, and no prior state was captured, rollback may not be possible).
2. Estimate the rollback duration based on the action type and affected segment count.
3. Classify rollback complexity:
   - `low`: Single-step reversion with high confidence.
   - `medium`: Multi-step reversion; some risk of side effects.
   - `high`: Complex reversion; high potential for additional disruption.

If rollback is assessed as infeasible (`feasible = false`), the verdict MUST be elevated to at least `uncertain`, and SHOULD be `unsafe` for production environments.

---

## 9. Determinism Requirements

Simulation MUST be deterministic. Given the same candidate action and the same digital twin state:

- The verdict MUST always be the same.
- Impact metrics MUST always produce the same values.
- The same simulation rules MUST be applied in the same order.

For the prototype's rule-based estimator, all impact estimates are computed from deterministic formulas applied to the mock topology. Random sampling, stochastic modelling, and Monte Carlo methods are reserved for a future ML-enhanced simulation layer and MUST NOT be used in version 0.x.

---

## 10. Conformance Requirements

1. Every candidate action SHOULD be simulated against the digital twin before execution.
2. Simulation MUST NOT modify production infrastructure or the canonical state.
3. The digital twin MUST be derived from the canonical state at simulation request time.
4. An `unsafe` verdict MUST block autonomous execution.
5. An `uncertain` verdict SHOULD trigger `manual_review`.
6. The simulation MUST assess rollback feasibility for every non-null action.
7. A `feasible = false` rollback assessment MUST elevate the verdict to at least `uncertain`.
8. Simulation MUST be deterministic: identical inputs MUST produce identical verdicts and metrics.
9. The simulation result MUST reference the canonical state version used.
10. All five simulation rules (SIM-001 through SIM-005) MUST be implemented in the prototype.

---

## 11. Security Considerations

- Simulation results are operationally sensitive: `unsafe` verdicts reveal specific infrastructure vulnerabilities or capacity limits. Access to simulation results MUST be restricted to authorised pipeline components and operators.
- The digital twin MUST NOT contain production credentials, API keys, or authentication tokens from the source systems it models.
- Simulation results MUST be included in the audit log so that the full reasoning chain (including pre-execution safety assessment) is preserved for compliance review.

---

## 12. Operational Considerations

- The mock topology in the prototype SHOULD be updated to reflect the actual target environment's segment structure when the framework is deployed in a pre-production testing context.
- Teams operating in dynamic cloud environments where topology changes frequently SHOULD ensure the digital twin sync interval is short enough to reflect near-current state at simulation time.
- Frequent `uncertain` verdicts in a stable network environment indicate that simulation rules need to be refined or that the mock topology does not accurately reflect the actual topology.
- Simulation duration SHOULD be monitored. Rule-based simulation on the prototype topology SHOULD complete in under 200ms. If simulation begins to block the pipeline for longer periods, the simulation layer SHOULD be made asynchronous with a pipeline timeout and fallback to `uncertain`.

---

## Appendix A: Examples

### A.1 Safe Simulation Result — apply_qos

```json
{
  "simulation_id": "s1m2u3l4-0001-4abc-9000-aabbccdd1111",
  "intent_id": "f3a9b2c1-4d7e-4f88-9012-abcdef012345",
  "decision_id": "d9e8f7a6-0001-4abc-b000-ccccdddd0001",
  "state_version": 1042,
  "verdict": "safe",
  "impact_metrics": {
    "latency_delta_ms": -15,
    "failed_paths": 0,
    "reachability_change": "none",
    "affected_services": ["payments-gateway"],
    "utilisation_delta_percent": 0
  },
  "mitigations": [],
  "rollback_feasibility": {
    "feasible": true,
    "estimated_rollback_duration_ms": 1000,
    "rollback_complexity": "low",
    "notes": "QoS policy can be removed without disruption"
  },
  "simulation_rules_applied": ["SIM-003"],
  "simulated_at": "2026-04-07T10:00:04Z"
}
```

### A.2 Unsafe Simulation Result — isolate_segment on active segment

```json
{
  "simulation_id": "s1m2u3l4-0002-4abc-9000-aabbccdd2222",
  "intent_id": "aabbccdd-0000-4abc-8000-000011112222",
  "decision_id": "d9e8f7a6-0003-4abc-b000-ccccdddd0003",
  "state_version": 1042,
  "verdict": "unsafe",
  "impact_metrics": {
    "latency_delta_ms": 120,
    "failed_paths": 4,
    "reachability_change": "partial_loss",
    "affected_services": ["payments-gateway", "checkout-api", "auth-service"],
    "utilisation_delta_percent": 35
  },
  "mitigations": [
    {
      "description": "Drain traffic from segment eu-west-1a to eu-west-1b before isolating to reduce service disruption",
      "action_modification": {
        "pre_action": "reroute_traffic",
        "pre_action_parameters": {
          "source_segment": "eu-west-1a",
          "target_segment": "eu-west-1b"
        }
      }
    }
  ],
  "rollback_feasibility": {
    "feasible": true,
    "estimated_rollback_duration_ms": 10000,
    "rollback_complexity": "high",
    "notes": "Re-integrating an isolated segment requires coordination with 3 upstream services"
  },
  "simulation_rules_applied": ["SIM-001", "SIM-005"],
  "simulated_at": "2026-04-07T10:00:04Z"
}
```

### A.3 Uncertain Simulation Result — degraded network state

```json
{
  "simulation_id": "s1m2u3l4-0003-4abc-9000-aabbccdd3333",
  "intent_id": "c3d4e5f6-0000-4bcd-9111-000022223333",
  "decision_id": "d9e8f7a6-0004-4abc-b000-ccccdddd0004",
  "state_version": 1042,
  "verdict": "uncertain",
  "impact_metrics": {
    "latency_delta_ms": 25,
    "failed_paths": 0,
    "reachability_change": "none",
    "affected_services": ["core-api"],
    "utilisation_delta_percent": 12
  },
  "mitigations": [
    {
      "description": "Resolve degraded network state before executing scale_bandwidth to improve simulation confidence",
      "action_modification": null
    }
  ],
  "rollback_feasibility": {
    "feasible": true,
    "estimated_rollback_duration_ms": 3000,
    "rollback_complexity": "medium",
    "notes": null
  },
  "simulation_rules_applied": ["SIM-004", "SIM-005"],
  "simulated_at": "2026-04-07T10:00:04Z"
}
```

---

## Appendix B: Change History

| Version | Date       | Author             | Description   |
|---------|------------|--------------------|---------------|
| 0.1.0   | 2026-04-07 | ANIF Working Group | Initial draft |
