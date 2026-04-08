# ANIF-400: Operations Overview

| Field        | Value                                                      |
|--------------|------------------------------------------------------------|
| Doc ID       | ANIF-400                                                   |
| Series       | Operations                                                 |
| Version      | 0.1.0                                                      |
| Status       | Draft                                                      |
| Authors      | ANIF Working Group                                         |
| Reviewers    | —                                                          |
| Approved by  | —                                                          |
| Created      | 2026-04-07                                                 |
| Last updated | 2026-04-07                                                 |
| Replaces     | N/A                                                        |
| Related docs | ANIF-401, ANIF-402, ANIF-403, ANIF-404, ANIF-405, ANIF-406, ANIF-407 |

---

## Abstract

This document serves as the entry point for the ANIF Operations series (ANIF-400 through ANIF-407). It defines the operational domains of the Autonomous Networking & Infrastructure Framework, describes how the operations documents relate to one another, establishes the operational model that spans reactive (Level 0) through fully autonomous (Level 4) modes, and identifies the key metrics, roles, and responsibilities that govern ANIF operational deployments.

---

## 1. Introduction

### 1.1 Purpose

This document establishes the conceptual and structural foundation for the ANIF Operations series. It provides a unified reference that operators, architects, and governance stakeholders can use to understand which operational concerns are addressed by which documents in this series, and how those concerns interrelate at runtime.

### 1.2 Scope

This document covers:

- The operational domains recognised by ANIF.
- The relationships between operations series documents (ANIF-401 through ANIF-407).
- The five-level operational maturity model from fully manual (Level 0) to fully autonomous (Level 4).
- The key operational metrics and their target thresholds at each maturity level.
- Operational roles and their responsibilities within an ANIF deployment.

### 1.3 Out of Scope

The following are out of scope for this document:

- Detailed normative requirements for any individual operational domain (see the individual documents listed in Section 4).
- Physical infrastructure provisioning or capacity planning.
- Integration specifications with external ITSM tooling.
- Security hardening procedures (addressed in ANIF-600 series).

### 1.4 Intended Audience

| Audience                     | Usage                                                        |
|------------------------------|--------------------------------------------------------------|
| Network Operations Engineers | Understanding operational domains and maturity progression   |
| Automation Engineers         | Understanding pipeline stages and feedback mechanisms        |
| Governance and Compliance    | Understanding audit, explainability, and human oversight     |
| Architecture Teams           | Understanding how operational documents map to system design |
| Senior Management            | Understanding maturity levels and progression governance     |

---

## 2. Normative References

- ANIF-103: Governance Policy Framework
- ANIF-104: Policy Evaluation Engine
- ANIF-107: Audit and Immutable Logging Standard
- ANIF-305: Intent Execution Pipeline
- ANIF-401: Observability Standard
- ANIF-402: Explainability Requirements
- ANIF-403: Closed-Loop Feedback and Learning
- ANIF-404: Human-in-Loop Controls
- ANIF-405: Incident and Outage Modeling
- ANIF-406: Governance Controls
- ANIF-407: Dark NOC Maturity Model
- RFC 2119: Key words for use in RFCs to Indicate Requirement Levels

---

## 3. Terms and Definitions

| Term                    | Definition                                                                                                        |
|-------------------------|-------------------------------------------------------------------------------------------------------------------|
| Dark NOC                | A network operations centre that operates with minimal or zero human intervention during routine operations.       |
| Operational Domain      | A bounded area of operational concern addressed by one or more documents in this series.                          |
| Maturity Level          | A discrete stage (0–4) in the progression from fully manual to fully autonomous network operations.               |
| MTTR                    | Mean Time to Restore — the average elapsed time between incident detection and confirmed service restoration.      |
| Automation Coverage     | The percentage of operational actions executed autonomously without human approval in a given period.             |
| Escalation Rate         | The proportion of pipeline executions that are elevated to manual_review or block mode.                           |
| False Positive Rate     | The proportion of escalations that were approved without any change to the proposed action.                       |
| Rollback Rate           | The proportion of executed actions that were subsequently reversed by the system or an operator.                  |
| Closed-Loop Feedback    | A mechanism by which execution outcomes are analysed and used to generate improvement suggestions for policies.   |
| Reasoning Chain         | An ordered sequence of decision steps, each with a stage, input summary, decision, and rationale.                 |
| Trace ID                | A globally unique identifier assigned at pipeline entry and propagated through all stages and log entries.        |

---

## 4. Operational Domains

### 4.1 Domain Overview

ANIF operations are organised into seven domains. Each domain is addressed by one or more documents in this series.

| Domain                    | Document(s)          | Summary                                                                 |
|---------------------------|----------------------|-------------------------------------------------------------------------|
| Observability             | ANIF-401             | What is measured, how it is logged, and what dashboards MUST be provided |
| Explainability            | ANIF-402             | How automated decisions are made human-readable on demand               |
| Closed-Loop Feedback      | ANIF-403             | How execution outcomes feed back to improve policies and thresholds      |
| Human-in-Loop Controls    | ANIF-404             | How humans approve, halt, or override automated actions                 |
| Incident and Outage Modeling | ANIF-405          | How known incident patterns are detected, matched, and remediated       |
| Governance Controls       | ANIF-406             | How the governance gate is implemented and audited                      |
| Maturity Progression      | ANIF-407             | How organisations progress through autonomy levels safely               |

### 4.2 Inter-Document Relationships

The following describes the primary runtime dependencies between operations documents:

- ANIF-401 (Observability) is the data foundation. All other operational domains depend on the telemetry and log infrastructure that ANIF-401 mandates.
- ANIF-402 (Explainability) builds on ANIF-401 audit logs to produce human-readable reasoning chains. Governance review (ANIF-404, ANIF-406) depends on ANIF-402 output for approval decisions.
- ANIF-403 (Closed-Loop Feedback) consumes ANIF-401 audit logs and ANIF-402 reasoning chains to produce tuning suggestions. It is an input to ANIF-407 maturity assessment.
- ANIF-404 (Human-in-Loop) defines the approval workflow that is triggered by ANIF-406 governance gate outcomes.
- ANIF-406 (Governance Controls) is the runtime enforcement of ANIF-103 policies. It controls which pipeline executions proceed automatically and which require ANIF-404 approval.
- ANIF-405 (Incident Modeling) generates candidate intents that pass through the standard pipeline, including ANIF-406 governance checks and ANIF-404 approval flows.
- ANIF-407 (Maturity Model) synthesises metrics from all other domains to assess and advance operational maturity level.

---

## 5. Operational Model

### 5.1 Level Descriptions

ANIF defines five operational maturity levels. The operational model represents a progression from fully reactive, human-driven operations at Level 0 to fully proactive, autonomous operations at Level 4. Detailed entry/exit criteria, KPIs, and rollback conditions for each level are defined in ANIF-407.

| Level | Name                  | Characteristics                                                                                   |
|-------|-----------------------|---------------------------------------------------------------------------------------------------|
| 0     | Full Manual           | Operator makes all decisions; ANIF system observes and logs only                                  |
| 1     | Assisted              | System recommends actions; operator approves all changes before execution                         |
| 2     | Supervised            | System executes low-risk actions autonomously; operator approves high-risk changes                |
| 3     | Conditional Autonomy  | System executes all actions unless a configured threshold is breached; operator monitors          |
| 4     | Full Autonomy         | System self-manages within policy; operator sets policy only; human override always available     |

### 5.2 Operational Progression Principle

An ANIF deployment MUST NOT advance to a higher maturity level unless:

- All entry criteria for the target level are satisfied (per ANIF-407).
- Level advancement is approved by a senior stakeholder (per ANIF-407, Section 4.6).
- A documented rollback plan to the prior level is in place.

An ANIF deployment MAY remain at any maturity level indefinitely and SHOULD revert to a lower level if rollback conditions are met (per ANIF-407).

### 5.3 Reactive to Proactive Transition

The fundamental operational shift across the five levels is from reactive to proactive posture:

| Posture    | Levels  | Operational Characteristic                                           |
|------------|---------|----------------------------------------------------------------------|
| Reactive   | 0–1     | System responds to events after human detection and decision         |
| Transitional | 2–3  | System detects and acts on common events; humans handle edge cases   |
| Proactive  | 4       | System anticipates conditions and acts before impact is felt         |

---

## 6. Key Operational Metrics

### 6.1 Metric Definitions and Targets

The following metrics MUST be tracked by all ANIF deployments at Level 2 and above. Level 0 and Level 1 deployments SHOULD track these metrics.

| Metric                  | Definition                                                          | L2 Target    | L3 Target    | L4 Target    |
|-------------------------|---------------------------------------------------------------------|--------------|--------------|--------------|
| MTTR                    | Mean time from incident detection to verified service restoration   | < 30 min     | < 15 min     | < 5 min      |
| Automation Coverage     | % of actions executed without human approval                        | 40–60%       | 70–85%       | ≥ 90%        |
| Escalation Rate         | % of pipeline executions elevated to manual_review or block         | < 40%        | < 20%        | < 10%        |
| False Positive Rate     | % of escalations approved without change to proposed action         | < 30%        | < 15%        | < 5%         |
| Execution Failure Rate  | % of executed actions that resulted in a failure outcome            | < 10%        | < 5%         | < 2%         |
| Rollback Rate           | % of executed actions subsequently reversed                         | < 8%         | < 4%         | < 2%         |
| Policy Compliance Rate  | % of pipeline executions where all policies evaluated successfully  | ≥ 95%        | ≥ 98%        | ≥ 99.5%      |
| Audit Completeness      | % of pipeline executions with complete audit records                | 100%         | 100%         | 100%         |

### 6.2 Metric Collection Requirements

- All metrics MUST be derived from the ANIF audit log (ANIF-107) as the authoritative source.
- Metrics MUST be computed over rolling 24-hour and 7-day windows at minimum.
- Alert thresholds defined in ANIF-401 MUST trigger when metrics breach the boundaries defined in this section.

---

## 7. Operational Roles and Responsibilities

### 7.1 Role Definitions

| Role                  | Description                                                                                     |
|-----------------------|-------------------------------------------------------------------------------------------------|
| automation_agent      | Service identity used by automated pipeline components; MAY submit intents for execution        |
| network_engineer      | Human operator; MAY submit intents, approve manual_review tickets, and invoke emergency halt    |
| senior_engineer       | Human operator with elevated authority; MUST approve high-risk governance tickets               |
| governance_officer    | Reviews and audits governance decisions; has read-only access to all audit records              |
| compliance_auditor    | Reviews explainability records for regulatory purposes; uses ANIF-402 /why endpoint             |
| system_administrator  | Manages ANIF infrastructure; does not participate in operational approval flows                 |

### 7.2 Responsibility Matrix

| Responsibility                        | automation_agent | network_engineer | senior_engineer | governance_officer |
|---------------------------------------|:----------------:|:----------------:|:---------------:|:------------------:|
| Submit intent                         | Yes              | Yes              | Yes             | No                 |
| Approve manual_review ticket          | No               | Yes              | Yes             | No                 |
| Approve high-risk ticket              | No               | No               | Yes             | No                 |
| Invoke emergency halt                 | No               | Yes              | Yes             | No                 |
| Accept/reject feedback suggestion     | No               | Yes              | Yes             | No                 |
| Read audit records                    | No               | Yes              | Yes             | Yes                |
| Advance maturity level                | No               | No               | Yes             | No                 |

---

## 5. Conformance Requirements

The following statements are normative for all ANIF-conformant deployments:

1. An ANIF deployment MUST implement observability as defined in ANIF-401.
2. An ANIF deployment MUST implement explainability as defined in ANIF-402.
3. An ANIF deployment at Level 2 or above MUST implement human-in-loop controls as defined in ANIF-404.
4. An ANIF deployment at Level 2 or above MUST implement governance controls as defined in ANIF-406.
5. An ANIF deployment MUST NOT advance maturity levels without satisfying entry criteria defined in ANIF-407.
6. All pipeline executions MUST produce a complete audit record regardless of maturity level.
7. Human override MUST remain available at all maturity levels including Level 4.

---

## 6. Security Considerations

- Role assignments MUST be enforced at the API layer; a caller's role MUST be verified on every request.
- Audit records MUST be append-only and MUST NOT be modifiable by any operational role.
- Trace IDs MUST NOT contain personally identifiable information.
- Governance approval tokens MUST be time-limited (15-minute expiry per ANIF-406).
- Emergency halt capability MUST be available even when primary automation infrastructure is degraded.

---

## 7. Operational Considerations

- Deployments transitioning between maturity levels MUST plan for a parallel-run period of at least 14 days during which both the current and target level behaviours are observed before cut-over.
- Metric dashboards MUST be reviewed at a minimum weekly cadence at Level 2, and daily at Levels 3 and 4.
- The operations series documents SHOULD be reviewed and updated whenever a significant change to the ANIF pipeline is deployed.
- Feedback suggestions (ANIF-403) MUST be reviewed on a defined schedule; suggestions SHOULD NOT remain unreviewed for more than 7 days.

---

## Appendix A: Examples

### A.1 Operational Domain at Runtime

A typical Level 2 execution proceeds through the following operational domains:

```
Intent submitted
    ↓
[ANIF-401] Observability: trace_id assigned, request logged
    ↓
[ANIF-406] Governance Controls: risk score evaluated, mode=manual_review (risk=72)
    ↓
[ANIF-404] Human-in-Loop: approval ticket created, operator notified
    ↓
Operator reviews: [ANIF-402] Explainability /why consulted
    ↓
Operator approves ticket
    ↓
[ANIF-305] Execution proceeds
    ↓
[ANIF-401] Outcome logged
    ↓
[ANIF-403] Outcome fed into feedback analysis
```

---

## Appendix B: Change History

| Version | Date       | Author             | Change                    |
|---------|------------|--------------------|---------------------------|
| 0.1.0   | 2026-04-07 | ANIF Working Group | Initial draft             |
