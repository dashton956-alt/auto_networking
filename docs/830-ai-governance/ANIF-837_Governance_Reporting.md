# ANIF-837: AI Governance Reporting and Metrics

| Field        | Value                                              |
|--------------|----------------------------------------------------|
| Doc ID       | ANIF-837                                           |
| Series       | AI Governance                                      |
| Version      | 0.1.0                                              |
| Status       | Draft                                              |
| Authors      | ANIF Working Group                                 |
| Reviewers    | —                                                  |
| Approved by  | —                                                  |
| Created      | 2026-04-08                                         |
| Last updated | 2026-04-08                                         |
| Replaces     | N/A                                                |
| Related docs | ANIF-822, ANIF-830, ANIF-831, ANIF-817             |

---

## Abstract

This document defines the mandatory governance reporting requirements for ANIF-conformant deployments. The governance committee MUST receive a monthly report covering: ethics incident counts by severity, active ethics strike counts, AI Council decisions, cost trends versus budget, override rates by agent, and hallucination rejection rates. Three escalation triggers require an emergency governance committee meeting regardless of the normal meeting schedule: any Severity 1 security incident, cost circuit breaker activation, and any agent override rate exceeding 20% of its recommendations.

---

## 1. Introduction

### 1.1 Purpose

Governance without regular, structured reporting is governance in name only. This document defines what the governance committee MUST know, how often it MUST be told, and what conditions require immediate escalation outside the normal reporting cycle.

### 1.2 Scope

This document covers mandatory monthly reporting content, escalation triggers for emergency meetings, and reporting format requirements.

### 1.3 Out of Scope

This document does not cover the governance committee's meeting procedures (see ANIF-831) or the AI-specific observability metrics feeding the reports (see ANIF-822).

### 1.4 Intended Audience

- The AI Risk Officer responsible for producing governance reports
- Governance committee members receiving and reviewing reports
- AI Council members providing input to reports
- Conformance assessors verifying reporting compliance

---

## 2. Normative References

| Reference | Title |
|---|---|
| ANIF-716 | Agent Failure and Progressive Intervention |
| ANIF-808 | Human-Agent Collaboration Model |
| ANIF-817 | AI Cost Optimisation and Governance |
| ANIF-822 | AI Observability and Model Health |
| ANIF-831 | AI Governance Structure and Accountability |
| RFC 2119 | Key words for use in RFCs to Indicate Requirement Levels |

---

## 3. Monthly Governance Report

### 3.1 Cadence and Delivery

A governance report MUST be produced and delivered to all governance committee members no later than the 10th calendar day of each month, covering the preceding calendar month. Reports delivered after this deadline are a governance process violation.

### 3.2 Mandatory Report Sections

#### 3.2.1 Ethics Incident Summary

| Item | Content |
|---|---|
| Incident count | Total ethics incidents in the period, broken down by severity (Critical, High, Medium, Low) |
| Trend | Month-over-month comparison |
| Open incidents | Count and age of ethics incidents not yet resolved |
| Incident descriptions | Summary of each Critical and High incident, including root cause and resolution status |

#### 3.2.2 Active Ethics Strikes

| Item | Content |
|---|---|
| Strike summary | Count of agents currently holding 1, 2, or 3 ethics strikes |
| New strikes | Agents that received a new strike in the reporting period |
| Strike history | Agents that have reached 3 strikes and their current lifecycle state |

#### 3.2.3 AI Council Decisions

| Item | Content |
|---|---|
| Decision count | Total council decisions in the period |
| Decision outcomes | Breakdown by: approved, rejected, escalated |
| Significant decisions | Summary of any council decision with significant operational impact |
| Voting patterns | Identification of any unusual voting patterns flagged by monitoring (ANIF-846 rule CR-SEC-05) |

#### 3.2.4 Cost Trends

| Item | Content |
|---|---|
| Total AI cost | Actual vs approved budget for the period |
| Cost by model tier | Breakdown of cost across small, mid, and full model tiers |
| Cost by agent role | Top 10 agent roles by token consumption |
| Circuit breaker events | Any cost circuit breaker activations during the period |
| Budget trajectory | Projected annual spend vs approved annual budget |

#### 3.2.5 Override Rates

| Item | Content |
|---|---|
| Overall override rate | Proportion of agent recommendations overridden across all agents |
| Override rate by agent | Per-agent override rate; agents above 20% threshold flagged |
| Override reasons | Most frequent override reason categories |
| Trend | Month-over-month comparison |

#### 3.2.6 AI Model Health

| Item | Content |
|---|---|
| Hallucination rejection rate | Per-agent hallucination rejection rate; agents above 3% threshold flagged |
| Model drift scores | Per-agent drift scores; agents above 0.21 threshold flagged |
| Confidence score trends | 30-day rolling average by agent role |
| Recommendation acceptance rates | Per-agent; flags at rates below 60% or above 98% |
| Token usage anomalies | Any anomalies detected in the period |

#### 3.2.7 Programme Status

| Item | Content |
|---|---|
| Current migration phase | Current phase and step per ANIF-823 |
| Milestone gate status | Status of any in-progress milestone gate assessment |
| DR drill status | Completion status of required quarterly and annual drills |
| Open risk register items | Count of open risks by severity; any risks above committee involvement threshold |

---

## 4. Escalation Triggers for Emergency Committee Meetings

The following conditions MUST trigger an emergency governance committee meeting within 48 hours, regardless of the normal meeting schedule:

| Trigger | Meeting Required Within |
|---|---|
| Any Severity 1 security incident | 24 hours |
| Cost circuit breaker activation (ANIF-817) | 48 hours |
| Any agent with override rate exceeding 20% of recommendations (sustained for more than 7 days) | 48 hours |
| Any Critical ethics violation | 48 hours |
| Any failure to complete a mandatory DR drill by its due date | 5 business days |

Emergency meetings MUST be documented and their outcomes recorded in the audit trail.

---

## 5. Report Format Requirements

Monthly governance reports MUST be:

- Produced in a structured, consistent format (not freeform narrative)
- Machine-readable where metrics are concerned (CSV or JSON summary alongside human-readable presentation)
- Retained for a minimum of 5 years as governance evidence artefacts
- Accessible to external auditors during the retention period

---

## 6. Conformance Requirements

| ID | Requirement |
|---|---|
| CR-837-01 | A monthly governance report MUST be delivered to all committee members by the 10th calendar day of each month. |
| CR-837-02 | All seven mandatory report sections MUST be present. |
| CR-837-03 | Each escalation trigger in section 4 MUST convene an emergency committee meeting within the specified timeframe. |
| CR-837-04 | Monthly governance reports MUST be retained for a minimum of 5 years. |

---

## 7. Security Considerations

Governance reports contain operational intelligence about the deployment's security posture, known weaknesses, and incident history. Reports MUST be classified as confidential. Distribution MUST be restricted to governance committee members, auditors, and named executive recipients.

---

## 8. Operational Considerations

Producing a consistent, complete monthly report requires that the underlying data systems (ethics audit trail, cost monitoring, override logging, AI observability) are operating correctly. Report production failures caused by data system outages MUST be noted in the report itself and the data gap described. A report that omits a mandatory section without explanation is non-compliant regardless of the cause.
