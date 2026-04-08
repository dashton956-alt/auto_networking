# ANIF-819: Disaster Recovery and Resilience

| Field        | Value                                              |
|--------------|----------------------------------------------------|
| Doc ID       | ANIF-819                                           |
| Series       | AI Agent Architecture                              |
| Version      | 0.1.0                                              |
| Status       | Draft                                              |
| Authors      | ANIF Working Group                                 |
| Reviewers    | —                                                  |
| Approved by  | —                                                  |
| Created      | 2026-04-08                                         |
| Last updated | 2026-04-08                                         |
| Replaces     | N/A                                                |
| Related docs | ANIF-800, ANIF-818, ANIF-405, ANIF-107             |

---

## Abstract

This document defines the five degradation levels that govern ANIF operations under failure conditions, from full AI operation to complete manual operation. Every degradation level increases human oversight — no degradation level reduces it. The full operational state of the system MUST be reconstructable from the audit log alone, ensuring that manual operation is always possible from a known baseline. Quarterly automated disaster recovery drills simulating Level 2 (deterministic only) MUST be conducted. Annual full manual operation drills (Level 4) MUST be conducted and their results reported to the governance committee.

---

## 1. Introduction

### 1.1 Purpose

AI-autonomous systems introduce a new failure mode: the AI itself may fail. An ANIF deployment that cannot operate when agents are offline or degraded is not safe for production infrastructure. This document specifies the normative degradation model that ensures every level of AI failure has a defined human-backed fallback, and that the transition between degradation levels is governed, tested, and audited.

### 1.2 Scope

This document covers:

- Five operational degradation levels and their definitions
- The transition triggers and requirements for each level change
- State reconstruction from audit log
- DR test requirements: quarterly and annual drills
- Drill result reporting obligations

### 1.3 Out of Scope

This document does not cover:

- Agent lifecycle state transitions (see ANIF-803)
- Agent scaling during degraded operation (see ANIF-818)
- Incident and outage modelling (see ANIF-405)
- Audit trail requirements (see ANIF-107)

### 1.4 Intended Audience

- Platform engineers designing resilient agent deployments
- NOC managers responsible for degraded operation procedures
- Governance officers overseeing DR programme
- Conformance assessors evaluating resilience claims

---

## 2. Normative References

| Reference | Title |
|---|---|
| ANIF-107 | Audit Trail Requirements |
| ANIF-405 | Incident and Outage Modelling |
| ANIF-724 | Ethics Audit Trail Requirements |
| ANIF-803 | Agent Lifecycle Management |
| ANIF-818 | Agent Framework Scaling |
| RFC 2119 | Key words for use in RFCs to Indicate Requirement Levels |

---

## 3. Terms and Definitions

| Term | Definition |
|---|---|
| Degradation level | A defined operational state reflecting the availability and capability of the AI agent framework |
| State reconstruction | The process of deriving the full current operational state from audit log records alone |
| DR drill | A scheduled exercise testing the ability to operate at a specified degradation level |
| Deterministic shadow | A rule-based component that can produce outputs without LLM invocation, as defined in ANIF-807 |
| Manual operation | Network operation performed entirely by human operators without any AI agent assistance |

---

## 4. Degradation Levels

### 4.1 Level Definitions

| Level | Name | Description |
|---|---|---|
| Level 0 | Full AI Operation | All agents active. Full autonomous pipeline operation within governance bounds. Normal operating state. |
| Level 1 | Degraded | One or more agent types are unavailable. Remaining agents compensate. Intent throughput may be reduced. Human oversight remains unchanged. |
| Level 2 | Deterministic Only | All LLM components are offline. Deterministic shadows handle all processing. LLM-dependent capabilities are suspended. All recommendations reviewed by humans before action. |
| Level 3 | Human-Assisted Pipeline | Automated agents advise but humans approve all actions without exception. No autonomous execution. The pipeline produces recommendations; humans make all decisions. |
| Level 4 | Full Manual Operation | All AI agents offline. NOC staff operate directly from the audit log and canonical state. No automation. |

### 4.2 Invariant: Oversight Only Increases

Transitioning to a higher degradation level MUST increase human oversight. No degradation-level transition is permitted that reduces human oversight compared to the level immediately below it. This invariant applies across all five levels.

---

## 5. Level Transition Requirements

### 5.1 Level 0 → Level 1

**Trigger:** One or more agent types enter SUSPENDED or FAILED lifecycle state.

**Requirements:**
- The Agent Pool Controller MUST detect the unavailability within 30 seconds.
- The system MUST log the degradation event with: affected agent types, time of detection, intent backlog at time of degradation.
- Remaining agents MUST continue operating. The pipeline MUST NOT halt unless the unavailable agents are on the critical path with no substitute.
- Human operators MUST be notified within 60 seconds.

### 5.2 Level 1 → Level 2

**Trigger:** All LLM agents are unavailable, or the LLM provider is unreachable.

**Requirements:**
- All deterministic shadows MUST be activated automatically within 60 seconds.
- LLM-specific capabilities that have no deterministic equivalent MUST be suspended and the affected intent types queued for human review.
- The system MUST log transition to Level 2 with: LLM unavailability reason, capabilities suspended, queue depth at transition time.
- Human operators MUST be notified immediately.

### 5.3 Level 2 → Level 3

**Trigger:** Deterministic shadows are also unavailable or returning error rates above 20%.

**Requirements:**
- The pipeline MUST switch to advisory-only mode: it produces recommendations but MUST NOT execute any action autonomously.
- All pending intents in EXECUTING state MUST be immediately halted and rolled back.
- All recommendations MUST enter PENDING_APPROVAL state regardless of risk score.
- Human operators MUST be notified and the approval queue MUST be prioritised for human attention.

### 5.4 Level 3 → Level 4

**Trigger:** The advisory pipeline itself is unavailable, or a human operator explicitly declares Level 4.

**Requirements:**
- All agent processes MUST be gracefully terminated.
- The audit log and canonical state MUST be made available to NOC staff via a read-only interface that is independent of the agent framework.
- A Level 4 declaration MUST be approved by a senior operations manager and logged with: authorising operator identity, reason, timestamp.
- The NOC team MUST be briefed on manual operation procedures within 15 minutes of Level 4 declaration.

---

## 6. State Reconstruction

### 6.1 Requirement

The full operational state of the ANIF deployment MUST be reconstructable from the audit log alone. This is not a recovery convenience — it is the architectural guarantee that enables Level 4 manual operation. If state cannot be reconstructed from the audit log, Level 4 operation is not possible.

### 6.2 Reconstructable State Elements

The following elements MUST be derivable from the audit log:

- All intents and their current lifecycle states
- All agent decisions and their inputs
- All network actions taken and their outcomes
- All policy evaluations and their results
- All human overrides and approvals
- The current canonical network state as of the last audit record

### 6.3 Reconstruction Test

The state reconstruction capability MUST be tested as part of every DR drill at Level 2 or above. The test MUST verify that a complete state picture can be produced from the audit log without accessing any live agent data.

---

## 7. DR Drill Requirements

### 7.1 Quarterly Level 2 Drill

A Level 2 drill MUST be conducted quarterly. The drill MUST:

1. Take all LLM components offline in a controlled manner.
2. Verify that deterministic shadows activate within the required 60-second window.
3. Process a representative sample of intents through the deterministic-only pipeline.
4. Verify state reconstruction from the audit log.
5. Measure and record the time to transition from Level 0 to Level 2.
6. Verify human notification latency meets the 60-second requirement.

### 7.2 Annual Level 4 Drill

A full manual operation drill MUST be conducted annually. The drill MUST:

1. Take all agent processes offline.
2. Require the NOC team to operate solely from the audit log and canonical state for a minimum 2-hour period.
3. Process a defined set of test scenarios manually.
4. Measure time to complete each scenario.
5. Identify manual operation gaps: scenarios where the NOC team could not complete the task from available data.

### 7.3 Drill Result Reporting

All DR drill results MUST be reported to the governance committee within 5 business days of the drill. The report MUST include:

- Drill type and date
- Scenarios tested and outcomes
- Any transition latency violations
- Manual operation gaps identified (Level 4 drills)
- Remediation actions and owners

Governance committee review of drill results is mandatory. Unreviewed drill results MUST be escalated to the AI Council (ANIF-901).

---

## 8. Recovery Requirements

### 8.1 Level Recovery

Recovery from a degradation level MUST be a deliberate, governed action. Automatic recovery from Level 2 or above back to Level 0 is not permitted — a human operator MUST explicitly authorise recovery. Recovery authorisation MUST be logged.

### 8.2 Pre-Recovery Checklist

Before authorising recovery to Level 0 from any degraded level, the authorising operator MUST verify:

- The root cause of degradation has been identified and resolved
- All intents that were processed during degradation have been reviewed for correctness
- No intents that required LLM reasoning were incorrectly processed by deterministic shadows
- The audit log is complete and shows no gaps during the degradation period

---

## 9. Conformance Requirements

| ID | Requirement |
|---|---|
| CR-819-01 | Transitioning to a higher degradation level MUST increase human oversight. No transition MUST reduce oversight. |
| CR-819-02 | The Agent Pool Controller MUST detect agent unavailability within 30 seconds. |
| CR-819-03 | Deterministic shadows MUST activate within 60 seconds of LLM unavailability. |
| CR-819-04 | Intents in EXECUTING state at Level 2 transition MUST be halted and rolled back. |
| CR-819-05 | Level 4 declaration MUST be approved by a senior operations manager and logged. |
| CR-819-06 | Full operational state MUST be reconstructable from the audit log alone. |
| CR-819-07 | Quarterly Level 2 drills MUST be conducted. |
| CR-819-08 | Annual Level 4 drills of at least 2 hours duration MUST be conducted. |
| CR-819-09 | DR drill results MUST be reported to the governance committee within 5 business days. |
| CR-819-10 | Recovery from Level 2 or above to Level 0 MUST require explicit human authorisation. |

---

## 10. Security Considerations

Degradation levels are a potential target for adversarial manipulation. An attacker who can force a Level 3 or Level 4 degradation removes autonomous governance controls and places full operational burden on human operators who may be less equipped to identify malicious intent submissions. DR resilience is therefore a security property as much as an operational one. Level 4 declaration authority MUST be limited to named senior operators with verified identities.

---

## 11. Operational Considerations

DR drill scheduling MUST account for operational load. Conducting a Level 4 drill during a peak change window increases risk. Drills SHOULD be conducted during planned low-activity periods with additional NOC staffing available. DR drill findings SHOULD be treated as improvement backlog items rather than audit failures — the purpose of drills is to identify gaps, not to demonstrate perfection.

## Appendix A: Degradation Level Quick Reference

| Level | LLM Available | Deterministic Available | Autonomous Execution | Human Oversight Level |
|---|---|---|---|---|
| 0 | Yes | Yes | Yes (within policy) | Governance bounds |
| 1 | Partial | Yes | Yes (reduced capacity) | Governance bounds |
| 2 | No | Yes | No | All recommendations reviewed |
| 3 | No | No (advisory only) | No | All actions approved by human |
| 4 | No | No | No | Full manual — no AI assistance |
