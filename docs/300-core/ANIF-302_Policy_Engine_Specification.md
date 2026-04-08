# ANIF-302: Policy Engine Specification

| Field        | Value                              |
|--------------|------------------------------------|
| Doc ID       | ANIF-302                           |
| Series       | Core                               |
| Version      | 0.1.0                              |
| Status       | Draft                              |
| Authors      | ANIF Working Group                 |
| Reviewers    | —                                  |
| Approved by  | —                                  |
| Created      | 2026-04-07                         |
| Last updated | 2026-04-07                         |
| Replaces     | N/A                                |
| Related docs | ANIF-300, ANIF-303, ANIF-304       |

---

## Abstract

This document is the normative specification for the ANIF Policy Engine. It defines the policy schema, the condition grammar used to express policy rules, the complete set of built-in policies and their evaluation logic, the evaluation result schema, and the operational modes of the engine. Policy evaluation MUST be 100% deterministic: given the same intent and the same active policy set, the engine MUST always produce the same result. Implementers of the `/evaluate-policy` endpoint MUST comply with this specification in full.

---

## 1. Introduction

### 1.1 Purpose

To provide a complete, normative definition of how the ANIF Policy Engine evaluates network intents against the active policy set, so that policy behaviour is predictable, auditable, and independently verifiable.

### 1.2 Scope

This document covers:

- The policy schema and all normative field requirements.
- The policy condition grammar: syntax, operators, and evaluation semantics.
- All four built-in policy definitions with their normative evaluation rules.
- The evaluation result schema returned by the engine.
- The dry-run evaluation mode.
- Determinism requirements.

### 1.3 Out of Scope

- Policy conflict detection and resolution algorithms (see ANIF-303).
- Risk scoring that consumes policy results (see ANIF-304).
- Policy authoring tooling and lifecycle management.
- Dynamic policy loading and hot-reload behaviour (future work).

### 1.4 Intended Audience

- Implementers of the `/evaluate-policy` endpoint.
- Policy authors creating custom policy rules.
- Security and compliance reviewers auditing policy definitions.
- Developers integrating the policy engine into the ANIF pipeline.

---

## 2. Normative References

- ANIF-300: Intent Framework Overview
- ANIF-301: Intent Authoring Standard
- ANIF-303: Policy Conflict Resolution and Precedence
- ANIF-304: Risk and Trust Quantification
- RFC 2119: Key words for use in RFCs to indicate requirement levels

---

## 3. Terms and Definitions

**Policy**
A named, versioned rule set that tests an intent against one or more conditions and produces an allow, deny, or warn decision.

**Condition**
A single predicate expressed in the ANIF condition grammar that tests a specific field of the intent against a value.

**Policy Rule**
A pair of a condition expression and an action (`allow`, `deny`, `warn`). A policy MUST contain one or more rules.

**Policy Evaluation Result**
The structured output produced by evaluating a single policy against an intent. Contains the policy name, triggered rule, and decision.

**Overall Result**
The aggregate result of evaluating all applicable policies against an intent. One of `pass`, `fail`, or `warn`.

**Resolved Policy Set**
The set of policies whose decisions survive conflict resolution (defined in ANIF-303) and are forwarded to the risk engine.

**Dry-Run Mode**
An evaluation mode in which the engine produces a full result but does not write an audit record and does not update pipeline state.

---

## 4. Determinism Requirement

Policy evaluation MUST be 100% deterministic.

- Given the same intent document and the same active policy set, the engine MUST always produce identical `policy_results`, `conflicts`, `overall_result`, and `resolved_policy_set`.
- The engine MUST NOT incorporate any runtime-variable inputs (timestamps, random values, network calls, or external state queries) during condition evaluation.
- Any dependency on external data (e.g., an approved region list for `data_residency`) MUST be resolved before evaluation begins and MUST be treated as a fixed input for the duration of that evaluation call.
- If the engine cannot guarantee determinism due to a missing input, it MUST return an error rather than proceed with a non-deterministic evaluation.

---

## 5. Policy Schema (Normative)

Every policy document MUST conform to the following schema.

```yaml
type: object
required: [name, rules]
properties:
  name:
    type: string
    description: >
      Unique identifier for this policy. MUST be a non-empty string.
      MUST be unique within the active policy set.

  category:
    type: string
    enum: [compliance, security, availability, performance]
    description: >
      The precedence category of this policy. MUST be declared for
      all policies. Used by the conflict resolution engine (ANIF-303)
      to determine which policy wins when two policies conflict.

  version:
    type: string
    description: >
      Semantic version string for this policy definition.
      SHOULD follow semver format (e.g., "1.0.0").

  rules:
    type: array
    minItems: 1
    description: >
      Ordered list of rules. MUST contain at least one rule.
      Rules are evaluated in order; the first rule whose condition
      evaluates to true determines the policy decision. If no rule
      matches, the policy MUST produce a default decision of allow.
    items:
      type: object
      required: [condition, action]
      properties:
        condition:
          type: string
          description: >
            A condition expression in the ANIF condition grammar
            (Section 6). MUST be a valid, parseable expression.
        action:
          type: string
          enum: [allow, deny, warn]
          description: >
            The decision to apply when the condition evaluates to true.
        reason:
          type: string
          description: >
            Human-readable explanation of why this rule exists.
            SHOULD be provided for all deny and warn actions.
```

---

## 6. Policy Condition Grammar

### 6.1 Expression Syntax

A condition expression MUST conform to the following grammar:

```
condition  ::= field_path ":" operator ":" value
field_path ::= identifier ("." identifier)*
operator   ::= "equals" | "not_equals" | "greater_than" | "less_than"
             | "contains" | "not_contains" | "in_list" | "not_in_list"
value      ::= string_literal | number_literal | boolean_literal | list_literal
list_literal ::= "[" (value ("," value)*)? "]"
```

**Examples:**
- `constraints.encryption:equals:false`
- `environment:equals:prod`
- `objectives.availability_percent:greater_than:99.98`
- `constraints.region:not_in_list:[EU,US]`
- `constraints.allowed_zones:contains:eu-west-1a`

### 6.2 Operator Definitions

| Operator       | Applicable Types        | Semantics                                                                 |
|----------------|-------------------------|---------------------------------------------------------------------------|
| equals         | string, number, boolean | Field value equals the specified literal. Type coercion is NOT performed. |
| not_equals     | string, number, boolean | Field value does not equal the specified literal.                         |
| greater_than   | number                  | Field value is strictly greater than the specified number.                |
| less_than      | number                  | Field value is strictly less than the specified number.                   |
| contains       | array, string           | Array field contains the specified value; or string field contains substring. |
| not_contains   | array, string           | Array field does not contain the specified value; or string does not contain substring. |
| in_list        | string, number          | Field value is one of the values in the specified list literal.            |
| not_in_list    | string, number          | Field value is not in the specified list literal.                          |

### 6.3 Missing Field Behaviour

When a condition references a field path that is not present in the intent document:

- The `equals` and `in_list` operators MUST evaluate to `false` for a missing field.
- The `not_equals` and `not_in_list` operators MUST evaluate to `true` for a missing field.
- The `contains` operator on a missing array MUST evaluate to `false`.
- The `not_contains` operator on a missing array MUST evaluate to `true`.
- Numeric comparison operators (`greater_than`, `less_than`) MUST evaluate to `false` for a missing field and MUST NOT raise an error.

### 6.4 Compound Conditions (Future)

Compound conditions using boolean connectives (`AND`, `OR`, `NOT`) are reserved for a future version. Implementations MUST NOT accept compound condition expressions in version 0.x. A single condition expression per rule MUST be enforced.

---

## 7. Built-In Policy Definitions (Normative)

The following four policies are built into the ANIF framework and are ALWAYS active regardless of the `policies` field in the intent. They cannot be disabled by the intent author.

### 7.1 zero_trust

**Category:** security
**Description:** All constraints must be explicitly declared. Any intent that leaves a security-relevant constraint unspecified is denied by default.

**Normative rule:** If any of the following fields is absent from the intent, the policy MUST produce a `deny` decision:
- `constraints.encryption`
- `constraints.region`
- `constraints.allowed_zones`

**Policy document:**
```yaml
name: zero_trust
category: security
version: "1.0.0"
rules:
  - condition: "constraints.encryption:equals:false"
    action: deny
    reason: "Zero trust requires encryption to be explicitly enabled"
  - condition: "constraints.region:not_in_list:[EU,US,APAC]"
    action: deny
    reason: "Zero trust requires a valid region to be declared"
```

**Additional logic (implemented in engine, not expressible in rule grammar v0.1):** If `constraints.allowed_zones` is absent, `zero_trust` MUST produce a `deny` decision with reason `"zero_trust: allowed_zones must be explicitly declared"`.

### 7.2 no_public_ingress

**Category:** security
**Description:** Services MUST NOT be accessible from the public internet. At least one allowed zone must be specified to restrict ingress scope.

**Normative rule:** If `constraints.allowed_zones` is absent or is an empty array, the policy MUST produce a `deny` decision.

**Policy document:**
```yaml
name: no_public_ingress
category: security
version: "1.0.0"
rules:
  - condition: "constraints.allowed_zones:equals:[]"
    action: deny
    reason: "Public ingress is prohibited; at least one allowed zone must be specified"
```

**Additional logic:** When `constraints.allowed_zones` is entirely absent (not just empty), the engine MUST treat this condition as matching and MUST produce a `deny` decision.

### 7.3 pci_compliant

**Category:** compliance
**Description:** Services subject to PCI-DSS requirements MUST have data-in-transit encryption enabled at all times.

**Normative rule:** If `constraints.encryption` equals `false`, or if `constraints.encryption` is absent, the policy MUST produce a `deny` decision.

**Policy document:**
```yaml
name: pci_compliant
category: compliance
version: "1.0.0"
rules:
  - condition: "constraints.encryption:equals:false"
    action: deny
    reason: "PCI compliance requires encryption to be true"
  - condition: "constraints.encryption:not_equals:true"
    action: deny
    reason: "PCI compliance requires encryption to be explicitly set to true"
```

### 7.4 data_residency

**Category:** compliance
**Description:** Service data MUST reside within an approved geographic region. The approved region list is maintained externally and MUST be resolved before evaluation.

**Normative rule:** If `constraints.region` is not present in the service's approved region list, the policy MUST produce a `deny` decision.

**Policy document (parameterised):**
```yaml
name: data_residency
category: compliance
version: "1.0.0"
rules:
  - condition: "constraints.region:not_in_list:[{approved_regions}]"
    action: deny
    reason: "Data residency policy: region is not in the approved region list for this service"
```

The `{approved_regions}` parameter MUST be resolved to the service-specific approved region list before evaluation. Resolving this list is a prerequisite step and MUST be completed before the engine begins condition evaluation.

---

## 8. Policy Evaluation Algorithm

The engine MUST evaluate policies in the following order and manner:

1. **Resolve active policy set:** Combine globally active policies (always includes all four built-in policies) with any policy names declared in the intent's `policies` field. Deduplicate.
2. **For each policy in the active policy set:**
   a. Evaluate rules in order of appearance.
   b. The first rule whose condition evaluates to `true` determines the policy decision.
   c. If no rule matches, the policy decision is `allow`.
   d. Record the triggered rule (or "no rule matched") and the decision.
3. **Aggregate results:** Collect all individual policy results.
4. **Determine overall_result:**
   - If any policy produced `deny` → `overall_result = fail`
   - If no policy produced `deny` but at least one produced `warn` → `overall_result = warn`
   - If all policies produced `allow` → `overall_result = pass`
5. **Detect conflicts:** Pass results to conflict detection (ANIF-303).
6. **Return evaluation result** (Section 9).

---

## 9. Policy Evaluation Result Schema

The engine MUST return a response conforming to the following structure.

```json
{
  "intent_id": "<UUID>",
  "evaluation_id": "<UUID>",
  "overall_result": "pass | fail | warn",
  "policy_results": [
    {
      "policy_name": "pci_compliant",
      "category": "compliance",
      "decision": "deny | allow | warn",
      "triggered_rule": "<condition expression or 'no rule matched'>",
      "reason": "<human-readable reason>"
    }
  ],
  "conflicts": [
    {
      "conflict_id": "<UUID>",
      "policies": ["<policy_name_a>", "<policy_name_b>"],
      "constraint": "<field path>",
      "decision_a": "allow | deny | warn",
      "decision_b": "allow | deny | warn",
      "resolution": "<winning_policy_name or 'escalated'>",
      "resolution_rationale": "<explanation>"
    }
  ],
  "resolved_policy_set": [
    {
      "policy_name": "<name>",
      "final_decision": "allow | deny | warn"
    }
  ],
  "evaluated_at": "<ISO 8601 timestamp>",
  "dry_run": false
}
```

All fields are REQUIRED unless marked otherwise. The `conflicts` array MAY be empty if no conflicts were detected.

---

## 10. Dry-Run Mode

When the `/evaluate-policy` endpoint is called with `dry_run=true` in the request body:

- The engine MUST perform a full evaluation and return the complete result.
- The engine MUST NOT write any record to the audit log.
- The engine MUST NOT update any pipeline state or intent status.
- The response MUST include `"dry_run": true`.
- The `evaluation_id` returned in a dry-run response MUST NOT be referenced in subsequent pipeline calls; it is ephemeral.

Dry-run mode is intended for policy testing and pre-submission validation tooling.

---

## 11. Conformance Requirements

1. The engine MUST be 100% deterministic: identical inputs MUST always produce identical outputs.
2. All four built-in policies (zero_trust, no_public_ingress, pci_compliant, data_residency) MUST be active for every evaluation.
3. Custom policies declared in the intent MUST be evaluated in addition to built-in policies, not instead of them.
4. The engine MUST evaluate all rules in a policy in declaration order and MUST stop at the first matching rule.
5. A policy with no matching rule MUST produce an `allow` decision.
6. The overall_result aggregation rules defined in Section 8 MUST be applied exactly.
7. Dry-run mode MUST NOT produce audit records or pipeline state changes.
8. Every evaluation MUST produce an `evaluation_id` (UUID v4).
9. The `conflicts` array MUST be populated by conflict detection before the result is returned.
10. The engine MUST reject policy documents that do not conform to the policy schema.

---

## 12. Security Considerations

- Policy documents MUST be stored in an access-controlled repository. Only authorised principals MAY add or modify policies.
- The built-in policies MUST NOT be modifiable by intent authors or pipeline operators. Modification of built-in policy definitions MUST require a framework release process.
- Policy evaluation results MUST be signed or checksummed before forwarding to the risk engine to prevent tampering.
- Dry-run mode MUST NOT be accessible in production pipelines without explicit authorisation, as it could be used to probe policy logic without leaving an audit trail.

---

## 13. Operational Considerations

- Policy rule sets SHOULD be tested in dry-run mode before deployment to production.
- The approved region list for `data_residency` MUST be kept up-to-date. Stale region lists will cause policy denials that do not reflect actual compliance requirements.
- Implementations SHOULD expose a policy listing endpoint so operators can inspect the active policy set at any time.
- In high-throughput deployments, policy evaluation results MAY be cached for identical intent documents within a short TTL (suggested maximum: 60 seconds). Cache invalidation MUST occur immediately when the active policy set changes.

---

## Appendix A: Examples

### A.1 Policy Evaluation Request

```json
{
  "intent_id": "f3a9b2c1-4d7e-4f88-9012-abcdef012345",
  "dry_run": false
}
```

### A.2 Successful Policy Pass Result

```json
{
  "intent_id": "f3a9b2c1-4d7e-4f88-9012-abcdef012345",
  "evaluation_id": "e7c1a2b3-0001-4bcd-8000-aabbccdd1234",
  "overall_result": "pass",
  "policy_results": [
    {
      "policy_name": "zero_trust",
      "category": "security",
      "decision": "allow",
      "triggered_rule": "no rule matched",
      "reason": "All required constraints are explicitly declared"
    },
    {
      "policy_name": "pci_compliant",
      "category": "compliance",
      "decision": "allow",
      "triggered_rule": "no rule matched",
      "reason": "Encryption is enabled"
    },
    {
      "policy_name": "data_residency",
      "category": "compliance",
      "decision": "allow",
      "triggered_rule": "no rule matched",
      "reason": "Region EU is in the approved region list"
    },
    {
      "policy_name": "no_public_ingress",
      "category": "security",
      "decision": "allow",
      "triggered_rule": "no rule matched",
      "reason": "allowed_zones is specified and non-empty"
    }
  ],
  "conflicts": [],
  "resolved_policy_set": [
    {"policy_name": "zero_trust", "final_decision": "allow"},
    {"policy_name": "pci_compliant", "final_decision": "allow"},
    {"policy_name": "data_residency", "final_decision": "allow"},
    {"policy_name": "no_public_ingress", "final_decision": "allow"}
  ],
  "evaluated_at": "2026-04-07T10:00:01Z",
  "dry_run": false
}
```

### A.3 Policy Denial Result

```json
{
  "intent_id": "aabbccdd-0000-4abc-8000-000011112222",
  "evaluation_id": "e7c1a2b3-0002-4bcd-8000-aabbccdd5678",
  "overall_result": "fail",
  "policy_results": [
    {
      "policy_name": "pci_compliant",
      "category": "compliance",
      "decision": "deny",
      "triggered_rule": "constraints.encryption:equals:false",
      "reason": "PCI compliance requires encryption to be true"
    }
  ],
  "conflicts": [],
  "resolved_policy_set": [
    {"policy_name": "pci_compliant", "final_decision": "deny"}
  ],
  "evaluated_at": "2026-04-07T10:00:01Z",
  "dry_run": false
}
```

### A.4 Custom Policy Definition (YAML)

```yaml
name: internal_only
category: security
version: "1.0.0"
rules:
  - condition: "constraints.region:not_in_list:[EU,US]"
    action: deny
    reason: "This service is restricted to EU and US regions only"
  - condition: "objectives.availability_percent:less_than:99.0"
    action: warn
    reason: "Availability target below internal SLA baseline of 99.0%"
```

---

## Appendix B: Change History

| Version | Date       | Author             | Description   |
|---------|------------|--------------------|---------------|
| 0.1.0   | 2026-04-07 | ANIF Working Group | Initial draft |
