# ANIF-901: AI Council Composition and Roles

| Field        | Value                                              |
|--------------|----------------------------------------------------|
| Doc ID       | ANIF-901                                           |
| Series       | AI Council                                         |
| Version      | 0.1.0                                              |
| Status       | Draft                                              |
| Authors      | ANIF Working Group                                 |
| Reviewers    | —                                                  |
| Approved by  | —                                                  |
| Created      | 2026-04-08                                         |
| Last updated | 2026-04-08                                         |
| Replaces     | N/A                                                |
| Related docs | ANIF-838, ANIF-900, ANIF-902, ANIF-906             |

---

## Abstract

This document defines the seven seats of the ANIF AI Council, the veto powers associated with each seat, quorum requirements per deliberation model, and deputy seat policy. The Ethics Chair holds an absolute veto over any council decision. The Security Chair holds a veto on matters with a security dimension. The Governance Chair holds final policy compliance authority. The Operations Chair, Architecture Chair, and Learning Chair hold weighted votes. The Human Advocate holds a permanent seat as guardian of the P-06 human oversight principle and may invoke a halt on any decision that reduces human oversight below ANIF-defined minimums.

---

## 1. Introduction

### 1.1 Purpose

A council with undefined seats and undefined voting rules is not a governance body — it is a discussion group. This document specifies the composition rules that make the ANIF AI Council a body capable of binding governance decisions.

### 1.2 Scope

Seven council seats, veto authority, quorum requirements, deputy seat policy, and conflict of interest provisions.

### 1.3 Out of Scope

Council type procedures (see ANIF-903, ANIF-904, ANIF-905), deliberation time limits and deadlock resolution (see ANIF-906), council record requirements (see ANIF-907).

### 1.4 Intended Audience

- Governance committee members appointing council seat holders
- HR and executive teams identifying candidates for council seats
- Council seat holders understanding their authority and obligations
- Conformance assessors verifying council establishment

---

## 2. Normative References

| Reference | Title |
|---|---|
| ANIF-838 | AI Governance Roles and Responsibilities |
| ANIF-900 | AI Council Overview |
| ANIF-902 | Council Mode Selector |
| ANIF-906 | Council Deliberation Standards |
| ANIF-907 | Council Audit and Accountability |
| RFC 2119 | Key words for use in RFCs to Indicate Requirement Levels |

---

## 3. Council Seats

The AI Council comprises seven seats. All seven seats MUST be filled by named individuals before any council is convened.

| Seat | Role | Vote Type | Veto Scope |
|---|---|---|---|
| Ethics Chair | Owns ethics framework; convenes ethics review panel | Weighted — double weight | Absolute veto over any decision |
| Security Chair | Leads security function; accountable for ANIF-840–849 | Weighted | Veto on any decision with a security dimension |
| Operations Chair | Leads network operations function | Weighted | None — weighted vote only |
| Architecture Chair | Leads network architecture function | Weighted | None — weighted vote only |
| Governance Chair | Holds governance compliance authority; typically AI Risk Officer | Weighted | Veto on any decision that violates a governance policy |
| Learning Chair | Responsible for Learning Agent governance (ANIF-812) | Weighted | None — weighted vote only |
| Human Advocate | Independent representative of human oversight principle | Special — halt authority | Halt authority on any decision that reduces human oversight below ANIF minimums |

### 3.1 Ethics Chair Absolute Veto

The Ethics Chair MAY exercise an absolute veto on any council decision. An absolute veto blocks the decision regardless of all other votes. The Ethics Chair MUST state the specific ANIF-700 series requirement or ethics principle that the vetoed decision violates. A veto exercised without a stated reason is invalid and MUST be recorded as a procedural error.

### 3.2 Security Chair Veto

The Security Chair MAY exercise a veto on any decision that the Security Chair determines has a security dimension. The Security Chair MUST state the specific ANIF-840 series requirement that the vetoed decision violates or the specific threat scenario from ANIF-841 that the decision exacerbates.

### 3.3 Governance Chair Veto

The Governance Chair MAY exercise a veto on any decision that violates an active governance policy. The Governance Chair MUST cite the specific policy and the specific clause that the decision contravenes.

### 3.4 Human Advocate Halt Authority

The Human Advocate MAY halt any council decision that would reduce human oversight below the minimums defined in ANIF-400 series, ANIF-700 series, or ANIF-800 series. A halt is not a veto — it pauses deliberation and requires the council to address the human oversight concern before proceeding. The Human Advocate MUST NOT be an employee of the AI programme team. The Human Advocate MUST be independent of the operational functions affected by council decisions.

---

## 4. Quorum Requirements

| Deliberation Model | Minimum Seats Present | Notes |
|---|---|---|
| Consensus | All 7 seats | No absent seats permitted for consensus decisions |
| Majority vote | 5 of 7 seats | The two absent seats MUST be documented in the council record |
| Weighted vote | 5 of 7 seats | A veto-holder absence MUST be covered by a confirmed deputy |
| Adversarial | All 7 seats | The adversarial model requires all perspectives present |

If quorum cannot be achieved, the decision MUST be escalated to the governance committee. The council MUST NOT proceed without quorum under any deliberation model.

---

## 5. Deputy Seat Policy

Each seat holder MUST designate a named deputy. Deputies MUST be pre-approved by the governance committee. A deputy has the same voting and veto authority as the primary seat holder. Only one individual — primary or deputy — MAY hold the seat at any given time.

A deputy may be invoked when:
- The primary seat holder is unavailable due to absence, illness, or conflict of interest
- The primary seat holder has declared a conflict of interest on the specific decision

The invocation of a deputy MUST be recorded in the council record.

---

## 6. Conflict of Interest

A seat holder MUST declare a conflict of interest and recuse themselves when:
- The decision directly affects a system or project in which the seat holder has a personal or financial interest
- The seat holder has a direct reporting relationship to the agent or team whose work is under review
- The seat holder has previously advocated for a specific outcome on the decision being reviewed

A recused seat holder is replaced by their deputy. If the deputy also has a conflict, the governance committee MUST appoint a temporary seat holder for that decision.

---

## 7. Conformance Requirements

| ID | Requirement |
|---|---|
| CR-901-01 | All seven council seats MUST be filled by named individuals before any council is convened. |
| CR-901-02 | Each seat holder MUST have a named deputy approved by the governance committee. |
| CR-901-03 | A veto exercised without a stated ANIF requirement reference is invalid and MUST be recorded as a procedural error. |
| CR-901-04 | The Human Advocate MUST NOT be an employee of the AI programme team. |
| CR-901-05 | Council decisions MUST NOT proceed without the required quorum for the selected deliberation model. |

---

## 8. Security Considerations

Council seat holders with veto authority are high-value social engineering targets. Compromising an Ethics Chair or Security Chair gives an attacker the ability to block legitimate governance decisions or, conversely, to approve harmful ones. Seat holder identities MUST be verified through the organisation's privileged identity management process. Council deliberation channels MUST be protected with the same access controls as security test reports.

---

## 9. Operational Considerations

The Human Advocate seat is the seat most organisations find difficult to fill. The independence requirement — not an employee of the AI programme team — means this seat cannot be filled from within the operations, engineering, or governance functions. Organisations SHOULD designate a senior individual from legal, risk, or an independent internal function. External appointment is permitted where no suitable internal candidate exists.
