# ANIF-906: Council Deliberation Standards

| Field        | Value                                              |
|--------------|----------------------------------------------------|
| Doc ID       | ANIF-906                                           |
| Series       | AI Council                                         |
| Version      | 0.1.0                                              |
| Status       | Draft                                              |
| Authors      | ANIF Working Group                                 |
| Reviewers    | —                                                  |
| Approved by  | —                                                  |
| Created      | 2026-04-08                                         |
| Last updated | 2026-04-08                                         |
| Replaces     | N/A                                                |
| Related docs | ANIF-900, ANIF-901, ANIF-902, ANIF-907             |

---

## Abstract

This document defines the four deliberation models available to the AI Council — majority, consensus, weighted, and adversarial — with their time limits, voting procedures, deadlock resolution rules, and recording requirements. Veto exercise requires a stated ANIF requirement reference; a veto without citation is procedurally invalid. All deliberations MUST be fully logged to the council record before the council session closes. These standards apply to all three council types (Build-Time, Runtime, and Review) wherever a deliberation model is in use.

---

## 1. Introduction

### 1.1 Purpose

Consistent deliberation standards ensure that council decisions are reproducible, accountable, and auditable regardless of which seat holders are present or which council type is in session. Without defined standards, deliberation quality depends entirely on the individuals in the room. With defined standards, the process is independent of the individuals.

### 1.2 Scope

Four deliberation models, their time limits, voting procedures, deadlock resolution, and logging requirements. Veto exercise standards.

### 1.3 Out of Scope

Mode selection logic — which model is chosen for which situation (see ANIF-902). Council type-specific procedures (see ANIF-903, ANIF-904, ANIF-905). Council record schema (see ANIF-907).

### 1.4 Intended Audience

- Council seat holders participating in deliberations
- Council facilitators managing the session
- Platform engineers implementing council session tooling
- Conformance assessors verifying deliberation standard compliance

---

## 2. Normative References

| Reference | Title |
|---|---|
| ANIF-901 | AI Council Composition and Roles |
| ANIF-902 | Council Mode Selector |
| ANIF-907 | Council Audit and Accountability |
| RFC 2119 | Key words for use in RFCs to Indicate Requirement Levels |

---

## 3. Deliberation Models

### 3.1 Majority Vote

| Parameter | Value |
|---|---|
| Time limit | 15 minutes from session open |
| Minimum quorum | 5 of 7 seats |
| Passing threshold | Simple majority of seats present |
| Veto applies | Yes |
| Typical use | Reversible, time-critical decisions |

Procedure: each seat holder states their vote (approve / block / abstain) and a one-sentence rationale. Votes are recorded in the order cast. The session chair announces the result when a majority is reached or the time limit expires.

### 3.2 Consensus

| Parameter | Value |
|---|---|
| Time limit | 30 minutes from session open |
| Minimum quorum | All 7 seats |
| Passing threshold | No outstanding objection from any veto seat |
| Veto applies | Yes |
| Typical use | Ethics-flagged decisions; irreversible high-risk decisions |

Procedure: the session chair presents the decision. Each seat holder states their position in turn. The council works to address objections within the time limit. Consensus is reached when all three veto seats have indicated no objection. Non-veto seat objections are recorded but do not prevent consensus.

### 3.3 Weighted Vote

| Parameter | Value |
|---|---|
| Time limit | 15 minutes from session open |
| Minimum quorum | 5 of 7 seats |
| Passing threshold | Sum of approval weights exceeds sum of block weights |
| Veto applies | Yes |
| Typical use | Domain-specific risk decisions; situations where specialist expertise dominates |

Seat weights for weighted voting:

| Seat | Weight |
|---|---|
| Ethics Chair | 3 |
| Security Chair | 2 |
| Governance Chair | 2 |
| Operations Chair | 2 |
| Architecture Chair | 2 |
| Learning Chair | 1 |
| Human Advocate | Special — halt authority only; no weight in weighted vote |

Total maximum weighted vote (excluding Human Advocate): 12. Simple approval majority is 7 or more weighted votes in favour. An absent seat contributes zero weight. A veto exercise overrides the weighted total.

### 3.4 Adversarial

| Parameter | Value |
|---|---|
| Time limit | 45 minutes from session open |
| Minimum quorum | All 7 seats |
| Passing threshold | Majority after challenge round |
| Veto applies | Yes |
| Typical use | Post-incident accountability; novel high-risk decisions; situations with active strike history |

Procedure: the session chair designates an advocate (argues for approval) and a challenger (argues for blocking). Each presents their position for up to 5 minutes. All other seats may question both positions for up to 10 minutes total. A structured vote is then taken under majority rules with full rationale recorded for each seat. The adversarial format is designed to surface assumptions and expose weaknesses in both the approval and blocking positions before the vote.

---

## 4. Veto Exercise Standards

A veto may be exercised by any seat with veto authority (ANIF-901) under any deliberation model. The following rules apply to all veto exercises:

1. A seat holder exercising a veto MUST state the specific ANIF document, section, and requirement that the vetoed decision violates.
2. A veto stated as "I am not comfortable with this" or "I disagree with the direction" without an ANIF reference is procedurally invalid.
3. An invalid veto MUST be recorded as a procedural error in the council record. It does not block the decision.
4. A valid veto immediately blocks the decision regardless of all other votes and regardless of remaining deliberation time.
5. The vetoing seat holder MUST confirm that the veto stands after the invalid-veto check is applied.

The requirement to cite a specific ANIF requirement is not a bureaucratic formality. It ensures that veto authority is grounded in the governance framework, not in personal preference or positional authority.

---

## 5. Deadlock Resolution

Deadlock occurs when the time limit expires without a decision under the consensus model. Under majority and weighted models, a tie is resolved as follows: ties block the decision (abstentions count as neither approve nor block). Under consensus, a non-decision at time limit follows the rules defined by the council type (ANIF-904 default-to-halt for Runtime; ANIF-903 deferral for Build-Time).

| Model | Deadlock Condition | Resolution |
|---|---|---|
| Majority | Equal approve/block votes at time limit | Decision is blocked; resubmission permitted |
| Consensus | Not all veto seats agree at time limit | Decision is deferred or halted per council type rules |
| Weighted | Equal weighted vote totals at time limit | Decision is blocked; resubmission permitted |
| Adversarial | Majority not reached at time limit | Decision is escalated to governance committee |

Escalation to the governance committee on deadlock MUST include the full deliberation record and the positions of all seats.

---

## 6. Session Recording Requirements

All council deliberations MUST be fully logged before the session closes. The following MUST be recorded in the council record (ANIF-907):

- Session open and close timestamps
- Seats present and absent, with deputy invocations noted
- Deliberation model in use
- Summary of each seat holder's stated position
- Every vote cast, with the seat holder's stated rationale
- Any veto exercises, with the cited ANIF requirement
- Any procedural errors (invalid vetoes, quorum failures)
- The final decision and its rationale
- Any conditions attached to the decision

The session MUST NOT close until the chair confirms all required fields are written to the council record. A council session closed with incomplete records is a conformance violation.

---

## 7. Conformance Requirements

| ID | Requirement |
|---|---|
| CR-906-01 | Council deliberation MUST complete within the time limit for the selected model. |
| CR-906-02 | A veto exercised without a stated ANIF requirement reference MUST be recorded as procedurally invalid and MUST NOT block the decision. |
| CR-906-03 | All council deliberations MUST be fully logged to the council record before the session closes. |
| CR-906-04 | Deadlock under the adversarial model MUST be escalated to the governance committee. |
| CR-906-05 | The Human Advocate's halt authority takes effect immediately and suspends deliberation until the human oversight concern is addressed. |

---

## 8. Security Considerations

Deliberation records describe the council's reasoning, including positions that were ultimately rejected. This information could assist an attacker in understanding the council's decision-making patterns and constructing future decisions to exploit them. Council records MUST be stored with the same access restrictions as security test reports (ANIF-848 section 10) and MUST NOT be accessible to agents whose decisions the council governs.

---

## 9. Operational Considerations

The 15-minute time limits for majority and weighted deliberations are intentionally short. They are designed for decisions that can be evaluated quickly — reversible, precedented, or time-critical. The 45-minute adversarial model is the appropriate vehicle for complex decisions. Organisations that find themselves routinely running over time in majority-model sessions are likely misclassifying decisions that should be using the adversarial or consensus models. A pattern of time limit breaches SHOULD trigger a review of the Mode Selector (ANIF-902) input factor calibration.
