# ANIF-722: LLM Output Validation

| Field        | Value                                              |
|--------------|----------------------------------------------------|
| Doc ID       | ANIF-722                                           |
| Series       | AI Ethics                                          |
| Version      | 0.1.0                                              |
| Status       | Draft                                              |
| Authors      | ANIF Working Group                                 |
| Reviewers    | —                                                  |
| Approved by  | —                                                  |
| Created      | 2026-04-07                                         |
| Last updated | 2026-04-07                                         |
| Replaces     | N/A                                                |
| Related docs | ANIF-705, ANIF-713, ANIF-720, ANIF-807             |

---

## Abstract

This document specifies the four-stage validation pipeline that every LLM output MUST pass before it is used in any downstream pipeline stage. The four stages are: schema check, hallucination check against canonical state, confidence threshold check, and prompt integrity hash verification. Stages MUST run in order. Any stage failure blocks the output and routes to manual review. Stage 4 failure — a prompt hash mismatch — is a security incident, not a routine validation failure.

---

## 1. Introduction

### 1.1 Purpose

LLM outputs cannot be trusted at face value. They may be structurally incorrect, factually wrong about the network, expressed with unjustified confidence, or may differ from what was originally submitted to the LLM. This document specifies the four checks that catch each of these failure modes before the output enters the pipeline.

### 1.2 Scope

This document covers:

- The specification of all four validation stages in execution order
- Pass and failure conditions for each stage
- Actions taken on failure for each stage
- The requirement that stages run in order and that all four run
- Canonical state freshness requirements for stage 2

### 1.3 Out of Scope

This document does not cover:

- The LLM guardrails policy (see ANIF-713)
- LLM agent manifest requirements (see ANIF-807)
- LLM ethics principles (see ANIF-705)
- The pipeline position of this validation block (see ANIF-720)

### 1.4 Intended Audience

- Platform engineers implementing LLM output validation
- AI engineers defining output schemas for their agents
- Security engineers implementing prompt integrity checks
- Build-time council members verifying validation implementation

---

## 2. Normative References

- ANIF-705 — LLM-Specific Ethics Principles
- ANIF-713 — LLM Guardrails Policy
- ANIF-716 — Agent Failure and Progressive Intervention
- ANIF-720 — Safeguard Architecture Overview
- ANIF-724 — Ethics Audit Trail Requirements
- ANIF-807 — LLM Agent Specification
- ANIF-847 — AI Security Incident Response
- RFC 2119 — Key words for use in RFCs to indicate requirement levels

---

## 3. Terms and Definitions

**Output schema:** The structured definition of the expected format and content of an LLM agent's output. Defined in the agent manifest. Used by stage 1 to validate structure.

**Hallucination:** An LLM output claim that asserts a fact about the network inconsistent with canonical state, or references network elements that do not exist in canonical state.

**Canonical state snapshot:** The authoritative network state at the time of validation. MUST be current — older than 5 minutes at the time of stage 2 is not acceptable.

**Prompt hash:** The SHA-256 hash of the complete prompt submitted to the LLM, written to the audit record before submission per ANIF-705 section 5.

**Calibrated confidence:** A confidence score validated against actual accuracy over a test distribution. Not self-reported by the LLM.

---

## 4. Validation Pipeline

The four stages MUST run in the following order. No stage MAY be skipped. No stage MAY run in parallel with another — they are sequential gates.

```
LLM Output
    │
    ▼
Stage 1: Schema Check
    │   Pass → continue
    │   Fail → block, manual_review, increment strike
    ▼
Stage 2: Hallucination Check
    │   Pass → continue
    │   Fail → block, manual_review, increment strike
    ▼
Stage 3: Confidence Check
    │   Pass → continue
    │   Fail → suppress, notify human, no strike
    ▼
Stage 4: Prompt Integrity Hash
    │   Pass → continue
    │   Fail → halt pipeline, Severity 1 security incident
    ▼
Output approved for downstream use
```

---

## 5. Stage 1 — Schema Check

### 5.1 Purpose

Verifies that the LLM output conforms to the declared output schema for the agent's role. An LLM that produces structurally incorrect output cannot be safely used in downstream processing without introducing unpredictable behaviour.

### 5.2 Pass Condition

The LLM output parses successfully against the output schema defined in the agent manifest. All required fields are present. All field types match the schema. All enum values are within the declared valid set.

### 5.3 Failure Condition

The LLM output does not parse against the schema, contains missing required fields, contains type mismatches, or contains values outside declared enum sets.

### 5.4 Failure Actions

1. Discard the LLM output — do not use it in any downstream stage
2. Route the intent to `manual_review`
3. Increment the agent's strike counter (ANIF-716)
4. Log the failure with: agent_id, intent_id, failure reason, timestamp

### 5.5 Schema Definition Requirement

Every LLM agent MUST define an output schema in its manifest. An agent without a declared output schema cannot be validated at stage 1 and MUST NOT be deployed. Absence of a schema is a build-time council (ANIF-903) blocking condition.

---

## 6. Stage 2 — Hallucination Check

### 6.1 Purpose

Verifies that factual claims in the LLM output are consistent with canonical state. Prevents hallucinated network facts from entering the decision pipeline.

### 6.2 Canonical State Requirement

The canonical state snapshot used for stage 2 MUST be no older than 5 minutes at the time the check runs. A snapshot older than 5 minutes MUST be refreshed before stage 2 proceeds. If canonical state cannot be refreshed, the output MUST be routed to `manual_review` — the check MUST NOT proceed with stale data.

### 6.3 Claim Extraction

The validation system MUST extract factual claims from the LLM output. A factual claim is any assertion about:

- The existence of a network element (device, link, segment, service)
- The state of a network element (operational, degraded, offline)
- A metric value (latency, throughput, availability) for a specific element
- A relationship between network elements (connected to, routes through, depends on)

### 6.4 Pass Condition

All extracted factual claims are consistent with canonical state. Claims about elements that exist in canonical state match the recorded state. No claims reference elements that do not exist in canonical state.

### 6.5 Failure Conditions

Either of the following constitutes a hallucination failure:

- A claim asserts a fact about a network element that contradicts its state in canonical state
- A claim references a network element (device, segment, service) that does not exist in canonical state

### 6.6 Failure Actions

1. Discard the LLM output
2. Route the intent to `manual_review`
3. Increment the agent's strike counter
4. Log the failure with: agent_id, intent_id, the specific claim that failed, the canonical state value that contradicted it
5. Check circuit breaker: if this is the third hallucination in 60 minutes, fire the hallucination circuit breaker (ANIF-713)

---

## 7. Stage 3 — Confidence Check

### 7.1 Purpose

Verifies that the LLM output meets the minimum confidence threshold for the agent's tier. Outputs that do not meet the threshold are suppressed rather than blocked — the pipeline routes to human decision rather than `manual_review`.

### 7.2 Thresholds

Confidence thresholds are defined in ANIF-713 section 5:

- Tier 2 agents: confidence ≥ 0.65
- Tier 3 agents: confidence ≥ 0.80

The confidence score MUST be calibrated per ANIF-705 section 6. An uncalibrated score MUST be treated as 0.0.

### 7.3 Pass Condition

The calibrated confidence score meets or exceeds the threshold for the agent's tier.

### 7.4 Failure Condition

The calibrated confidence score is below the threshold for the agent's tier, or the score is uncalibrated.

### 7.5 Failure Actions

Confidence check failure is treated differently from stages 1 and 2. A low-confidence output is the system working correctly — the agent is declining to recommend when it is not sufficiently certain.

1. Suppress the output — do not use it in downstream processing
2. Notify the human counterpart role (ANIF-808) that no recommendation was produced and why
3. Do NOT increment the strike counter
4. Log the suppression with: agent_id, intent_id, confidence score, threshold, timestamp

---

## 8. Stage 4 — Prompt Integrity Hash

### 8.1 Purpose

Verifies that the prompt submitted to the LLM was not modified between the time it was logged (pre-submission) and the time it was actually submitted. Detects prompt injection attacks that occur within the pipeline itself.

### 8.2 Pass Condition

The SHA-256 hash of the prompt as submitted to the LLM matches the hash recorded in the audit record before submission.

### 8.3 Failure Condition

The hash of the submitted prompt does not match the hash in the audit record.

### 8.4 Failure Actions

Stage 4 failure is a security incident, not a routine validation failure:

1. Halt the entire pipeline for this intent — do not route to `manual_review`, halt completely
2. Classify as a Severity 1 security incident (ANIF-847)
3. Notify the security team immediately
4. Do NOT increment the agent's strike counter — this is a security breach, not an agent failure
5. Preserve the full audit record state for forensic investigation
6. Log the mismatch with: agent_id, intent_id, recorded hash, actual hash, timestamp

### 8.5 Pre-Submission Logging Requirement

The prompt hash MUST be written to the audit record before the prompt is submitted to the LLM. The sequence is: construct prompt → compute hash → write hash to audit record → submit prompt → run stage 4 check. An implementation that submits the prompt before logging the hash cannot satisfy the integrity guarantee of this check.

---

## 9. Validation Result Record

The result of the four-stage validation MUST be written to the audit record (ANIF-724):

| Field | Type | Description |
|---|---|---|
| `stage1_result` | enum: pass/fail | Schema check result |
| `stage2_result` | enum: pass/fail/skipped | Hallucination check result. Skipped if no factual claims extracted |
| `stage3_result` | enum: pass/suppressed | Confidence check result |
| `stage4_result` | enum: pass/fail | Hash check result |
| `canonical_state_age_seconds` | integer | Age of canonical state used in stage 2 |
| `confidence_score` | float | The confidence score checked in stage 3 |
| `hallucination_details` | array | Claims that failed stage 2, if any |

---

## 10. Conformance Requirements

All four stages MUST run in order for every LLM output before it is used downstream.

Stage 2 MUST use canonical state no older than 5 minutes. Stale canonical state MUST block stage 2.

Stage 4 failure MUST produce a Severity 1 security incident. It MUST NOT be treated as a routine validation failure.

An agent without a declared output schema MUST NOT be deployed.

---

## 11. Security Considerations

Stage 4 is the primary defence against prompt injection attacks that occur within the pipeline — between the intent intake and the LLM submission. It does not defend against injection in the original intent (that is ANIF-842's responsibility), but it does detect if the pipeline itself has been compromised. Both defences are needed.

---

## 12. Operational Considerations

The 5-minute canonical state freshness requirement for stage 2 has latency implications for environments where canonical state updates are slow. Organisations with slow canonical state update cycles SHOULD optimise their source-of-truth collection pipelines rather than relaxing the freshness requirement.

---

## Appendix A: Change History

| Version | Date | Author | Changes |
|---|---|---|---|
| 0.1.0 | 2026-04-07 | ANIF Working Group | Initial draft |
