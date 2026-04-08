# ANIF-201: Business Architecture

| Field        | Value                    |
|--------------|--------------------------|
| Doc ID       | ANIF-201                 |
| Series       | Architecture             |
| Version      | 0.1.0                    |
| Status       | Draft                    |
| Authors      | ANIF Working Group       |
| Reviewers    | —                        |
| Approved by  | —                        |
| Created      | 2026-04-07               |
| Last updated | 2026-04-07               |
| Replaces     | N/A                      |
| Related docs | ANIF-200, ANIF-407       |

---

## Abstract

This document defines the Business Architecture for the Autonomous Networking & Infrastructure
Framework (ANIF). It describes the business capability map, value streams, stakeholder model,
governing business rules, capability maturity progression, and key performance indicators for
measuring autonomous operations success. All technical architecture decisions in the 200-series
MUST be traceable to a business capability or principle identified in this document.

---

## 1. Introduction

### 1.1 Purpose

This document establishes the business context, justification, and success criteria for the
ANIF platform. It ensures that every technical component serves a defined business need and
that the framework can be measured objectively against business outcomes.

### 1.2 Scope

This document covers:

- The business capability map for autonomous networking operations
- Value streams from business intent to network outcome
- Stakeholder identification and their interaction needs
- Business rules that drive technical decisions
- Capability maturity levels (Dark NOC progression)
- KPIs for measuring automation success
- Business justification for each ANIF principle

### 1.3 Out of Scope

- Technical implementation details (see ANIF-203, ANIF-204)
- Security controls and access models (see ANIF-205)
- Detailed operational procedures (see 400-series)
- Financial modelling or ROI calculations

### 1.4 Intended Audience

- Network operations leadership and management
- Business analysts translating business requirements to technical specifications
- Programme managers overseeing ANIF adoption
- Compliance and audit officers assessing governance alignment
- Architecture review boards

---

## 2. Normative References

- RFC 2119: Key words for use in RFCs to Indicate Requirement Levels
- ANIF-000: Framework Constitution
- ANIF-200: Reference Architecture
- TMForum IG1253: Autonomous Networks Technical Architecture
- TMForum GB921: eTOM Business Process Framework
- ITIL 4: IT Service Management framework
- ANIF-407: Operational KPIs and Metrics

---

## 3. Terms and Definitions

| Term                   | Definition                                                                                        |
|------------------------|---------------------------------------------------------------------------------------------------|
| Business Capability    | An organisational ability that enables a specific business outcome, independent of how it is implemented. |
| Value Stream           | The end-to-end sequence of activities that creates value for a stakeholder from a specific trigger. |
| Dark NOC               | A network operations model where routine tasks are handled autonomously, requiring human intervention only for exceptions. |
| Capability Maturity    | A model describing levels of process sophistication from fully manual to fully autonomous.        |
| Escalation Rate        | The proportion of automated actions that are escalated to human review.                           |
| Automation Coverage    | The percentage of network change events handled without human initiation.                         |
| MTTR                   | Mean Time To Remediate — the average time from incident detection to resolution.                  |

---

## 4. Business Architecture

### 4.1 Business Capability Map

ANIF enables six primary business capabilities. Each capability maps to one or more ANIF
technical components.

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                    ANIF Business Capability Map                              │
├──────────────────────┬───────────────────────────────────────────────────────┤
│  CAPABILITY DOMAIN   │  CAPABILITIES                                         │
├──────────────────────┼───────────────────────────────────────────────────────┤
│                      │ 1.1 Intent Expression & Ingestion                     │
│  1. Intent           │ 1.2 Intent Validation & Normalisation                 │
│     Management      │ 1.3 Intent Lifecycle Tracking                          │
│                      │ 1.4 Multi-source Intent Aggregation                   │
├──────────────────────┼───────────────────────────────────────────────────────┤
│                      │ 2.1 Policy Authoring & Version Control                │
│  2. Policy           │ 2.2 Policy Evaluation Against Intent                  │
│     Governance      │ 2.3 Conflict Detection & Resolution                    │
│                      │ 2.4 Compliance Policy Enforcement                     │
├──────────────────────┼───────────────────────────────────────────────────────┤
│                      │ 3.1 Risk Quantification                               │
│  3. Risk             │ 3.2 Trust Level Assessment                            │
│     Management      │ 3.3 Risk Appetite Configuration                        │
│                      │ 3.4 Risk Trend Analysis                               │
├──────────────────────┼───────────────────────────────────────────────────────┤
│                      │ 4.1 Bounded Action Execution                          │
│  4. Autonomous       │ 4.2 Rollback & Recovery                               │
│     Execution       │ 4.3 Vendor-Neutral Adapter Management                  │
│                      │ 4.4 Execution Status Reporting                        │
├──────────────────────┼───────────────────────────────────────────────────────┤
│                      │ 5.1 Governance Mode Management                        │
│  5. Human            │ 5.2 Approval Workflow                                 │
│     Oversight       │ 5.3 Immutable Audit Trail                              │
│                      │ 5.4 Explainability & Decision Transparency            │
├──────────────────────┼───────────────────────────────────────────────────────┤
│                      │ 6.1 Execution Outcome Capture                         │
│  6. Continuous       │ 6.2 Feedback Analysis & Suggestion Generation         │
│     Improvement     │ 6.3 Policy Refinement Workflows                        │
│                      │ 6.4 Maturity Level Progression                        │
└──────────────────────┴───────────────────────────────────────────────────────┘
```

### 4.2 Value Streams

ANIF supports three primary value streams:

#### 4.2.1 Value Stream 1: Autonomous Remediation

**Trigger**: Network anomaly detected (threshold breach, SLA violation, capacity alert)
**Outcome**: Network state restored to desired condition without human initiation

```
Anomaly Detected
      │
      ▼
Intent Expressed (by automation system or monitoring tool)
      │
      ▼
Intent Validated (schema, constraints, region bounds)
      │
      ▼
Policy Evaluated (SLA rules, compliance obligations, change windows)
      │
      ▼
Risk Scored (blast radius, reversibility, historical precedent)
      │
      ▼
Decision Made (bounded action selected)
      │
      ▼
Governance Check (mode = auto if risk < threshold)
      │
      ▼
Action Executed (reroute_traffic / apply_qos / scale_bandwidth / isolate_segment)
      │
      ▼
Network State Restored → SLA Preserved
      │
      ▼
Audit Record Written → Compliance Evidence Generated
```

**Business Value**: MTTR reduction; eliminates human latency in routine remediations.

#### 4.2.2 Value Stream 2: Controlled Change with Human Oversight

**Trigger**: Planned change request or high-risk automated detection
**Outcome**: Change reviewed, approved, and executed with full traceability

```
Change Intent Submitted
      │
      ▼
Risk Score Exceeds Threshold → Governance Mode = manual_review
      │
      ▼
Approval Ticket Created → Notification to Senior Engineer
      │
      ▼
Senior Engineer Reviews Decision Rationale and Audit Context
      │
      ▼
Approve → Action Executed        Reject → Intent Closed (blocked)
      │
      ▼
Audit Record: approval captured, approver identity recorded
```

**Business Value**: Human control retained for high-impact changes; full traceability for audit.

#### 4.2.3 Value Stream 3: Continuous Policy Improvement

**Trigger**: Periodic feedback analysis or post-incident review
**Outcome**: Policy or risk model refined to improve future automation accuracy

```
Execution History Accumulated
      │
      ▼
GET /feedback/analysis → Suggestions Generated
      │
      ▼
Policy Administrator Reviews Suggestions
      │
      ▼
Accept Suggestion → Policy Updated    Reject → Logged for review
      │
      ▼
Next Automation Cycle benefits from improved policy
```

**Business Value**: Automation quality improves over time; reduces false positives and escalations.

### 4.3 Stakeholder Map

Implementations MUST accommodate the needs of all stakeholders listed below.

| Stakeholder             | Role in ANIF           | Primary Needs                                                         |
|-------------------------|------------------------|-----------------------------------------------------------------------|
| Network Engineer        | Intent author, operator| Express intent easily; understand decisions; execute manual overrides |
| Senior Engineer         | Approver               | Review high-risk decisions; trust rationale; fast approval workflow   |
| Automation Agent        | Machine intent source  | Submit intents via API; receive structured outcomes; handle rejections|
| Policy Administrator    | Policy governance      | Author and update policies; review conflicts; manage feedback         |
| Compliance Officer      | Audit consumer         | Access immutable audit trail; verify compliance evidence              |
| Network Operations Mgr  | Oversight              | Monitor automation coverage; review KPIs; understand escalation trends|
| Security Team           | Risk oversight         | Review isolate_segment actions; verify RBAC enforcement; audit access |
| Vendor/Integration Eng  | Adapter author         | Clear adapter API contract; isolated integration context              |

### 4.4 Business Rules

The following business rules MUST be enforced by the ANIF platform. These rules translate
directly into technical requirements in downstream components.

| Rule ID | Business Rule                                                                                       | Technical Enforcement                              |
|---------|-----------------------------------------------------------------------------------------------------|----------------------------------------------------|
| BR-01   | No autonomous action may be taken without a validated intent on record.                             | Intent Engine; audit record required before execution |
| BR-02   | Actions affecting compliance-scoped resources MUST be reviewed by a senior engineer.                | Governance Gate; RBAC role check                   |
| BR-03   | Every executed action MUST be reversible or the action MUST NOT be executed.                        | P-01 Reversibility; rollback handler mandatory     |
| BR-04   | No action may be executed that violates a declared data residency constraint.                        | Intent constraints propagated to Action Executor   |
| BR-05   | Risk scores exceeding the configured threshold MUST escalate to manual review.                      | Risk Engine threshold; Governance Gate mode routing|
| BR-06   | Approval tickets MUST expire within 15 minutes of creation.                                         | Governance Gate; ticket expiry enforcement         |
| BR-07   | Audit records MUST NOT be deleted or modified after creation.                                       | Audit Service; no DELETE endpoint permitted        |
| BR-08   | Automation agents MUST NOT approve their own submitted intents.                                     | RBAC; automation_agent role cannot approve         |
| BR-09   | `isolate_segment` actions MUST require explicit capability declaration from the operator.           | Action Executor; capability check at execution     |
| BR-10   | Policy conflicts MUST be surfaced to the operator rather than silently resolved.                    | Policy Engine; conflict_detected flag in output    |

### 4.5 Capability Maturity: Dark NOC Progression

ANIF defines five maturity levels aligned with the TMForum Autonomous Networks framework.
Organisations MUST progress through these levels sequentially. Skipping levels is NOT RECOMMENDED.

```
Level 0: Manual
┌─────────────────────────────────────────────────────────────┐
│ All network changes initiated and executed by human staff.  │
│ Monitoring, diagnosis, and execution are manual processes.  │
│ ANIF role: None. Baseline for comparison.                   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
Level 1: Assisted
┌─────────────────────────────────────────────────────────────┐
│ ANIF validates intents and evaluates policy.                │
│ Decisions are presented to engineers for action.            │
│ ANIF role: Intent Engine + Policy Engine + Audit Service.   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
Level 2: Partial Automation
┌─────────────────────────────────────────────────────────────┐
│ Low-risk actions executed autonomously (mode = auto).       │
│ High-risk actions require human approval.                   │
│ ANIF role: Full pipeline; Governance Gate mode = hybrid.    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
Level 3: Conditional Autonomy
┌─────────────────────────────────────────────────────────────┐
│ Most actions autonomous; human oversight via exception.     │
│ Continuous feedback loop refines policy automatically.      │
│ ANIF role: Full pipeline + Feedback Loop active.            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
Level 4: Full Autonomy (Dark NOC)
┌─────────────────────────────────────────────────────────────┐
│ Human intervention only for novel or critical situations.   │
│ System self-tunes policy and risk models.                   │
│ ANIF role: Full pipeline + self-improving risk/policy model.│
└─────────────────────────────────────────────────────────────┘
```

Organisations adopting ANIF SHOULD begin at Level 1, validate governance and audit controls,
and advance to higher levels only when KPI thresholds for the current level are met.

### 4.6 KPIs for Autonomous Operations

The following KPIs MUST be tracked by organisations deploying ANIF. KPI targets are illustrative;
organisations SHOULD calibrate targets to their operational context.

| KPI ID | Metric                          | Definition                                                      | Target Direction | Illustrative Target |
|--------|---------------------------------|-----------------------------------------------------------------|------------------|---------------------|
| KPI-01 | MTTR Reduction                  | Reduction in mean time to remediate vs. manual baseline         | Decrease         | ≥ 60% reduction     |
| KPI-02 | Escalation Rate                 | % of intents routed to manual_review governance mode            | Decrease         | < 15% at Level 2    |
| KPI-03 | False Positive Rate             | % of autonomous actions later deemed incorrect or reversed      | Decrease         | < 5%                |
| KPI-04 | Automation Coverage             | % of network change events handled without human initiation     | Increase         | ≥ 80% at Level 3    |
| KPI-05 | Approval Turnaround Time        | Average time from ticket creation to approval/rejection         | Decrease         | < 5 minutes         |
| KPI-06 | Rollback Frequency              | % of executions that trigger rollback                           | Decrease         | < 2%                |
| KPI-07 | Audit Completeness              | % of pipeline executions with full audit trail                  | Increase         | 100% (mandatory)    |
| KPI-08 | Policy Conflict Rate            | % of intents triggering a policy conflict                       | Decrease         | < 10%               |
| KPI-09 | Feedback Acceptance Rate        | % of improvement suggestions accepted by policy administrators  | Increase (quality indicator) | > 40%  |
| KPI-10 | Time-to-Autonomy                | Elapsed time from Level 0 baseline to achieving Level 2 maturity| Decrease        | < 6 months          |

### 4.7 Business Justification for ANIF Principles

Each ANIF governing principle (P-01 through P-12) addresses a specific business risk or
requirement. Implementations MUST maintain traceability between principles and business needs.

| Principle   | Name                  | Business Justification                                                            |
|-------------|-----------------------|-----------------------------------------------------------------------------------|
| P-01        | Reversibility         | Reduces operational risk; ensures autonomous actions cannot cause irreversible outages. |
| P-02        | Auditability          | Satisfies compliance obligations; provides evidence for post-incident investigation.|
| P-03        | Determinism           | Ensures predictable behaviour; required for regulatory approval of automation.    |
| P-04        | Explainability        | Enables human operators to trust and verify automated decisions.                   |
| P-05        | Least Privilege       | Limits blast radius of compromised or misconfigured components.                    |
| P-06        | Human Override        | Regulatory and operational requirement; humans retain ultimate authority.          |
| P-07        | Fail Safe             | Prevents cascading failures when a pipeline component encounters an error.         |
| P-08        | Vendor Neutrality     | Protects against vendor lock-in; enables multi-vendor network environments.        |
| P-09        | Incremental Adoption  | Reduces adoption risk; enables phased rollout aligned with organisational readiness.|
| P-10        | Test-First            | Ensures reliability; reduces production incidents from untested automation logic.  |
| P-11        | Data Residency        | Satisfies legal and regulatory requirements for data localisation.                 |
| P-12        | Continuous Learning   | Ensures the system improves over time and adapts to changing network conditions.   |

---

## 5. Conformance Requirements

1. Implementations MUST support all six business capability domains defined in Section 4.1.
2. All three value streams MUST be demonstrable in a conformant ANIF deployment.
3. Business rules BR-01 through BR-10 MUST be enforced by corresponding technical controls.
4. KPIs KPI-01 through KPI-10 MUST be measurable from the Audit Service and pipeline data.
5. Implementations MUST support progression through all five maturity levels without architectural
   changes; only configuration and policy updates SHOULD be required for level transitions.
6. All twelve governing principles MUST have corresponding technical enforcement mechanisms.

---

## 6. Security Considerations

- Stakeholder access to ANIF capabilities MUST be controlled by the RBAC model defined in ANIF-205.
- Compliance Officer access to audit records MUST be read-only; no modification rights.
- Automation Agent role MUST NOT include approval authority (BR-08).
- KPI data derived from audit records inherits the sensitivity classification of those records.

---

## 7. Operational Considerations

- KPIs SHOULD be surfaced via a dashboard consuming data from `GET /audit` and
  `GET /feedback/analysis`.
- Maturity level assessments SHOULD be conducted quarterly and documented.
- Business rule changes MUST be versioned and reflected in policy sets before taking effect.
- Stakeholder onboarding programmes SHOULD be developed for each role defined in Section 4.3.

---

## Appendix A: Examples

### A.1 Capability Maturity Assessment Scorecard

| Capability Domain       | Level 0 | Level 1 | Level 2 | Level 3 | Level 4 |
|-------------------------|---------|---------|---------|---------|---------|
| Intent Management       | Manual  | ANIF    | ANIF    | ANIF    | ANIF    |
| Policy Governance       | Manual  | ANIF    | ANIF    | ANIF+Auto| ANIF+Auto|
| Risk Management         | Manual  | Assisted| ANIF    | ANIF    | Self-tuning|
| Autonomous Execution    | None    | None    | Low-risk| Most    | All     |
| Human Oversight         | All     | All     | Exceptions| Exceptions| Critical only|
| Continuous Improvement  | Manual  | Manual  | Assisted| ANIF    | Autonomous|

### A.2 Stakeholder RACI Matrix (Sample: Autonomous Remediation)

| Activity                    | Network Eng | Senior Eng | Automation Agent | Policy Admin | Compliance |
|-----------------------------|-------------|------------|------------------|--------------|------------|
| Submit Intent               | R/A         | —          | R/A              | —            | —          |
| Policy Evaluation           | I           | I          | I                | R/A          | C          |
| Risk Assessment             | I           | I          | I                | C            | I          |
| Auto Execution Approval     | —           | —          | —                | —            | —          |
| Manual Review Approval      | C           | R/A        | —                | C            | I          |
| Audit Access                | R           | R          | —                | R            | R/A        |

R = Responsible, A = Accountable, C = Consulted, I = Informed

---

## Appendix B: Change History

| Version | Date       | Author             | Summary                  |
|---------|------------|--------------------|--------------------------|
| 0.1.0   | 2026-04-07 | ANIF Working Group | Initial draft            |
