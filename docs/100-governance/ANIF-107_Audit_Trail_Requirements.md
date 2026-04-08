# ANIF-107: Audit Trail Requirements

| Field        | Value                                                       |
|--------------|-------------------------------------------------------------|
| Doc ID       | ANIF-107                                                    |
| Series       | Governance                                                  |
| Version      | 0.1.0                                                       |
| Status       | Draft                                                       |
| Authors      | ANIF Working Group                                          |
| Reviewers    | —                                                           |
| Approved by  | —                                                           |
| Created      | 2026-04-07                                                  |
| Last updated | 2026-04-07                                                  |
| Replaces     | N/A                                                         |
| Related docs | ANIF-002, ANIF-103, ANIF-106, ANIF-402                     |

---

## Abstract

This document specifies the mandatory audit trail requirements for the ANIF autonomous networking pipeline. It defines the audit coverage requirement (every pipeline stage MUST write a record), the minimum audit record schema, immutability requirements, the write-before-return constraint, query interface requirements, retention periods by compliance regime, and audit record integrity mechanisms including hash chaining. This document is a hard requirement: implementations that do not satisfy it are not conformant with ANIF at any level above L1 Aware.

---

## 1. Introduction

### 1.1 Purpose

An autonomous system that cannot be audited cannot be trusted. Auditability (P-02) and Explainability (P-04) are foundational ANIF principles that exist specifically because autonomous decisions are made without direct human involvement at execution time. The audit trail is the primary mechanism by which:

- Humans can reconstruct why any autonomous action was taken.
- Policy violations are detected.
- Compliance evidence is produced for regulatory audits.
- Incidents are investigated.
- The reasoning chain of automation agents is preserved and verifiable.

This document specifies the minimum requirements that ALL conformant ANIF implementations MUST satisfy. These requirements are not optional and MUST NOT be partially implemented.

### 1.2 Scope

This document covers:

- Mandatory audit coverage: which pipeline stages must produce records.
- The minimum schema for every audit record.
- Immutability requirements for audit records.
- The write-before-return constraint that governs when records must be written.
- Query interface requirements: endpoints, latency targets, and filter capabilities.
- Retention periods by compliance regime.
- Integrity protection mechanisms including hash chaining.

### 1.3 Out of Scope

- Application logging for debugging purposes (distinct from audit records).
- Infrastructure-level metrics and telemetry (ANIF-402).
- Forensic analysis procedures following incidents (ANIF-405, ANIF-406).
- SIEM integration architecture (implementation-specific).

### 1.4 Intended Audience

| Audience                | Purpose                                                                           |
|-------------------------|-----------------------------------------------------------------------------------|
| Compliance Officer      | Verify completeness; produce evidence packages; confirm retention                  |
| Policy Administrator    | Understand what the audit trail captures; configure audit policies                 |
| Senior Engineer         | Use audit trail for incident investigation; understand query interface              |
| Network Engineer        | Understand what is recorded about their actions and automation agent activity      |
| Automation Agent        | Understand that every action is recorded; provide required reasoning chain context |

---

## 2. Normative References

| Reference      | Title                                                          |
|----------------|----------------------------------------------------------------|
| ANIF-001       | ANIF Constitution and Guiding Principles                       |
| ANIF-002       | ANIF Core Glossary                                             |
| ANIF-103       | Autonomous Action Policy                                       |
| ANIF-104       | Change Management Policy                                       |
| ANIF-105       | Escalation and Exception Policy                                |
| ANIF-106       | Data Residency and Compliance Policy                           |
| ANIF-402       | Audit and Observability                                        |
| ISO 8601       | Date and time format standard                                  |
| RFC 4122       | A Universally Unique Identifier (UUID) URN Namespace           |
| RFC 2119       | Key words for use in RFCs to Indicate Requirement Levels       |

---

## 3. Terms and Definitions

| Term                    | Definition                                                                                              |
|-------------------------|---------------------------------------------------------------------------------------------------------|
| Audit Record            | A structured, immutable record capturing the inputs, outputs, and outcome of a single pipeline stage.  |
| Audit Trail             | The complete, ordered sequence of audit records for a given intent lifecycle.                          |
| Pipeline Stage          | A discrete processing step: validate, policy, risk, decision, governance, execute, rollback.            |
| Write-Before-Return     | The requirement that an audit record MUST be durably written before the pipeline stage returns a response.|
| Immutability            | The property that a written record cannot be modified or deleted after it is written.                   |
| Hash Chain              | A cryptographic linking of sequential records where each record's hash includes the hash of its predecessor.|
| Reasoning Chain         | An ordered list of decision steps produced by the pipeline explaining how the output was reached.       |
| Operator ID             | The identifier of the human or automation agent responsible for a pipeline stage action.                |
| Durable Write           | A write that is persisted to stable storage before being acknowledged as complete.                      |

---

## 4. Audit Trail Requirements

### 4.1 Mandatory Audit Coverage

4.1.1 Every pipeline stage MUST write an audit record before returning its result to the next stage or the caller. This is an absolute requirement with no exceptions.

4.1.2 The following pipeline stages MUST each produce exactly one audit record per execution:

| Stage        | Trigger Condition                                       | Mandatory? |
|--------------|---------------------------------------------------------|------------|
| `validate`   | Every intent submission, regardless of outcome          | YES — MUST |
| `policy`     | Every intent that passes validate stage                 | YES — MUST |
| `risk`       | Every intent that passes policy stage                   | YES — MUST |
| `decision`   | Every intent that passes risk stage                     | YES — MUST |
| `governance` | Every intent that passes decision stage                 | YES — MUST |
| `execute`    | Every intent approved for execution                     | YES — MUST |
| `rollback`   | Every rollback operation, including failed rollbacks    | YES — MUST |

4.1.3 If a stage fails before completing its processing, the audit record MUST still be written. The record MUST capture the failure with `outcome: failure` and include available error detail in `output_summary`.

4.1.4 Stages that do not complete (e.g., because the previous stage rejected the intent) MUST NOT write audit records. The last stage to execute is responsible for the terminal audit record.

4.1.5 A complete audit trail for a successfully executed and verified change MUST contain a minimum of 6 records (validate → policy → risk → decision → governance → execute). A change that triggers rollback MUST contain a minimum of 7 records.

### 4.2 Mandatory Audit Record Schema

Every audit record MUST include all of the following fields. Fields listed as "required" MUST NOT be null or absent in any conformant record.

| Field             | Type                          | Required | Description                                                                 |
|-------------------|-------------------------------|----------|-----------------------------------------------------------------------------|
| `record_id`       | UUID (RFC 4122 v4)            | YES      | Unique identifier for this audit record. Generated by the pipeline.          |
| `intent_id`       | UUID (RFC 4122 v4)            | YES      | The intent that triggered this pipeline execution.                           |
| `timestamp`       | ISO-8601 datetime with timezone| YES      | The time at which this record was written. MUST be UTC.                      |
| `stage`           | enum (see §4.1.2)             | YES      | The pipeline stage that produced this record.                                |
| `operator_id`     | string or null                | YES      | Identity of the human operator or automation agent responsible. null if system-initiated with no operator context. |
| `input_summary`   | object                        | YES      | A structured summary of the inputs to this stage. MUST NOT contain raw payloads. |
| `output_summary`  | object                        | YES      | A structured summary of the outputs from this stage.                        |
| `outcome`         | enum                          | YES      | One of: `success`, `failure`, `escalated`, `blocked`.                       |
| `reasoning_chain` | array of strings              | YES      | Ordered list of reasoning steps explaining the stage outcome. MUST NOT be empty for `decision` and `governance` stages. |
| `duration_ms`     | integer (≥ 0)                 | YES      | The wall-clock time in milliseconds from stage start to audit write.         |

#### 4.2.1 Additional Mandatory Fields by Stage

Beyond the minimum schema above, the following stages require additional fields:

| Stage        | Additional Required Fields                                                             |
|--------------|----------------------------------------------------------------------------------------|
| `governance` | `governance_mode` (enum: auto/manual_review/block), `ticket_id` (UUID or null), `applied_policies` (array of policy IDs) |
| `execute`    | `action_type` (enum), `target` (string), `rollback_available` (boolean), `post_verification_outcome` (enum: pass/fail/pending) |
| `rollback`   | `original_execute_record_id` (UUID), `rollback_reason` (string), `rollback_outcome` (enum: success/failure) |
| `policy`     | `policies_evaluated` (array of policy IDs), `policies_violated` (array of policy IDs, may be empty) |
| `risk`       | `risk_score` (integer 0–100), `risk_factors` (array of contributing factors)           |

#### 4.2.2 Field Constraints

- `record_id`: MUST be unique across all records in the audit store. Duplicate record_ids MUST be rejected.
- `timestamp`: MUST use ISO-8601 extended format with timezone offset, e.g. `2026-04-07T14:30:00.000Z`. Localised timestamps without timezone MUST NOT be used.
- `stage`: MUST be one of the seven values defined in Section 4.1.2.
- `outcome`: MUST accurately reflect the stage result. `success` means the stage completed and passed. `failure` means the stage encountered an error. `escalated` means the stage transferred control to a human. `blocked` means the stage halted the pipeline.
- `reasoning_chain`: MUST contain at minimum one entry. For `decision` and `governance` stages, MUST contain sufficient entries to reconstruct the decision logic. Entries MUST be human-readable strings.
- `duration_ms`: MUST reflect actual execution time. A value of 0 MAY be used only if the stage completed in sub-millisecond time.
- `input_summary` and `output_summary`: MUST be structured objects, not free-form strings. MUST NOT contain raw packet payloads, passwords, tokens, or PII beyond operator identifiers.

### 4.3 Write-Before-Return Requirement

4.3.1 The audit write MUST complete before the pipeline stage returns its result. This is the write-before-return constraint. A stage MUST NOT return `success` to the next stage unless its audit record has been durably written.

4.3.2 "Durably written" means the record has been acknowledged by the audit store as persisted to stable storage. An in-memory write or a write to a non-durable buffer does NOT satisfy this requirement.

4.3.3 If the audit write fails, the pipeline stage MUST:
- NOT proceed to the next stage.
- Return `outcome: failure` to the caller.
- Attempt to write a minimal failure record (if partial write capability is available).
- Trigger an alert to the policy_administrator and senior_engineer.

4.3.4 The write-before-return constraint applies to ALL stages including `execute`. An action MUST NOT be considered complete until its execute audit record is written.

4.3.5 Implementations MAY use asynchronous write pipelines provided the durable-write acknowledgement is received synchronously before the stage returns. Eventual-consistency audit writes MUST NOT be used.

### 4.4 Immutability Requirements

4.4.1 Audit records MUST be append-only. The audit store MUST NOT expose any endpoint or internal mechanism for updating or deleting individual audit records.

4.4.2 No role — including policy_administrator, compliance_officer, and system administrator — MUST have the ability to modify or delete audit records within their retention period. Any system that grants such access is non-conformant.

4.4.3 Audit records MAY only be purged after their retention period has expired. Purge operations MUST themselves be logged per ANIF-106 §4.7.4.

4.4.4 The audit store MUST be logically separated from mutable operational data stores. A combined store that exposes update/delete APIs for any data MUST NOT be used for audit records unless those records are in a logically isolated partition with immutability enforced at the storage layer.

### 4.5 Query Interface Requirements

4.5.1 The audit store MUST expose a query interface satisfying the following endpoint requirements:

| Endpoint                      | Description                                                     | Latency Target |
|-------------------------------|-----------------------------------------------------------------|----------------|
| `GET /audit/{intent_id}`      | Returns all audit records for the specified intent, ordered by timestamp ascending. | < 100ms at p99 |
| `GET /audit/{intent_id}/why`  | Returns a human-readable explanation of the pipeline decision for the specified intent. Synthesised from `reasoning_chain` fields. | < 200ms at p99 |
| `GET /audit`                  | Returns audit records filterable by query parameters. Paginated. | < 500ms at p99 |

4.5.2 The `GET /audit` endpoint MUST support filtering by at minimum the following parameters:

| Filter Parameter   | Type            | Description                                               |
|--------------------|-----------------|-----------------------------------------------------------|
| `stage`            | enum            | Filter by pipeline stage.                                  |
| `outcome`          | enum            | Filter by outcome (success/failure/escalated/blocked).     |
| `date_from`        | ISO-8601 date   | Include records at or after this date.                     |
| `date_to`          | ISO-8601 date   | Include records at or before this date.                    |
| `operator_id`      | string          | Filter by operator identity.                               |
| `action_type`      | enum            | Filter by action type (for execute stage records).         |
| `environment`      | string          | Filter by target environment.                              |

4.5.3 `GET /audit/{intent_id}` MUST return an empty array (not a 404) if no records exist for the given intent_id. A 404 MUST only be returned if the intent_id is syntactically invalid.

4.5.4 Pagination: `GET /audit` MUST support cursor-based or offset pagination. Default page size MUST be 50 records; maximum page size MUST NOT exceed 1000 records.

4.5.5 Access control: all audit query endpoints MUST require authentication. `GET /audit/{intent_id}` and `GET /audit/{intent_id}/why` SHOULD be accessible to network_engineer and higher. `GET /audit` with broad date ranges MUST require senior_engineer or compliance_officer role.

4.5.6 The `GET /audit/{intent_id}/why` response MUST be produced in natural language, synthesising the `reasoning_chain` fields from all records for the intent into a coherent narrative. It MUST include: what action was proposed, what policies were evaluated, what risk score was computed, what governance mode was assigned, and what the final outcome was.

### 4.6 Retention Periods by Compliance Regime

Audit records MUST be retained per the retention schedule defined in ANIF-106 §4.7. The following table is reproduced here for completeness:

| Compliance Regime     | Applicable Operations                    | Minimum Retention  |
|-----------------------|------------------------------------------|--------------------|
| General operations    | Non-regulated                            | 1 year             |
| GDPR                  | EU-region operations                     | 3 years            |
| PCI-DSS               | pci_compliant operations                 | 3 years (12mo accessible) |
| Financial services    | Financial network segments               | 7 years            |
| SOX                   | US-region financial operations           | 7 years            |
| Recommended minimum   | All operations (no specific regime)      | 7 years            |

Where multiple regimes apply, the longest retention period MUST govern. Implementations SHOULD default to 7 years for all records to avoid under-retention of records whose compliance regime cannot be determined at write time.

### 4.7 Audit Record Integrity

4.7.1 Audit records MUST be protected against post-hoc tampering. The recommended mechanism is hash chaining, where each record includes a cryptographic hash of the previous record in the sequence.

4.7.2 Hash chaining requirements:

| Field             | Description                                                                  |
|-------------------|------------------------------------------------------------------------------|
| `record_hash`     | SHA-256 hash of the canonical JSON serialisation of the current record (excluding `record_hash` and `prev_hash` fields). |
| `prev_hash`       | The `record_hash` of the immediately preceding record in the audit sequence for this intent. For the first record in a sequence, this MUST be the hash of a well-known genesis value. |
| `chain_id`        | An identifier for the hash chain covering this intent.                       |

4.7.3 Hash chain verification: the audit system MUST expose a `GET /audit/{intent_id}/verify` endpoint that recomputes the hash chain and returns a verification result: `{ "valid": true/false, "broken_at": record_id or null }`.

4.7.4 Hash chain integrity MUST be verified at minimum daily by an automated process. Failures MUST trigger an immediate alert to the compliance_officer and senior_engineer. A broken hash chain MUST be treated as a potential security incident.

4.7.5 Where jurisdictional requirements mandate a higher integrity standard (e.g., qualified electronic timestamps for financial records), implementations MUST apply those requirements in addition to hash chaining.

4.7.6 Alternative integrity mechanisms (e.g., Write Once Read Many (WORM) storage, blockchain-based logs, tamper-evident hardware modules) MAY be used instead of or in addition to hash chaining, provided they satisfy the tamper-evidence requirement.

### 4.8 Audit System Availability and Durability

4.8.1 The audit store MUST be a separate service from the operational pipeline. A failure of the audit store MUST trigger the write-before-return failure mode (Section 4.3.3), not a bypass.

4.8.2 The audit store MUST have a Recovery Time Objective (RTO) of ≤ 1 hour and a Recovery Point Objective (RPO) of ≤ 0 records (no audit records may be lost).

4.8.3 Audit store backups MUST be performed at minimum daily. Backup integrity MUST be verified at minimum weekly through restoration testing.

4.8.4 The audit store MUST be deployed with redundancy appropriate to the environment. Prod deployments MUST have at minimum two replicas with synchronous replication.

---

## 5. Conformance Requirements

5.1 Conformant implementations MUST write an audit record at every pipeline stage before the stage returns per Section 4.1. This is a hard L2+ conformance requirement.

5.2 Conformant implementations MUST implement the minimum audit record schema defined in Section 4.2. All required fields MUST be present and populated.

5.3 Conformant implementations MUST satisfy the write-before-return constraint defined in Section 4.3.

5.4 Conformant implementations MUST expose an append-only audit store with no update or delete endpoints per Section 4.4.

5.5 Conformant implementations MUST expose the three query endpoints defined in Section 4.5 with the specified latency targets.

5.6 Conformant implementations MUST retain audit records for the applicable retention periods defined in Section 4.6.

5.7 Conformant implementations MUST implement hash chaining or an equivalent tamper-evidence mechanism per Section 4.7.

5.8 Conformant implementations MUST implement hash chain verification at minimum daily, with alerting on failure per Section 4.7.4.

---

## 6. Security Considerations

6.1 The audit trail is a high-value attack target: an adversary who can modify or delete audit records can conceal malicious actions. The audit store MUST be treated as a security-critical component.

6.2 Network access to the audit store MUST be restricted. The audit store MUST NOT be directly accessible from the internet. API access MUST be authenticated and TLS-protected.

6.3 Audit store credentials MUST be rotated at minimum quarterly and MUST be stored in a secrets management system. MUST NOT be stored in configuration files or source code.

6.4 `operator_id` fields in audit records may constitute personal data under GDPR. Access to audit records MUST be restricted as defined in Section 4.5.5 and ANIF-106 §6.4.

6.5 The hash chain verification endpoint (`GET /audit/{intent_id}/verify`) MUST be restricted to compliance_officer and senior_engineer roles. Exposing it to automation_agent or network_engineer roles could assist an adversary in verifying their own tampering.

6.6 Write-before-return failures (audit store unavailability) MUST NOT be silently ignored. An adversary who can cause audit store unavailability could suppress audit records. Audit store availability MUST be monitored continuously with immediate alerting.

---

## 7. Operational Considerations

7.1 Audit record volume grows with intent submission rate. Operators MUST capacity-plan the audit store based on expected intent volume, record size (estimated 2–10 KB per record), and retention period.

7.2 Query performance targets (< 100ms for `GET /audit/{intent_id}`) MUST be validated under production load. Indexes on `intent_id`, `timestamp`, `stage`, and `outcome` fields are recommended.

7.3 Hash chain verification should be integrated into the daily operational health check. A failed verification should page the on-call senior_engineer immediately.

7.4 The `GET /audit/{intent_id}/why` endpoint is the primary tool for human operators to understand why the system made a specific decision. This endpoint SHOULD be prominently featured in operational runbooks.

7.5 Audit record schema evolution MUST be managed carefully. New fields MAY be added to records. Existing required fields MUST NOT be removed or renamed without a major version increment of this document.

7.6 When querying audit records as part of incident investigation, operators SHOULD always start with `GET /audit/{intent_id}/why` for a human-readable summary before querying individual stage records.

---

## Appendix A: Examples

### A.1 Minimum Conformant Audit Record (validate stage)

```json
{
  "record_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "intent_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "timestamp": "2026-04-07T14:30:00.123Z",
  "stage": "validate",
  "operator_id": "eng-jane-smith",
  "input_summary": {
    "action_type": "reroute_traffic",
    "environment": "prod",
    "region": "EU",
    "schema_version": "1.2.0"
  },
  "output_summary": {
    "validation_result": "pass",
    "checks_performed": ["schema", "semantic", "action_type_permitted"]
  },
  "outcome": "success",
  "reasoning_chain": [
    "Schema validation passed against intent-schema v1.2.0",
    "Action type 'reroute_traffic' is in the permitted bounded action set",
    "Region 'EU' is a valid region code",
    "No semantic conflicts detected"
  ],
  "duration_ms": 12,
  "record_hash": "sha256:abc123...",
  "prev_hash": "sha256:genesis..."
}
```

### A.2 Governance Stage Record (manual_review)

```json
{
  "record_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
  "intent_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "timestamp": "2026-04-07T14:30:00.487Z",
  "stage": "governance",
  "operator_id": null,
  "input_summary": {
    "risk_score": 55,
    "action_type": "reroute_traffic",
    "environment": "prod"
  },
  "output_summary": {
    "governance_mode": "manual_review",
    "ticket_id": "c3d4e5f6-a7b8-9012-cdef-012345678902"
  },
  "outcome": "escalated",
  "reasoning_chain": [
    "Risk score 55 falls within prod manual_review band (40-69)",
    "Action type 'reroute_traffic' does not require mandatory manual_review",
    "Prod environment threshold applied: manual_review for risk >= 40",
    "Approval ticket created; senior_engineer notified"
  ],
  "duration_ms": 45,
  "governance_mode": "manual_review",
  "ticket_id": "c3d4e5f6-a7b8-9012-cdef-012345678902",
  "applied_policies": ["POL-003", "POL-017"],
  "record_hash": "sha256:def456...",
  "prev_hash": "sha256:abc123..."
}
```

### A.3 GET /audit/{intent_id}/why Sample Response

```
Intent f47ac10b (reroute_traffic, prod, EU) — Outcome: manual_review (pending approval)

Summary: A request was submitted to reroute traffic in the production EU environment. The 
intent passed schema validation and policy checks. The risk scoring engine assigned a score 
of 55 based on the production environment, traffic volume (high), and segment criticality 
(medium). Under the production risk threshold policy (manual_review for scores 40-69), this 
action requires senior engineer approval before execution. An approval ticket has been created 
(ticket C3D4E5F6) and the on-call senior engineer has been notified. The ticket expires in 
15 minutes.

Policies applied: POL-003 (prod risk thresholds), POL-017 (EU region routing)
Risk factors: environment=prod (+20), traffic_volume=high (+15), segment_criticality=medium (+10), 
              action_type=reroute_traffic (+10)
Next action: Awaiting senior engineer approval or rejection of ticket C3D4E5F6
```

### A.4 Hash Chain Verification Response

```json
{
  "intent_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "record_count": 6,
  "verified": true,
  "broken_at": null,
  "verified_at": "2026-04-07T14:35:00.000Z",
  "verifier": "audit-integrity-service"
}
```

---

## Appendix B: Change History

| Version | Date       | Author             | Description          |
|---------|------------|--------------------|----------------------|
| 0.1.0   | 2026-04-07 | ANIF Working Group | Initial draft        |
