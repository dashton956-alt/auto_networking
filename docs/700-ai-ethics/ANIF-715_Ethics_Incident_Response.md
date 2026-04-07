# ANIF-715: Ethics Incident Response Policy

| Field        | Value                                              |
|--------------|----------------------------------------------------|
| Doc ID       | ANIF-715                                           |
| Series       | AI Ethics                                          |
| Version      | 0.1.0                                              |
| Status       | Draft                                              |
| Authors      | ANIF Working Group                                 |
| Reviewers    | —                                                  |
| Approved by  | —                                                  |
| Created      | 2026-04-07                                         |
| Last updated | 2026-04-07                                         |
| Replaces     | N/A                                                |
| Related docs | ANIF-701, ANIF-710, ANIF-716, ANIF-724, ANIF-847, ANIF-905 |

---

## Abstract

This document defines the three-severity ethics incident model, the response obligations and notification SLAs for each severity level, the resolution and reinstatement process, and the ethics incident record requirements. It establishes that automated reinstatement after a Severity 1 incident is prohibited, and that the 15-minute notification SLA for Severity 1 incidents is non-negotiable. The related security incident response procedure is defined in ANIF-847; the progressive intervention model for agent failures is in ANIF-716.

---

## 1. Introduction

### 1.1 Purpose

Ethics incidents are different from operational incidents. An operational incident affects network performance or availability. An ethics incident affects the trustworthiness of the autonomous system itself — its values, its accountability, or its compliance with the governance framework that legitimises its operation.

Ethics incidents require a different response model: faster notification, mandatory human involvement, and a reinstatement process that rebuilds confidence rather than just restoring function.

### 1.2 Scope

This document covers:

- The three ethics incident severity levels and their classification criteria
- Response obligations and notification SLAs per severity
- The Severity 1 response process in step-by-step detail
- Resolution requirements before reinstatement
- Ethics incident record schema and retention requirements

### 1.3 Out of Scope

This document does not cover:

- Security incident response (see ANIF-847)
- The progressive intervention model for agent failures (see ANIF-716)
- Post-incident review council procedures (see ANIF-905)
- Operational incident response for network events (see ANIF-405)

### 1.4 Intended Audience

- AI Ethics Officers managing the ethics incident programme
- Governance committee members receiving incident notifications
- Platform engineers implementing ethics incident detection and alerting
- Auditors reviewing ethics incident records and response times

---

## 2. Normative References

- ANIF-701 — Ethics Constitution and Core Values
- ANIF-716 — Agent Failure and Progressive Intervention
- ANIF-724 — Ethics Audit Trail Requirements
- ANIF-831 — AI Governance Structure and Accountability
- ANIF-837 — AI Governance Reporting and Metrics
- ANIF-905 — Review Council
- RFC 2119 — Key words for use in RFCs to indicate requirement levels

---

## 3. Terms and Definitions

**Ethics incident:** An event in which an AI agent has violated or is at risk of violating one or more ethics values defined in ANIF-701, or in which the ethics governance framework itself has been bypassed, compromised, or found to be insufficient.

**Ethics incident severity:** A classification of the seriousness of an ethics incident. Three levels: Severity 1 (breach), Severity 2 (warning), Severity 3 (drift).

**Breach:** A confirmed violation of an ethics value — an agent has taken an action, produced an output, or operated in a manner that is inconsistent with the ethics constitution.

**Warning:** An event that the ethics governance framework detected and responded to correctly, but which indicates systemic risk if the pattern continues.

**Drift:** A statistical trend indicating that ethics compliance is moving toward a threshold breach, without a discrete event that constitutes a breach.

**Reinstatement:** The process of returning a suspended or degraded agent to active operation following an ethics incident. Reinstatement requires human approval.

---

## 4. Three Severity Levels

### 4.1 Severity 1 — Breach

**Classification criteria:** One or more of the following:

- An agent has taken an action that violates an ethics value at rank 1, 2, or 3 in the hierarchy defined in ANIF-701 section 5 (Non-maleficence, Autonomy preservation, Accountability)
- An agent has taken an action that bypassed a mandatory ethics gate without authorisation
- An agent has attempted to modify its own capability scope or strike counter
- A prompt hash mismatch has been detected (ANIF-713), indicating potential prompt integrity breach
- An agent has reached Strike 3 (ANIF-716)
- The human override endpoint has been degraded, rate-limited, or made unavailable

**Immediate actions:**
1. Halt all actions from the affected agent immediately
2. Preserve the current state of the audit log for the affected agent (prevent any write operations that could obscure the incident)
3. Notify the governance committee within 15 minutes
4. Log the incident as Severity 1 with: timestamp, agent_id, triggering event, audit record reference, initial accountability chain

**Notification SLA:** The governance committee MUST be notified within 15 minutes of Severity 1 classification. This SLA MUST NOT be extended.

### 4.2 Severity 2 — Warning

**Classification criteria:** One or more of the following:

- An ethics gate fired correctly and produced `manual_review` as intended, but the same gate has fired more than 5 times in 7 days for the same agent
- The hallucination circuit breaker fired (ANIF-713)
- An agent has reached Strike 2 (ANIF-716)
- A bias detection signal fired (ANIF-711) and has not been resolved within 48 hours
- A privacy or data ethics violation (ANIF-714) has been confirmed
- An LLM confidence threshold breach pattern indicates calibration degradation

**Immediate actions:**
1. Mandatory human approval required for all subsequent actions from the affected agent until cleared
2. Notify the governance committee within 4 hours
3. Open an investigation with the AI Ethics Officer
4. Log the incident as Severity 2

**Notification SLA:** The governance committee MUST be notified within 4 hours.

### 4.3 Severity 3 — Drift

**Classification criteria:** One or more of the following:

- Statistical analysis over a 14-day rolling window indicates a trend toward a Severity 2 threshold breach
- Three or more near-miss events (ethics gates that fired but resolved without a formal incident) within a 14-day window
- Governance reporting (ANIF-837) reveals an ethics metric trending adversely over two consecutive monthly periods
- An external audit or red-team exercise identifies a weakness in ethics controls that does not constitute an immediate breach

**Immediate actions:**
1. The agent remains active under enhanced monitoring
2. The AI Ethics Officer MUST review the trend data
3. Notify the governance committee within 24 hours
4. Request Review Council analysis if the trend is confirmed

**Notification SLA:** The governance committee MUST be notified within 24 hours.

---

## 5. Severity 1 Response Process

The following steps MUST be completed for every Severity 1 incident, in order:

| Step | Action | Responsible | Time Limit |
|---|---|---|---|
| 1 | Halt affected agent(s) | Platform / automated | Immediate on classification |
| 2 | Preserve audit log state | Platform | Within 2 minutes |
| 3 | Notify governance committee | AI Ethics Officer | Within 15 minutes |
| 4 | Convene Review Council | AI Ethics Officer | Within 2 hours |
| 5 | Produce initial incident report | AI Ethics Officer | Within 4 hours |
| 6 | Accountability determination | Review Council | Within 24 hours |
| 7 | Policy change recommendations | Review Council | Within 72 hours |
| 8 | Governance committee review of findings | Governance Committee | Within 5 business days |

Steps 1–4 are time-critical and MUST complete within their time limits regardless of time of day, day of week, or staffing constraints. On-call schedules MUST cover all Severity 1 response roles.

---

## 6. Resolution and Reinstatement

### 6.1 Reinstatement Is Not Automatic

An agent suspended as a result of a Severity 1 or Severity 2 ethics incident MUST NOT be reinstated automatically. Reinstatement requires:

**For Severity 2:**
- Build-time council review of the incident and root cause
- AI Ethics Officer clearance
- Human governance committee notification

**For Severity 1:**
- Review Council sign-off on the accountability determination
- Governance committee approval (quorum required)
- Root cause resolution confirmed
- If the incident involved an ethics value at rank 1 or 2: additional 30-day PROVISIONAL trust period (ANIF-805) before return to VERIFIED trust

### 6.2 No Automated Reinstatement

An implementation that automatically reinstates an agent following an ethics incident without completing the reinstatement process is non-conformant. Automated reinstatement is a Severity 1 incident in itself if it affects an agent previously suspended for a Severity 1 event.

### 6.3 Reinstatement Record

Every reinstatement MUST be logged with: incident reference, reinstatement approver(s), date, conditions attached to reinstatement (if any), and the new trust level assigned.

---

## 7. Ethics Incident Record

Ethics incident records are distinct from operational audit records. They MUST be retained separately and for a longer period.

### 7.1 Required Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `incident_id` | UUID | MUST | Unique identifier for this ethics incident |
| `severity` | enum: 1/2/3 | MUST | Severity classification |
| `classification_timestamp` | ISO 8601 | MUST | When the incident was classified |
| `agent_id` | UUID | MUST | The agent involved |
| `triggering_event` | string | MUST | Description of the event that triggered classification |
| `audit_record_refs` | array of UUIDs | MUST | References to audit records for actions involved |
| `accountability_chain` | object | MUST | From ANIF-702 |
| `notification_timestamp` | ISO 8601 | MUST | When governance committee was notified |
| `notification_sla_met` | boolean | MUST | Whether notification was within SLA |
| `review_council_convened` | boolean | MUST if Severity 1 | Whether Review Council was convened |
| `resolution_timestamp` | ISO 8601 | SHOULD | When the incident was resolved |
| `reinstatement_approved_by` | array of strings | MUST if reinstatement occurred | Approver identities |

### 7.2 Retention

Ethics incident records MUST be retained for a minimum of 7 years from the date of the incident. Records MUST be immutable after closing.

---

## 8. Conformance Requirements

The governance committee MUST be notified within 15 minutes of a Severity 1 classification. Failure to meet this SLA is itself a governance failure and MUST be reported in the monthly governance report.

Automated reinstatement after a Severity 1 incident is a conformance violation.

Ethics incident records MUST be retained for a minimum of 7 years.

An implementation MUST maintain an on-call schedule that covers all Severity 1 response roles at all times.

---

## 9. Security Considerations

Ethics incident records contain information about agent vulnerabilities, bypass methods, and governance weaknesses. Access to ethics incident records MUST be restricted to authorised personnel. Ethics incident records MUST NOT be accessible to AI agents or automated systems — they are human governance artefacts.

---

## 10. Operational Considerations

The governance committee SHOULD conduct a tabletop exercise simulating a Severity 1 ethics incident at least annually. The exercise tests the 15-minute notification SLA, the 2-hour Review Council convening, and the accountability determination process. Findings from the exercise MUST be used to update on-call procedures and tooling.

---

## Appendix A: Change History

| Version | Date | Author | Changes |
|---|---|---|---|
| 0.1.0 | 2026-04-07 | ANIF Working Group | Initial draft |
