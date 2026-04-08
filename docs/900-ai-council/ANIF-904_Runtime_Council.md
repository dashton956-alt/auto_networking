# ANIF-904: Runtime Council

| Field        | Value                                              |
|--------------|----------------------------------------------------|
| Doc ID       | ANIF-904                                           |
| Series       | AI Council                                         |
| Version      | 0.1.0                                              |
| Status       | Draft                                              |
| Authors      | ANIF Working Group                                 |
| Reviewers    | —                                                  |
| Approved by  | —                                                  |
| Created      | 2026-04-08                                         |
| Last updated | 2026-04-08                                         |
| Replaces     | N/A                                                |
| Related docs | ANIF-301, ANIF-819, ANIF-900, ANIF-901, ANIF-902, ANIF-906 |

---

## Abstract

This document defines the Runtime Council: its trigger conditions, time limits, decision types, and default behaviour when no decision is reached within the deliberation window. The Runtime Council convenes during live execution when the governance gate routes an intent to `council_review` mode. Triggers include intents with harm_severity_score ≥ 80, actions affecting five-nines availability domains, actions with no precedent in episodic memory, and Severity 1 ethics signals during active intent processing. Hard time limits apply per deliberation model. If no decision is reached within the time limit, the intent MUST be halted — the default is always halt, never proceed.

---

## 1. Introduction

### 1.1 Purpose

The governance gate handles the majority of intents through automated routing. A small proportion require live human deliberation because their characteristics place them beyond the parameters of automated governance. The Runtime Council provides that deliberation under real operational time pressure.

### 1.2 Scope

Runtime Council trigger conditions, convening requirements, time limits, decision types, and default-to-halt behaviour.

### 1.3 Out of Scope

Council composition and quorum requirements (see ANIF-901), mode selection logic (see ANIF-902), Build-Time Council procedures (see ANIF-903), Review Council procedures (see ANIF-905), deliberation time limits by model (see ANIF-906).

### 1.4 Intended Audience

- Governance gate platform engineers implementing `council_review` routing
- Council seat holders who may be called into runtime session
- NOC managers understanding when automated operation is suspended
- Conformance assessors verifying Runtime Council capability

---

## 2. Normative References

| Reference | Title |
|---|---|
| ANIF-301 | Policy Engine and Governance Gate |
| ANIF-402 | Human-in-the-Loop Decision Framework |
| ANIF-715 | Ethics Incident Response Policy |
| ANIF-819 | Disaster Recovery and Resilience |
| ANIF-841 | AI Threat Model |
| ANIF-847 | AI Security Incident Response |
| ANIF-900 | AI Council Overview |
| ANIF-901 | AI Council Composition and Roles |
| ANIF-902 | Council Mode Selector |
| ANIF-906 | Council Deliberation Standards |
| ANIF-907 | Council Audit and Accountability |
| RFC 2119 | Key words for use in RFCs to Indicate Requirement Levels |

---

## 3. Trigger Conditions

The governance gate MUST route an intent to `council_review` mode under any of the following conditions:

| Trigger | Threshold | Rationale |
|---|---|---|
| High harm severity | `harm_severity_score ≥ 80` | Actions at this severity level exceed automated governance gate capacity |
| Five-nines domain | Intent affects infrastructure with ≥ 99.999% availability SLA | Availability impact requires human deliberation |
| No episodic precedent | No matching entry in episodic memory for this intent type and context combination | Novel situations cannot be safely handled by precedent-based automation |
| Severity 1 ethics signal | A Severity 1 ethics event (ANIF-715) is active on the processing agent | Ethics signal present during active processing requires council oversight |
| Multi-tier impact | Intent simultaneously affects three or more network tiers | Scope exceeds single-tier governance gate parameters |

---

## 4. Convening Requirements

When the governance gate triggers `council_review`, the following actions MUST occur within 5 minutes:

1. Intent processing MUST be paused. The intent MUST NOT be executed while awaiting council decision.
2. All council seat holders MUST be notified via the designated council alert channel.
3. The Mode Selector (ANIF-902) MUST evaluate the intent and select the deliberation model.
4. The mode selection record MUST be written to the council record before seat holders are notified of the selected model.
5. The following information MUST be presented to seat holders in the council session: intent description, triggering condition(s), Mode Selector evaluation, risk score, ethics flag status, and any active security or ethics incidents on the submitting agent.

---

## 5. Time Limits

Runtime Council deliberation MUST complete within the time limits defined in ANIF-906 for the selected deliberation model. Time limits run from the moment the council session is declared open — not from when all seat holders have joined.

| Deliberation Model | Time Limit |
|---|---|
| Majority | 15 minutes |
| Weighted | 15 minutes |
| Consensus | 30 minutes |
| Adversarial | 45 minutes |

These limits are absolute. Extensions are not permitted. If the time limit expires before a decision is reached, the default-to-halt rule applies.

---

## 6. Decision Types

| Decision | Definition | Effect |
|---|---|---|
| Approved | Council decides the intent may proceed | Intent resumes processing through the pipeline |
| Blocked | Council decides the intent MUST NOT proceed | Intent is cancelled; outcome recorded as `CANCELLED_COUNCIL`; submitter notified with blocking rationale |
| Deferred | Council requires additional information or human pre-condition | Intent is held in `QUEUED` state pending the specified pre-condition; a maximum hold time MUST be stated |
| Escalated | Decision exceeds council authority; escalated to governance committee | Intent is halted; governance committee notified within 30 minutes |

### 6.1 Approval Conditions

A council approval MAY include conditions on execution — for example, requiring human observation throughout execution, or limiting the action to a specific subset of the originally requested scope. Conditions MUST be enforceable by the pipeline and MUST be recorded in the council record.

---

## 7. Default-to-Halt Rule

If no decision is reached within the applicable time limit, the intent MUST be halted. The system MUST NOT default to proceeding with an intent when no council decision has been reached. The halted intent is recorded with outcome `HALTED_COUNCIL_TIMEOUT`. The halt MUST be notified to the governance committee within 1 hour. A timeout pattern — three or more council timeouts in 30 days — MUST be reported to the governance committee as a structural governance issue.

---

## 8. Relationship to Manual Operation

A Runtime Council session does not activate full manual operation (ANIF-819 Level 4). The ANIF-819 degradation level remains unchanged during a Runtime Council session; only the specific intent under review is paused. If a Level 3 or Level 4 security incident is declared (ANIF-847), manual operation supersedes Runtime Council governance and the Runtime Council is dissolved. The security incident response takes precedence.

---

## 9. Conformance Requirements

| ID | Requirement |
|---|---|
| CR-904-01 | Intent processing MUST be paused within 5 minutes of a `council_review` governance gate trigger. |
| CR-904-02 | The Mode Selector MUST complete evaluation before the council session opens. |
| CR-904-03 | Runtime Council deliberation MUST complete within the time limits defined in ANIF-906. |
| CR-904-04 | If no decision is reached within the time limit, the intent MUST be halted. |
| CR-904-05 | A council timeout MUST NOT result in the intent proceeding. |
| CR-904-06 | Three or more council timeouts in 30 days MUST be reported to the governance committee. |

---

## 10. Security Considerations

The Runtime Council's halt-on-timeout default is itself a denial-of-service vector. An attacker who can reliably trigger `council_review` routing and prevent quorum — for example, by compromising seat holder availability — can halt any intent they choose. Runtime Council trigger thresholds MUST be protected from manipulation (see ANIF-902 security considerations). Unusually high rates of `council_review` triggers MUST be investigated as a potential manipulation attempt.

---

## 11. Operational Considerations

The Runtime Council imposes real-time availability requirements on seat holders that the Build-Time Council does not. Organisations MUST maintain on-call arrangements for all seven seats and all seven deputies. Council alerts MUST reach seat holders immediately — a 30-minute delay in receiving an alert in a 15-minute deliberation window is a structural failure. Council alert channel delivery MUST be tested monthly.
