# ANIF-702: Accountability Chain Model

| Field        | Value                                              |
|--------------|----------------------------------------------------|
| Doc ID       | ANIF-702                                           |
| Series       | AI Ethics                                          |
| Version      | 0.1.0                                              |
| Status       | Draft                                              |
| Authors      | ANIF Working Group                                 |
| Reviewers    | —                                                  |
| Approved by  | —                                                  |
| Created      | 2026-04-07                                         |
| Last updated | 2026-04-07                                         |
| Replaces     | N/A                                                |
| Related docs | ANIF-701, ANIF-004, ANIF-107, ANIF-724, ANIF-831  |

---

## Abstract

This document defines the four-layer shared accountability model that applies to every autonomous action taken within an ANIF-conformant system. Accountability is shared across designer, deployer, operator, and approver layers. No layer may transfer its accountability to another. Every incident trace MUST resolve to a named human at each layer. An action whose accountability chain cannot be fully resolved MUST be blocked before execution.

---

## 1. Introduction

### 1.1 Purpose

When an autonomous network action causes an incident, accountability must be assignable. "The AI did it" is not an acceptable answer. The accountability chain model ensures that every action traces to named human individuals at four distinct layers, each bearing responsibility for their portion of the decision.

This model does not assign blame after the fact — it assigns responsibility by design. Before any action executes, the accountability chain must be complete. If it is not, the action does not execute.

### 1.2 Scope

This document covers:

- The four accountability layers and the scope of each
- The accountability chain record and its mandatory fields
- Incident trace requirements for post-incident investigation
- The prohibition on accountability transfer between layers
- The relationship between accountability and the audit trail

### 1.3 Out of Scope

This document does not cover:

- Disciplinary or legal consequences of accountability — these are organisational matters
- The governance committee structure (see ANIF-831)
- Role definitions beyond accountability scope (see ANIF-004 for RACI, ANIF-801 for agent roles)
- Incident response procedures (see ANIF-715, ANIF-847)

### 1.4 Intended Audience

- Governance and compliance officers establishing accountability frameworks
- Platform engineers implementing audit record schemas
- HR and legal teams defining organisational accountability obligations
- Auditors and regulators reviewing accountability evidence

---

## 2. Normative References

- ANIF-701 — Ethics Constitution and Core Values (Accountability value)
- ANIF-004 — Roles and RACI
- ANIF-107 — Audit Trail Requirements
- ANIF-724 — Ethics Audit Trail Requirements
- ANIF-831 — AI Governance Structure and Accountability
- RFC 2119 — Key words for use in RFCs to indicate requirement levels

---

## 3. Terms and Definitions

**Accountability layer:** One of four defined roles in the accountability chain. Each layer is occupied by a named human individual for every action.

**Accountability transfer:** The act of a layer citing another layer's decision as grounds for its own accountability exclusion. Accountability transfer is prohibited.

**Concurrent accountability:** All four layers bear accountability simultaneously for their portion of the chain. No layer's accountability is conditional on another layer's failure.

**Incident trace:** The post-incident reconstruction of the accountability chain from the audit log, identifying the decision point and accountable human at each layer.

---

## 4. Four Accountability Layers

Every autonomous action MUST have a named human accountable at each of the following four layers.

### 4.1 Designer Layer

**Who:** The agent author — the engineer, data scientist, or team who designed and built the AI agent.

**Accountability scope:**
- The agent's capability boundaries as declared in its manifest
- Bias present in training data or model design
- Limitations declared (or that should have been declared) in the agent manifest
- The accuracy of non-determinism declarations per ANIF-807
- The adequacy of the deterministic shadow implementation per ANIF-723

**Designer accountability activates when:** The incident is attributable to a design flaw, undisclosed limitation, or training data quality issue that the designer knew or should have known about.

### 4.2 Deployer Layer

**Who:** The platform or DevOps engineer responsible for deploying the agent into the operational environment.

**Accountability scope:**
- The deployment configuration applied to the agent
- The accuracy and completeness of the capability scope signing
- The version of the agent deployed and any version upgrade decisions
- The environment in which the agent operates (production, non-production, test)
- Compliance of the deployment with build-time council conditions (ANIF-903)

**Deployer accountability activates when:** The incident is attributable to a deployment configuration error, incorrect version deployment, or failure to apply build-time council conditions.

### 4.3 Operator Layer

**Who:** The network operator, NOC engineer, or network architect who submitted the intent that the agent acted upon, or who configured the policy environment within which the agent operated.

**Accountability scope:**
- The intent submitted to the pipeline, including its constraints and target
- Policy configuration decisions that affected the agent's operating environment
- Override decisions made or not made during execution
- The decision to allow an intent to proceed into the pipeline without modification

**Operator accountability activates when:** The incident is attributable to an intent that was incorrectly specified, a policy configuration that created unsafe operating conditions, or a failure to exercise override when the situation required it.

### 4.4 Approver Layer

**Who:** The human who approved the action at the governance gate — either the manual reviewer who approved a `manual_review` decision, or the governance committee member who approved a `council_review` decision.

**Accountability scope:**
- The approval decision made at the governance gate
- The adequacy of the review conducted before approval
- The risk acceptance documented at the time of approval
- Any conditions attached to the approval and whether they were satisfied

**Approver accountability is nullable** when the governance mode was `auto` and no human review occurred. In this case, the approver field in the audit record is null, and accountability for the approval decision is distributed across the designer layer (who configured the risk thresholds), the deployer layer (who deployed those thresholds), and the operator layer (who submitted the intent that triggered auto-approval).

---

## 5. Accountability Chain Record

Every audit record MUST include an accountability chain object. The schema extends the base audit record defined in ANIF-107.

### 5.1 Mandatory Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `designer_id` | string | MUST | IAM identity of the agent designer. MUST be resolvable to a named human |
| `deployer_id` | string | MUST | IAM identity of the agent deployer |
| `operator_id` | string | MUST | IAM identity of the operator who submitted the intent |
| `approver_id` | string | MUST if manual_review or council_review | IAM identity of the human approver. Null if governance mode was auto |
| `designer_org_unit` | string | SHOULD | Organisational unit of the designer, for governance reporting |
| `deployer_org_unit` | string | SHOULD | Organisational unit of the deployer |

### 5.2 Identity Resolution

All identity fields MUST be resolvable to a named human individual in the organisation's IAM system at the time the audit record is queried. An identity that cannot be resolved is an incomplete accountability chain. An implementation MUST alert the governance committee when an unresolvable identity is detected in an audit record.

### 5.3 Record Immutability

Accountability chain records are subject to the same immutability requirements as audit records defined in ANIF-107. Records MUST NOT be modified after writing. Correction of a genuine data entry error MUST be made by appending a new record with a reference to the corrected record — not by modifying the original.

---

## 6. Incident Trace Requirements

When an incident occurs, the accountability chain MUST be reconstructable from the audit log.

### 6.1 Reconstruction Timeline

The accountability chain for an incident MUST be reconstructable within 30 minutes of the incident being declared. Implementations MUST provide tooling or API endpoints that support rapid chain reconstruction from an intent_id or audit record_id.

### 6.2 Decision Point Identification

The incident trace MUST identify the specific decision point at each layer where accountability attaches:

- **Designer layer:** Which agent design decision contributed to the incident
- **Deployer layer:** Which deployment configuration or version choice contributed
- **Operator layer:** Which intent field or policy configuration contributed
- **Approver layer:** Which approval decision contributed, or why auto-approval was permitted

### 6.3 Trace Completeness

An incident trace is complete when all four layers have been identified with named individuals and specific decision points. A partial trace MUST be flagged and escalated to the governance committee until it is resolved.

---

## 7. No Accountability Transfer

A layer MUST NOT cite another layer's decision as grounds for its own accountability exclusion. The following patterns are explicitly prohibited:

- A designer citing the deployer's configuration as the reason the agent behaved incorrectly
- A deployer citing the designer's undisclosed limitation as the reason deployment proceeded
- An operator citing the agent's autonomous decision as the reason the intent proceeded
- An approver citing the risk score as the reason manual review was not thorough

All four layers bear concurrent accountability for their portion of the chain. The conduct of one layer does not reduce the accountability of another.

---

## 8. Accountability and Governance Reporting

Accountability chain data feeds governance reporting per ANIF-837. Monthly governance reports MUST include:

- Number of incidents by primary accountable layer
- Trend in accountability chain completeness rate
- Count of unresolvable identity alerts
- Patterns in designer or deployer accountability that indicate systemic training or process issues

---

## 9. Conformance Requirements

Every audit record MUST contain a complete accountability chain with all mandatory fields populated.

An action whose accountability chain cannot be completed before execution MUST be blocked. The blocking reason MUST be logged.

Records with incomplete accountability chains MUST be flagged and escalated to the governance committee within 24 hours of detection.

An implementation MUST NOT permit the accountability chain to be populated with placeholder or synthetic identities. All identity values MUST refer to real individuals resolvable in the organisation's IAM system.

---

## 10. Security Considerations

Accountability records are a target for adversarial modification. An attacker who can alter accountability chain records can evade responsibility for induced failures. The append-only requirement from ANIF-107 MUST be applied to accountability chain records. Access to modify accountability records MUST be restricted to the audit system service account only — no human operator MUST have direct write access.

---

## 11. Operational Considerations

Organisations MUST ensure that all four accountability roles are staffed before deploying AI agents in production. Deploying AI agents in environments where the designer, deployer, operator, or approver roles are not filled by identifiable individuals is a conformance violation.

When an individual leaves the organisation, their accountability chain entries MUST be preserved in the IAM system as read-only historical records. Their successor MUST be identified and recorded for all subsequently deployed agents.

---

## Appendix A: Change History

| Version | Date | Author | Changes |
|---|---|---|---|
| 0.1.0 | 2026-04-07 | ANIF Working Group | Initial draft |
