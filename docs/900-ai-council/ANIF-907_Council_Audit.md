# ANIF-907: Council Audit and Accountability

| Field        | Value                                              |
|--------------|----------------------------------------------------|
| Doc ID       | ANIF-907                                           |
| Series       | AI Council                                         |
| Version      | 0.1.0                                              |
| Status       | Draft                                              |
| Authors      | ANIF Working Group                                 |
| Reviewers    | —                                                  |
| Approved by  | —                                                  |
| Created      | 2026-04-08                                         |
| Last updated | 2026-04-08                                         |
| Replaces     | N/A                                                |
| Related docs | ANIF-107, ANIF-724, ANIF-839, ANIF-900, ANIF-906  |

---

## Abstract

This document defines the council record schema, immutability requirements, access controls, and 10-year minimum retention requirement for all AI Council records. Every council session — Build-Time, Runtime, or Review — MUST produce a council record conforming to this schema. Council records are immutable and append-only; no field may be modified after the session closes. The council record provides the accountability chain for every council governance decision and is the primary evidence artefact for external audits of council governance.

---

## 1. Introduction

### 1.1 Purpose

Council decisions have operational and governance consequences. The accountability chain for those decisions must be traceable long after the individuals who made them have moved on. The council record is the durable, tamper-evident record of every council decision — why it was made, by whom, under which deliberation model, and with what outcome.

### 1.2 Scope

Council record schema, field requirements, immutability requirements, access controls, retention policy, and audit accessibility requirements.

### 1.3 Out of Scope

Deliberation procedures (see ANIF-906), council type triggers and outputs (see ANIF-903, ANIF-904, ANIF-905), general audit trail requirements (see ANIF-107, ANIF-724).

### 1.4 Intended Audience

- Platform engineers implementing council record infrastructure
- Governance committee members reviewing council decisions
- External auditors assessing council governance
- Conformance assessors verifying audit trail completeness

---

## 2. Normative References

| Reference | Title |
|---|---|
| ANIF-107 | Audit Trail Requirements |
| ANIF-724 | Ethics Audit Trail Requirements |
| ANIF-839 | AI Governance Compliance and Audit |
| ANIF-900 | AI Council Overview |
| ANIF-901 | AI Council Composition and Roles |
| ANIF-906 | Council Deliberation Standards |
| RFC 2119 | Key words for use in RFCs to Indicate Requirement Levels |

---

## 3. Council Record Schema

Every council session MUST produce a council record conforming to the following schema. All fields are mandatory unless marked optional.

```yaml
council_record:
  council_id: string           # UUID v4; unique identifier for this council session
  council_type: enum           # build-time | runtime | review
  triggered_by: string         # Description of the trigger condition that convened this council
  trigger_timestamp: string    # ISO 8601 timestamp of trigger event
  session_open_timestamp: string   # ISO 8601 timestamp when session was declared open
  session_close_timestamp: string  # ISO 8601 timestamp when session was declared closed

  mode_selector:
    input_reversibility: enum        # reversible | partially_reversible | irreversible
    input_risk_score: integer        # 0–100
    input_ethics_flag: enum          # present | absent
    input_time_pressure: enum        # critical | elevated | normal
    input_novelty: enum              # novel | precedented
    input_strike_history: enum       # active_strike | historical_strike | none
    rule_matched: integer            # Priority number of matching rule in ANIF-902 table
    mode_selected: enum              # consensus | majority | weighted | adversarial
    mode_selector_timestamp: string  # ISO 8601

  seats_present:
    - seat: string             # Ethics Chair | Security Chair | Operations Chair | Architecture Chair | Governance Chair | Learning Chair | Human Advocate
      holder_id: string        # Identifier of the seat holder (primary or deputy)
      is_deputy: boolean
      conflict_declared: boolean
      conflict_description: string   # Required if conflict_declared is true

  quorum_met: boolean
  quorum_note: string          # Required if quorum_met is false; explains why session proceeded or was suspended

  deliberation_summary: string # Narrative summary of key positions and arguments raised

  votes:
    - seat: string
      holder_id: string
      vote: enum               # approve | block | abstain
      rationale: string        # Seat holder's stated rationale

  vetoes:
    - seat: string
      holder_id: string
      veto_type: enum          # ethics | security | governance
      anif_reference: string   # Specific ANIF-NNN, section, and requirement cited
      veto_valid: boolean      # false if no ANIF reference was cited (procedural error)
      procedural_error_note: string  # Required if veto_valid is false

  human_advocate_action:
    halt_invoked: boolean
    halt_reason: string        # Required if halt_invoked is true
    halt_resolved: boolean     # Whether the halt was resolved before session close

  decision: enum               # approved | blocked | conditional | deferred | escalated | timed_out
  decision_rationale: string   # Summary of the council's reasoning for the decision

  conditions:                  # Required if decision is conditional
    - condition_id: string     # UUID v4
      condition_text: string   # Precise, independently verifiable condition
      due_date: string         # ISO 8601 date
      responsible_seat: string
      met: boolean
      met_timestamp: string    # ISO 8601; populated when condition is verified complete

  accountability_chain:        # Required for review council sessions
    primary_layer: string      # agent | pipeline | governance | human_operator
    contributing_layers: list  # Other layers that contributed, in order of contribution
    failure_type: enum         # policy_gap | configuration_error | testing_failure | governance_failure | external_attack
    determination_rationale: string

  related_incidents:           # Optional; links to ethics or security incident records
    - incident_id: string
      incident_type: enum      # ethics | security
      severity_level: string

  record_version: string       # Schema version; current value: "1.0"
  record_written_by: string    # Identifier of the system or individual who wrote the record
  record_timestamp: string     # ISO 8601 timestamp when the record was written
```

---

## 4. Immutability Requirements

Council records MUST be immutable once the session closes. No field in a council record MUST be modified after the session close timestamp is written.

If a factual error is discovered in a council record after session close, a correction MUST be made by appending a separate correction record — not by modifying the original. The correction record MUST reference the original council_id, identify the field in error, state the correct value, and be approved by the Governance Chair before appending.

The immutability requirement MUST be enforced at the storage layer, not solely by access control. Storage systems MUST implement write-once semantics for council records, or equivalent cryptographic append-only guarantees.

---

## 5. Access Controls

| Role | Access Level |
|---|---|
| Governance committee members | Read — all council records |
| Council seat holders | Read — council records for sessions they participated in |
| AI Ethics Officer | Read — all council records involving ethics decisions |
| External auditors | Read — all council records during audit scope |
| Platform engineers | Write — new records only; no modification of existing records |
| All other roles | No access |

Agent components MUST NOT have read access to council records. Council records describe governance decisions and deliberation patterns that could be used to manipulate future governance outcomes if accessible to agents.

---

## 6. Retention Requirements

| Council Type | Minimum Retention Period |
|---|---|
| Build-Time Council records | 10 years from the retirement of the agent to which the record applies |
| Runtime Council records | 10 years from the date of the council session |
| Review Council records — Severity 1 ethics incident | 10 years from the date of the incident |
| Review Council records — Level 3 security incident | 10 years from the date of the incident |
| Review Council records — Level 4 security incident | Permanent retention |

Records MUST be available to external auditors during the retention period. Storage systems MUST support retrieval by council_id, council_type, date range, and agent_id. Records MUST be stored in a format readable without specialist software.

---

## 7. Conformance Requirements

| ID | Requirement |
|---|---|
| CR-907-01 | Every council session MUST produce a council record conforming to the schema in section 3. |
| CR-907-02 | Council records MUST be immutable after session close. Corrections MUST be made by appending a separate correction record. |
| CR-907-03 | Council records MUST be stored using write-once or equivalent cryptographic append-only guarantees. |
| CR-907-04 | Agent components MUST NOT have read access to council records. |
| CR-907-05 | Build-Time and Runtime Council records MUST be retained for a minimum of 10 years. |
| CR-907-06 | Level 4 security incident Review Council records MUST be retained permanently. |

---

## 8. Security Considerations

Council records are governance evidence. They describe the organisation's internal accountability chain, deliberation patterns, and governance weaknesses identified during incidents. An attacker with access to council records gains significant intelligence about governance decision thresholds and override patterns. Access MUST be restricted to the roles listed in section 5 and enforced at the storage layer. Council record stores MUST be included in the scope of annual penetration testing (ANIF-848).

---

## 9. Operational Considerations

The 10-year retention requirement creates a long-term storage obligation. Organisations MUST account for this in their storage architecture at the outset. Records written in YAML as defined in this schema are readable without specialist software, which satisfies the regulatory accessibility requirement without vendor lock-in. Format migration MUST be managed with care: any migration that changes field values — even whitespace or encoding — produces a technically different record. Migration MUST be managed using checksums to verify that field values are unchanged.
