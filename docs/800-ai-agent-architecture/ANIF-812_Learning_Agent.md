# ANIF-812: Learning Agent and Network Intelligence

| Field        | Value                                              |
|--------------|----------------------------------------------------|
| Doc ID       | ANIF-812                                           |
| Series       | AI Agent Architecture                              |
| Version      | 0.1.0                                              |
| Status       | Draft                                              |
| Authors      | ANIF Working Group                                 |
| Reviewers    | —                                                  |
| Approved by  | —                                                  |
| Created      | 2026-04-08                                         |
| Last updated | 2026-04-08                                         |
| Replaces     | N/A                                                |
| Related docs | ANIF-801, ANIF-806, ANIF-908, ANIF-403             |

---

## Abstract

This document defines the normative requirements for the Network Knowledge Broker — the learning agent role responsible for collecting, validating, and distributing operational intelligence to other agents in the ANIF system. The Learning Agent aggregates three categories of knowledge — network pattern knowledge, operational knowledge, and resolution knowledge — from six input sources including human expert feedback. No knowledge update MUST be distributed to other agents without prior human approval. Knowledge is distributed in role-scoped packages so that each receiving agent receives only the intelligence relevant to its declared function. Negative examples — records of what failed and why — MUST be captured and distributed alongside positive examples.

---

## 1. Introduction

### 1.1 Purpose

An ANIF deployment operating over time accumulates operational experience that can improve agent decision quality. The Learning Agent provides the governed mechanism through which that experience is captured, validated, and distributed — without allowing agents to update their own behaviour autonomously. Human approval at the distribution gate ensures that operational learning remains under human direction.

### 1.2 Scope

This document covers:

- The three categories of network knowledge
- The six input sources for knowledge collection
- The knowledge package schema
- Role-scoped knowledge distribution
- The mandatory human approval gate before distribution
- Negative example handling

### 1.3 Out of Scope

This document does not cover:

- Closed-loop feedback and continuous improvement mechanics (see ANIF-403)
- Agent lifecycle state transitions driven by learning outcomes (see ANIF-803)
- AI Council review of learning recommendations (see ANIF-908)
- Agent observability metrics used as input signals (see ANIF-806)

### 1.4 Intended Audience

- AI engineers implementing the Network Knowledge Broker agent
- Network architects contributing expert knowledge
- Governance officers approving knowledge distributions
- Platform architects designing knowledge storage

---

## 2. Normative References

| Reference | Title |
|---|---|
| ANIF-403 | Closed Loop Feedback and Learning |
| ANIF-801 | Agent Types, Roles and Human Counterparts |
| ANIF-803 | Agent Lifecycle Management |
| ANIF-806 | Agent Observability Standard |
| ANIF-908 | AI Council Learning Review |
| RFC 2119 | Key words for use in RFCs to Indicate Requirement Levels |

---

## 3. Terms and Definitions

| Term | Definition |
|---|---|
| Knowledge package | A structured, versioned collection of knowledge items approved for distribution to a defined set of agent roles |
| Knowledge item | A single unit of knowledge: a fact, pattern, resolution, or negative example with provenance and confidence metadata |
| Role-scoped distribution | The practice of delivering knowledge only to agent roles for which the knowledge is relevant |
| Negative example | A record of an action or decision that produced a harmful, incorrect, or suboptimal outcome, retained to prevent repetition |
| Knowledge broker | The Learning Agent role responsible for aggregating, curating, and distributing network intelligence |

---

## 4. Knowledge Categories

The Learning Agent MUST maintain three distinct knowledge categories. Each category is stored, versioned, and distributed independently.

### 4.1 Network Pattern Knowledge

Facts and patterns about the specific network environment being managed. Includes:

- Traffic patterns and their seasonal or temporal characteristics
- Device behaviour under specific conditions (e.g., router X drops packets at load > 80%)
- Topology-specific routing anomalies
- Observed failure modes for specific hardware or software versions

### 4.2 Operational Knowledge

Intelligence about how the organisation operates and makes decisions. Includes:

- Change window preferences and historical approval patterns
- SLA breach thresholds that have triggered escalation in the past
- Human operator override patterns (what recommendations operators consistently reject)
- Maintenance coordination patterns

### 4.3 Resolution Knowledge

Structured records of how specific incident or problem types were resolved. Includes:

- Incident classification to resolution mapping
- Root cause patterns and their associated diagnostic steps
- Successful and unsuccessful remediation attempts
- Rollback trigger conditions and outcomes

---

## 5. Input Sources

The Learning Agent MUST accept knowledge contributions from the following six input sources.

| Source | Knowledge Types Contributed | Input Mechanism |
|---|---|---|
| NOC Manager | Operational knowledge (escalation patterns, shift handover insights) | Structured feedback form post-incident |
| Problem Manager | Resolution knowledge (root cause analysis, permanent fix outcomes) | Problem record closure data |
| Change Manager | Operational knowledge (change approval patterns, freeze periods) | Change record completion data |
| Project Manager | Operational knowledge (planned maintenance, resource availability) | Project task completion data |
| Network Observers (Tier 1 agents) | Network pattern knowledge (observed traffic, anomalies, device states) | Automated event stream |
| Human Expert Feedback | All three categories (ad hoc expert input) | Expert annotation interface |

### 5.1 Source Quality Tracking

The Learning Agent MUST track the quality of each input source by measuring how knowledge items from that source perform after distribution — specifically, whether agent decisions informed by the knowledge improved or degraded outcomes. Sources with degraded quality scores (below 0.60 on a 0.0–1.0 scale) MUST be flagged for review and their knowledge items MUST NOT be distributed without enhanced human review until the quality score recovers above 0.70.

---

## 6. Knowledge Package Schema

Every knowledge package MUST conform to the following schema:

```yaml
knowledge_package_id: UUID v4
version: semantic version (e.g., 1.0.0)
category: enum [network_pattern | operational | resolution]
target_roles: list of agent role identifiers
approval_status: enum [pending | approved | rejected]
approver_id: string (human identity)
approval_timestamp: ISO 8601
knowledge_items:
  - item_id: UUID v4
    type: enum [positive_example | negative_example | pattern | fact]
    description: string
    source: string (source identifier)
    confidence: float (0.0–1.0)
    evidence: string (reference to supporting record, e.g., incident_id or intent_id)
    applicable_conditions: string (when this knowledge applies)
    created: ISO 8601
```

The `evidence` field MUST reference a verifiable record in the audit trail or ITSM system. Knowledge items with no verifiable evidence MUST NOT be approved for distribution.

---

## 7. Human Approval Gate

### 7.1 Mandatory Approval

No knowledge package MUST be distributed to any agent without explicit human approval. The approval gate is non-negotiable — automated approval of knowledge packages is a conformance violation.

### 7.2 Approval Process

1. The Learning Agent compiles a candidate knowledge package and sets `approval_status: pending`.
2. The package is submitted to the governance committee's knowledge review queue.
3. An authorised reviewer examines each knowledge item, verifies evidence references, and assesses potential impact.
4. The reviewer sets `approval_status: approved` or `rejected` and records their identity in `approver_id`.
5. Approved packages are released to the distribution system. Rejected packages are retained for audit purposes.

### 7.3 Approval SLA

Knowledge packages MUST be reviewed within 5 business days of submission. Packages pending review for more than 5 business days MUST be escalated to the AI Council (ANIF-908).

---

## 8. Role-Scoped Distribution

An approved knowledge package MUST be delivered only to agents whose declared roles match the `target_roles` list. The distribution system MUST enforce role scope at delivery time — an agent MUST NOT receive a knowledge package not addressed to its role, even if the package is approved.

Agents MUST apply received knowledge packages to future decisions only within the scope declared in `applicable_conditions`. Applying knowledge outside its declared applicable conditions is a conformance violation.

---

## 9. Negative Example Handling

### 9.1 Mandatory Capture

Negative examples — records of failed, harmful, or suboptimal decisions — MUST be captured and retained alongside positive examples. Negative examples are as important as positive examples for preventing the repetition of harmful patterns.

### 9.2 Negative Example Sources

Negative examples MUST be generated from:

- Intents that reached FAILED state and their associated root cause
- Human overrides of agent recommendations (from ANIF-808 override records)
- Ethics violations logged by the ethics audit trail (ANIF-724)
- Execution rollbacks

### 9.3 Negative Example Distribution

Negative examples MUST be distributed to agents in the same role scope that the original failure occurred in. A negative example produced by an Intent Validation Agent MUST be distributed to all Intent Validation Agents, not to unrelated roles.

Negative examples require the same human approval process as positive knowledge items (section 7).

---

## 10. Conformance Requirements

| ID | Requirement |
|---|---|
| CR-812-01 | No knowledge package MUST be distributed without prior human approval. |
| CR-812-02 | Knowledge items MUST reference verifiable evidence. Items without verifiable evidence MUST NOT be approved. |
| CR-812-03 | Knowledge packages MUST be delivered only to agents whose roles match the `target_roles` list. |
| CR-812-04 | Knowledge packages pending review for more than 5 business days MUST be escalated to the AI Council. |
| CR-812-05 | Input sources with quality scores below 0.60 MUST be flagged and their items withheld from distribution pending review. |
| CR-812-06 | Negative examples MUST be captured from failed intents, human overrides, ethics violations, and rollbacks. |
| CR-812-07 | Negative examples MUST undergo the same approval process as positive knowledge items. |

---

## 11. Security Considerations

Knowledge distribution is a vector for supply chain manipulation. An attacker who can inject approved knowledge items can alter agent decision patterns at scale without touching agent code. The evidence verification requirement (section 7.2) is the primary defence: knowledge that cannot be traced to a real operational event MUST NOT be approved. The approver MUST verify evidence references directly, not rely on the Learning Agent's summary.

---

## 12. Operational Considerations

Knowledge package quality degrades over time as network conditions change. Operators SHOULD set a knowledge package expiry period appropriate to their environment — network pattern knowledge may expire within 90 days in a high-change environment, while resolution knowledge may remain valid for 12 months. Expired knowledge packages MUST be reviewed before re-approval rather than automatically renewed.
