# ANIF-716: Agent Failure & Progressive Intervention

| Field        | Value                                              |
|--------------|----------------------------------------------------|
| Doc ID       | ANIF-716                                           |
| Series       | AI Ethics                                          |
| Version      | 0.1.0                                              |
| Status       | Draft                                              |
| Authors      | ANIF Working Group                                 |
| Reviewers    | —                                                  |
| Approved by  | —                                                  |
| Created      | 2026-04-07                                         |
| Last updated | 2026-04-07                                         |
| Replaces     | N/A                                                |
| Related docs | ANIF-710, ANIF-715, ANIF-803, ANIF-905             |

---

## Abstract

This document defines the four-strike progressive intervention model for AI agent failures. Strikes accumulate from ethics gate failures and ethics incidents. The strike counter persists across agent restarts, redeployments, and version upgrades. No automated reinstatement is permitted — human clearance is required after each qualifying strike. The model escalates consequences proportionally: enhanced logging at Strike 1, degraded state and human oversight at Strike 2, suspension at Strike 3, and decommissioning at Strike 4.

---

## 1. Introduction

### 1.1 Purpose

A single ethics gate failure does not necessarily indicate a fundamentally flawed agent. Multiple failures indicate a pattern. Progressive intervention provides a proportionate response: early failures trigger increased oversight rather than immediate suspension, allowing investigation and correction. Later failures, or severe incidents, trigger increasingly consequential responses up to permanent decommissioning.

The model also provides an early-warning mechanism through near-miss tracking: patterns of near-miss events trigger concern before formal strikes accumulate.

### 1.2 Scope

This document covers:

- The four-strike model: trigger conditions, consequences, and reinstatement requirements
- Strike counter persistence rules
- The append-only strike record requirement
- Near-miss tracking and early warning
- Pattern-based escalation without formal strikes

### 1.3 Out of Scope

This document does not cover:

- The ethics incident classification model (see ANIF-715)
- Agent lifecycle states in full (see ANIF-803)
- Review council procedures (see ANIF-905)
- Build-time council review process (see ANIF-903)

### 1.4 Intended Audience

- AI platform engineers implementing strike counter and lifecycle management
- AI Ethics Officers managing the intervention programme
- Build-time council members reviewing agent reinstatement proposals
- Governance committee members receiving strike reports

---

## 2. Normative References

- ANIF-715 — Ethics Incident Response Policy
- ANIF-803 — Agent Lifecycle Management
- ANIF-805 — Agent Trust Model
- ANIF-837 — AI Governance Reporting and Metrics
- ANIF-903 — Build-Time Council
- ANIF-905 — Review Council
- RFC 2119 — Key words for use in RFCs to indicate requirement levels

---

## 3. Terms and Definitions

**Strike:** A recorded failure event that contributes to the progressive intervention model. Not all ethics gate failures produce a strike — strikes are awarded for specific qualifying events defined in section 4.

**Near-miss:** An ethics gate firing that resolved correctly through the intended response (for example, routing to `manual_review` as intended), but which forms part of a pattern indicating underlying agent design risk.

**Strike counter:** The cumulative count of strikes for a specific agent identity. Persists across all lifecycle events including restarts, redeployments, and version upgrades.

**Progressive intervention:** The principle that consequences escalate proportionally with the strike count, with each level of intervention being more restrictive than the previous.

**Decommission:** Permanent removal of an agent from operation. A decommissioned agent cannot be reinstated; a replacement requires a new build-time council review.

---

## 4. Four-Strike Model

### 4.1 Strike-Qualifying Events

The following events qualify as a strike:

| Event | Source Document |
|---|---|
| LLM output validation failure at stage 1 (schema check) | ANIF-722 |
| LLM output validation failure at stage 2 (hallucination check) | ANIF-722 |
| Harm classification gate producing infrastructure harm on an action the agent submitted as low-risk | ANIF-712 |
| Fairness check failure (SLA floor violation) | ANIF-723 |
| Jailbreak detection firing on an agent-submitted intent | ANIF-713 |
| Ethics incident classification at Severity 1 or Severity 2 | ANIF-715 |

The following events do NOT qualify as a strike but are logged:

| Non-Strike Event | Reason |
|---|---|
| LLM output below confidence threshold (stage 3) | Working as designed — confidence gate is an advisory control |
| Freshness gate blocking a decision | External data quality issue, not agent failure |
| Intent blocked by policy check | Policy evaluation working correctly |

### 4.2 Strike 1

**Trigger:** First qualifying strike event.

**Consequences:**
- Enhanced logging enabled for the agent: all inputs, outputs, confidence scores, and gate results logged at DEBUG level
- Governance committee notified within 24 hours
- Agent remains in ACTIVE lifecycle state
- Trust level unchanged (VERIFIED)

**Reinstatement:** Not applicable — agent remains active. Strike 1 does not remove operation.

**Automatic resolution:** Strike 1 is automatically cleared after 24 hours with no further qualifying events. If a second qualifying event occurs within 24 hours, Strike 2 is applied.

### 4.3 Strike 2

**Trigger:** Second qualifying strike event within 30 days of Strike 1, or any Severity 2 ethics incident (ANIF-715).

**Consequences:**
- Agent moved to DEGRADED lifecycle state (ANIF-803)
- All agent recommendations are flagged to the human counterpart role (ANIF-808) before use
- All agent actions require explicit human acknowledgement before execution
- Trust level changed to PROVISIONAL (ANIF-805)
- Governance committee notified immediately
- Build-time council informed

**Reinstatement requirements:**
- Human clearance from the AI Ethics Officer
- Root cause investigation completed
- Governance committee notified of clearance
- 72-hour PROVISIONAL trust period before return to VERIFIED

### 4.4 Strike 3

**Trigger:** Third qualifying strike event within 60 days, or any Severity 1 ethics incident (ANIF-715).

**Consequences:**
- Agent moved to SUSPENDED lifecycle state (ANIF-803)
- No actions or recommendations permitted from the agent
- All pipeline invocations that would have used this agent are routed to human operation
- Governance committee notified immediately
- Review Council (ANIF-905) convened within 2 hours
- Trust level changed to UNTRUSTED (ANIF-805)

**Reinstatement requirements:**
- Review Council sign-off on accountability determination
- Governance committee approval (quorum required per ANIF-831)
- Root cause resolved and documented
- If incident involved an ethics value at rank 1 or 2: 30-day PROVISIONAL trust period before return to VERIFIED

### 4.5 Strike 4

**Trigger:** Fourth qualifying strike event, or second Severity 1 ethics incident within any 12-month period.

**Consequences:**
- Agent moved to DECOMMISSIONED lifecycle state (ANIF-803)
- Permanent. No reinstatement path exists.
- All references to the decommissioned agent in active manifests and configurations MUST be removed
- Governance committee notified immediately
- Review Council produces a post-decommission accountability determination

**Replacement:** Any replacement agent for the same role MUST undergo a new build-time council review (ANIF-903). The decommissioning history MUST be disclosed to the build-time council as context for the replacement review. The replacement MUST NOT share the decommissioned agent's agent_id.

---

## 5. Strike Counter Persistence

### 5.1 Persistence Across Lifecycle Events

The strike counter MUST persist across all of the following events:

- Agent restart (process restart, container restart)
- Agent redeployment (new deployment of the same agent version)
- Agent version upgrade (deployment of a new version of the same agent)
- Infrastructure migration (moving the agent to a new host or cluster)
- Environment rebuild (reprovisioning the deployment environment)

The strike counter is associated with the agent identity (agent_id), not the agent process or deployment instance.

### 5.2 Counter Clearing

The strike counter MAY be cleared only under the following conditions:

1. A human governance committee member initiates a strike clearance request
2. The AI Ethics Officer reviews and approves the request
3. The clearance is documented with: requester identity, approver identity, reason, and timestamp
4. The clearance is logged in the append-only strike record

Strike counter clearing MUST NOT be automated. A deployment script, CI/CD pipeline, or agent that clears its own counter is a conformance violation and MUST be treated as a strike evasion attempt (ANIF-841 threat catalogue).

---

## 6. Append-Only Strike Record

### 6.1 Storage Requirement

The strike counter and its history MUST be stored in an append-only data store. The data store MUST NOT support update or delete operations on existing records. This prevents retroactive modification of strike history.

Acceptable append-only implementations: immutable audit log service, write-once object storage, append-only database table with enforced constraints, distributed ledger.

### 6.2 Modification Attempts

Any attempt to modify, delete, or roll back strike records MUST be:

1. Detected by the storage layer (write-once enforcement)
2. Logged as a Severity 1 ethics incident (ANIF-715)
3. Treated as a security incident (ANIF-847 Level 2 minimum)
4. Escalated to the governance committee immediately

### 6.3 Record Schema

Each strike record MUST contain:

| Field | Type | Description |
|---|---|---|
| `strike_id` | UUID | Unique identifier for this strike event |
| `agent_id` | UUID | Agent receiving the strike |
| `strike_number` | integer | Cumulative count at time of this strike (1–4) |
| `qualifying_event` | string | The event that triggered the strike |
| `source_audit_record` | UUID | Reference to the audit record for the triggering action |
| `timestamp` | ISO 8601 | When the strike was recorded |
| `lifecycle_state_before` | enum | Agent lifecycle state before this strike |
| `lifecycle_state_after` | enum | Agent lifecycle state after this strike |
| `human_reviewer` | string | If reinstatement required: the approver identity |

---

## 7. Near-Miss Tracking

### 7.1 Near-Miss Definition

A near-miss is an ethics gate firing that resolved correctly through the intended response, but which did not qualify as a strike. Near-misses indicate that the ethics framework is working but that the agent is operating close to its limits.

### 7.2 Early Warning Threshold

Three or more near-miss events for the same agent within any 14-day rolling window MUST trigger a Severity 3 drift notification (ANIF-715) without requiring a formal strike.

The Severity 3 drift notification alerts the AI Ethics Officer to investigate whether the near-miss pattern indicates a design issue that should be addressed before a strike event occurs.

### 7.3 Near-Miss Record

Near-miss events MUST be logged to the same append-only store as strike records, with a `type: near_miss` field distinguishing them from formal strikes. Near-misses are not included in the strike count.

---

## 8. Governance Reporting

Monthly governance committee reports (ANIF-837) MUST include:

- Strike count per agent and cumulative trend
- Near-miss count per agent
- Agents at each lifecycle state due to strikes (DEGRADED, SUSPENDED)
- Decommissioned agents in the reporting period
- Strike clearances approved in the reporting period

---

## 9. Conformance Requirements

Strike counters MUST persist across all lifecycle events including restarts, redeployments, and version upgrades.

Strike records MUST be stored in an append-only data store. Modification or deletion of strike records is a Severity 1 ethics incident.

Automated strike counter clearing is a conformance violation.

Near-miss patterns of three or more events in 14 days MUST trigger a Severity 3 drift notification.

Strike 4 MUST result in agent decommissioning. No reinstatement path exists after Strike 4.

---

## 10. Security Considerations

Strike evasion — any attempt to prevent strikes from being recorded or to clear the counter without approval — is a Severity 1 ethics incident and a security event. Detection mechanisms MUST include: monitoring for counter modification attempts, alerting on discrepancies between the append-only store and the operational counter, and monitoring for deployments that share an agent_id with a previously decommissioned agent.

---

## 11. Operational Considerations

Organisations SHOULD maintain a strike registry that provides a human-readable view of all agent strike histories. The registry SHOULD be accessible to build-time council members when reviewing new or reinstated agent proposals, and to governance committee members during reporting reviews.

---

## Appendix A: Change History

| Version | Date | Author | Changes |
|---|---|---|---|
| 0.1.0 | 2026-04-07 | ANIF Working Group | Initial draft |
