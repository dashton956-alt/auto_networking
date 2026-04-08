# ANIF-303: Policy Conflict Resolution and Precedence

| Field        | Value                              |
|--------------|------------------------------------|
| Doc ID       | ANIF-303                           |
| Series       | Core                               |
| Version      | 0.1.0                              |
| Status       | Draft                              |
| Authors      | ANIF Working Group                 |
| Reviewers    | —                                  |
| Approved by  | —                                  |
| Created      | 2026-04-07                         |
| Last updated | 2026-04-07                         |
| Replaces     | N/A                                |
| Related docs | ANIF-302, ANIF-304, ANIF-406       |

---

## Abstract

This document is the normative specification for policy conflict detection, conflict resolution, and precedence handling within the ANIF Policy Engine. When two or more policies produce contradictory decisions for the same constraint in an intent, conflict detection identifies the collision and resolution logic determines which decision governs. This document defines the precedence hierarchy, the resolution algorithm, the handling of equal-precedence conflicts, and the audit obligations that apply to every resolution event.

---

## 1. Introduction

### 1.1 Purpose

To define, unambiguously and normatively, how the ANIF framework behaves when active policies produce contradictory decisions so that pipeline behaviour is deterministic, traceable, and compliant with governance requirements.

### 1.2 Scope

This document covers:

- The definition of a policy conflict.
- When conflict detection runs in the pipeline.
- The four-level precedence hierarchy.
- The resolution algorithm for different-precedence conflicts.
- The handling and escalation of equal-precedence conflicts.
- Audit obligations for all conflict events.
- Example conflict scenarios with resolution outcomes.

### 1.3 Out of Scope

- Policy rule syntax and the condition grammar (see ANIF-302).
- The risk scoring that consumes the resolved policy set (see ANIF-304).
- Human-in-the-loop governance mechanics triggered by manual_review mode (see ANIF-100 series).

### 1.4 Intended Audience

- Implementers of the conflict detection and resolution subsystem within the policy engine.
- Policy authors who need to understand how their policies interact.
- Governance and compliance reviewers auditing policy conflict records.
- Platform architects designing the policy evaluation pipeline.

---

## 2. Normative References

- ANIF-302: Policy Engine Specification
- ANIF-304: Risk and Trust Quantification
- ANIF-406: Audit Log Specification
- RFC 2119: Key words for use in RFCs to indicate requirement levels

---

## 3. Terms and Definitions

**Policy Conflict**
A condition in which two or more active policies produce contradictory decisions (`allow` vs `deny`, or `allow` vs `warn`) for the same intent field or constraint scope.

**Contradictory Decisions**
Two decisions are contradictory if and only if one is `deny` and the other is `allow` or `warn`, for the same constraint or intent field evaluated by both policies.

**Precedence Category**
A classification applied to every policy that determines its priority in conflict resolution. One of: `compliance`, `security`, `availability`, `performance`.

**Precedence Hierarchy**
The ordered ranking of precedence categories from highest to lowest:
`compliance > security > availability > performance`

**Winning Policy**
The policy whose decision is applied when a conflict exists between two policies of different precedence categories.

**Equal-Precedence Conflict**
A conflict between two policies that share the same precedence category. These conflicts cannot be resolved by the hierarchy and MUST be escalated.

**Escalation**
The process of suspending autonomous pipeline progression and routing the intent to human review due to an unresolvable equal-precedence conflict.

**Resolved Policy Set**
The set of policies whose final decisions survive conflict resolution and are forwarded to the risk engine.

---

## 4. Conflict Detection

### 4.1 When Conflict Detection Runs

Conflict detection MUST run after all individual policy evaluations have completed and before risk scoring begins. The conflict detection phase MUST NOT modify individual policy evaluation results; it operates on the complete set of results as a read-only input.

The sequence is:

```
Individual policy evaluation (ANIF-302)
          ↓
Conflict detection (this document)
          ↓
Conflict resolution (this document)
          ↓
Resolved policy set forwarded to risk engine (ANIF-304)
```

### 4.2 Conflict Detection Criteria

A conflict exists between policy A and policy B if and only if:

1. Both policies evaluated the same intent field or constraint scope (i.e., their triggered rules reference overlapping field paths), AND
2. Their decisions are contradictory (one produced `deny` or `warn`, the other produced `allow`; or one produced `deny`, the other produced `warn`).

Formally, for policies A and B with decisions `d_A` and `d_B`:
- A conflict exists if `d_A ≠ d_B` AND at least one of `d_A`, `d_B` is `deny`.
- A conflict also exists if `d_A = warn` AND `d_B = allow` (or vice versa), as these represent different risk postures that require explicit resolution.

### 4.3 Conflict Detection MUST Be Exhaustive

The detection algorithm MUST compare every pair of policy results in the evaluated set. If n policies are evaluated, all n*(n-1)/2 pairs MUST be checked. The detection algorithm MUST NOT short-circuit after finding the first conflict.

---

## 5. Precedence Hierarchy (Normative)

Every policy MUST declare a `category` field (see ANIF-302, Section 5). The precedence hierarchy is:

| Rank | Category     | Rationale                                                              |
|------|--------------|------------------------------------------------------------------------|
| 1    | compliance   | Regulatory and legal obligations that cannot be overridden by technical preference. |
| 2    | security     | Security controls that protect against active threats and data breach.  |
| 3    | availability | Service continuity requirements that affect business operations.        |
| 4    | performance  | Optimisation preferences that improve but do not define service viability. |

This ordering is normative. Implementations MUST apply it exactly. The hierarchy MUST NOT be configurable at runtime; changes require a framework version update.

---

## 6. Conflict Resolution Algorithm

### 6.1 Different-Precedence Conflict Resolution

When a conflict is detected between policy A (category `cat_A`) and policy B (category `cat_B`) where `cat_A ≠ cat_B`:

1. Determine which policy has higher precedence according to the hierarchy in Section 5.
2. The higher-precedence policy's decision MUST be applied to the resolved policy set.
3. The lower-precedence policy's decision MUST be overridden and NOT included in the resolved policy set.
4. A conflict record MUST be created containing:
   - `conflict_id`: UUID v4
   - `policies`: [policy_A_name, policy_B_name]
   - `constraint`: the field path(s) in contention
   - `decision_a` and `decision_b`: the original decisions
   - `winner`: the name of the winning policy
   - `loser`: the name of the overridden policy
   - `resolution_rationale`: a human-readable explanation citing the precedence categories
   - `resolution_type`: `"precedence_hierarchy"`
5. The conflict record MUST be written to the audit log.
6. The conflict record MUST be included in the policy evaluation result returned to the caller.

**Example:** A `compliance` policy denies an intent because `constraints.encryption = false`. A `performance` policy would allow the same intent to proceed. The `compliance` policy wins. The `deny` decision is applied. The `performance` `allow` is overridden.

### 6.2 Equal-Precedence Conflict Resolution

When a conflict is detected between policy A and policy B where they share the same precedence category (`cat_A = cat_B`):

1. The conflict CANNOT be resolved by precedence hierarchy.
2. Both policy decisions MUST be flagged in the conflict record.
3. The overall result MUST be set to `warn` (NOT `fail`, to allow the governance layer to handle it).
4. The pipeline MUST NOT proceed autonomously past the governance stage.
5. The decision engine MUST set `mode = manual_review` for intents with unresolved equal-precedence conflicts (see ANIF-305).
6. An escalation ticket MUST be created with:
   - `ticket_id`: UUID v4
   - `conflict_id`: the conflict UUID
   - `intent_id`: the intent being evaluated
   - `policies_in_conflict`: list of policy names
   - `description`: summary of the contradictory decisions
   - `created_at`: ISO 8601 timestamp
7. The conflict record MUST include `resolution_type: "escalated"` and the `ticket_id`.
8. The conflict record and escalation ticket MUST be written to the audit log.

**Example:** Two `security` policies conflict — one requires explicit zone declaration (deny if absent), another permits operation without zone scoping for internal services (allow). Both are `security` category. Neither wins by precedence. The conflict is escalated.

### 6.3 Warn vs Allow Conflicts

When policy A produces `warn` and policy B produces `allow` for overlapping constraints:

- This is a lower-severity conflict; no deny is produced.
- The resolution MUST apply the higher-precedence policy's decision.
- If categories are equal, the `warn` decision MUST be preserved (conservative default) and the conflict recorded.
- `warn` decisions are NEVER upgraded to `deny` by conflict resolution.

### 6.4 Resolution Is Not Transitive for Three-Party Conflicts

When three or more policies conflict simultaneously:

1. All pairwise conflicts MUST be detected and recorded individually.
2. Resolution is applied pairwise: for each pair, the higher-precedence policy wins.
3. The final resolved policy set reflects all pairwise resolutions applied in the order: compliance decisions first, then security, then availability, then performance.
4. If pairwise resolution produces an inconsistency (e.g., policy A beats B, B beats C, but C beats A — which cannot occur with a strict hierarchy), implementation MUST treat this as an equal-precedence conflict and escalate.

---

## 7. Built-In Policy Conflict Scenarios

### 7.1 Encryption: Compliance vs Performance

| Policy         | Category    | Decision | Reason                                    |
|----------------|-------------|----------|-------------------------------------------|
| pci_compliant  | compliance  | deny     | `constraints.encryption = false`         |
| perf_optimiser | performance | allow    | Encryption adds unacceptable latency overhead |

**Resolution:** `pci_compliant` wins. `deny` is applied. `perf_optimiser` allow is overridden.
**Rationale:** `compliance (rank 1) > performance (rank 4)`

### 7.2 Zone Restriction: Two Security Policies

| Policy              | Category | Decision | Reason                                          |
|---------------------|----------|----------|-------------------------------------------------|
| no_public_ingress   | security | deny     | `constraints.allowed_zones` is absent           |
| internal_bypass     | security | allow    | Internal service flag exempts zone requirement  |

**Resolution:** Equal-precedence conflict. Both flagged. `mode = manual_review`. Escalation ticket created.
**Rationale:** Both are `security (rank 2)`. Hierarchy cannot resolve.

### 7.3 Region: Compliance vs Availability

| Policy           | Category     | Decision | Reason                                                  |
|------------------|--------------|----------|---------------------------------------------------------|
| data_residency   | compliance   | deny     | `constraints.region = APAC` not in EU-only approved list|
| ha_availability  | availability | allow    | APAC replica required for failover SLA                  |

**Resolution:** `data_residency` wins. `deny` is applied. Availability allow is overridden.
**Rationale:** `compliance (rank 1) > availability (rank 3)`

---

## 8. Resolved Policy Set

After conflict resolution, the resolved policy set MUST:

- Contain exactly one final decision per evaluated policy.
- Reflect winning decisions for all resolved conflicts.
- NOT contain any overridden decisions from losing policies.
- Be the sole input to the risk engine for policy-based risk factor calculation (ANIF-304).

The resolved policy set MUST be included in the policy evaluation result returned to the caller and MUST be stored in the intent's pipeline record.

---

## 9. Audit Requirements

All conflict events MUST be written to the audit log (ANIF-406). The following audit obligations apply:

1. Every detected conflict MUST produce an audit record, even if it is resolved without escalation.
2. The audit record MUST include the full `conflict_id`, `intent_id`, `policies`, `decisions`, `resolution_type`, and `resolution_rationale`.
3. Equal-precedence conflict escalation MUST produce a separate audit record for the escalation ticket creation.
4. Audit records for conflict resolution MUST be written atomically with the policy evaluation result — if the evaluation result is written, all associated conflict records MUST also be written.
5. Conflict audit records MUST NOT be modifiable after the fact. The audit log for conflict events MUST be append-only.

---

## 10. Conformance Requirements

1. Conflict detection MUST run after all individual policy evaluations and before risk scoring.
2. Conflict detection MUST be exhaustive: all policy pairs MUST be checked.
3. Every policy MUST declare a `category` field; the engine MUST reject policies without a category.
4. The precedence hierarchy (`compliance > security > availability > performance`) MUST be applied exactly as defined.
5. Higher-precedence policy decisions MUST override lower-precedence decisions; the override MUST be recorded.
6. Equal-precedence conflicts MUST result in `mode = manual_review` and MUST create an escalation ticket.
7. All conflict resolutions MUST be written to the audit log.
8. The resolved policy set MUST contain exactly one final decision per policy.
9. The `warn` decision MUST NOT be upgraded to `deny` by conflict resolution logic.

---

## 11. Security Considerations

- Escalation tickets are sensitive artifacts as they reveal active policy conflicts. Access to escalation ticket data MUST be restricted to authorised operators and auditors.
- Conflict records in the audit log MUST be tamper-evident. Any modification to a conflict record after creation MUST be detected and alerted.
- The precedence hierarchy MUST be hard-coded in the implementation and MUST NOT be configurable via API or configuration file without a framework release process, to prevent hierarchy manipulation attacks.

---

## 12. Operational Considerations

- Frequent equal-precedence conflicts indicate a policy set design problem. Platform teams SHOULD review the active policy set if escalation tickets are being generated at high volume.
- Policy authors SHOULD assign the lowest applicable category to their policies (e.g., use `availability` rather than `compliance` for SLA-related policies) to minimise unintended hierarchy wins.
- A policy conflict dashboard SHOULD be maintained to surface recurring conflicts for policy consolidation.

---

## Appendix A: Examples

### A.1 Full Conflict Resolution Record (JSON)

```json
{
  "conflict_id": "c1a2b3d4-0001-4abc-9000-ffff00001111",
  "intent_id": "f3a9b2c1-4d7e-4f88-9012-abcdef012345",
  "policies": ["pci_compliant", "perf_optimiser"],
  "constraint": "constraints.encryption",
  "decision_a": "deny",
  "decision_b": "allow",
  "winner": "pci_compliant",
  "loser": "perf_optimiser",
  "resolution_rationale": "pci_compliant (compliance, rank 1) overrides perf_optimiser (performance, rank 4) per precedence hierarchy",
  "resolution_type": "precedence_hierarchy",
  "resolved_at": "2026-04-07T10:00:02Z"
}
```

### A.2 Equal-Precedence Escalation Record (JSON)

```json
{
  "conflict_id": "c1a2b3d4-0002-4abc-9000-ffff00002222",
  "intent_id": "a1b2c3d4-4444-4abc-8000-000011112222",
  "policies": ["no_public_ingress", "internal_bypass"],
  "constraint": "constraints.allowed_zones",
  "decision_a": "deny",
  "decision_b": "allow",
  "winner": null,
  "loser": null,
  "resolution_rationale": "Both policies are category 'security' (rank 2); equal-precedence conflict cannot be resolved by hierarchy",
  "resolution_type": "escalated",
  "escalation_ticket_id": "t9a8b7c6-0001-4def-a000-123456789abc",
  "resolved_at": null,
  "detected_at": "2026-04-07T10:00:02Z"
}
```

### A.3 Escalation Ticket (JSON)

```json
{
  "ticket_id": "t9a8b7c6-0001-4def-a000-123456789abc",
  "conflict_id": "c1a2b3d4-0002-4abc-9000-ffff00002222",
  "intent_id": "a1b2c3d4-4444-4abc-8000-000011112222",
  "policies_in_conflict": ["no_public_ingress", "internal_bypass"],
  "description": "Two security-category policies produce contradictory decisions on constraints.allowed_zones. Manual review required to determine which policy should govern this intent.",
  "status": "open",
  "created_at": "2026-04-07T10:00:02Z",
  "resolved_at": null
}
```

---

## Appendix B: Change History

| Version | Date       | Author             | Description   |
|---------|------------|--------------------|---------------|
| 0.1.0   | 2026-04-07 | ANIF Working Group | Initial draft |
