# ANIF-405: Incident and Outage Modeling

| Field        | Value                              |
|--------------|------------------------------------|
| Doc ID       | ANIF-405                           |
| Series       | Operations                         |
| Version      | 0.1.0                              |
| Status       | Draft                              |
| Authors      | ANIF Working Group                 |
| Reviewers    | —                                  |
| Approved by  | —                                  |
| Created      | 2026-04-07                         |
| Last updated | 2026-04-07                         |
| Replaces     | N/A                                |
| Related docs | ANIF-400, ANIF-403, ANIF-407       |

---

## Abstract

This document defines the incident and outage modeling requirements for ANIF-conformant deployments. Incident modeling enables the system to recognise known failure patterns from telemetry, match them to pre-defined incident templates, generate candidate remediation intents for human review or autonomous execution, and verify that recovery is successful before closing the incident. This document specifies the incident classification schema, detection mechanisms, runbook mapping, scenario confidence scoring, post-incident learning integration, and recovery verification requirements.

---

## 1. Introduction

### 1.1 Purpose

This document establishes normative requirements for incident and outage modeling within ANIF systems. Incident modeling accelerates response to known failure classes by providing the pipeline with structured templates that define: what the failure looks like (telemetry signatures), what remediation actions are appropriate (runbook mapping), and how success is verified (recovery verification criteria). These templates reduce MTTR by eliminating the time required to diagnose common failures from scratch.

### 1.2 Scope

This document covers:

- The incident classification schema (severity, blast radius, type).
- Incident detection: telemetry signature matching to incident templates.
- Automated candidate intent generation for known incident types.
- Runbook mapping: incident type to candidate action types.
- Scenario confidence scoring.
- Post-incident learning and integration with ANIF-403.
- Recovery verification requirements before incident closure.
- Escalation requirements when automated recovery fails.

### 1.3 Out of Scope

- Physical incident response procedures.
- Integration with external ITSM platforms (implementation-specific).
- The intent execution pipeline itself (covered in ANIF-305).
- Governance gate and human approval for generated intents (covered in ANIF-404, ANIF-406).
- Digital twin or simulation framework implementation details.

### 1.4 Intended Audience

| Audience                     | Usage                                                              |
|------------------------------|--------------------------------------------------------------------|
| Network Operations Engineers | Understanding incident classification and automated response flow  |
| Automation Engineers         | Implementing incident detection and template matching              |
| Governance and Compliance    | Auditing incident response decisions                               |
| Architecture Teams           | Integrating incident modeling with the broader ANIF pipeline       |

---

## 2. Normative References

- ANIF-103: Governance Policy Framework
- ANIF-305: Intent Execution Pipeline
- ANIF-400: Operations Overview
- ANIF-403: Closed-Loop Feedback and Learning
- ANIF-404: Human-in-Loop Controls
- ANIF-406: Governance Controls
- ANIF-407: Dark NOC Maturity Model
- ANIF-107: Audit and Immutable Logging Standard
- RFC 2119: Key words for use in RFCs to Indicate Requirement Levels

---

## 3. Terms and Definitions

| Term                    | Definition                                                                                                       |
|-------------------------|------------------------------------------------------------------------------------------------------------------|
| Incident Template       | A pre-defined record that describes a known failure class: its telemetry signatures, classification, and runbook.|
| Telemetry Signature     | A set of observable metric or event conditions that, when matched, indicate a specific incident type.           |
| Blast Radius            | The scope of service or infrastructure affected by an incident.                                                  |
| Candidate Intent        | A system-generated intent proposal in response to a detected incident; requires human or governance approval.    |
| Runbook                 | A mapping from an incident type to one or more candidate action types that may remediate it.                     |
| Scenario Confidence     | A numeric score (0–100) indicating how closely a detected telemetry pattern matches a known incident template.   |
| Recovery Verification   | Post-remediation checks that confirm the incident condition has been resolved before closing the incident.       |
| Post-Incident Learning  | The process of recording an incident and its resolution in the feedback system (ANIF-403).                      |

---

## 4. Incident and Outage Modeling Requirements

### 4.1 Incident Classification Schema

Every incident detected or modelled by ANIF MUST be classified using the following three-dimensional schema:

#### 4.1.1 Severity

| Severity | Label      | Description                                                                   | Expected Response Time |
|----------|------------|-------------------------------------------------------------------------------|------------------------|
| P0       | Critical   | Complete service outage or critical infrastructure failure                    | Immediate (< 5 min)    |
| P1       | High       | Significant degradation affecting multiple customers or zones                 | Urgent (< 15 min)      |
| P2       | Medium     | Partial degradation affecting a subset of users or a single zone              | Standard (< 30 min)    |
| P3       | Low        | Minor anomaly or capacity concern with no immediate customer impact           | Scheduled (< 4 hr)     |

#### 4.1.2 Blast Radius

| Blast Radius | Scope                                                           |
|--------------|-----------------------------------------------------------------|
| service      | A single service or application endpoint is affected            |
| zone         | All services within a single availability zone are affected     |
| region       | All zones within a single geographic region are affected        |
| global       | Multiple regions are affected                                   |

#### 4.1.3 Type

| Type          | Description                                                             |
|---------------|-------------------------------------------------------------------------|
| connectivity  | Network path failures, BGP route withdrawal, link down events           |
| performance   | Throughput degradation, latency spike, packet loss above threshold      |
| security      | Anomalous traffic patterns, potential DDoS, policy violation detected   |
| capacity      | Bandwidth exhaustion, buffer overflow, CPU/memory saturation            |
| control_plane | Routing protocol instability, management plane unreachable              |

### 4.2 Incident Detection

#### 4.2.1 Telemetry Signature Matching

The incident detection subsystem MUST:

1. Continuously evaluate incoming telemetry streams against the registered set of incident templates.
2. Compute a scenario confidence score (0–100) for each active incident template against the current telemetry state.
3. Trigger an incident record creation when a template's confidence score reaches or exceeds the configured detection threshold (default: 70).
4. Assign a unique `incident_id` to each detected incident.
5. Write an audit record for each incident detection event.

#### 4.2.2 Telemetry Signature Specification

Each incident template MUST define its telemetry signature as a structured set of conditions. A signature MUST specify:

- The metric or event name being observed.
- The operator (e.g., >, <, =, absent).
- The threshold value or expected value.
- The duration for which the condition must persist before matching (default: 30 seconds).

**Example signature (connectivity loss on a link):**

```json
{
  "template_id":   "INC-CONN-001",
  "signature": [
    { "metric": "interface_link_state", "operator": "=", "value": "down", "duration_seconds": 30 },
    { "metric": "bgp_prefix_withdrawal_count", "operator": ">", "value": 5, "duration_seconds": 30 }
  ]
}
```

#### 4.2.3 Detection Threshold

- The detection threshold (default 70) SHOULD be configurable per incident template to allow tuning of sensitivity.
- Lowering the threshold increases sensitivity but may increase false incident detections.
- The detection threshold SHOULD be reviewed as part of post-incident learning (Section 4.6).

### 4.3 Automated Response Capability

#### 4.3.1 Candidate Intent Generation

When an incident is detected with confidence ≥ 70, the system MAY generate a candidate intent for remediation. The candidate intent MUST:

1. Reference the triggering `incident_id`.
2. Specify the action type(s) recommended by the incident template's runbook.
3. Include an `intent_source` field set to `incident_detection` to distinguish system-generated intents from operator-submitted intents.
4. Pass through the standard ANIF intent execution pipeline, including policy evaluation, risk scoring, and governance gate.

#### 4.3.2 Candidate Intent Governance

System-generated candidate intents are subject to the same governance rules as operator-submitted intents. In particular:

- A candidate intent for a P0 incident on a production segment will typically produce a high risk_score and MUST pass through the governance gate accordingly.
- At maturity Level 2, P0 candidate intents will typically require manual_review unless the action type is pre-approved as low-risk.
- At maturity Level 3 and Level 4, P0 candidate intents MAY proceed automatically if governance rules permit.

### 4.4 Runbook Mapping

The following table defines the normative mapping between incident types and candidate action types. This mapping MUST be used when generating candidate intents unless a more specific template overrides it.

| Incident Type   | Severity | Candidate Action Types                                          |
|-----------------|----------|-----------------------------------------------------------------|
| connectivity    | P0, P1   | `reroute_traffic`, `failover_to_backup_path`                   |
| connectivity    | P2, P3   | `alert_and_investigate`, `adjust_route_weight`                  |
| performance     | P0, P1   | `scale_bandwidth`, `shed_load`, `reroute_traffic`              |
| performance     | P2, P3   | `adjust_qos_policy`, `alert_and_investigate`                    |
| security        | P0       | `isolate_segment`, `block_source_prefix`                        |
| security        | P1, P2   | `rate_limit_source`, `notify_security_team`                     |
| security        | P3       | `alert_and_investigate`                                         |
| capacity        | P0, P1   | `scale_bandwidth`, `shed_low_priority_load`                     |
| capacity        | P2, P3   | `adjust_capacity_policy`, `alert_and_investigate`               |
| control_plane   | P0       | `restart_routing_process`, `failover_control_plane`             |
| control_plane   | P1, P2   | `alert_and_investigate`, `notify_noc_team`                      |

Note: `isolate_segment` MUST always trigger `manual_review` mode per ANIF-404 Rule R-01, regardless of severity or confidence score.

#### 4.4.1 Soft vs Hard Failure Variants

Each runbook entry SHOULD include variants for soft failure (degraded but recoverable) and hard failure (complete loss):

- **Hard failure variant:** More aggressive action (e.g., full failover) with higher risk_score.
- **Soft failure variant:** Conservative action (e.g., weight adjustment) with lower risk_score.

The incident template MUST specify which variant applies based on the telemetry signature severity.

### 4.5 Scenario Confidence Scoring

The scenario confidence score (0–100) represents how closely the current telemetry state matches a known incident template.

#### 4.5.1 Scoring Method

The confidence score MUST be computed as a weighted sum of matched signature conditions:

```
confidence = sum(condition_weight[i] * match_score[i]) / sum(condition_weight[i]) * 100
```

Where:
- `condition_weight[i]` is the importance weight assigned to condition `i` in the template (default: 1.0 for all conditions).
- `match_score[i]` is 1.0 if condition `i` is fully matched, 0.5 if partially matched (value within 10% of threshold), and 0.0 if not matched.

#### 4.5.2 Confidence Bands

| Confidence Score | Interpretation                                                               |
|------------------|------------------------------------------------------------------------------|
| 0–49             | Insufficient match; do not trigger incident; continue monitoring             |
| 50–69            | Low confidence; log candidate incident for awareness; do not generate intent |
| 70–84            | Moderate confidence; generate candidate intent; require governance approval  |
| 85–94            | High confidence; generate candidate intent; expedite governance review       |
| 95–100           | Very high confidence; generate candidate intent; auto-proceed at Level 3+    |

#### 4.5.3 Confidence Score in Audit Log

The confidence score MUST be included in the audit record for every incident detection event and every candidate intent generation event.

### 4.6 Post-Incident Learning

#### 4.6.1 Incident Resolution Recording

When an incident is resolved, the system MUST record the following to the feedback subsystem (ANIF-403):

1. `incident_id` and classification (severity, blast_radius, type).
2. Template that matched and its confidence score at detection time.
3. Candidate intent(s) generated and their outcomes.
4. Time from detection to resolution (MTTR contribution).
5. Whether automated remediation was successful, partially successful, or required manual escalation.

#### 4.6.2 Template Refinement

- Post-incident learning records SHOULD be reviewed as part of the regular feedback analysis cycle (ANIF-403).
- If a template consistently produces false detections (confidence ≥ 70 but incident is not confirmed), the detection threshold for that template SHOULD be raised.
- Template refinement MUST follow the same human-review constraint as other feedback suggestions (ANIF-403, Section 4.2): changes MUST NOT be auto-applied.

### 4.7 Recovery Verification

#### 4.7.1 Verification Requirement

After executing a remediation action, the system MUST verify that the incident condition is resolved before:

1. Setting the incident status to `resolved`.
2. Writing the resolution record to the feedback subsystem.
3. Closing the associated approval ticket as complete.

#### 4.7.2 Verification Method

Recovery verification MUST:

1. Re-evaluate the incident template's telemetry signature against current telemetry.
2. Confirm that the signature conditions are no longer matched (confidence score falls below 30).
3. Wait a minimum of 60 seconds after remediation action completion before performing verification, to allow telemetry to stabilise.
4. Perform up to 3 verification attempts, with 60-second intervals between attempts.

#### 4.7.3 Verification Failure

If verification fails after 3 attempts:

1. The incident status MUST remain `active` (not `resolved`).
2. The system MUST generate an escalation event and notify the on-call engineer.
3. The system MUST NOT automatically retry the same remediation action.
4. A new candidate intent MAY be generated using an alternative runbook action if the template defines one.
5. If automated recovery has already been attempted twice without success, the incident MUST be escalated to mandatory manual_review regardless of current maturity level.

### 4.8 Escalation After Recovery Failure

- If automated recovery fails twice for the same incident, all subsequent candidate intents for that incident MUST be routed through `manual_review` regardless of governance rules, risk score, or maturity level.
- This escalation override MUST be logged in the audit record with `event_type: audit` and a rationale of "Automated recovery failed twice; mandatory human review required."

---

## 5. Conformance Requirements

1. An ANIF deployment implementing incident modeling MUST implement the three-dimensional classification schema (severity, blast_radius, type) as defined in Section 4.1.
2. Every incident detection event MUST generate an audit record.
3. Candidate intents generated by the incident detection subsystem MUST pass through the full standard ANIF governance pipeline.
4. Recovery verification MUST be performed before any incident is set to `resolved` status.
5. If automated recovery fails twice, subsequent candidate intents MUST be routed to `manual_review`.
6. Post-incident data MUST be recorded to the feedback subsystem (ANIF-403).

---

## 6. Security Considerations

- Security incident types (type=security) MUST always generate a high or critical severity assessment; security incidents MUST NOT be downgraded to P3 based on confidence score alone.
- Candidate intents generated for security incidents MUST be subject to additional scrutiny; security incident intents SHOULD default to manual_review at all maturity levels except Level 4.
- Incident template data MUST be stored securely; template signatures represent knowledge of system vulnerabilities and MUST be access-controlled.
- Incident IDs MUST NOT encode information about the specific vulnerability or failure mode in plain text.

---

## 7. Operational Considerations

- The incident template library SHOULD be reviewed and updated quarterly, and after any significant infrastructure change.
- Detection threshold tuning SHOULD be informed by the false detection rate tracked in post-incident learning records.
- Organisations SHOULD conduct regular scenario injection tests (using a test environment or digital twin) to verify that templates correctly detect the failure conditions they model.
- MTTR metrics derived from incident modeling SHOULD be surfaced in the maturity model dashboard (ANIF-407) as a key progression metric.

---

## Appendix A: Examples

### A.1 Incident Template Example — Connectivity Loss

```json
{
  "template_id":     "INC-CONN-001",
  "name":            "Link Failure with BGP Route Withdrawal",
  "severity":        "P1",
  "blast_radius":    "zone",
  "type":            "connectivity",
  "detection_threshold": 70,
  "signature": [
    { "metric": "interface_link_state", "operator": "=", "value": "down", "duration_seconds": 30, "weight": 2.0 },
    { "metric": "bgp_prefix_withdrawal_count", "operator": ">", "value": 5, "duration_seconds": 30, "weight": 1.5 },
    { "metric": "traffic_drop_rate", "operator": ">", "value": 0.3, "duration_seconds": 30, "weight": 1.0 }
  ],
  "runbook": {
    "hard_failure": ["reroute_traffic", "failover_to_backup_path"],
    "soft_failure": ["adjust_route_weight", "alert_and_investigate"]
  },
  "recovery_criteria": [
    { "metric": "interface_link_state", "operator": "=", "value": "up" },
    { "metric": "traffic_drop_rate", "operator": "<", "value": 0.02 }
  ]
}
```

### A.2 Incident Lifecycle

```
1. Telemetry: interface_link_state=down for 35 seconds on core-router-01
2. Template INC-CONN-001 matches: confidence=82
3. Incident created: INC-20260407-001, severity=P1, blast_radius=zone, type=connectivity
4. Candidate intent generated: action_type=reroute_traffic, intent_source=incident_detection
5. Governance gate: risk_score=65, environment=prod, mode=auto (trust_score=75, no rule triggered)
6. Execution: reroute_traffic completed, outcome=success
7. Recovery verification (T+60s): signature re-evaluated, confidence=8 (below 30)
8. Incident resolved: status=resolved, MTTR=4m23s
9. Post-incident record written to feedback subsystem
```

---

## Appendix B: Change History

| Version | Date       | Author             | Change                    |
|---------|------------|--------------------|---------------------------|
| 0.1.0   | 2026-04-07 | ANIF Working Group | Initial draft             |
