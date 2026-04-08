# ANIF-601: Worked Examples

| Field        | Value                                              |
|--------------|----------------------------------------------------|
| Doc ID       | ANIF-601                                           |
| Series       | Annex                                              |
| Version      | 0.1.0                                              |
| Status       | Draft                                              |
| Authors      | ANIF Working Group                                 |
| Reviewers    | —                                                  |
| Approved by  | —                                                  |
| Created      | 2026-04-07                                         |
| Last updated | 2026-04-07                                         |
| Replaces     | N/A                                                |
| Related docs | ANIF-301, ANIF-302, ANIF-303, ANIF-304, ANIF-305  |

---

## Abstract

This document provides complete, end-to-end worked examples of the ANIF pipeline. Each example presents a realistic scenario with the full JSON bodies of every request and response at every pipeline stage, from initial intent submission through to audit retrieval. Examples are designed to be directly usable as test fixtures.

---

## 1. Introduction

### 1.1 Purpose

Abstract pipeline descriptions are necessary but not sufficient for implementors. This document bridges the gap by showing exactly what flows through the pipeline in four representative scenarios:

1. Happy path — all stages pass, execution succeeds.
2. Policy failure — intent fails policy evaluation and is escalated.
3. High-risk block — risk score exceeds the block threshold and the pipeline halts.
4. Policy conflict — two policies contain contradictory rules; conflict resolution is applied.

### 1.2 Conventions Used

All HTTP examples show the method, path, request body (where applicable), and the full response envelope. Timestamps are fixed for readability. UUIDs are shortened to illustrative values. All responses follow the standard ANIF envelope:

```json
{
  "status": "ok|error",
  "data": {},
  "errors": [],
  "trace_id": "trace-XXXXXXXX"
}
```

### 1.3 Pipeline Stage Order

The standard pipeline order is:

```
1. POST /validate-intent
2. POST /evaluate-policy
3. POST /score-risk
4. POST /decide
5. POST /governance/check
6. POST /execute
```

The orchestrator at `POST /orchestrate` runs these stages sequentially and returns a summary. Each stage writes an audit record before returning.

---

## 2. Normative References

- ANIF-301: Intent Validation
- ANIF-302: Policy Engine
- ANIF-303: Risk Scoring
- ANIF-304: Decision Engine
- ANIF-305: Governance Gate
- ANIF-600: Schema Reference

---

## 3. Terms and Definitions

**Happy path** — a pipeline execution in which all stages complete with `success` or `allow` outcomes and execution proceeds without human intervention.

**Escalation** — a pipeline outcome in which human approval is required before execution may proceed.

**Halt** — a pipeline outcome in which execution is permanently blocked and no further stages are run.

**Dry run** — a pipeline execution in which all stages are simulated but the execution stage does not apply changes to network state.

---

## 4. Example 1: Happy Path — Payments Service (prod, EU, pci_compliant)

### 4.1 Scenario Description

An operator submits a high-priority intent for the payments service in the EU production environment. The intent requests low latency, high availability, encryption, and compliance with zero trust and PCI DSS policies. All stages pass. Execution succeeds.

### 4.2 Intent Submission

**Request:**
```
POST /validate-intent
Content-Type: application/json
```

```json
{
  "service": "payments",
  "environment": "prod",
  "objectives": {
    "latency_ms": 50,
    "availability_percent": 99.99,
    "throughput_mbps": 500
  },
  "constraints": {
    "region": "EU",
    "encryption": true,
    "allowed_zones": ["zone-a", "zone-b"]
  },
  "policies": ["zero_trust", "pci_compliant"],
  "priority": "critical"
}
```

**Response — HTTP 200:**
```json
{
  "status": "ok",
  "data": {
    "intent_id": "a1b2c3d4-0001-0001-0001-000000000001",
    "valid": true,
    "validation_warnings": [],
    "schema_version": "1.0.0"
  },
  "errors": [],
  "trace_id": "trace-00000001"
}
```

### 4.3 Policy Evaluation

**Request:**
```
POST /evaluate-policy
Content-Type: application/json
```

```json
{
  "intent_id": "a1b2c3d4-0001-0001-0001-000000000001",
  "intent": {
    "service": "payments",
    "environment": "prod",
    "objectives": {
      "latency_ms": 50,
      "availability_percent": 99.99,
      "throughput_mbps": 500
    },
    "constraints": {
      "region": "EU",
      "encryption": true,
      "allowed_zones": ["zone-a", "zone-b"]
    },
    "policies": ["zero_trust", "pci_compliant"],
    "priority": "critical"
  }
}
```

**Response — HTTP 200:**
```json
{
  "status": "ok",
  "data": {
    "intent_id": "a1b2c3d4-0001-0001-0001-000000000001",
    "passed": true,
    "violations": [],
    "warnings": [],
    "policies_evaluated": [
      {
        "policy": "zero_trust",
        "result": "allow",
        "rules_matched": [
          {"condition": "constraints.encryption:equals:true", "action": "allow"}
        ]
      },
      {
        "policy": "pci_compliant",
        "result": "allow",
        "rules_matched": [
          {"condition": "constraints.encryption:equals:true", "action": "allow"},
          {"condition": "constraints.region:in_list:EU,US", "action": "allow"},
          {"condition": "environment:equals:prod", "action": "allow"}
        ]
      }
    ]
  },
  "errors": [],
  "trace_id": "trace-00000002"
}
```

### 4.4 Risk Scoring

Risk factors evaluated:

| Factor                   | Condition met?                         | Weight |
|--------------------------|----------------------------------------|--------|
| Production environment   | environment = prod                     | +30    |
| Degraded network signal  | Telemetry: healthy                     | +0     |
| Isolate segment action   | No isolate_segment recommended yet     | +0     |
| Policy failure           | No policy violations                   | +0     |
| Critical priority        | priority = critical                    | +5     |
| High availability target | availability_percent = 99.99 >= 99.9   | +5     |

**Total risk_score: 40**. Default thresholds: warn=40, block=70. Score equals warn threshold → `warn`.

**Request:**
```
POST /score-risk
Content-Type: application/json
```

```json
{
  "intent_id": "a1b2c3d4-0001-0001-0001-000000000001",
  "intent": { "...": "same as above" },
  "policy_result": { "passed": true, "violations": [] }
}
```

**Response — HTTP 200:**
```json
{
  "status": "ok",
  "data": {
    "intent_id": "a1b2c3d4-0001-0001-0001-000000000001",
    "risk_score": 40,
    "trust_score": 78,
    "safety_decision": "warn",
    "justification": [
      "prod environment: +30",
      "critical priority: +5",
      "high availability target (99.99%): +5"
    ],
    "threshold_applied": {
      "warn_threshold": 40,
      "block_threshold": 70,
      "profile": "default"
    }
  },
  "errors": [],
  "trace_id": "trace-00000003"
}
```

### 4.5 Decision

The decision engine receives a `warn` safety decision. For a `warn` outcome on a `critical` priority intent, the decision engine resolves to `auto_approve` with warnings recorded, rather than escalating — this is the `critical` priority override rule.

**Request:**
```
POST /decide
Content-Type: application/json
```

```json
{
  "intent_id": "a1b2c3d4-0001-0001-0001-000000000001",
  "safety_decision": "warn",
  "risk_score": 40,
  "trust_score": 78,
  "policy_passed": true,
  "priority": "critical"
}
```

**Response — HTTP 200:**
```json
{
  "status": "ok",
  "data": {
    "intent_id": "a1b2c3d4-0001-0001-0001-000000000001",
    "mode": "auto_approve",
    "recommended_action": {
      "action_type": "apply_qos",
      "parameters": {
        "policy_name": "latency-priority",
        "bandwidth_limit_mbps": 500
      },
      "risk_level": "medium"
    },
    "rationale": "Risk at warn threshold but priority=critical triggers auto_approve override. Warnings noted.",
    "warnings": [
      "Risk score at warn boundary (40/40). Monitor execution closely."
    ]
  },
  "errors": [],
  "trace_id": "trace-00000004"
}
```

### 4.6 Governance Check

**Request:**
```
POST /governance/check
Content-Type: application/json
```

```json
{
  "intent_id": "a1b2c3d4-0001-0001-0001-000000000001",
  "decision_mode": "auto_approve",
  "risk_score": 40,
  "priority": "critical"
}
```

**Response — HTTP 200:**
```json
{
  "status": "ok",
  "data": {
    "intent_id": "a1b2c3d4-0001-0001-0001-000000000001",
    "governance_result": "approved",
    "ticket_id": null,
    "approved_by": "system:auto",
    "conditions": []
  },
  "errors": [],
  "trace_id": "trace-00000005"
}
```

### 4.7 Execution

**Request:**
```
POST /execute
Content-Type: application/json
```

```json
{
  "intent_id": "a1b2c3d4-0001-0001-0001-000000000001",
  "action": {
    "action_type": "apply_qos",
    "parameters": {
      "policy_name": "latency-priority",
      "bandwidth_limit_mbps": 500
    },
    "risk_level": "medium"
  },
  "dry_run": false
}
```

**Response — HTTP 200:**
```json
{
  "status": "ok",
  "data": {
    "execution_id": "exec-00000001",
    "intent_id": "a1b2c3d4-0001-0001-0001-000000000001",
    "outcome": "success",
    "adapter": "mock_qos_adapter",
    "applied_at": "2026-04-07T14:32:05.012Z",
    "rollback_available": true
  },
  "errors": [],
  "trace_id": "trace-00000006"
}
```

### 4.8 Orchestrate — Full Pipeline Summary

**Request:**
```
POST /orchestrate
Content-Type: application/json
```

```json
{
  "intent": {
    "service": "payments",
    "environment": "prod",
    "objectives": {
      "latency_ms": 50,
      "availability_percent": 99.99,
      "throughput_mbps": 500
    },
    "constraints": {
      "region": "EU",
      "encryption": true,
      "allowed_zones": ["zone-a", "zone-b"]
    },
    "policies": ["zero_trust", "pci_compliant"],
    "priority": "critical"
  },
  "dry_run": false
}
```

**Response — HTTP 200:**
```json
{
  "status": "ok",
  "data": {
    "intent_id": "a1b2c3d4-0001-0001-0001-000000000001",
    "pipeline_outcome": "success",
    "stages": [
      {"stage": "intent_validation", "outcome": "success", "duration_ms": 8},
      {"stage": "policy_evaluation", "outcome": "success", "duration_ms": 12},
      {"stage": "risk_scoring",      "outcome": "success", "duration_ms": 6},
      {"stage": "decision",          "outcome": "success", "duration_ms": 4},
      {"stage": "governance",        "outcome": "success", "duration_ms": 3},
      {"stage": "execution",         "outcome": "success", "duration_ms": 45}
    ],
    "execution_id": "exec-00000001",
    "total_duration_ms": 78
  },
  "errors": [],
  "trace_id": "trace-00000007"
}
```

### 4.9 Audit Why — GET /audit/{intent_id}/why

```
GET /audit/a1b2c3d4-0001-0001-0001-000000000001/why
```

**Response — HTTP 200:**
```json
{
  "status": "ok",
  "data": {
    "intent_id": "a1b2c3d4-0001-0001-0001-000000000001",
    "narrative": [
      "STAGE 1 — intent_validation (success, 8ms): Intent structure validated against intent_schema. All required fields present. No constraint violations.",
      "STAGE 2 — policy_evaluation (success, 12ms): zero_trust: encryption=true satisfies all rules. pci_compliant: encryption=true and region=EU satisfy all rules. Both policies passed.",
      "STAGE 3 — risk_scoring (success, 6ms): Base score 0. prod environment +30. critical priority +5. High availability target +5. Total: 40. Threshold warn=40, block=70. Decision: warn (score equals warn threshold).",
      "STAGE 4 — decision (success, 4ms): safety_decision=warn. priority=critical triggers auto_approve override. Recommended action: apply_qos with latency-priority profile.",
      "STAGE 5 — governance (success, 3ms): Decision mode auto_approve. No human approval required. System auto-approved.",
      "STAGE 6 — execution (success, 45ms): Mock QoS adapter applied latency-priority policy. Execution confirmed. Rollback registered."
    ]
  },
  "errors": [],
  "trace_id": "trace-00000008"
}
```

---

## 5. Example 2: Policy Failure — PCI Compliant + Encryption Disabled

### 5.1 Scenario Description

An operator submits an intent for the payments service with encryption disabled. This violates the `pci_compliant` policy. The pipeline escalates to manual review.

### 5.2 Intent Submission

**Request:**
```
POST /validate-intent
Content-Type: application/json
```

```json
{
  "service": "payments",
  "environment": "prod",
  "objectives": {
    "latency_ms": 100,
    "availability_percent": 99.5
  },
  "constraints": {
    "region": "EU",
    "encryption": false
  },
  "policies": ["pci_compliant"],
  "priority": "high"
}
```

**Response — HTTP 200:** Intent is structurally valid (encryption:false is a valid boolean).
```json
{
  "status": "ok",
  "data": {
    "intent_id": "a1b2c3d4-0002-0002-0002-000000000002",
    "valid": true,
    "validation_warnings": [],
    "schema_version": "1.0.0"
  },
  "errors": [],
  "trace_id": "trace-00000010"
}
```

### 5.3 Policy Evaluation — Failure

```
POST /evaluate-policy
```

**Response — HTTP 200** (policy failure does not return HTTP 4xx; the API returns 200 with `passed: false`):
```json
{
  "status": "ok",
  "data": {
    "intent_id": "a1b2c3d4-0002-0002-0002-000000000002",
    "passed": false,
    "violations": [
      {
        "policy": "pci_compliant",
        "rule": "constraints.encryption:equals:false",
        "triggered_action": "deny",
        "message": "PCI DSS requires encryption in transit. constraints.encryption must be true."
      }
    ],
    "warnings": [],
    "policies_evaluated": [
      {
        "policy": "pci_compliant",
        "result": "deny",
        "rules_matched": [
          {
            "condition": "constraints.encryption:equals:false",
            "action": "deny"
          }
        ]
      }
    ]
  },
  "errors": [],
  "trace_id": "trace-00000011"
}
```

### 5.4 Risk Scoring — With Policy Failure

Risk factors:

| Factor                | Condition                        | Weight |
|-----------------------|----------------------------------|--------|
| Production environment| environment = prod               | +30    |
| Policy failure        | pci_compliant denied             | +15    |

**Total risk_score: 45**. Default thresholds: warn=40, block=70. Decision: `warn`.

**Response:**
```json
{
  "status": "ok",
  "data": {
    "intent_id": "a1b2c3d4-0002-0002-0002-000000000002",
    "risk_score": 45,
    "trust_score": 55,
    "safety_decision": "warn",
    "justification": [
      "prod environment: +30",
      "policy_failure (pci_compliant): +15"
    ],
    "threshold_applied": {
      "warn_threshold": 40,
      "block_threshold": 70,
      "profile": "default"
    }
  },
  "errors": [],
  "trace_id": "trace-00000012"
}
```

### 5.5 Decision — Manual Review

The decision engine receives `safety_decision: warn` AND `policy_passed: false`. Policy failure always overrides the critical priority auto_approve rule. The engine sets `mode: manual_review`.

**Response:**
```json
{
  "status": "ok",
  "data": {
    "intent_id": "a1b2c3d4-0002-0002-0002-000000000002",
    "mode": "manual_review",
    "recommended_action": null,
    "rationale": "Policy violation detected (pci_compliant denied). Manual review required regardless of priority. Operator must resolve encryption constraint before re-submission or explicitly approve via governance.",
    "warnings": [
      "constraints.encryption=false violates pci_compliant policy",
      "Risk score 45 is above warn threshold"
    ]
  },
  "errors": [],
  "trace_id": "trace-00000013"
}
```

### 5.6 Governance — Escalation Ticket Created

```
POST /governance/check
```

```json
{
  "intent_id": "a1b2c3d4-0002-0002-0002-000000000002",
  "decision_mode": "manual_review",
  "risk_score": 45,
  "priority": "high"
}
```

**Response — HTTP 200:**
```json
{
  "status": "ok",
  "data": {
    "intent_id": "a1b2c3d4-0002-0002-0002-000000000002",
    "governance_result": "pending",
    "ticket_id": "GOV-00045",
    "approved_by": null,
    "escalated_to": "network-ops-team",
    "conditions": [
      "Operator must confirm encryption exemption is intentional and approved by CISO.",
      "If approved, intent must be re-submitted with policy_override flag."
    ],
    "expires_at": "2026-04-08T14:32:00.000Z"
  },
  "errors": [],
  "trace_id": "trace-00000014"
}
```

### 5.7 Pipeline Summary from /orchestrate

```json
{
  "status": "ok",
  "data": {
    "intent_id": "a1b2c3d4-0002-0002-0002-000000000002",
    "pipeline_outcome": "escalated",
    "halted_at": null,
    "stages": [
      {"stage": "intent_validation", "outcome": "success",   "duration_ms": 7},
      {"stage": "policy_evaluation", "outcome": "failure",   "duration_ms": 11},
      {"stage": "risk_scoring",      "outcome": "success",   "duration_ms": 5},
      {"stage": "decision",          "outcome": "escalated", "duration_ms": 4},
      {"stage": "governance",        "outcome": "escalated", "duration_ms": 8}
    ],
    "execution_id": null,
    "ticket_id": "GOV-00045",
    "total_duration_ms": 35
  },
  "errors": [],
  "trace_id": "trace-00000015"
}
```

### 5.8 Operator Actions

To approve: `POST /governance/approve/GOV-00045`

To reject: `POST /governance/reject/GOV-00045`

**Approve response:**
```json
{
  "status": "ok",
  "data": {
    "ticket_id": "GOV-00045",
    "outcome": "approved",
    "approved_by": "operator:alice",
    "approved_at": "2026-04-07T16:00:00.000Z",
    "note": "CISO exemption reference: EXEMPT-2026-0042. Proceeding with monitoring."
  },
  "errors": [],
  "trace_id": "trace-00000016"
}
```

---

## 6. Example 3: High-Risk Block — Prod + Degraded Network + Isolate Segment

### 6.1 Scenario Description

The orchestrator is evaluating an intent that requires isolating a network segment in the production environment. Telemetry signals indicate the network is in a degraded state. The cumulative risk score exceeds the block threshold; the pipeline halts permanently.

### 6.2 Intent Submission

```json
{
  "service": "core-routing",
  "environment": "prod",
  "objectives": {
    "availability_percent": 99.0
  },
  "constraints": {
    "region": "EU",
    "encryption": true,
    "allowed_zones": ["zone-a"]
  },
  "policies": ["zero_trust"],
  "priority": "high"
}
```

**Intent ID assigned:** `a1b2c3d4-0003-0003-0003-000000000003`

Validation passes — HTTP 200 as expected.

### 6.3 Policy Evaluation — Passes

All zero_trust rules are satisfied. `passed: true`.

### 6.4 Risk Scoring — Block

Telemetry context injected by the orchestrator indicates `network_state: degraded`. The decision engine has recommended `action_type: isolate_segment` based on the service and telemetry context before risk scoring begins.

Risk factors:

| Factor                  | Condition                             | Weight |
|-------------------------|---------------------------------------|--------|
| Production environment  | environment = prod                    | +30    |
| Degraded network signal | telemetry.network_state = degraded    | +20    |
| Isolate segment action  | recommended action_type = isolate_segment | +25 |

**Total risk_score: 75**. Default thresholds: warn=40, block=70. Score 75 >= 70 → `block`.

**Request:**
```
POST /score-risk
```

```json
{
  "intent_id": "a1b2c3d4-0003-0003-0003-000000000003",
  "intent": { "...": "as above" },
  "policy_result": { "passed": true, "violations": [] },
  "telemetry_context": {
    "network_state": "degraded",
    "affected_zones": ["zone-a"]
  },
  "candidate_action": {
    "action_type": "isolate_segment",
    "parameters": { "segment_id": "seg-eu-core-01", "reason": "degraded telemetry" },
    "risk_level": "high"
  }
}
```

**Response:**
```json
{
  "status": "ok",
  "data": {
    "intent_id": "a1b2c3d4-0003-0003-0003-000000000003",
    "risk_score": 75,
    "trust_score": 60,
    "safety_decision": "block",
    "justification": [
      "prod environment: +30",
      "degraded network state (telemetry): +20",
      "isolate_segment action type: +25"
    ],
    "threshold_applied": {
      "warn_threshold": 40,
      "block_threshold": 70,
      "profile": "default"
    }
  },
  "errors": [],
  "trace_id": "trace-00000020"
}
```

### 6.5 Decision — Block

```
POST /decide
```

**Response:**
```json
{
  "status": "ok",
  "data": {
    "intent_id": "a1b2c3d4-0003-0003-0003-000000000003",
    "mode": "block",
    "recommended_action": null,
    "rationale": "Risk score 75 exceeds block threshold 70. Isolating a network segment during degraded network state carries unacceptable risk of service-wide outage. No action will be taken.",
    "warnings": []
  },
  "errors": [],
  "trace_id": "trace-00000021"
}
```

### 6.6 Pipeline Halts — No Execution

The orchestrator receives `mode: block` from the decision engine and halts. Governance and execution stages are not invoked.

**Orchestrate pipeline summary:**
```json
{
  "status": "ok",
  "data": {
    "intent_id": "a1b2c3d4-0003-0003-0003-000000000003",
    "pipeline_outcome": "blocked",
    "halted_at": "risk",
    "stages": [
      {"stage": "intent_validation", "outcome": "success", "duration_ms": 7},
      {"stage": "policy_evaluation", "outcome": "success", "duration_ms": 9},
      {"stage": "risk_scoring",      "outcome": "blocked", "duration_ms": 6},
      {"stage": "decision",          "outcome": "blocked", "duration_ms": 3}
    ],
    "execution_id": null,
    "ticket_id": null,
    "total_duration_ms": 25
  },
  "errors": [],
  "trace_id": "trace-00000022"
}
```

### 6.7 Audit Records for Stages That Ran

```
GET /audit/a1b2c3d4-0003-0003-0003-000000000003
```

**Response:**
```json
{
  "status": "ok",
  "data": {
    "intent_id": "a1b2c3d4-0003-0003-0003-000000000003",
    "records": [
      {
        "record_id": "rec-0003-0001",
        "stage": "intent_validation",
        "timestamp": "2026-04-07T15:00:00.007Z",
        "outcome": "success",
        "duration_ms": 7
      },
      {
        "record_id": "rec-0003-0002",
        "stage": "policy_evaluation",
        "timestamp": "2026-04-07T15:00:00.016Z",
        "outcome": "success",
        "duration_ms": 9
      },
      {
        "record_id": "rec-0003-0003",
        "stage": "risk_scoring",
        "timestamp": "2026-04-07T15:00:00.022Z",
        "outcome": "blocked",
        "reasoning_chain": [
          "prod environment adds 30 to risk score",
          "degraded network state adds 20 to risk score",
          "isolate_segment action type adds 25 to risk score",
          "total risk_score=75 exceeds block_threshold=70",
          "safety_decision set to block"
        ],
        "duration_ms": 6
      },
      {
        "record_id": "rec-0003-0004",
        "stage": "decision",
        "timestamp": "2026-04-07T15:00:00.025Z",
        "outcome": "blocked",
        "reasoning_chain": [
          "Received safety_decision=block from risk scoring",
          "Block decisions are final; no escalation path exists",
          "recommended_action set to null",
          "Pipeline halted"
        ],
        "duration_ms": 3
      }
    ]
  },
  "errors": [],
  "trace_id": "trace-00000023"
}
```

---

## 7. Example 4: Policy Conflict Resolution

### 7.1 Scenario Description

An intent is submitted that activates two policies. One policy mandates minimum latency (performance policy) and would allow the intent. A second policy mandates that public ingress is never allowed (security policy) and would deny the intent. The policies conflict. The conflict resolution mechanism applies the principle that security/compliance policies supersede performance policies.

### 7.2 Intent

```json
{
  "service": "api-gateway",
  "environment": "prod",
  "objectives": {
    "latency_ms": 5,
    "availability_percent": 99.9
  },
  "constraints": {
    "region": "US",
    "encryption": true
  },
  "policies": ["no_public_ingress", "zero_trust"],
  "priority": "high"
}
```

**Intent ID:** `a1b2c3d4-0004-0004-0004-000000000004`

The intent includes a load balancer configuration in its `parameters` (passed as additional orchestrator context) that enables a public-facing endpoint, which triggers the `no_public_ingress` policy.

### 7.3 Policy Evaluation — Conflict Detected

```json
{
  "status": "ok",
  "data": {
    "intent_id": "a1b2c3d4-0004-0004-0004-000000000004",
    "passed": false,
    "conflict_detected": true,
    "conflict_details": {
      "conflicting_policies": ["no_public_ingress", "zero_trust"],
      "conflict_type": "security_vs_performance",
      "description": "no_public_ingress denies the requested load-balancer configuration. zero_trust would allow it given encryption=true. These are contradictory outcomes for the same resource.",
      "resolution_applied": "security_wins",
      "resolution_rationale": "ANIF conflict resolution rule CR-01: security and compliance policy outcomes supersede performance and availability policy outcomes."
    },
    "violations": [
      {
        "policy": "no_public_ingress",
        "rule": "constraints.load_balancer_type:equals:public",
        "triggered_action": "deny",
        "message": "Public ingress is not permitted. Use an internal load balancer."
      }
    ],
    "warnings": [
      "Policy conflict detected between no_public_ingress and zero_trust. Resolved in favour of no_public_ingress (security_wins)."
    ],
    "policies_evaluated": [
      {
        "policy": "no_public_ingress",
        "result": "deny",
        "rules_matched": [
          {"condition": "constraints.load_balancer_type:equals:public", "action": "deny"}
        ]
      },
      {
        "policy": "zero_trust",
        "result": "allow",
        "rules_matched": [
          {"condition": "constraints.encryption:equals:true", "action": "allow"}
        ]
      }
    ]
  },
  "errors": [],
  "trace_id": "trace-00000030"
}
```

### 7.4 Risk Scoring After Conflict Resolution

Risk factors after resolution:

| Factor               | Condition                                   | Weight |
|----------------------|---------------------------------------------|--------|
| Production environment| environment = prod                         | +30    |
| Policy failure        | no_public_ingress denied                   | +15    |

**Total risk_score: 45**. Decision: `warn`.

### 7.5 Decision — Manual Review with Conflict Context

```json
{
  "status": "ok",
  "data": {
    "intent_id": "a1b2c3d4-0004-0004-0004-000000000004",
    "mode": "manual_review",
    "recommended_action": null,
    "rationale": "Policy conflict resolved (security_wins over zero_trust). Denial stands. Operator must change load balancer type to internal before re-submission.",
    "conflict_resolution_applied": "CR-01: security_wins",
    "warnings": [
      "Policy conflict between no_public_ingress and zero_trust was detected and resolved.",
      "Intent cannot proceed with public load balancer in prod environment."
    ]
  },
  "errors": [],
  "trace_id": "trace-00000031"
}
```

### 7.6 Audit Why — Conflict Explanation

```
GET /audit/a1b2c3d4-0004-0004-0004-000000000004/why
```

```json
{
  "status": "ok",
  "data": {
    "intent_id": "a1b2c3d4-0004-0004-0004-000000000004",
    "narrative": [
      "STAGE 1 — intent_validation (success, 6ms): Intent conforms to schema. All required fields present.",
      "STAGE 2 — policy_evaluation (failure, 14ms): Conflict detected. no_public_ingress denied the public load balancer configuration. zero_trust allowed the intent (encryption=true). Conflict resolution rule CR-01 applied: security policy (no_public_ingress) supersedes performance policy (zero_trust). Final outcome: deny.",
      "STAGE 3 — risk_scoring (success, 5ms): prod environment +30, policy_failure +15. Total: 45. Above warn threshold (40). Decision: warn.",
      "STAGE 4 — decision (escalated, 4ms): policy_passed=false and mode=manual_review. Pipeline escalated. Operator must remediate no_public_ingress violation."
    ]
  },
  "errors": [],
  "trace_id": "trace-00000032"
}
```

---

## 8. Conformance Requirements

8.1 All request bodies in worked examples conform to the schemas defined in ANIF-600.

8.2 All response envelopes use the standard `{status, data, errors, trace_id}` structure.

8.3 Pipeline outcome values (`success`, `escalated`, `blocked`) MUST match the values defined in `audit_record_schema.outcome`.

8.4 Test suites derived from these examples MUST use the exact intent structures shown and MUST assert the documented outcomes deterministically.

---

## 9. Security Considerations

9.1 Example intent objects are illustrative and contain no real service credentials, real zone identifiers, or production configuration values.

9.2 The `operator_id` in worked examples uses placeholder values (`operator:alice`). Real implementations MUST use authenticated identity tokens.

9.3 Example trace IDs and record IDs are simplified for readability. Production implementations MUST use UUID v4 values.

---

## 10. Operational Considerations

10.1 These worked examples should be encoded as integration test fixtures in `tests/fixtures/` and `tests/integration/`.

10.2 The risk score calculations in each example use the default threshold profile. Teams deploying in high-security environments should validate examples against the `strict` profile.

---

## Appendix A: Example Fixture Files

The following fixture files should be created in `tests/fixtures/`:

- `intent_payments_happy.json` — Example 1 intent
- `intent_payments_no_encryption.json` — Example 2 intent
- `intent_core_routing_degraded.json` — Example 3 intent
- `intent_api_gateway_conflict.json` — Example 4 intent

---

## Appendix B: Change History

| Version | Date       | Author             | Summary       |
|---------|------------|--------------------|---------------|
| 0.1.0   | 2026-04-07 | ANIF Working Group | Initial draft |
