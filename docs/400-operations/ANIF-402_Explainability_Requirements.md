# ANIF-402: Explainability Requirements

| Field        | Value                              |
|--------------|------------------------------------|
| Doc ID       | ANIF-402                           |
| Series       | Operations                         |
| Version      | 0.1.0                              |
| Status       | Draft                              |
| Authors      | ANIF Working Group                 |
| Reviewers    | —                                  |
| Approved by  | —                                  |
| Created      | 2026-04-07                         |
| Last updated | 2026-04-07                         |
| Replaces     | N/A                                |
| Related docs | ANIF-400, ANIF-401, ANIF-107       |

---

## Abstract

This document defines the explainability requirements for ANIF-conformant deployments. Explainability is the capability by which any automated decision made within the ANIF pipeline can be rendered as a clear, human-readable account of the reasoning that produced it. This document specifies: the principle that every automated decision MUST be explainable on demand (P-04); the reasoning_chain data structure; the `GET /audit/{intent_id}/why` endpoint specification; explanation format requirements; compliance use of the explainability API; and the testing requirements for explainability coverage.

---

## 1. Introduction

### 1.1 Purpose

This document establishes normative requirements for the explainability capability of ANIF systems. Explainability serves three distinct operational functions:

1. **Operator trust:** Human operators reviewing governance tickets or investigating anomalies MUST be able to understand why a system made a given decision.
2. **Compliance and audit:** Regulatory and internal audit officers MUST be able to reconstruct the full reasoning for any decision from the audit log without requiring access to the running system.
3. **Feedback and improvement:** The closed-loop feedback system (ANIF-403) relies on explainability records to identify patterns in false positives and policy failures.

### 1.2 Scope

This document covers:

- The normative requirement that every automated decision MUST be explainable.
- The `reasoning_chain` data structure and its fields.
- The `GET /audit/{intent_id}/why` endpoint specification.
- Explanation language and format requirements.
- Compliance use of explainability records.
- Testing requirements for the explainability capability.

### 1.3 Out of Scope

- The internal storage mechanism for reasoning chain data (covered by ANIF-107).
- Dashboard visualisation of reasoning chains (covered by ANIF-401).
- The feedback analysis algorithm that consumes explainability data (covered by ANIF-403).
- Authentication and authorisation for the explainability API (covered by ANIF-103).

### 1.4 Intended Audience

| Audience                     | Usage                                                                    |
|------------------------------|--------------------------------------------------------------------------|
| Network Operations Engineers | Using /why to understand governance decisions and approve/reject tickets  |
| Compliance and Audit Officers | Reconstructing decision reasoning for regulatory review                  |
| Platform Engineers           | Implementing the explainability API and reasoning chain emission          |
| Quality Assurance Engineers  | Verifying explainability coverage across pipeline outcomes               |

---

## 2. Normative References

- ANIF-107: Audit and Immutable Logging Standard
- ANIF-400: Operations Overview
- ANIF-401: Observability Standard
- ANIF-103: Governance Policy Framework
- ANIF-305: Intent Execution Pipeline
- RFC 2119: Key words for use in RFCs to Indicate Requirement Levels

---

## 3. Terms and Definitions

| Term               | Definition                                                                                                          |
|--------------------|---------------------------------------------------------------------------------------------------------------------|
| Explainability     | The property of an automated decision system by which any decision can be rendered as a human-readable rationale.   |
| Reasoning Chain    | An ordered list of decision steps representing the sequence of decisions made by the pipeline for a given intent.   |
| Decision Step      | A single entry in a reasoning_chain; records the pipeline stage, input summary, decision taken, and rationale.     |
| /why Endpoint      | The `GET /audit/{intent_id}/why` API endpoint that returns the human-readable explanation for an intent's decisions.|
| P-04               | ANIF Principle 4: Every automated decision MUST be explainable on demand.                                           |
| P-06               | ANIF Principle 6: Human override is absolute; humans may halt or reverse any automated action at any time.          |
| Compliance Reconstruction | The ability of an audit officer to reproduce the reasoning for a decision using only the audit log records.   |

---

## 4. Explainability Requirements

### 4.1 Universal Explainability Requirement

In accordance with ANIF Principle P-04, every automated decision made by an ANIF pipeline component MUST be explainable on demand.

Specifically:

1. Every policy evaluation decision MUST produce a reasoning_chain step.
2. Every risk score assignment MUST produce a reasoning_chain step explaining the contributing factors.
3. Every governance mode decision (auto, manual_review, block) MUST produce a reasoning_chain step identifying the triggering rule.
4. Every execution decision (proceed, defer, abort) MUST produce a reasoning_chain step.
5. Every rollback decision MUST produce a reasoning_chain step.
6. The complete reasoning_chain for an intent MUST be retrievable via the `/why` endpoint as long as the audit record is retained.

### 4.2 Reasoning Chain Data Structure

The `reasoning_chain` for an intent is an ordered list of `decision_step` objects. Each `decision_step` MUST contain the following fields:

```json
{
  "step_number":    "<integer — 1-based sequential index within this intent's reasoning chain>",
  "stage":          "<string — the pipeline stage that produced this step>",
  "timestamp":      "<ISO 8601 datetime — when this step was recorded>",
  "input_summary":  "<string — plain-English summary of the inputs relevant to this decision>",
  "decision":       "<string — the decision taken at this step>",
  "rationale":      "<string — plain-English explanation of why this decision was taken>",
  "policy_id":      "<string or null — the policy ID if this step relates to a policy evaluation>",
  "risk_score":     "<integer or null — the risk score if this step relates to risk assessment>",
  "outcome":        "<string — one of: pass, fail, escalate, block, execute, rollback, defer>"
}
```

#### 4.2.1 Field Requirements

- `step_number`: MUST be assigned sequentially from 1. MUST NOT be reused within a single intent's chain.
- `stage`: MUST match a registered pipeline stage name (see ANIF-401, Section 4.4.1).
- `input_summary`: MUST be a human-readable sentence or short paragraph; MUST NOT be a raw JSON dump of input parameters.
- `decision`: MUST be stated in plain English; MUST NOT be a numeric code or internal enum value.
- `rationale`: MUST explain the reason in terms an operator can act upon; see Section 4.4 for language requirements.
- `policy_id`: MUST reference the specific policy that was evaluated if applicable; MUST be `null` for non-policy steps.
- `outcome`: MUST reflect the actual outcome of this step.

### 4.3 The /why Endpoint

#### 4.3.1 Endpoint Specification

`GET /audit/{intent_id}/why`

Returns a human-readable explanation of all decisions made for the specified intent, stitched together from the reasoning chains of all pipeline stages.

**Path Parameters:**

| Parameter  | Type   | Required | Description                    |
|------------|--------|----------|--------------------------------|
| intent_id  | UUID v4 | Yes     | The identifier of the intent   |

**Query Parameters:**

| Parameter     | Type    | Required | Default | Description                                           |
|---------------|---------|----------|---------|-------------------------------------------------------|
| format        | string  | No       | json    | Response format: `json` or `text`                     |
| include_chain | boolean | No       | true    | Whether to include the full reasoning_chain array     |

**Response Schema (JSON):**

```json
{
  "intent_id":        "<UUID v4>",
  "intent_summary":   "<string — plain-English description of what the intent requested>",
  "final_outcome":    "<string — the overall outcome: executed, rejected, rolled_back, pending>",
  "explanation":      "<string — a single coherent narrative paragraph explaining the full decision sequence>",
  "reasoning_chain":  [
    {
      "step_number":   1,
      "stage":         "policy",
      "timestamp":     "2026-04-07T14:23:01.452Z",
      "input_summary": "Intent requested to update firewall rules for segment prod-42 with encryption=false.",
      "decision":      "Policy evaluation failed",
      "rationale":     "Policy pci_compliant failed because the intent specifies encryption=false, which violates the PCI-DSS encryption-in-transit requirement for production segments.",
      "policy_id":     "pci_compliant",
      "risk_score":    null,
      "outcome":       "fail"
    }
  ],
  "trace_id":         "<UUID v4>",
  "generated_at":     "<ISO 8601 datetime>"
}
```

**HTTP Status Codes:**

| Condition                  | HTTP Status | Response                            |
|----------------------------|-------------|-------------------------------------|
| Intent found, explanation available | 200 | Full response body              |
| Intent ID not found        | 404         | `{"error": "intent_not_found"}`     |
| Intent found, explanation pending | 202 | `{"status": "reasoning_chain_building"}` |
| Server error               | 500         | `{"error": "internal_server_error"}` |

#### 4.3.2 /why Endpoint Requirements

- The `/why` endpoint MUST be available for any intent whose audit records are retained.
- The `/why` endpoint MUST return a response within 2000 ms for intents with fewer than 50 reasoning chain steps.
- The `/why` endpoint MUST include all reasoning chain steps from all pipeline stages, not only the final decision.
- The `/why` endpoint MUST return meaningful content for all pipeline outcomes including: execution success, policy failure, risk escalation, governance block, approval expiry, and rollback.
- The `explanation` field MUST be a single coherent narrative that an operator with no knowledge of the internal system can read and understand.

### 4.4 Explanation Language Requirements

#### 4.4.1 Plain English Requirement

All explanation text MUST be written in plain English. The following principles apply:

1. **No internal codes:** Rationale text MUST NOT contain raw internal error codes. For example:
   - Acceptable: `"Policy pci_compliant failed because encryption=false"`
   - Not acceptable: `"POLICY_FAIL_001: enc_false"`

2. **Causal language:** Rationale MUST state the cause. For example:
   - Acceptable: `"The governance engine selected manual_review because the risk score of 72 meets or exceeds the manual review threshold of 70."`
   - Not acceptable: `"Risk threshold exceeded."`

3. **Action-oriented:** Where a decision results in an action, the rationale SHOULD explain what the operator needs to do or what will happen next. For example:
   - `"An approval ticket has been created. A senior_engineer must approve within 15 minutes or the request will expire and must be resubmitted."`

4. **Factual and non-speculative:** Rationale MUST describe the actual inputs and rule that triggered the decision, not inferred intent. Probabilistic language MUST NOT be used unless a confidence score is explicitly being described.

#### 4.4.2 Prohibited Language Patterns

The following patterns MUST NOT appear in explanation text surfaced to operators:

| Prohibited                        | Reason                                          |
|-----------------------------------|-------------------------------------------------|
| Internal error codes (e.g., E4021) | Opaque to operators; use descriptive text       |
| Stack traces or exception messages | Security risk and not actionable for operators  |
| Raw JSON field names as rationale  | Not human-readable                              |
| "Unknown reason"                   | Indicates missing reasoning chain data          |
| Empty string                       | The rationale field MUST NOT be empty           |

### 4.5 Explainability for Compliance

#### 4.5.1 Compliance Reconstruction Requirement

A compliance auditor MUST be able to reconstruct the complete reasoning for any ANIF decision using only the audit log records, without requiring access to the running ANIF system.

This means:

1. The `reasoning_chain` MUST be stored in the audit log as part of the audit record at the time of the decision, not computed on-the-fly when the `/why` endpoint is called.
2. The explanation returned by `/why` MUST be reproducible: calling `/why` on the same `intent_id` at different times MUST return the same `reasoning_chain` (barring format changes).
3. Audit records MUST include sufficient information to identify: who submitted the intent, what action was proposed, which policies were evaluated and with what result, what risk score was assigned and why, which governance rule triggered the mode decision, and who approved or rejected the ticket if applicable.

#### 4.5.2 Retention for Compliance

- Reasoning chain data MUST be retained for the same period as the associated audit records (per ANIF-107).
- Reasoning chain data MUST be stored in the same append-only, tamper-evident store as audit records.
- Reasoning chain data MUST NOT be purged independently of its associated audit record.

### 4.6 Integration with Governance Review

- The governance approval interface MUST surface the reasoning_chain for an intent when presenting an approval ticket to an operator.
- Operators reviewing a manual_review ticket MUST be able to call `GET /audit/{intent_id}/why` directly from the approval interface.
- The reasoning chain MUST be included in any approval notification sent to the on-call engineer.

---

## 5. Conformance Requirements

1. An ANIF deployment MUST implement the `GET /audit/{intent_id}/why` endpoint.
2. Every pipeline stage MUST emit at least one `decision_step` to the reasoning chain before returning a response.
3. The `explanation` field returned by `/why` MUST contain a human-readable narrative for all outcome types.
4. Reasoning chain data MUST be stored in the append-only audit log and MUST be immutable after writing.
5. The `/why` endpoint MUST NOT return `"Unknown reason"` or empty rationale for any step; if reasoning data is unavailable, the response MUST indicate a data integrity error.
6. Explanation text MUST NOT contain internal error codes, stack traces, or raw field names as rationale.

---

## 6. Security Considerations

- The `/why` endpoint MUST require authentication; unauthenticated access MUST be denied with HTTP 401.
- Access to the `/why` endpoint for a given `intent_id` MUST be restricted to: the operator who submitted the intent, users with the `governance_officer` role, and users with the `compliance_auditor` role.
- Explanation text MUST NOT include credentials, API keys, or secrets that may have appeared in intent parameters.
- Explanation text MUST be sanitised to prevent injection attacks if rendered in web interfaces.

---

## 7. Operational Considerations

- Reasoning chain data generation adds latency to each pipeline stage. Each stage MUST target a reasoning chain write overhead of less than 10 ms.
- The explainability service SHOULD be independently deployable so that audit queries do not compete with live pipeline traffic.
- Operators SHOULD be trained to use the `/why` endpoint as the primary diagnostic tool when investigating unexpected governance decisions.
- The quality of explanation text SHOULD be reviewed periodically; operators SHOULD be able to report unclear explanations through an internal feedback channel.

---

## 8. Explainability Testing Requirements

### 8.1 Coverage Requirements

- Tests MUST verify that `/why` returns meaningful content for all of the following pipeline outcomes:
  - Execution success (all policies pass, governance mode=auto, execution completes).
  - Policy failure (one or more policies fail, governance mode=block).
  - Risk escalation (risk_score ≥ 70, governance mode=manual_review).
  - Approval expiry (approval ticket not actioned within 15 minutes).
  - Manual rejection (operator rejects the approval ticket).
  - Rollback (post-execution verification failure triggers rollback).
  - Governance block (operator lacks required role, governance mode=block).

### 8.2 Quality Assertions

- Tests MUST assert that no `rationale` field in any `decision_step` is empty or contains `"Unknown reason"`.
- Tests MUST assert that no `rationale` field contains internal error codes matching the pattern `[A-Z]+_[A-Z]+_[0-9]+`.
- Tests MUST assert that the `explanation` narrative field is non-empty for all tested outcomes.
- Tests MUST assert that all `step_number` values within a single intent's reasoning chain are unique and sequential.

---

## Appendix A: Examples

### A.1 Example /why Response — Policy Failure Leading to Block

```json
{
  "intent_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "intent_summary": "Update firewall rules for segment prod-42 to permit inbound traffic on port 8080 with TLS disabled.",
  "final_outcome": "rejected",
  "explanation": "The intent was rejected at the policy evaluation stage. The policy 'pci_compliant' failed because the intent specifies encryption=false, which violates the PCI-DSS requirement for encryption in transit on production segments. As a result, the governance engine set mode to 'block' and the intent was not executed. No network changes were made.",
  "reasoning_chain": [
    {
      "step_number": 1,
      "stage": "policy",
      "timestamp": "2026-04-07T14:23:01.452Z",
      "input_summary": "Intent requested to permit port 8080 traffic with encryption=false on production segment prod-42.",
      "decision": "Policy pci_compliant failed",
      "rationale": "Policy pci_compliant failed because encryption=false. All production segments are required to enforce TLS for inbound traffic per PCI-DSS control 4.1. This intent would violate that control.",
      "policy_id": "pci_compliant",
      "risk_score": null,
      "outcome": "fail"
    },
    {
      "step_number": 2,
      "stage": "governance",
      "timestamp": "2026-04-07T14:23:01.498Z",
      "input_summary": "One or more policies failed with a safety_decision of block.",
      "decision": "Governance mode set to block",
      "rationale": "The governance engine evaluated the policy results and found safety_decision=block due to the pci_compliant failure. Per governance rule 5, a safety_decision of block always results in mode=block regardless of other parameters. The intent cannot proceed.",
      "policy_id": null,
      "risk_score": 88,
      "outcome": "block"
    }
  ],
  "trace_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "generated_at": "2026-04-07T14:30:00.000Z"
}
```

---

## Appendix B: Change History

| Version | Date       | Author             | Change                    |
|---------|------------|--------------------|---------------------------|
| 0.1.0   | 2026-04-07 | ANIF Working Group | Initial draft             |
