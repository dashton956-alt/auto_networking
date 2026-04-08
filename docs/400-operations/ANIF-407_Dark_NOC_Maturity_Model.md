# ANIF-407: Dark NOC Maturity Model

| Field        | Value                              |
|--------------|------------------------------------|
| Doc ID       | ANIF-407                           |
| Series       | Operations                         |
| Version      | 0.1.0                              |
| Status       | Draft                              |
| Authors      | ANIF Working Group                 |
| Reviewers    | —                                  |
| Approved by  | —                                  |
| Created      | 2026-04-07                         |
| Last updated | 2026-04-07                         |
| Replaces     | N/A                                |
| Related docs | ANIF-400, ANIF-403, ANIF-500       |

---

## Abstract

This document defines the Dark NOC Maturity Model for ANIF-conformant deployments. The model describes five discrete operational maturity levels (0 through 4), ranging from fully manual operations to full autonomous self-management. For each level, this document provides normative entry and exit criteria, required ANIF components, KPI targets, and rollback conditions. It also specifies the governance requirements for level advancement, the process for declaring an organisation's current ANIF conformance level, and the relationship between Dark NOC maturity levels and ANIF conformance levels L1 through L4.

---

## 1. Introduction

### 1.1 Purpose

This document establishes the normative framework by which organisations assess their current operational autonomy level, define a progression path, and demonstrate readiness to advance to higher levels of autonomous network management. The maturity model provides a shared vocabulary for discussing automation progress and a structured gate process that ensures advancement is evidence-based and reversible.

### 1.2 Scope

This document covers:

- The five maturity level definitions (Level 0 through Level 4).
- Required ANIF components for each level.
- Normative entry and exit criteria for each level.
- KPI targets at each level.
- Rollback/downgrade criteria for each level.
- Progression governance: approval requirements and evidence standards.
- Level declaration process for organisations.
- Relationship to ANIF conformance levels L1 through L4.

### 1.3 Out of Scope

- Implementation instructions for specific ANIF components (covered in respective component documents).
- Vendor-specific tooling recommendations.
- Business case or ROI analysis for Dark NOC progression.
- Workforce change management (addressed in implementation planning documents).

### 1.4 Intended Audience

| Audience                       | Usage                                                                  |
|--------------------------------|------------------------------------------------------------------------|
| Senior Management              | Understanding level definitions and governance requirements             |
| Network Operations Leadership  | Planning and executing maturity progression                             |
| Governance and Compliance      | Auditing level declarations and progression evidence                    |
| Architecture Teams             | Understanding required components at each level                         |
| Operations Engineers           | Understanding KPI targets and operational obligations per level          |

---

## 2. Normative References

- ANIF-400: Operations Overview
- ANIF-401: Observability Standard
- ANIF-402: Explainability Requirements
- ANIF-403: Closed-Loop Feedback and Learning
- ANIF-404: Human-in-Loop Controls
- ANIF-405: Incident and Outage Modeling
- ANIF-406: Governance Controls
- ANIF-500: Conformance Framework
- ANIF-107: Audit and Immutable Logging Standard
- RFC 2119: Key words for use in RFCs to Indicate Requirement Levels

---

## 3. Terms and Definitions

| Term                      | Definition                                                                                                     |
|---------------------------|----------------------------------------------------------------------------------------------------------------|
| Maturity Level            | A discrete stage (0–4) characterising the degree to which ANIF automation operates autonomously.              |
| Entry Criteria            | Conditions that MUST be satisfied before an organisation may operate at a given maturity level.                |
| Exit Criteria             | Evidence that MUST be demonstrated to qualify for advancement to the next maturity level.                      |
| Rollback Condition        | A metric breach or operational failure that MUST trigger reversion to the previous maturity level.             |
| Level Declaration         | An organisation's formal statement of its current ANIF conformance level, supported by evidence.              |
| KPI                       | Key Performance Indicator — a quantitative measure used to assess operational performance.                     |
| Progression Governance    | The approval and evidence process required before advancing to a higher maturity level.                        |
| ANIF Conformance Level    | The L1–L4 conformance designations defined in ANIF-500, aligned with Dark NOC maturity levels.                |
| P-06                      | ANIF Principle 6: Human override is absolute at all maturity levels.                                           |

---

## 4. Maturity Level Definitions

### 4.1 Overview

| Level | Name                  | Autonomy Characteristic                                               | ANIF Conformance |
|-------|-----------------------|-----------------------------------------------------------------------|------------------|
| 0     | Full Manual           | No automation; system observes and logs only                          | Pre-conformance  |
| 1     | Assisted              | Recommendations provided; all changes human-approved                  | L1               |
| 2     | Supervised            | Low-risk actions automated; high-risk actions human-approved          | L2               |
| 3     | Conditional Autonomy  | All actions automated unless threshold breached; human monitors       | L3               |
| 4     | Full Autonomy         | Self-managing within policy; human sets policy and retains override   | L4               |

---

### 4.2 Level 0: Full Manual

#### 4.2.1 Description

At Level 0, all network operational decisions are made and executed by human operators. The ANIF system is deployed in observation mode: it logs events, captures telemetry, and generates reports, but does not recommend or execute any actions autonomously.

#### 4.2.2 Key Characteristics

- All intent is authored and executed manually by operators.
- ANIF pipeline is deployed but governance gate always returns `manual_review`.
- Observability and audit infrastructure is active and validated.
- No automated execution capability is enabled.

#### 4.2.3 Required ANIF Components

| Component                  | Requirement |
|----------------------------|-------------|
| ANIF-401 Observability     | MUST be deployed and validated |
| ANIF-107 Audit Logging     | MUST be deployed and validated |
| ANIF-402 Explainability    | SHOULD be deployed (required for Level 1) |
| ANIF-406 Governance Gate   | SHOULD be deployed in observe-only mode |

#### 4.2.4 Entry Criteria

- ANIF observability infrastructure is deployed and producing complete audit records.
- On-call operator coverage is established for all operational hours.
- Baseline operational metrics (MTTR, incident counts) have been recorded for at least 30 days.

#### 4.2.5 Exit Criteria (to advance to Level 1)

The following MUST be demonstrated over a minimum 30-day observation period:

| Criterion                                                          | Threshold      |
|--------------------------------------------------------------------|----------------|
| Audit completeness rate                                            | 100%           |
| Observability infrastructure uptime                                | ≥ 99.5%        |
| ANIF-402 /why endpoint deployed and returning valid responses      | Yes            |
| ANIF-406 governance gate deployed in shadow mode                   | Yes            |
| 30-day baseline MTTR recorded                                      | Yes            |
| Operator training on ANIF review interface completed               | 100% of team   |

#### 4.2.6 KPIs at Level 0

| KPI                     | Measurement        | Target |
|-------------------------|--------------------|--------|
| MTTR                    | Baseline (record)  | Record baseline — no target |
| Automation Coverage     | %                  | 0% (by definition) |
| Audit Completeness      | %                  | 100%   |
| Observability Uptime    | %                  | ≥ 99.5% |

#### 4.2.7 Rollback Conditions

Level 0 is the baseline; there is no lower level to revert to. If observability or audit infrastructure fails to meet the entry criteria, the organisation MUST NOT attempt to advance.

---

### 4.3 Level 1: Assisted

#### 4.3.1 Description

At Level 1, the ANIF system analyses telemetry and policy state and generates recommended actions for operator review. Operators review recommendations, author the corresponding intents, and approve all executions. No automated execution occurs without explicit human approval.

#### 4.3.2 Key Characteristics

- System generates intent recommendations; operators review and approve before execution.
- Governance gate is active; all executions route through the approval workflow.
- Explainability API is available and used by operators for all approval decisions.
- Feedback analysis is active and generating suggestions for operator review.

#### 4.3.3 Required ANIF Components

| Component                   | Requirement |
|-----------------------------|-------------|
| ANIF-401 Observability      | MUST be deployed and fully operational |
| ANIF-402 Explainability     | MUST be deployed and operational |
| ANIF-404 Human-in-Loop      | MUST be deployed; all executions require approval |
| ANIF-406 Governance Gate    | MUST be deployed; all intents evaluated |
| ANIF-107 Audit Logging      | MUST be fully operational |
| ANIF-403 Feedback           | SHOULD be deployed; suggestions reviewed by operators |

#### 4.3.4 Entry Criteria

All Level 0 exit criteria MUST be met. Additionally:

- ANIF-404 human-in-loop controls are deployed and tested.
- ANIF-406 governance gate is deployed and evaluating all rules.
- Role assignments (network_engineer, senior_engineer) are assigned and tested.
- Approval workflow has been exercised in a non-production environment.

#### 4.3.5 Exit Criteria (to advance to Level 2)

The following MUST be demonstrated over a minimum 30-day operating period at Level 1:

| Criterion                                                           | Threshold     |
|---------------------------------------------------------------------|---------------|
| Audit completeness rate                                             | 100%          |
| Approval ticket expiry rate                                         | < 15%         |
| False positive rate (escalations approved without change)           | < 40%         |
| /why endpoint queried for ≥ 80% of approval decisions              | Yes           |
| Feedback suggestions reviewed within 7 days (% resolved)          | ≥ 80%         |
| MTTR improvement vs Level 0 baseline                                | ≥ 10%         |
| Zero governance rule violations (R-05, R-06 bypasses)              | Yes           |

#### 4.3.6 KPIs at Level 1

| KPI                     | Target         |
|-------------------------|----------------|
| MTTR                    | ≥ 10% improvement over Level 0 baseline |
| Automation Coverage     | 0–5% (recommendations only) |
| Escalation Rate         | N/A (all executions are manual_review at this level) |
| False Positive Rate     | < 40%          |
| Audit Completeness      | 100%           |
| Ticket Expiry Rate      | < 15%          |

#### 4.3.7 Rollback Conditions from Level 1

The deployment MUST revert to Level 0 if any of the following occur:

- Audit completeness falls below 99% for any 7-day period.
- A governance rule bypass (R-05 or R-06 override) is detected.
- Observability infrastructure is unavailable for more than 4 hours in any 24-hour period.

---

### 4.4 Level 2: Supervised

#### 4.4.1 Description

At Level 2, the ANIF system executes low-risk actions autonomously (mode=auto). High-risk actions (risk_score ≥ 70, isolate_segment, or other manual_review triggers) require human approval. Operators actively monitor the system's autonomous decisions and are expected to review feedback suggestions regularly.

#### 4.4.2 Key Characteristics

- Actions with mode=auto execute without human approval.
- Actions with mode=manual_review require senior_engineer approval within 15 minutes.
- Actions with mode=block are refused and logged.
- Operators monitor the dashboard for anomalies in autonomous decisions.
- Closed-loop feedback is active and regularly reviewed.
- Incident modeling SHOULD be deployed and generating candidate intents.

#### 4.4.3 Required ANIF Components

| Component                   | Requirement |
|-----------------------------|-------------|
| ANIF-401 Observability      | MUST be fully operational with all dashboards active |
| ANIF-402 Explainability     | MUST be fully operational |
| ANIF-403 Feedback           | MUST be deployed and feedback reviewed weekly minimum |
| ANIF-404 Human-in-Loop      | MUST be deployed; senior_engineer coverage required |
| ANIF-405 Incident Modeling  | SHOULD be deployed |
| ANIF-406 Governance Gate    | MUST be fully operational with all rules active |
| ANIF-107 Audit Logging      | MUST be fully operational |

#### 4.4.4 Entry Criteria

All Level 1 exit criteria MUST be met. Additionally:

- Governance gate has been validated across all six rules in a staging environment.
- Senior engineer on-call rotation is established with < 10-minute average response time.
- Alert thresholds (ANIF-401) are configured and tested.
- Rollback capability has been tested in a non-production environment.

#### 4.4.5 Exit Criteria (to advance to Level 3)

The following MUST be demonstrated over a minimum 60-day operating period at Level 2:

| Criterion                                                           | Threshold     |
|---------------------------------------------------------------------|---------------|
| Automation Coverage                                                 | 40–70%        |
| Escalation Rate (24h rolling average)                               | < 30%         |
| False Positive Rate                                                 | < 20%         |
| Execution Failure Rate                                              | < 8%          |
| Rollback Rate                                                       | < 6%          |
| MTTR vs Level 1                                                     | ≥ 20% improvement |
| Zero unreviewed feedback suggestions older than 14 days             | Yes           |
| No critical alert left unacknowledged for > 30 minutes              | Yes (100% compliance over 60 days) |
| Incident modeling generating valid candidate intents                | If deployed: ≥ 90% of P0/P1 incidents |

#### 4.4.6 KPIs at Level 2

| KPI                     | Target         |
|-------------------------|----------------|
| MTTR                    | < 30 min       |
| Automation Coverage     | 40–60%         |
| Escalation Rate         | < 40%          |
| False Positive Rate     | < 30%          |
| Execution Failure Rate  | < 10%          |
| Rollback Rate           | < 8%           |
| Policy Compliance Rate  | ≥ 95%          |

#### 4.4.7 Rollback Conditions from Level 2

The deployment MUST revert to Level 1 if any of the following occur:

- Execution Failure Rate exceeds 20% for any 7-day period.
- Rollback Rate exceeds 15% for any 7-day period.
- MTTR increases by more than 25% above the Level 1 baseline for any 14-day period.
- A critical alert is unacknowledged for more than 2 hours.
- A governance bypass of R-05 or R-06 is detected.

---

### 4.5 Level 3: Conditional Autonomy

#### 4.5.1 Description

At Level 3, the ANIF system executes all actions autonomously unless a configured threshold is breached or a governance rule is triggered. Operators transition from active approvers to active monitors. The system is expected to handle the majority of operational events without human intervention; humans focus on exception handling and policy governance.

#### 4.5.2 Key Characteristics

- The vast majority of actions execute via mode=auto.
- manual_review is triggered only by specific conditions (R-01, R-02 with tightened thresholds, R-04).
- Operators monitor dashboards continuously and respond to escalations.
- Incident modeling is fully operational and generating candidate intents for known incident types.
- Feedback analysis is reviewed at minimum weekly; tuning suggestions are acted upon promptly.

#### 4.5.3 Required ANIF Components

| Component                   | Requirement |
|-----------------------------|-------------|
| All Level 2 components      | MUST remain fully operational |
| ANIF-405 Incident Modeling  | MUST be deployed and fully operational |
| ANIF-403 Feedback           | MUST be reviewed weekly; suggestions actioned within 7 days |

#### 4.5.4 Entry Criteria

All Level 2 exit criteria MUST be met. Additionally:

- Incident modeling has been validated in a staging environment for all defined incident types.
- Thresholds have been tuned based on Level 2 feedback analysis data.
- Operators are trained for monitoring-mode responsibilities (exception handling, escalation response).
- A formal level advancement approval has been obtained from a senior stakeholder (Section 4.7).

#### 4.5.5 Exit Criteria (to advance to Level 4)

The following MUST be demonstrated over a minimum 90-day operating period at Level 3:

| Criterion                                                             | Threshold     |
|-----------------------------------------------------------------------|---------------|
| Automation Coverage                                                   | ≥ 75%         |
| Escalation Rate                                                       | < 15%         |
| False Positive Rate                                                   | < 10%         |
| Execution Failure Rate                                                | < 4%          |
| Rollback Rate                                                         | < 3%          |
| MTTR vs Level 2                                                       | ≥ 30% improvement |
| Incident modeling: ≥ 95% of P0/P1 incidents auto-detected and resolved| Yes          |
| Zero critical alerts unacknowledged for > 15 minutes                  | Yes           |
| Feedback suggestion backlog: zero suggestions > 7 days old            | Yes           |

#### 4.5.6 KPIs at Level 3

| KPI                     | Target         |
|-------------------------|----------------|
| MTTR                    | < 15 min       |
| Automation Coverage     | 70–85%         |
| Escalation Rate         | < 20%          |
| False Positive Rate     | < 15%          |
| Execution Failure Rate  | < 5%           |
| Rollback Rate           | < 4%           |
| Policy Compliance Rate  | ≥ 98%          |

#### 4.5.7 Rollback Conditions from Level 3

The deployment MUST revert to Level 2 if any of the following occur:

- Execution Failure Rate exceeds 10% for any 7-day period.
- Rollback Rate exceeds 8% for any 7-day period.
- MTTR increases by more than 30% above the Level 2 baseline for any 14-day period.
- Escalation Rate exceeds 30% for any 7-day period.
- A security incident is detected that is attributable to an autonomous action.
- Human override (P-06) is invoked more than 5 times in a 7-day period (indicates loss of confidence in automation).

---

### 4.6 Level 4: Full Autonomy

#### 4.6.1 Description

At Level 4, the ANIF system self-manages the network within the boundaries of defined policies. Human operators focus exclusively on policy authorship, strategic governance, and exception handling. The system continuously monitors itself, adapts to changing conditions, and escalates only when it encounters a scenario genuinely outside its policy envelope. Human override (P-06) remains available and exercisable at all times.

#### 4.6.2 Key Characteristics

- The system executes all routine operations without human approval.
- manual_review is reserved for novel scenarios outside the policy envelope.
- Feedback analysis drives continuous policy refinement; suggestions are reviewed and acted upon promptly.
- Incident modeling provides autonomous recovery for all catalogued incident types.
- Human operators set policy and respond to genuinely novel escalations.
- Human override (P-06) is always available and exercisable.

#### 4.6.3 Required ANIF Components

| Component                   | Requirement |
|-----------------------------|-------------|
| All Level 3 components      | MUST remain fully operational |
| All ANIF-400 series docs    | MUST be fully implemented |
| ANIF-500 Conformance        | Formal L4 conformance declaration MUST be obtained |

#### 4.6.4 Entry Criteria

All Level 3 exit criteria MUST be met. Additionally:

- ANIF-500 L4 conformance assessment has been completed and passed.
- A formal level advancement approval from a senior stakeholder with executive authority has been obtained.
- A documented rollback plan to Level 3 is in place and tested.
- Independent review of the governance framework has been completed by a qualified third party.

#### 4.6.5 Exit Criteria

Level 4 is the highest defined maturity level. There is no advancement beyond Level 4. Instead, organisations at Level 4 MUST:

- Perform a formal re-assessment against Level 4 KPIs every 6 months.
- Revert to Level 3 if rollback conditions are met (Section 4.6.7).

#### 4.6.6 KPIs at Level 4

| KPI                     | Target         |
|-------------------------|----------------|
| MTTR                    | < 5 min        |
| Automation Coverage     | ≥ 90%          |
| Escalation Rate         | < 10%          |
| False Positive Rate     | < 5%           |
| Execution Failure Rate  | < 2%           |
| Rollback Rate           | < 2%           |
| Policy Compliance Rate  | ≥ 99.5%        |
| Incident Auto-Resolution| ≥ 99% of catalogued types |

#### 4.6.7 Rollback Conditions from Level 4

The deployment MUST revert to Level 3 if any of the following occur:

- Execution Failure Rate exceeds 5% for any 7-day period.
- Rollback Rate exceeds 5% for any 7-day period.
- MTTR degrades to more than 15 minutes sustained over any 14-day period.
- A security incident attributable to autonomous action occurs.
- Human override (P-06) is invoked more than 3 times in a 7-day period.
- ANIF-500 re-assessment results in failure to maintain L4 conformance.

---

## 5. Progression Governance

### 5.1 Level Advancement Approval

Level advancement MUST be approved before the deployment transitions to operating at a higher maturity level. The following requirements apply:

| Advancement          | Required Approver                              | Evidence Required                                 |
|----------------------|------------------------------------------------|---------------------------------------------------|
| Level 0 → Level 1   | Operations Manager or equivalent               | 30-day baseline data, training completion records |
| Level 1 → Level 2   | Senior Engineering Lead                        | Level 1 exit criteria evidence package            |
| Level 2 → Level 3   | Director of Network Operations or equivalent   | Level 2 exit criteria evidence package, risk review |
| Level 3 → Level 4   | VP or C-level with executive authority         | Level 3 exit criteria evidence, independent review |

### 5.2 Evidence Package Requirements

An evidence package submitted for level advancement MUST include:

1. KPI data for the required operating period, sourced from the ANIF audit log.
2. A summary of all rollback events during the operating period and their resolutions.
3. A summary of feedback suggestions generated, reviewed, and actioned.
4. A statement confirming all exit criteria are met, signed by the approving authority.
5. A documented rollback plan for the target level.
6. A change log of any policy or threshold changes made during the operating period.

### 5.3 Level Declarations

Organisations MAY formally declare their current ANIF conformance level. A level declaration:

- MUST be supported by a completed evidence package (Section 5.2).
- MUST be reviewed and renewed annually.
- MUST be updated within 30 days if a rollback condition is triggered.
- MAY be submitted to the ANIF Working Group for external validation.

---

## 6. Relationship to ANIF Conformance Levels

The Dark NOC maturity levels map to ANIF conformance levels as follows:

| Dark NOC Level | ANIF Conformance Level | Description                                              |
|----------------|------------------------|----------------------------------------------------------|
| Level 0        | Pre-conformance        | Observability deployed; no automation                    |
| Level 1        | L1                     | Human-in-loop controls and governance gate operational  |
| Level 2        | L2                     | Selective autonomous execution with governance controls  |
| Level 3        | L3                     | Broad autonomous execution with threshold-based escalation |
| Level 4        | L4                     | Full autonomous self-management within policy            |

Formal ANIF conformance levels (L1–L4) are assessed and certified through the process defined in ANIF-500. Operating at a given Dark NOC maturity level is a prerequisite for seeking the corresponding ANIF conformance level designation but does not automatically confer it; formal assessment is required.

---

## 7. Conformance Requirements

1. An organisation claiming to operate at a given maturity level MUST satisfy all entry criteria for that level as defined in this document.
2. An organisation MUST NOT advance to a higher maturity level without satisfying all exit criteria for the current level.
3. Level advancement MUST be approved by the appropriate approver as defined in Section 5.1.
4. An evidence package MUST be produced and retained for each level advancement.
5. Rollback conditions are normative: if a rollback condition is triggered, the organisation MUST revert to the prior level within 48 hours and MUST notify the approving authority.
6. Human override capability (P-06) MUST remain operational at all maturity levels including Level 4.

---

## 8. Security Considerations

- Level advancement decisions MUST be logged as governance events in the ANIF audit log.
- Evidence packages MUST be stored in a tamper-evident manner.
- At Level 4, the expanded autonomous execution scope increases the blast radius of any misconfigured policy; policy changes at Level 4 MUST be reviewed by at least two senior engineers before deployment.
- Rollback capability from Level 4 to Level 3 MUST be tested at least once every 6 months.

---

## 9. Operational Considerations

- Organisations SHOULD plan for a transition period of at least 60 days at each level before beginning the evidence collection period for exit criteria.
- Maturity level KPI dashboards SHOULD be visible to senior management to maintain organisational awareness of progression status.
- Organisations SHOULD maintain a designated maturity programme owner responsible for tracking exit criteria, managing evidence packages, and coordinating advancement approvals.
- Culture change is often the limiting factor in progression; technical readiness SHOULD be assessed separately from organisational readiness.

---

## Appendix A: Examples

### A.1 KPI Summary Table Across Levels

| KPI                     | Level 0 | Level 1     | Level 2   | Level 3   | Level 4  |
|-------------------------|---------|-------------|-----------|-----------|----------|
| MTTR                    | Baseline| ≥10% better | < 30 min  | < 15 min  | < 5 min  |
| Automation Coverage     | 0%      | 0–5%        | 40–60%    | 70–85%    | ≥ 90%    |
| Escalation Rate         | N/A     | N/A (all manual) | < 40% | < 20%  | < 10%    |
| False Positive Rate     | N/A     | < 40%       | < 30%     | < 15%     | < 5%     |
| Execution Failure Rate  | N/A     | N/A         | < 10%     | < 5%      | < 2%     |
| Rollback Rate           | N/A     | N/A         | < 8%      | < 4%      | < 2%     |
| Policy Compliance Rate  | N/A     | 100%        | ≥ 95%     | ≥ 98%     | ≥ 99.5%  |

### A.2 Level Advancement Checklist (Level 2 → Level 3)

```
Level 2 Exit Criteria Verification Checklist
Operating period: 60 days minimum

[ ] Automation Coverage ≥ 40% (current: ___%)
[ ] Escalation Rate < 30% (current: ___%)
[ ] False Positive Rate < 20% (current: ___%)
[ ] Execution Failure Rate < 8% (current: ___%)
[ ] Rollback Rate < 6% (current: ___%)
[ ] MTTR improvement ≥ 20% vs Level 1 (current: ___%)
[ ] No feedback suggestions > 14 days old (current oldest: ___ days)
[ ] No critical alert unacknowledged > 30 min (100% compliance confirmed: Y/N)
[ ] Incident modeling generating candidate intents for ≥ 90% of P0/P1 incidents: Y/N

Evidence package prepared by: _______________
Reviewed by: _______________
Approved for Level 3 by: _______________  Date: ___________
```

---

## Appendix B: Change History

| Version | Date       | Author             | Change                    |
|---------|------------|--------------------|---------------------------|
| 0.1.0   | 2026-04-07 | ANIF Working Group | Initial draft             |
