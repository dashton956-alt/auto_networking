# ANIF-403: Closed-Loop Feedback and Learning

| Field        | Value                              |
|--------------|------------------------------------|
| Doc ID       | ANIF-403                           |
| Series       | Operations                         |
| Version      | 0.1.0                              |
| Status       | Draft                              |
| Authors      | ANIF Working Group                 |
| Reviewers    | —                                  |
| Approved by  | —                                  |
| Created      | 2026-04-07                         |
| Last updated | 2026-04-07                         |
| Replaces     | N/A                                |
| Related docs | ANIF-400, ANIF-407, ANIF-107       |

---

## Abstract

This document defines the closed-loop feedback and learning requirements for ANIF-conformant deployments. The feedback subsystem analyses execution outcomes to surface tuning suggestions for policies and thresholds. A central principle of this document is that no suggestion is ever auto-applied: all suggestions MUST be reviewed and accepted or rejected by a human operator (P-06, P-12). This document specifies the feedback pipeline, the suggestion data model, false positive detection, confidence scoring, the deterministic analysis algorithm, and the audit requirements for accepted or rejected suggestions.

---

## 1. Introduction

### 1.1 Purpose

This document establishes normative requirements for the closed-loop feedback subsystem. The purpose of the feedback subsystem is to enable continuous operational improvement by:

1. Identifying patterns in execution outcomes that suggest policy thresholds are miscalibrated.
2. Detecting over-escalation (false positives) where the system requests human review for actions that are routinely approved unchanged.
3. Generating specific, actionable tuning suggestions for human review.
4. Maintaining a human-controlled improvement loop so that no parameter changes are applied without explicit operator consent.

### 1.2 Scope

This document covers:

- The feedback pipeline stages from outcome capture to human review.
- The feedback analysis API (`GET /feedback/analysis`, `POST /feedback/accept/{id}`, `POST /feedback/reject/{id}`).
- The suggestion data model and confidence scoring.
- False positive detection logic.
- Frequent failure pattern detection.
- The deterministic analysis algorithm.
- Audit requirements for suggestion lifecycle events.
- The constraint that suggestions are never auto-applied.

### 1.3 Out of Scope

- Machine learning models for trend detection (permitted at higher maturity levels but not required in the prototype).
- Automatic application of accepted suggestions to the live policy engine (out of scope for prototype; logged as suggestion acceptance only).
- Integration with external ITSM tooling.
- Policy authoring and update workflows (covered in ANIF-103).

### 1.4 Intended Audience

| Audience                     | Usage                                                            |
|------------------------------|------------------------------------------------------------------|
| Network Operations Engineers | Reviewing and acting on tuning suggestions                       |
| Automation Engineers         | Implementing the feedback analysis algorithm                     |
| Governance and Compliance    | Auditing the suggestion lifecycle                                |
| Architecture Teams           | Understanding feedback data flows and dependencies               |

---

## 2. Normative References

- ANIF-107: Audit and Immutable Logging Standard
- ANIF-400: Operations Overview
- ANIF-401: Observability Standard
- ANIF-402: Explainability Requirements
- ANIF-407: Dark NOC Maturity Model
- RFC 2119: Key words for use in RFCs to Indicate Requirement Levels

---

## 3. Terms and Definitions

| Term                  | Definition                                                                                                              |
|-----------------------|-------------------------------------------------------------------------------------------------------------------------|
| Feedback Pipeline     | The sequence of stages by which execution outcomes are collected, analysed, and surfaced as suggestions.               |
| Suggestion            | A specific, human-reviewable proposal to adjust a policy condition or numeric threshold.                               |
| False Positive        | An escalation to manual_review that was subsequently approved without any change to the proposed action.               |
| Over-escalation       | A pattern where a disproportionate fraction of escalations are false positives, indicating thresholds may be too low.  |
| Confidence Level      | A categorical assessment (low/medium/high) of the reliability of a tuning suggestion.                                 |
| Suggestion Acceptance | An operator action explicitly approving a suggestion, recorded in the audit log.                                       |
| Suggestion Rejection  | An operator action explicitly declining a suggestion, recorded in the audit log.                                       |
| P-06                  | ANIF Principle 6: Human override is absolute.                                                                           |
| P-12                  | ANIF Principle 12: No automated parameter change without human review and explicit acceptance.                          |

---

## 4. Closed-Loop Feedback Requirements

### 4.1 Feedback Pipeline Overview

The feedback pipeline consists of the following stages, executed in order:

```
Stage 1: Outcome Capture
   ↓ Execution outcomes written to audit log (ANIF-401, ANIF-107)

Stage 2: Feedback Analysis
   ↓ GET /feedback/analysis analyses last N audit records
   ↓ Deterministic algorithm computes patterns
   ↓ Suggestions generated and stored

Stage 3: Human Review
   ↓ Operator reviews suggestions via dashboard or API
   ↓ POST /feedback/accept/{id} OR POST /feedback/reject/{id}

Stage 4: Outcome Recording
   ↓ Acceptance or rejection logged to audit (ANIF-107)
   ↓ (Prototype) Policy change is NOT automatically applied
   ↓ (Prototype) Acceptance logged as suggestion_accepted event for future manual policy update
```

### 4.2 No Auto-Application Constraint

In accordance with ANIF Principles P-06 and P-12:

1. Suggestions MUST NEVER be automatically applied to the live policy engine or risk scoring parameters.
2. Every suggestion MUST remain in `pending` status until explicitly accepted or rejected by a human operator with the `network_engineer` role or above.
3. The feedback analysis system MUST NOT modify any policy condition, threshold, or weight without an explicit human acceptance action.
4. Even when a suggestion has confidence=high, the system MUST NOT apply it automatically.

This constraint applies at all maturity levels including Level 4. The autonomy granted at higher maturity levels applies to network action execution, not to policy parameter changes.

### 4.3 Feedback Analysis Endpoint

`GET /feedback/analysis`

Analyses the last N pipeline executions and returns detected patterns and tuning suggestions.

**Query Parameters:**

| Parameter   | Type    | Required | Default | Description                                     |
|-------------|---------|----------|---------|-------------------------------------------------|
| n           | integer | No       | 50      | Number of most recent executions to analyse     |
| environment | string  | No       | all     | Filter to a specific environment (prod/staging) |
| min_confidence | string | No    | low     | Minimum confidence level to include (low/medium/high) |

**Response Schema:**

```json
{
  "analysis_id":            "<UUID v4>",
  "analysed_at":            "<ISO 8601 datetime>",
  "execution_window":       { "from": "<ISO 8601>", "to": "<ISO 8601>" },
  "executions_analysed":    50,
  "false_positive_rate":    0.18,
  "block_rate":             0.07,
  "frequent_policy_failures": [
    {
      "policy_id":           "pci_compliant",
      "failure_count":       12,
      "failure_rate":        0.24,
      "sample_intent_ids":   ["<UUID>", "<UUID>"]
    }
  ],
  "suggested_tuning":       [
    {
      "suggestion_id":       "<UUID v4>",
      "type":                "threshold",
      "target":              "risk_score_manual_review_threshold",
      "current_value":       70,
      "suggested_value":     80,
      "rationale":           "18% of escalations in the last 50 executions were approved without change. This indicates the manual_review threshold of 70 may be triggering over-escalation. Raising to 80 would reduce false positives based on the observed risk score distribution.",
      "confidence":          "medium",
      "supporting_evidence": "9 out of 50 executions had risk_score between 70 and 79 and were approved without change.",
      "status":              "pending",
      "created_at":          "<ISO 8601 datetime>"
    }
  ]
}
```

**HTTP Status Codes:**

| Condition                  | HTTP Status | Response                                    |
|----------------------------|-------------|---------------------------------------------|
| Analysis successful        | 200         | Full response body                          |
| Insufficient data (< 10 executions) | 200 | Body with `"suggestions": []` and warning  |
| Server error               | 500         | `{"error": "internal_server_error"}`        |

### 4.4 Suggestion Data Model

Each suggestion MUST contain the following fields:

| Field                | Type               | Required | Description                                                                   |
|----------------------|--------------------|----------|-------------------------------------------------------------------------------|
| suggestion_id        | UUID v4            | Yes      | Globally unique identifier for this suggestion                                |
| type                 | string             | Yes      | One of: `threshold`, `policy_condition`                                       |
| target               | string             | Yes      | The specific threshold name or policy condition being suggested for adjustment |
| current_value        | any                | Yes      | The current configured value of the target                                    |
| suggested_value      | any                | Yes      | The proposed new value                                                        |
| rationale            | string             | Yes      | Plain-English explanation of why this adjustment is suggested                 |
| confidence           | string             | Yes      | One of: `low`, `medium`, `high`                                               |
| supporting_evidence  | string             | Yes      | Description of the data pattern that supports this suggestion                 |
| status               | string             | Yes      | One of: `pending`, `accepted`, `rejected`                                     |
| created_at           | ISO 8601 datetime  | Yes      | When this suggestion was generated                                            |
| reviewed_at          | ISO 8601 datetime  | No       | When this suggestion was accepted or rejected (null if pending)               |
| reviewed_by          | string             | No       | operator_id of the reviewer (null if pending)                                 |
| rejection_reason     | string             | No       | Required if status=rejected; the operator's stated reason                     |

### 4.5 False Positive Detection

False positives are defined as manual_review escalations that were subsequently approved without any change to the proposed action.

#### 4.5.1 Detection Algorithm

The feedback analysis system MUST detect false positives as follows:

1. Query the audit log for all executions in the analysis window where `governance_mode = manual_review`.
2. For each such execution, check whether the corresponding approval ticket was approved with no modification to the original intent.
3. Compute `false_positive_rate = count(unmodified_approvals) / count(manual_review_escalations)`.
4. If `false_positive_rate > 0.15`, generate a suggestion of type `threshold` recommending evaluation of the risk score threshold.
5. If `false_positive_rate > 0.30`, set suggestion confidence to `high`.
6. If `false_positive_rate` is between `0.15` and `0.30`, set suggestion confidence to `medium`.
7. If fewer than 10 executions are available for analysis, suppress false positive suggestions and include a warning in the response.

#### 4.5.2 False Positive Rate Reporting

- The `false_positive_rate` field in the analysis response MUST always be computed and returned, regardless of whether a suggestion is generated.
- Trending false positive rate MUST be available in the observability dashboard (ANIF-401).

### 4.6 Frequent Failure Pattern Detection

The feedback analysis system MUST detect frequent policy failures as follows:

1. Query the audit log for all executions in the analysis window where any policy evaluation resulted in `outcome: fail`.
2. Group failures by `policy_id`.
3. For each policy with a `failure_rate > 0.10` (fails in more than 10% of analysed executions), include it in `frequent_policy_failures`.
4. For any policy in `frequent_policy_failures` with `failure_rate > 0.20`, generate a suggestion of type `policy_condition` recommending review of that policy's conditions and thresholds.
5. Set confidence based on the number of executions supporting the pattern:
   - `low`: pattern observed in fewer than 5 executions.
   - `medium`: pattern observed in 5–19 executions.
   - `high`: pattern observed in 20 or more executions.

### 4.7 Suggestion Confidence Levels

| Confidence | Definition                                                                            |
|------------|---------------------------------------------------------------------------------------|
| low        | Pattern observed in a single occurrence or fewer than 5 executions; may be noise.   |
| medium     | Emerging pattern observed in 5–19 executions; warrants attention but not urgent.    |
| high       | Consistent pattern observed over 20 or more executions; strong signal for review.   |

- Confidence levels are informational; they assist the operator in prioritising review.
- Confidence level MUST NOT be used by the system to auto-apply a suggestion.

### 4.8 Accepting a Suggestion

`POST /feedback/accept/{suggestion_id}`

**Path Parameters:**

| Parameter     | Type    | Required | Description                    |
|---------------|---------|----------|--------------------------------|
| suggestion_id | UUID v4 | Yes      | The suggestion to accept       |

**Request Body:**

```json
{
  "operator_id":  "<string — authenticated operator identity>",
  "notes":        "<string — optional notes from the reviewing operator>"
}
```

**Behaviour:**

1. The system MUST validate that the suggestion exists and is in `pending` status.
2. The system MUST update the suggestion status to `accepted`.
3. The system MUST write an audit record with `event_type: audit`, `stage: feedback`, and `outcome: suggestion_accepted`.
4. The system MUST NOT modify any policy, threshold, or parameter as a result of this call (prototype constraint).
5. The response MUST confirm the acceptance and remind the operator that actual policy changes require a separate manual update workflow.

**Response:**

```json
{
  "suggestion_id":   "<UUID v4>",
  "status":          "accepted",
  "accepted_by":     "<operator_id>",
  "accepted_at":     "<ISO 8601 datetime>",
  "audit_record_id": "<string>",
  "note":            "Suggestion accepted and logged. Actual policy parameter change requires a separate policy update workflow. No automated changes have been applied."
}
```

### 4.9 Rejecting a Suggestion

`POST /feedback/reject/{suggestion_id}`

**Request Body:**

```json
{
  "operator_id":       "<string — authenticated operator identity>",
  "rejection_reason":  "<string — required; the operator's reason for rejection>"
}
```

**Behaviour:**

1. The system MUST validate that the suggestion exists and is in `pending` status.
2. The `rejection_reason` field MUST be present and non-empty; rejection without a reason MUST be refused with HTTP 400.
3. The system MUST update the suggestion status to `rejected`.
4. The system MUST write an audit record with `event_type: audit`, `stage: feedback`, and `outcome: suggestion_rejected`.

### 4.10 Feedback Analysis Algorithm

The feedback analysis algorithm MUST be deterministic. The same input data (audit log records over the same time window) MUST produce the same suggestions and confidence values. Specifically:

- The algorithm MUST NOT use random number generation, probabilistic models, or machine learning inference.
- The algorithm MUST operate exclusively on data in the ANIF audit log.
- The algorithm MUST be reproducible: running the analysis twice on the same data MUST yield identical output.
- Operators MUST be able to verify analysis results by independently querying the audit log.

Non-deterministic ML-based trend detection is permitted as an optional enhancement at Level 3 and above but MUST supplement rather than replace the deterministic algorithm.

### 4.11 Suggestion Review Schedule

- Pending suggestions SHOULD NOT remain unreviewed for more than 7 days.
- The observability dashboard MUST display the count and age of unreviewed pending suggestions.
- If any suggestion remains pending for more than 7 days, an alert MUST be generated (severity: Warning).

---

## 5. Conformance Requirements

1. An ANIF deployment MUST implement `GET /feedback/analysis`.
2. An ANIF deployment MUST implement `POST /feedback/accept/{suggestion_id}` and `POST /feedback/reject/{suggestion_id}`.
3. Suggestions MUST NEVER be automatically applied; the no-auto-application constraint is mandatory at all maturity levels.
4. The feedback analysis algorithm MUST be deterministic as defined in Section 4.10.
5. Every suggestion acceptance and rejection MUST generate an audit record.
6. The `rejection_reason` field MUST be required when rejecting a suggestion.

---

## 6. Security Considerations

- The `/feedback/accept` and `/feedback/reject` endpoints MUST require authentication and MUST verify that the caller has the `network_engineer` role or above.
- Suggestion data MUST NOT be modifiable after acceptance or rejection; the status transition is one-way.
- Audit records for suggestion lifecycle events MUST be append-only and tamper-evident (ANIF-107).
- The analysis endpoint MUST NOT expose individual operator identities in aggregate statistics; identities are recorded in the audit log but SHOULD be anonymised in aggregate analysis output.

---

## 7. Operational Considerations

- Feedback analysis SHOULD be run on a scheduled basis (at minimum, nightly) in addition to being available on demand.
- Analysis windows SHOULD be configurable; the default of N=50 executions is appropriate for prototype but MAY need tuning in production environments with higher throughput.
- Operators SHOULD review feedback suggestions as part of the regular operational cadence, not only reactively.
- The feedback subsystem SHOULD be monitored with the same observability standards as the main pipeline; analysis failures MUST be alerted.

---

## Appendix A: Examples

### A.1 Example Feedback Analysis Response with Suggestions

```json
{
  "analysis_id": "a1b2c3d4-0000-4000-8000-112233445566",
  "analysed_at": "2026-04-07T22:00:00.000Z",
  "execution_window": {
    "from": "2026-04-06T10:00:00.000Z",
    "to":   "2026-04-07T22:00:00.000Z"
  },
  "executions_analysed": 50,
  "false_positive_rate": 0.22,
  "block_rate": 0.06,
  "frequent_policy_failures": [
    {
      "policy_id": "no_public_exposure",
      "failure_count": 11,
      "failure_rate": 0.22,
      "sample_intent_ids": ["uuid-1", "uuid-2", "uuid-3"]
    }
  ],
  "suggested_tuning": [
    {
      "suggestion_id": "sug-0001-aaaa-bbbb-cccc",
      "type": "threshold",
      "target": "risk_score_manual_review_threshold",
      "current_value": 70,
      "suggested_value": 75,
      "rationale": "22% of escalations in the last 50 executions were approved without modification. This rate exceeds the 15% false positive threshold. Raising the manual_review threshold from 70 to 75 is suggested to reduce unnecessary escalations.",
      "confidence": "medium",
      "supporting_evidence": "11 out of 50 executions had risk_score 70–74 and were approved without change.",
      "status": "pending",
      "created_at": "2026-04-07T22:00:01.000Z"
    }
  ]
}
```

---

## Appendix B: Change History

| Version | Date       | Author             | Change                    |
|---------|------------|--------------------|---------------------------|
| 0.1.0   | 2026-04-07 | ANIF Working Group | Initial draft             |
