# ANIF-724: Ethics Audit Trail Requirements

| Field        | Value                                              |
|--------------|----------------------------------------------------|
| Doc ID       | ANIF-724                                           |
| Series       | AI Ethics                                          |
| Version      | 0.1.0                                              |
| Status       | Draft                                              |
| Authors      | ANIF Working Group                                 |
| Reviewers    | —                                                  |
| Approved by  | —                                                  |
| Created      | 2026-04-07                                         |
| Last updated | 2026-04-07                                         |
| Replaces     | N/A                                                |
| Related docs | ANIF-107, ANIF-702, ANIF-720, ANIF-907             |

---

## Abstract

This document extends the base audit trail requirements of ANIF-107 with mandatory AI-specific fields. Every action involving an AI agent MUST write an ethics audit record containing these fields in addition to the base audit record. Ethics audit records MUST be written and confirmed before the API response is returned to the caller (write-before-return). Retention is a minimum of seven years.

---

## 1. Introduction

### 1.1 Purpose

The base audit trail defined in ANIF-107 captures what happened in the pipeline. The ethics audit trail captures why — the AI-specific decision factors that distinguish autonomous action from deterministic automation. Without AI-specific fields, an audit record cannot support accountability chain reconstruction, ethics incident investigation, or regulatory inspection for AI-governed actions.

### 1.2 Scope

This document covers:

- The mandatory AI-specific fields extending the ANIF-107 base record
- The write-before-return requirement for ethics audit records
- Retention requirements
- Access control requirements
- The relationship between ethics audit records and council records (ANIF-907)

### 1.3 Out of Scope

This document does not cover:

- The base audit record schema (see ANIF-107)
- The accountability chain model (see ANIF-702)
- Council record schema (see ANIF-907)
- Ethics incident records (see ANIF-715)

### 1.4 Intended Audience

- Platform engineers implementing the audit write pipeline
- Compliance officers reviewing audit completeness
- Auditors and regulators requiring AI-specific evidence
- Ethics officers investigating incidents

---

## 2. Normative References

- ANIF-107 — Audit Trail Requirements
- ANIF-702 — Accountability Chain Model
- ANIF-712 — Harm Classification and Prevention Policy
- ANIF-722 — LLM Output Validation
- ANIF-723 — Fairness Enforcement Controls
- RFC 2119 — Key words for use in RFCs to indicate requirement levels

---

## 3. Terms and Definitions

**Ethics audit record:** The combination of the base audit record (ANIF-107) and the AI-specific fields defined in this document. Not a separate record — an extension of the same record.

**Write-before-return:** The requirement that the audit record write operation MUST complete and be confirmed before the API response is returned to the caller. The response MUST NOT be returned optimistically before the write succeeds.

**AI-involved action:** Any action in which at least one pipeline stage was processed by an AI component. This includes actions where an LLM produced a recommendation that was accepted, and actions where a deterministic shadow was substituted for an LLM output.

---

## 4. Mandatory AI-Specific Fields

The following fields MUST be added to every audit record for AI-involved actions. They extend the base record schema from ANIF-107.

### 4.1 Agent Identity Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `agent_id` | UUID | MUST | Identity of the agent that produced the decision or recommendation |
| `agent_version` | string | MUST | Version string of the agent at time of action |
| `agent_tier` | enum: 0/1/2/3 | MUST | Tier of the agent per ANIF-800 |
| `agent_trust_level` | enum | MUST | SYSTEM / VERIFIED / PROVISIONAL / UNTRUSTED at time of action |

### 4.2 Determinism Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `deterministic` | boolean | MUST | Whether the agent declared deterministic: true in its manifest |
| `llm_used` | boolean | MUST | Whether an LLM component was invoked for this action |
| `llm_model_id` | string | MUST if LLM used | Model identifier and version (e.g., claude-sonnet-4-6) |
| `shadow_used_as_substitution` | boolean | MUST if LLM used | Whether deterministic shadow replaced LLM output |

### 4.3 LLM Audit Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `llm_prompt_hash` | string (SHA-256) | MUST if LLM used | Hash of the submitted prompt, written before submission |
| `llm_prompt_length_tokens` | integer | SHOULD if LLM used | Token count of the submitted prompt |
| `llm_confidence_score` | float 0–1 | MUST if LLM used | Calibrated confidence score of the LLM output |
| `llm_validation_stage1` | enum: pass/fail | MUST if LLM used | Schema check result |
| `llm_validation_stage2` | enum: pass/fail/skipped | MUST if LLM used | Hallucination check result |
| `llm_validation_stage3` | enum: pass/suppressed | MUST if LLM used | Confidence check result |
| `llm_validation_stage4` | enum: pass/fail | MUST if LLM used | Prompt integrity hash result |

### 4.4 Fairness Audit Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `fairness_check_result` | enum: pass/fail/not_applicable | MUST | Result of ANIF-723 SLA floor check |
| `fairness_freshness_gate_result` | enum: pass/fail | MUST | Result of ANIF-723 ground truth freshness gate |
| `reproducibility_check_result` | enum: pass/fail/shadow_used/shadow_unavailable | MUST if Tier 3 | Result of ANIF-723 reproducibility check |
| `ai_shadow_divergence` | float | MUST if reproducibility ran | Measured divergence between AI and shadow |

### 4.5 Harm Classification Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `harm_class` | enum: service/infrastructure/cascading/none | MUST | From ANIF-712 |
| `harm_severity_score` | integer 0–100 | MUST | From ANIF-712 |
| `blast_radius_segment_count` | integer | MUST | Estimated affected segment count |
| `harm_gate_outcome` | enum: pass/manual_review_forced/council_review_forced | MUST | Gate decision |
| `simulation_completed` | boolean | MUST if cascading harm | Whether digital twin simulation ran |

### 4.6 Accountability Chain Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `accountability_designer_id` | string | MUST | IAM identity of the agent designer (ANIF-702) |
| `accountability_deployer_id` | string | MUST | IAM identity of the agent deployer |
| `accountability_operator_id` | string | MUST | IAM identity of the operator who submitted the intent |
| `accountability_approver_id` | string | MUST if manual/council review | IAM identity of the approver. Null if auto |

### 4.7 Ethics Gate Results

| Field | Type | Required | Description |
|---|---|---|---|
| `ethics_gates_passed` | array of strings | MUST | List of safeguard stage names that passed |
| `ethics_gates_failed` | array of strings | MUST | List of safeguard stage names that blocked |
| `ethics_gates_skipped` | array of strings | MUST | List of safeguard stage names skipped (with reason) |

---

## 5. Write-Before-Return

### 5.1 Requirement

The ethics audit record MUST be written to the audit store and the write MUST be confirmed before the API response is returned to the caller. This extends the write-before-return requirement from ANIF-107 to include all AI-specific fields.

### 5.2 What "Confirmed" Means

A write is confirmed when the audit store has acknowledged receipt of the record. For a database: a successful commit. For a message queue: an acknowledgement from the broker. An optimistic response (returning before the write is committed) does not satisfy this requirement.

### 5.3 Write Failure Handling

If the audit write fails:

1. The API response MUST NOT be returned until the write either succeeds or the failure is escalated
2. If the write fails after retry: the action MUST be treated as if it did not complete and the caller MUST receive an error response
3. The write failure MUST be logged to an out-of-band monitoring channel
4. The write failure MUST be treated as a Severity 2 ethics condition if it affects more than three records in one hour

### 5.4 Rationale

Returning a success response before the audit record is committed creates a window in which the action has occurred but no audit evidence exists. If the system fails before the write completes, the action is unauditable. Write-before-return eliminates this window entirely.

---

## 6. Retention Requirements

Ethics audit records MUST be retained for a minimum of 7 years from the date of the action. This exceeds the base audit record retention in ANIF-107 and governs for AI-involved actions.

Ethics audit records MUST be immutable after writing. The same append-only constraints that apply to base audit records (ANIF-107) apply here.

Deletion or modification of ethics audit records is a Severity 1 ethics incident (ANIF-715).

---

## 7. Access Control

Ethics audit records MAY contain sensitive information including LLM prompt hashes, confidence scores, and accountability chain identities. Access MUST be restricted to:

- Governance committee members
- AI Ethics Officer
- Authorised auditors (read-only)
- Security team (for security incident investigation)

AI agents MUST NOT have read or write access to ethics audit records. Audit records are human governance artefacts.

---

## 8. Conformance Requirements

Every AI-involved action MUST produce an ethics audit record with all mandatory fields populated.

The write-before-return requirement MUST be implemented. Optimistic responses before audit write confirmation are non-conformant.

Ethics audit records MUST be retained for a minimum of 7 years.

AI agents MUST NOT have access to ethics audit records.

---

## 9. Security Considerations

Ethics audit records are a high-value target — they contain evidence of agent behaviour and accountability chains. An adversary who can modify or delete audit records can erase evidence of misconduct. The append-only requirement and access controls are the primary defences. Audit record integrity SHOULD be monitored through independent checksums or hash chaining.

---

## 10. Operational Considerations

Organisations SHOULD implement a regular review process to verify audit record completeness — specifically checking that all AI-involved actions have complete ethics audit records with all mandatory fields populated. Records with null mandatory fields indicate incomplete audit implementation and MUST be investigated.

---

## Appendix A: Change History

| Version | Date | Author | Changes |
|---|---|---|---|
| 0.1.0 | 2026-04-07 | ANIF Working Group | Initial draft |
