# ANIF-301: Intent Authoring Standard

| Field        | Value                              |
|--------------|------------------------------------|
| Doc ID       | ANIF-301                           |
| Series       | Core                               |
| Version      | 0.1.0                              |
| Status       | Draft                              |
| Authors      | ANIF Working Group                 |
| Reviewers    | —                                  |
| Approved by  | —                                  |
| Created      | 2026-04-07                         |
| Last updated | 2026-04-07                         |
| Replaces     | N/A                                |
| Related docs | ANIF-300, ANIF-302, ANIF-600       |

---

## Abstract

This document is the normative specification for how ANIF intents MUST be authored. It defines every field in the intent schema, specifies required versus optional fields, documents all validation rules applied at submission time, and provides canonical examples of valid and invalid intents. Authors of intent documents and implementers of the `/validate-intent` endpoint MUST comply with this standard.

---

## 1. Introduction

### 1.1 Purpose

To provide an unambiguous, normative reference for intent document structure and content so that intent authors, tooling developers, and validation engine implementers share a single authoritative definition of a well-formed intent.

### 1.2 Scope

This document covers:

- The canonical intent schema with normative field descriptions.
- Required and optional field classifications.
- Default values for optional fields when omitted.
- All field-level and cross-field validation rules applied by the framework.
- Examples of valid and invalid intents with expected validation responses.
- The procedure for updating an intent (re-submission).

### 1.3 Out of Scope

- Policy evaluation logic (see ANIF-302).
- Risk scoring (see ANIF-304).
- API authentication and authorisation (see ANIF-500 series).

### 1.4 Intended Audience

- Network operators and engineers who author intent documents.
- Tooling and SDK developers building intent submission interfaces.
- Implementers of the `/validate-intent` API endpoint.
- Compliance reviewers verifying that intent submission controls are correctly implemented.

---

## 2. Normative References

- ANIF-300: Intent Framework Overview
- ANIF-302: Policy Engine Specification
- ANIF-600: Annexes (Schema Registry)
- RFC 2119: Key words for use in RFCs to indicate requirement levels

---

## 3. Terms and Definitions

**Required field**
A field that MUST be present in a submitted intent document. Absence of a required field MUST cause validation to fail with an error.

**Optional field**
A field that MAY be omitted. When omitted, the framework MUST apply the specified default value.

**Validation error**
A terminal error produced when an intent document violates a required constraint. Validation errors MUST prevent `intent_id` assignment.

**Validation warning**
A non-terminal condition produced when an intent document contains a value that is permitted but flagged for operator attention. Validation warnings MUST NOT prevent `intent_id` assignment.

**Cross-field rule**
A validation rule that tests a condition spanning two or more fields simultaneously.

---

## 4. Intent Schema (Normative)

The canonical intent schema is defined in YAML Schema notation below and is the authoritative field specification. The schema is also published in the ANIF Schema Registry (ANIF-600).

```yaml
type: object
required: [service, objectives, constraints]
properties:
  service:
    type: string
    description: >
      Unique identifier of the service this intent governs.
      MUST be a non-empty string. MUST match the service identifier
      registered in the service catalogue.

  environment:
    type: string
    enum: [prod, staging, dev]
    default: dev
    description: >
      The deployment environment to which this intent applies.
      When omitted, the framework MUST treat the intent as targeting
      the dev environment and apply non-production thresholds.

  objectives:
    type: object
    description: >
      Measurable outcome targets the service MUST achieve.
      At least one objective property MUST be present.
    properties:
      latency_ms:
        type: number
        minimum: 1
        description: >
          Maximum acceptable end-to-end latency in milliseconds.
          MUST be a positive number greater than or equal to 1.
      availability_percent:
        type: number
        minimum: 90
        maximum: 100
        description: >
          Minimum acceptable service availability as a percentage.
          MUST be between 90 and 100 inclusive.
      throughput_mbps:
        type: number
        description: >
          Minimum acceptable throughput in megabits per second.
          MUST be a positive number when specified.

  constraints:
    type: object
    description: >
      Boundaries within which the objectives must be achieved.
      At least one constraint property MUST be present.
    properties:
      region:
        type: string
        enum: [EU, US, APAC]
        description: >
          Geographic region within which the service MUST operate.
          MUST be one of the enumerated values.
      encryption:
        type: boolean
        description: >
          Whether data in transit MUST be encrypted.
          When set to false, pci_compliant policy will deny the intent.
      allowed_zones:
        type: array
        items:
          type: string
        description: >
          List of availability zones in which the service MAY operate.
          MUST contain at least one entry when no_public_ingress policy
          is applied. MUST contain at least two entries when
          availability_percent is 99.99 or higher.

  policies:
    type: array
    items:
      type: string
      enum: [zero_trust, no_public_ingress, pci_compliant, data_residency]
    description: >
      Named policy tags that MUST be applied during policy evaluation
      in addition to any globally active policies. Each entry MUST be
      a recognised policy name from the policy registry.

  priority:
    type: string
    enum: [low, medium, high, critical]
    description: >
      Urgency classification of this intent. When environment is prod,
      priority MUST be high or critical. When omitted, the framework
      MUST default to medium.
    default: medium
```

---

## 5. Required Fields

The following fields MUST be present in every submitted intent document. Absence of any required field MUST cause validation to fail and MUST prevent `intent_id` assignment.

### 5.1 service

- Type: string
- Constraint: MUST be non-empty.
- Constraint: MUST match a service identifier registered in the service catalogue.
- Error if absent: `"service: required field missing"`
- Error if empty string: `"service: value must be a non-empty string"`

### 5.2 objectives

- Type: object
- Constraint: MUST be present and MUST contain at least one of `latency_ms`, `availability_percent`, or `throughput_mbps`.
- Error if absent: `"objectives: required field missing"`
- Error if empty object: `"objectives: at least one objective property must be specified"`

### 5.3 constraints

- Type: object
- Constraint: MUST be present and MUST contain at least one property.
- Error if absent: `"constraints: required field missing"`
- Error if empty object: `"constraints: at least one constraint property must be specified"`

---

## 6. Optional Fields and Defaults

Optional fields MAY be omitted. When omitted, the framework MUST substitute the default value listed below before any further processing. Default substitution MUST be recorded in the validated intent record so that downstream components see the fully resolved intent.

| Field       | Default  | Notes                                                                 |
|-------------|----------|-----------------------------------------------------------------------|
| environment | `dev`    | Non-production thresholds apply. Priority constraint relaxed.         |
| priority    | `medium` | Affects trust score calculation (see ANIF-304).                       |
| policies    | `[]`     | Only globally active policies are applied. No additional policy tags. |

---

## 7. Field-Level Validation Rules

Validation rules are applied by the `/validate-intent` endpoint after schema conformance is verified. Rules are evaluated in the order listed. All applicable rules are evaluated; multiple errors MAY be returned in a single response.

### 7.1 latency_ms Minimum Value

**Rule ID:** VAL-001
**Type:** Warning (non-blocking)
**Condition:** `objectives.latency_ms` is present AND `objectives.latency_ms < 10`
**Effect:** Validation succeeds; `intent_id` is assigned. A warning is included in the validation response.
**Warning message:** `"objectives.latency_ms: value below 10 ms is unlikely to be achievable in most environments; proceeding with intent submission"`

### 7.2 availability_percent Range

**Rule ID:** VAL-002
**Type:** Error (blocking)
**Condition:** `objectives.availability_percent` is present AND (`objectives.availability_percent < 90` OR `objectives.availability_percent > 100`)
**Effect:** Validation fails; `intent_id` is not assigned.
**Error message:** `"objectives.availability_percent: value must be between 90 and 100 inclusive"`

### 7.3 Production Environment Requires High or Critical Priority

**Rule ID:** VAL-003
**Type:** Error (blocking)
**Condition:** `environment = prod` AND `priority` is not `high` or `critical`
**Effect:** Validation fails; `intent_id` is not assigned.
**Error message:** `"priority: production environment requires priority to be 'high' or 'critical'; received '{value}'"`

### 7.4 PCI Compliant Policy Requires Encryption

**Rule ID:** VAL-004
**Type:** Error (blocking)
**Condition:** `policies` contains `pci_compliant` AND (`constraints.encryption` is absent OR `constraints.encryption = false`)
**Effect:** Validation fails; `intent_id` is not assigned.
**Error message:** `"constraints.encryption: pci_compliant policy requires encryption to be true"`

### 7.5 High Availability Requires Multiple Zones

**Rule ID:** VAL-005
**Type:** Error (blocking)
**Condition:** `objectives.availability_percent >= 99.99` AND (`constraints.allowed_zones` is absent OR `constraints.allowed_zones` has fewer than 2 entries)
**Effect:** Validation fails; `intent_id` is not assigned.
**Error message:** `"constraints.allowed_zones: availability_percent >= 99.99 requires at least 2 allowed zones; {n} provided"`

### 7.6 Region Enumeration

**Rule ID:** VAL-006
**Type:** Error (blocking)
**Condition:** `constraints.region` is present AND value is not one of `EU`, `US`, `APAC`
**Effect:** Validation fails; `intent_id` is not assigned.
**Error message:** `"constraints.region: value must be one of ['EU', 'US', 'APAC']; received '{value}'"`

### 7.7 Policy Name Enumeration

**Rule ID:** VAL-007
**Type:** Error (blocking)
**Condition:** Any entry in `policies` is not one of `zero_trust`, `no_public_ingress`, `pci_compliant`, `data_residency`
**Effect:** Validation fails; `intent_id` is not assigned.
**Error message:** `"policies: unrecognised policy name '{value}'; valid values are [zero_trust, no_public_ingress, pci_compliant, data_residency]"`

---

## 8. Validation Response Schema

The `/validate-intent` endpoint MUST return a response conforming to the following structure.

**On success:**
```json
{
  "intent_id": "<UUID v4>",
  "status": "validated",
  "warnings": ["<warning message>", ...],
  "validated_intent": { "<fully resolved intent with defaults applied>" }
}
```

**On failure:**
```json
{
  "status": "validation_failed",
  "errors": ["<error message>", ...],
  "warnings": ["<warning message>", ...]
}
```

The `errors` array MUST contain at least one entry on failure. The `warnings` array MAY be empty. `intent_id` MUST NOT appear in failure responses.

---

## 9. Intent Versioning and Re-Submission

ANIF does not support in-place modification of validated intents (see ANIF-300, Section 4.4.1). To change an intent after validation, the operator MUST:

1. Compose a new intent document incorporating the desired changes.
2. Submit the new document to `POST /validate-intent`.
3. A new `intent_id` will be assigned if the new document is valid.
4. The operator MUST use the new `intent_id` for all subsequent pipeline calls.
5. The original intent and its `intent_id` remain in the audit log and are not deleted.

Operators SHOULD record the relationship between successive intents for the same service in their service management tooling. ANIF does not maintain an intent lineage graph in this version.

---

## 10. Conformance Requirements

1. Submissions MUST include all required fields (`service`, `objectives`, `constraints`).
2. Optional fields that are omitted MUST have their defaults applied before further processing.
3. All field-level validation rules (VAL-001 through VAL-007) MUST be evaluated on every submission.
4. Multiple errors MAY be returned in a single response; validation MUST NOT short-circuit on the first error.
5. `intent_id` MUST NOT be assigned when any blocking validation rule is violated.
6. Warnings MUST be included in the response and MUST NOT prevent `intent_id` assignment.

---

## 11. Security Considerations

- Intent documents MAY contain sensitive service identifiers and operational parameters. Submission endpoints MUST require authentication.
- Validation error messages MUST NOT expose internal system paths, database identifiers, or configuration values beyond the field name and value that caused the error.
- The validated intent stored by the framework MUST be signed or checksummed to detect tampering, as it forms the basis for all downstream pipeline decisions.

---

## 12. Operational Considerations

- Authors SHOULD validate intents against the published schema locally before submission to reduce round-trips.
- Tooling that generates intents programmatically MUST apply the same validation rules locally so that submission errors are caught at generation time.
- When `environment` is omitted and a `prod`-level service name is accidentally submitted without the `prod` environment tag, the intent will be processed under non-production thresholds. Authors MUST explicitly set `environment: prod` for production service intents.

---

## Appendix A: Examples

### A.1 Valid Intent — Payments Service, Production, EU, PCI Compliant

```json
{
  "service": "payments-gateway",
  "environment": "prod",
  "objectives": {
    "latency_ms": 45,
    "availability_percent": 99.99,
    "throughput_mbps": 500
  },
  "constraints": {
    "region": "EU",
    "encryption": true,
    "allowed_zones": ["eu-west-1a", "eu-west-1b"]
  },
  "policies": ["zero_trust", "pci_compliant", "data_residency"],
  "priority": "critical"
}
```

**Expected response:**
```json
{
  "intent_id": "f3a9b2c1-4d7e-4f88-9012-abcdef012345",
  "status": "validated",
  "warnings": [],
  "validated_intent": { "...fully resolved..." }
}
```

### A.2 Invalid Intent — Production Without High Priority

```json
{
  "service": "payments-gateway",
  "environment": "prod",
  "objectives": { "availability_percent": 99.5 },
  "constraints": { "region": "EU" },
  "priority": "low"
}
```

**Expected response:**
```json
{
  "status": "validation_failed",
  "errors": [
    "priority: production environment requires priority to be 'high' or 'critical'; received 'low'"
  ],
  "warnings": []
}
```

### A.3 Invalid Intent — PCI Compliant Without Encryption

```json
{
  "service": "checkout-api",
  "environment": "prod",
  "objectives": { "availability_percent": 99.9 },
  "constraints": { "region": "EU", "encryption": false },
  "policies": ["pci_compliant"],
  "priority": "high"
}
```

**Expected response:**
```json
{
  "status": "validation_failed",
  "errors": [
    "constraints.encryption: pci_compliant policy requires encryption to be true"
  ],
  "warnings": []
}
```

### A.4 Invalid Intent — High Availability Without Sufficient Zones

```json
{
  "service": "core-api",
  "environment": "prod",
  "objectives": { "availability_percent": 99.99 },
  "constraints": { "region": "US", "encryption": true, "allowed_zones": ["us-east-1a"] },
  "priority": "critical"
}
```

**Expected response:**
```json
{
  "status": "validation_failed",
  "errors": [
    "constraints.allowed_zones: availability_percent >= 99.99 requires at least 2 allowed zones; 1 provided"
  ],
  "warnings": []
}
```

### A.5 Valid Intent With Warning — Very Low Latency Target

```json
{
  "service": "realtime-stream",
  "environment": "prod",
  "objectives": { "latency_ms": 5, "availability_percent": 99.9 },
  "constraints": { "region": "US", "encryption": true },
  "priority": "high"
}
```

**Expected response:**
```json
{
  "intent_id": "a1b2c3d4-0000-4abc-9000-111122223333",
  "status": "validated",
  "warnings": [
    "objectives.latency_ms: value below 10 ms is unlikely to be achievable in most environments; proceeding with intent submission"
  ],
  "validated_intent": { "...fully resolved..." }
}
```

### A.6 Multiple Errors in a Single Submission

```json
{
  "service": "billing-service",
  "environment": "prod",
  "objectives": { "availability_percent": 99.99 },
  "constraints": { "region": "EU", "encryption": false, "allowed_zones": ["eu-central-1a"] },
  "policies": ["pci_compliant"],
  "priority": "medium"
}
```

**Expected response:**
```json
{
  "status": "validation_failed",
  "errors": [
    "priority: production environment requires priority to be 'high' or 'critical'; received 'medium'",
    "constraints.encryption: pci_compliant policy requires encryption to be true",
    "constraints.allowed_zones: availability_percent >= 99.99 requires at least 2 allowed zones; 1 provided"
  ],
  "warnings": []
}
```

---

## Appendix B: Change History

| Version | Date       | Author             | Description   |
|---------|------------|--------------------|---------------|
| 0.1.0   | 2026-04-07 | ANIF Working Group | Initial draft |
