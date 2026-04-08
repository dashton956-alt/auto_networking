# ANIF-600: Schema Reference

| Field        | Value                                              |
|--------------|----------------------------------------------------|
| Doc ID       | ANIF-600                                           |
| Series       | Annex                                              |
| Version      | 0.1.0                                              |
| Status       | Draft                                              |
| Authors      | ANIF Working Group                                 |
| Reviewers    | —                                                  |
| Approved by  | —                                                  |
| Created      | 2026-04-07                                         |
| Last updated | 2026-04-07                                         |
| Replaces     | N/A                                                |
| Related docs | ANIF-301, ANIF-302, ANIF-304, ANIF-107             |

---

## Abstract

This document is the authoritative narrative reference for all data schemas used within the Autonomous Networking & Infrastructure Framework (ANIF). It describes the purpose, structure, field semantics, validation constraints, and usage examples for every schema in the ANIF schema library. Schemas are defined as YAML files in the `/schemas/` directory of the reference prototype and are mirrored by Pydantic v2 models in the Python implementation. Two schemas — `risk_score_schema` and `audit_record_schema` — are defined normatively here and must be created as corresponding YAML files.

---

## 1. Introduction

### 1.1 Purpose

ANIF exchanges structured data between pipeline stages. Every object that crosses a stage boundary must conform to a defined schema. This document specifies those schemas so that:

- Implementors know exactly what fields to produce and consume at each stage.
- Validators can enforce structural and semantic correctness at API ingress.
- Test authors can construct valid and invalid fixtures with confidence.
- Operators can interpret log and audit data.

### 1.2 Schema Library Location

All normative YAML schema files reside in `schemas/` at the root of the `anif-prototype/` repository:

```
anif-prototype/
└── schemas/
    ├── intent_schema.yml
    ├── action_schema.yml
    ├── policy_schema.yml
    ├── risk_score_schema.yml     # defined here; must be created
    └── audit_record_schema.yml   # defined here; must be created
```

### 1.3 Schema Authoring Conventions

All schemas follow JSON Schema Draft 07 semantics expressed in YAML. Required fields are listed explicitly under the `required` key. Enumerations constrain string fields to closed value sets. Numeric fields carry `minimum`/`maximum` constraints where appropriate. Descriptions are embedded as `description` keys in each property.

### 1.4 Scope

This document covers:

- `intent_schema` — operator-submitted network service intent
- `action_schema` — an autonomous remediation or configuration action
- `policy_schema` — a named set of conditional rules governing intent evaluation
- `risk_score_schema` — the risk and trust assessment output of the Risk Scoring module
- `audit_record_schema` — a single immutable audit entry written by each pipeline stage

---

## 2. Normative References

- JSON Schema Draft 07: https://json-schema.org/draft-07/
- ANIF-301: Intent Validation
- ANIF-302: Policy Engine
- ANIF-304: Decision Engine
- ANIF-107: Data Governance and Audit
- ISO 8601: Date and time format
- RFC 4122: UUID format

---

## 3. Terms and Definitions

**Schema** — a machine-readable specification of the structure, types, and constraints of a data object.

**Intent** — an operator-supplied declaration of a desired network service state, expressed as a structured object conforming to `intent_schema`.

**Action** — a discrete autonomous operation that modifies network state, conforming to `action_schema`.

**Policy** — a named collection of conditional rules that constrain permissible intent and action, conforming to `policy_schema`.

**Risk score** — a numeric assessment (0–100) of the risk associated with executing a given intent, produced by the Risk Scoring module.

**Audit record** — an immutable log entry recording the input, output, and reasoning at a single pipeline stage.

**Pydantic model** — a Python class using Pydantic v2 that validates and serialises data against a schema.

---

## 4. Schema Definitions

### 4.1 Intent Schema (`intent_schema`)

#### 4.1.1 Overview

The intent schema defines the structure of a network service intent submitted by an operator or automation system. It is the primary input to the ANIF pipeline. All fields describe the desired service state; they do not prescribe implementation method.

#### 4.1.2 Field Reference

| Field                             | Type            | Required | Description                                                                                     |
|-----------------------------------|-----------------|----------|-------------------------------------------------------------------------------------------------|
| `service`                         | string          | Yes      | Logical name of the network service. Free-form identifier used throughout pipeline tracing.     |
| `environment`                     | string (enum)   | No       | Deployment environment. One of: `prod`, `staging`, `dev`. Defaults to context-dependent.        |
| `objectives`                      | object          | Yes      | Performance objectives the service must meet.                                                   |
| `objectives.latency_ms`           | number          | No       | Maximum acceptable end-to-end latency in milliseconds. Minimum: 1.                             |
| `objectives.availability_percent` | number          | No       | Minimum availability as a percentage. Range: 90–100 inclusive.                                 |
| `objectives.throughput_mbps`      | number          | No       | Minimum required throughput in megabits per second.                                             |
| `constraints`                     | object          | Yes      | Hard constraints the implementation must respect.                                               |
| `constraints.region`              | string (enum)   | No       | Geographic region. One of: `EU`, `US`, `APAC`.                                                 |
| `constraints.encryption`          | boolean         | No       | If `true`, all traffic must be encrypted in transit.                                            |
| `constraints.allowed_zones`       | array[string]   | No       | List of availability zone identifiers where the service may be placed.                          |
| `policies`                        | array[string]   | No       | Names of policies that must be satisfied. Valid values: `zero_trust`, `no_public_ingress`, `pci_compliant`, `data_residency`. |
| `priority`                        | string (enum)   | No       | Execution priority. One of: `low`, `medium`, `high`, `critical`.                               |

#### 4.1.3 Constraints Summary

- `objectives.availability_percent` must be between 90 and 100 inclusive.
- `objectives.latency_ms` must be at least 1.
- `environment` must be one of the three defined values; free-text environments are not valid.
- `policies` entries are constrained to the closed enumeration; custom policies are injected via the policy engine, not via this field.

#### 4.1.4 Example

```yaml
service: payments
environment: prod
objectives:
  latency_ms: 50
  availability_percent: 99.99
  throughput_mbps: 500
constraints:
  region: EU
  encryption: true
  allowed_zones:
    - zone-a
    - zone-b
policies:
  - zero_trust
  - pci_compliant
priority: critical
```

#### 4.1.5 Pydantic v2 Mapping

```python
from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum

class Environment(str, Enum):
    prod = "prod"
    staging = "staging"
    dev = "dev"

class Region(str, Enum):
    EU = "EU"
    US = "US"
    APAC = "APAC"

class PolicyName(str, Enum):
    zero_trust = "zero_trust"
    no_public_ingress = "no_public_ingress"
    pci_compliant = "pci_compliant"
    data_residency = "data_residency"

class Priority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"

class Objectives(BaseModel):
    latency_ms: Optional[float] = Field(None, ge=1)
    availability_percent: Optional[float] = Field(None, ge=90, le=100)
    throughput_mbps: Optional[float] = None

class Constraints(BaseModel):
    region: Optional[Region] = None
    encryption: Optional[bool] = None
    allowed_zones: Optional[List[str]] = None

class Intent(BaseModel):
    service: str
    environment: Optional[Environment] = None
    objectives: Objectives
    constraints: Constraints
    policies: Optional[List[PolicyName]] = None
    priority: Optional[Priority] = None
```

---

### 4.2 Action Schema (`action_schema`)

#### 4.2.1 Overview

The action schema defines a single autonomous remediation or configuration action that the ANIF decision engine may recommend or the execution engine may perform. Actions are produced by the decision engine and consumed by the action execution layer.

#### 4.2.2 Field Reference

| Field         | Type           | Required | Description                                                                                          |
|---------------|----------------|----------|------------------------------------------------------------------------------------------------------|
| `action_type` | string (enum)  | Yes      | The category of action to perform. See enumeration below.                                            |
| `parameters`  | object         | No       | Action-specific parameters. Schema is open (`additionalProperties: true`); validated per action type. |
| `risk_level`  | string (enum)  | No       | Assessed risk level of this action. One of: `low`, `medium`, `high`.                                |

#### 4.2.3 Action Type Enumeration

| Value              | Description                                                                  |
|--------------------|------------------------------------------------------------------------------|
| `reroute_traffic`  | Redirect traffic flows to an alternate path or segment.                      |
| `apply_qos`        | Apply Quality of Service rules to prioritise or throttle traffic classes.    |
| `scale_bandwidth`  | Increase or decrease allocated bandwidth for a service or link.              |
| `isolate_segment`  | Quarantine a network segment by removing it from the forwarding plane.       |

#### 4.2.4 Parameters Conventions

Although `parameters` is an open object, implementors should follow these conventions per action type:

| `action_type`      | Expected parameters                                              |
|--------------------|------------------------------------------------------------------|
| `reroute_traffic`  | `target_path` (string), `source_segment` (string)               |
| `apply_qos`        | `policy_name` (string), `bandwidth_limit_mbps` (number)         |
| `scale_bandwidth`  | `direction` ("up"\|"down"), `delta_mbps` (number)               |
| `isolate_segment`  | `segment_id` (string), `reason` (string)                        |

#### 4.2.5 Example

```yaml
action_type: reroute_traffic
parameters:
  target_path: path-b
  source_segment: segment-eu-west-1
risk_level: medium
```

#### 4.2.6 Pydantic v2 Mapping

```python
from pydantic import BaseModel
from typing import Optional, Dict, Any
from enum import Enum

class ActionType(str, Enum):
    reroute_traffic = "reroute_traffic"
    apply_qos = "apply_qos"
    scale_bandwidth = "scale_bandwidth"
    isolate_segment = "isolate_segment"

class RiskLevel(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"

class Action(BaseModel):
    action_type: ActionType
    parameters: Optional[Dict[str, Any]] = None
    risk_level: Optional[RiskLevel] = None
```

---

### 4.3 Policy Schema (`policy_schema`)

#### 4.3.1 Overview

The policy schema defines a named policy consisting of one or more conditional rules. The policy engine evaluates each rule against the current intent and context. Rules are order-independent; all matching rules are applied and their outcomes aggregated.

#### 4.3.2 Field Reference

| Field              | Type          | Required | Description                                                                               |
|--------------------|---------------|----------|-------------------------------------------------------------------------------------------|
| `name`             | string        | Yes      | Unique policy identifier. Must match an entry in the `PolicyName` enumeration or be a registered custom policy name. |
| `rules`            | array[object] | Yes      | Ordered list of conditional rules. At least one rule is required.                        |
| `rules[].condition`| string        | No       | Condition expression in the canonical condition syntax (see 4.3.4).                      |
| `rules[].action`   | string (enum) | No       | Outcome when the condition evaluates to true. One of: `allow`, `deny`, `warn`.           |

#### 4.3.3 Rule Evaluation Semantics

- Rules are evaluated in listed order.
- The first `deny` result terminates evaluation and returns a denial.
- `warn` results are accumulated; execution may proceed with warnings.
- `allow` results do not terminate evaluation; they record a positive match.
- If no rule matches, the default outcome is `allow`.

#### 4.3.4 Condition Syntax

Conditions are expressed as a colon-delimited triple:

```
field_path:operator:value
```

**`field_path`** — dot-separated path into the intent object. Examples: `constraints.encryption`, `environment`, `objectives.latency_ms`.

**`operator`** — one of:

| Operator        | Description                                                        |
|-----------------|--------------------------------------------------------------------|
| `equals`        | Field value equals the literal value (string comparison)           |
| `not_equals`    | Field value does not equal the literal value                       |
| `greater_than`  | Numeric field value is strictly greater than the numeric literal   |
| `less_than`     | Numeric field value is strictly less than the numeric literal      |
| `contains`      | String field value contains the substring literal                  |
| `not_contains`  | String field value does not contain the substring literal          |
| `in_list`       | Field value is in the comma-separated list of values               |
| `not_in_list`   | Field value is not in the comma-separated list of values           |

**`value`** — the comparison operand. For `in_list` and `not_in_list`, values are comma-separated without spaces: `EU,US`.

**Examples:**

```
constraints.encryption:equals:false
environment:in_list:prod,staging
objectives.latency_ms:less_than:10
constraints.region:not_equals:EU
policies:contains:pci_compliant
```

#### 4.3.5 Example Policy

```yaml
name: pci_compliant
rules:
  - condition: "constraints.encryption:equals:false"
    action: deny
  - condition: "constraints.region:not_in_list:EU,US"
    action: deny
  - condition: "environment:equals:prod"
    action: allow
```

#### 4.3.6 Pydantic v2 Mapping

```python
from pydantic import BaseModel
from typing import List, Optional
from enum import Enum

class RuleAction(str, Enum):
    allow = "allow"
    deny = "deny"
    warn = "warn"

class PolicyRule(BaseModel):
    condition: Optional[str] = None
    action: Optional[RuleAction] = None

class Policy(BaseModel):
    name: str
    rules: List[PolicyRule]
```

---

### 4.4 Risk Score Schema (`risk_score_schema`)

#### 4.4.1 Overview

The risk score schema defines the output of the Risk Scoring module (ANIF-303). It captures numeric risk and trust assessments, the safety decision reached, the contributing factors, and which threshold set was applied. This schema must be created as `schemas/risk_score_schema.yml`.

#### 4.4.2 YAML Definition

```yaml
type: object
required: [risk_score, trust_score, safety_decision, justification, threshold_applied]
properties:
  risk_score:
    type: integer
    minimum: 0
    maximum: 100
    description: >
      Aggregate risk score from 0 (no risk) to 100 (maximum risk).
      Computed by summing factor weights. Capped at 100.
  trust_score:
    type: integer
    minimum: 0
    maximum: 100
    description: >
      Trust level of the intent source and context, from 0 (untrusted) to
      100 (fully trusted). Derived from operator credentials, freshness of
      telemetry, and policy compliance history.
  safety_decision:
    type: string
    enum: [allow, warn, block]
    description: >
      The safety outcome based on risk_score vs thresholds:
        allow  — risk_score < warn_threshold
        warn   — warn_threshold <= risk_score < block_threshold
        block  — risk_score >= block_threshold
  justification:
    type: array
    items:
      type: string
    description: >
      Ordered list of human-readable factor descriptions that contributed to
      the risk_score. Each entry names the factor and its weight.
  threshold_applied:
    type: object
    required: [warn_threshold, block_threshold, profile]
    properties:
      warn_threshold:
        type: integer
        minimum: 0
        maximum: 100
      block_threshold:
        type: integer
        minimum: 0
        maximum: 100
      profile:
        type: string
        description: Name of the threshold profile applied (e.g., "default", "strict", "permissive").
```

#### 4.4.3 Field Reference

| Field                              | Type          | Required | Description                                                                 |
|------------------------------------|---------------|----------|-----------------------------------------------------------------------------|
| `risk_score`                       | integer       | Yes      | Aggregate risk score, 0–100. Higher is riskier.                            |
| `trust_score`                      | integer       | Yes      | Trust level, 0–100. Higher is more trusted.                                |
| `safety_decision`                  | string (enum) | Yes      | Decision outcome: `allow`, `warn`, or `block`.                             |
| `justification`                    | array[string] | Yes      | Ordered list of factor descriptions contributing to the risk score.        |
| `threshold_applied`                | object        | Yes      | The threshold set used for the allow/warn/block decision.                  |
| `threshold_applied.warn_threshold` | integer       | Yes      | Minimum score at which `warn` is issued.                                   |
| `threshold_applied.block_threshold`| integer       | Yes      | Minimum score at which `block` is issued.                                  |
| `threshold_applied.profile`        | string        | Yes      | Name of the applied threshold profile.                                     |

#### 4.4.4 Standard Risk Factors and Weights

| Factor                    | Condition                            | Weight |
|---------------------------|--------------------------------------|--------|
| Production environment    | `environment == prod`                | +30    |
| Staging environment       | `environment == staging`             | +10    |
| Degraded network signal   | Telemetry indicates degraded state   | +20    |
| Isolate segment action    | `action_type == isolate_segment`     | +25    |
| Policy failure            | Any policy evaluation returns `deny` | +15    |
| Encryption disabled       | `constraints.encryption == false`    | +10    |
| Critical priority         | `priority == critical`               | +5     |
| High availability target  | `availability_percent >= 99.9`       | +5     |

#### 4.4.5 Default Threshold Profile

| Profile   | warn_threshold | block_threshold |
|-----------|---------------|-----------------|
| default   | 40            | 70              |
| strict    | 25            | 50              |
| permissive| 60            | 85              |

#### 4.4.6 Example

```json
{
  "risk_score": 45,
  "trust_score": 72,
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
}
```

---

### 4.5 Audit Record Schema (`audit_record_schema`)

#### 4.5.1 Overview

The audit record schema defines the structure of a single immutable audit entry. Every pipeline stage must write an audit record before returning its result. Audit records are append-only and collectively form the complete provenance trail for an intent's journey through the pipeline. This schema must be created as `schemas/audit_record_schema.yml`.

#### 4.5.2 YAML Definition

```yaml
type: object
required: [record_id, intent_id, timestamp, stage, input_summary, output_summary, outcome]
properties:
  record_id:
    type: string
    format: uuid
    description: Globally unique identifier for this audit record (RFC 4122 UUID v4).
  intent_id:
    type: string
    format: uuid
    description: Identifier of the intent this record pertains to.
  timestamp:
    type: string
    format: date-time
    description: ISO-8601 UTC timestamp of when this record was written.
  stage:
    type: string
    enum:
      - intent_validation
      - policy_evaluation
      - risk_scoring
      - decision
      - governance
      - execution
      - rollback
      - feedback
    description: Pipeline stage that produced this record.
  operator_id:
    type: [string, "null"]
    description: Identifier of the human operator if manually involved; null for automated stages.
  input_summary:
    type: object
    additionalProperties: true
    description: Condensed representation of the stage's input. Must not contain secrets.
  output_summary:
    type: object
    additionalProperties: true
    description: Condensed representation of the stage's output. Must not contain secrets.
  outcome:
    type: string
    enum: [success, failure, escalated, blocked]
    description: >
      Result of the stage:
        success   — stage completed normally
        failure   — stage encountered an error
        escalated — stage escalated to human governance
        blocked   — stage halted the pipeline
  reasoning_chain:
    type: array
    items:
      type: string
    description: >
      Ordered list of reasoning steps explaining why this outcome was reached.
      Written by the stage in plain English. Used by GET /audit/{intent_id}/why.
  duration_ms:
    type: integer
    minimum: 0
    description: Wall-clock time the stage took to complete, in milliseconds.
```

#### 4.5.3 Field Reference

| Field             | Type             | Required | Description                                                                          |
|-------------------|------------------|----------|--------------------------------------------------------------------------------------|
| `record_id`       | string (UUID)    | Yes      | Unique identifier for this record. Generate using UUID v4.                          |
| `intent_id`       | string (UUID)    | Yes      | Intent that triggered this record. Constant across all records for one pipeline run. |
| `timestamp`       | string (ISO-8601)| Yes      | UTC timestamp written at record creation time.                                      |
| `stage`           | string (enum)    | Yes      | Pipeline stage name. Must match the stage enumeration exactly.                      |
| `operator_id`     | string or null   | No       | Human operator ID if a manual action triggered or reviewed this stage.              |
| `input_summary`   | object           | Yes      | Key/value summary of stage input. Omit credentials and PII.                        |
| `output_summary`  | object           | Yes      | Key/value summary of stage output.                                                  |
| `outcome`         | string (enum)    | Yes      | One of: `success`, `failure`, `escalated`, `blocked`.                              |
| `reasoning_chain` | array[string]    | No       | Human-readable reasoning steps. Required if `outcome` is `escalated` or `blocked`. |
| `duration_ms`     | integer          | No       | Execution time of the stage in milliseconds.                                        |

#### 4.5.4 Write Discipline

Every pipeline stage MUST write its audit record as the last operation before returning its response. If a stage crashes after writing its record, the record stands as evidence of the crash. If a stage crashes before writing, a compensating timeout-based record writer in the orchestrator must write a `failure` record after the timeout window.

#### 4.5.5 Example

```json
{
  "record_id": "b3f7c2a1-1234-4abc-9def-000000000001",
  "intent_id": "a1b2c3d4-5678-4efg-abcd-000000000099",
  "timestamp": "2026-04-07T14:32:01.004Z",
  "stage": "policy_evaluation",
  "operator_id": null,
  "input_summary": {
    "service": "payments",
    "policies_checked": ["zero_trust", "pci_compliant"]
  },
  "output_summary": {
    "passed": true,
    "warnings": [],
    "violations": []
  },
  "outcome": "success",
  "reasoning_chain": [
    "zero_trust: all rules passed",
    "pci_compliant: encryption=true satisfies rule 1; region=EU satisfies rule 2"
  ],
  "duration_ms": 12
}
```

---

## 5. Conformance Requirements

5.1 All intent objects submitted to `POST /validate-intent` MUST conform to `intent_schema`. Non-conforming objects MUST be rejected with HTTP 422.

5.2 All action objects produced by the decision engine MUST conform to `action_schema`. Invalid action objects MUST NOT be forwarded to the execution layer.

5.3 All policy definitions loaded by the policy engine MUST conform to `policy_schema`. Policies that fail schema validation at load time MUST be rejected and the engine MUST NOT start.

5.4 All risk assessment outputs MUST conform to `risk_score_schema`. The `safety_decision` field MUST be derived programmatically from `risk_score` and the thresholds in `threshold_applied`; it MUST NOT be set arbitrarily.

5.5 Every pipeline stage MUST produce an audit record conforming to `audit_record_schema` before returning its response. Stages that fail to write audit records are non-conformant.

5.6 Pydantic v2 models MUST be kept in sync with their corresponding YAML schema files. Any change to a YAML schema file MUST be accompanied by a corresponding change to the Pydantic model.

---

## 6. Security Considerations

6.1 The `operator_id` field in audit records MUST reference an authenticated identity. Unauthenticated submissions MUST record `operator_id: null` and MUST NOT claim an identity.

6.2 `input_summary` and `output_summary` in audit records MUST NOT contain credentials, tokens, private keys, or personally identifiable information. Implementors MUST apply a sanitisation step before writing audit records.

6.3 Schema files MUST be treated as code. Changes to schema files MUST follow the same review and approval process as source code changes.

6.4 The `allowed_zones` field in intent constraints MUST be validated against a system-managed list of authorised zones. Arbitrary zone names from untrusted input MUST be rejected by the policy engine.

---

## 7. Operational Considerations

7.1 Schema changes MUST be backward compatible within a minor version. Fields may be added (with `required: false`) but existing required fields MUST NOT be removed or renamed within a minor version.

7.2 When a breaking schema change is necessary, a new major version of the schema file is created, and both versions MUST be supported concurrently for at least one minor release cycle.

7.3 Implementors SHOULD cache loaded schemas at startup and reload on SIGHUP. Schema hot-reloading is acceptable in dev/staging environments but SHOULD be disabled in production.

---

## Appendix A: Examples

### A.1 Minimal Valid Intent

```yaml
service: monitoring
objectives: {}
constraints: {}
```

### A.2 Full Valid Intent

See section 4.1.4.

### A.3 Intent with Invalid Availability

The following is invalid because `availability_percent: 85` is below the minimum of 90:

```yaml
service: reporting
objectives:
  availability_percent: 85
constraints: {}
```

Expected validation error:
```json
{
  "status": "error",
  "data": {},
  "errors": [
    {
      "field": "objectives.availability_percent",
      "message": "Value 85 is less than minimum 90"
    }
  ],
  "trace_id": "trace-00000001"
}
```

---

## Appendix B: Change History

| Version | Date       | Author             | Summary          |
|---------|------------|--------------------|------------------|
| 0.1.0   | 2026-04-07 | ANIF Working Group | Initial draft    |
