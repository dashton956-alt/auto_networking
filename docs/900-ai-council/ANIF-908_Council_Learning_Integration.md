# ANIF-908: Council and Learning Agent Integration

| Field        | Value                                              |
|--------------|----------------------------------------------------|
| Doc ID       | ANIF-908                                           |
| Series       | AI Council                                         |
| Version      | 0.1.0                                              |
| Status       | Draft                                              |
| Authors      | ANIF Working Group                                 |
| Reviewers    | —                                                  |
| Approved by  | —                                                  |
| Created      | 2026-04-08                                         |
| Last updated | 2026-04-08                                         |
| Replaces     | N/A                                                |
| Related docs | ANIF-812, ANIF-900, ANIF-902, ANIF-903, ANIF-905  |

---

## Abstract

This document defines how AI Council decisions feed into the Learning Agent (ANIF-812) to improve future agent behaviour and council governance. Council decisions generate three types of learning signal: positive examples (approved actions with good outcomes), negative examples (blocked actions or outcome-wrong approvals), and council pattern signals (consistent overrides of the same agent design pattern). All learning packages require human approval before incorporation into agent knowledge. The council MUST NOT update its own mode selection rules without human oversight — council self-modification is prohibited. The feedback loop closes: Review Council generates learning packages, Learning Agent submits for human approval, approved packages update agent knowledge, and better future agent behaviour reduces the frequency of council escalation.

---

## 1. Introduction

### 1.1 Purpose

A council that reviews decisions but whose decisions never improve the system is an accountability body without a learning function. This document defines the feedback loop that connects council governance outcomes to agent knowledge, ensuring that the organisational cost of council review produces durable improvement in agent behaviour.

### 1.2 Scope

Three types of learning signal from council decisions, the council pattern signal for systematic agent design issues, the prohibition on council self-modification, and the feedback loop from Review Council to Learning Agent to agent knowledge updates.

### 1.3 Out of Scope

Learning Agent operation and knowledge package schema (see ANIF-812), Review Council output requirements (see ANIF-905), council record requirements (see ANIF-907).

### 1.4 Intended Audience

- Learning Chair seat holders responsible for council-to-learning feedback
- Learning Agent operators processing council-generated packages
- Governance committee members overseeing the feedback loop
- Platform engineers implementing council-to-learning integration

---

## 2. Normative References

| Reference | Title |
|---|---|
| ANIF-812 | Learning Agent |
| ANIF-900 | AI Council Overview |
| ANIF-902 | Council Mode Selector |
| ANIF-903 | Build-Time Council |
| ANIF-904 | Runtime Council |
| ANIF-905 | Review Council |
| ANIF-907 | Council Audit and Accountability |
| RFC 2119 | Key words for use in RFCs to Indicate Requirement Levels |

---

## 3. Learning Signals from Council Decisions

### 3.1 Positive Examples

A positive learning example is generated when:
- A council approves an action, and
- The action produces a successful outcome (as determined by post-execution evaluation)

The positive example MUST include: the intent type, the context characteristics that made the council approve, the outcome, and the council_id for traceability. Positive examples teach agents which actions were appropriate under which conditions.

### 3.2 Negative Examples

A negative example is generated when:
- A council blocks an action — the action itself is the negative example, and
- An outcome-wrong approval occurs: the council approved an action that produced a bad outcome — the approval decision is the negative example

Outcome-wrong negative examples are the most valuable learning signal — they identify cases where the council's own judgement was incorrect. These MUST be produced by the Review Council following any post-approval incident analysis.

A negative example MUST include: the intent type, the specific characteristics that made the action inappropriate or risky, the outcome (where applicable), the blocking rationale, and the council_id.

### 3.3 Council Pattern Signals

A council pattern signal is generated when the Learning Chair identifies that the council has consistently overridden, blocked, or flagged the same agent design pattern across multiple sessions. The threshold for generating a pattern signal is three or more council decisions in 90 days that share a common agent characteristic.

A council pattern signal is not a learning package for agents — it is a signal to the Build-Time Council that an agent design issue exists. The pattern signal MUST be submitted to the Build-Time Council for assessment. The Build-Time Council MUST evaluate whether the pattern represents a systematic agent design deficiency that requires a capability manifest change or agent redesign.

---

## 4. Learning Package Production

The Learning Chair holds responsibility for identifying and packaging learning signals from council decisions. The Learning Chair MUST:

1. Review every completed council session record within 5 business days
2. Identify whether a positive example, negative example, or neither should be generated
3. For Review Council sessions, confirm the three mandatory outputs include learning packages (ANIF-905 section 5.3)
4. Submit completed learning packages to the Learning Agent for human approval (ANIF-812)

Learning packages generated from council decisions follow the knowledge package schema defined in ANIF-812. The `source_council_id` field MUST be populated with the council_id of the session that generated the package.

---

## 5. Human Approval Requirement

All learning packages — regardless of source — MUST go through the human approval gate defined in ANIF-812 before any agent knowledge is updated. Council authority does not substitute for human approval. A decision reached by the Review Council does not automatically authorise agent knowledge updates; the updates MUST be separately reviewed and approved by a human with Learning Agent approval authority.

This requirement prevents the council from becoming a mechanism for authorising knowledge changes without individual human review. The human approval gate is independent of the council process and MUST NOT be bypassed even for learning packages endorsed by all seven council seats.

---

## 6. Council Self-Modification Prohibition

The council MUST NOT update its own mode selection rules (ANIF-902) without human oversight. Specifically:

- The Mode Selector decision matrix (ANIF-902 section 4) MUST NOT be modified through the learning package process
- Proposed changes to the Mode Selector MUST follow the policy lifecycle (ANIF-833)
- Any learning package that proposes modification to council governance procedures is out of scope for the Learning Agent and MUST be redirected to the policy lifecycle process

A council that can modify its own decision rules through its own decisions is not subject to effective human oversight. The prohibition on council self-modification is a structural governance requirement, not a preference.

---

## 7. Feedback Loop Summary

The complete feedback loop from incident to improved agent behaviour operates as follows:

1. **Incident occurs** — Severity 1 ethics or Level 3+ security incident triggers Review Council
2. **Review Council convenes** — produces accountability determination, policy change recommendations, and learning packages (ANIF-905)
3. **Learning packages submitted** — Learning Chair submits packages to Learning Agent within 10 business days
4. **Human approval gate** — Learning Agent operator presents packages for human review and approval (ANIF-812)
5. **Approved packages incorporated** — agent knowledge base is updated
6. **Better future decisions** — updated agent knowledge reduces the frequency of escalation to council review
7. **Pattern monitoring** — Learning Chair monitors for council pattern signals and escalates to Build-Time Council where a systematic design issue is identified

---

## 8. Conformance Requirements

| ID | Requirement |
|---|---|
| CR-908-01 | The Learning Chair MUST review every completed council session record within 5 business days to identify learning signals. |
| CR-908-02 | Outcome-wrong negative examples MUST be produced for any post-approval incident. |
| CR-908-03 | Learning packages MUST include the `source_council_id` of the generating session. |
| CR-908-04 | All learning packages from council sessions MUST go through the Learning Agent human approval gate before agent knowledge is updated. |
| CR-908-05 | Council authority MUST NOT substitute for the Learning Agent human approval gate. |
| CR-908-06 | The Mode Selector decision matrix MUST NOT be modified through the learning package process; changes MUST follow the policy lifecycle. |
| CR-908-07 | Three or more council decisions sharing a common agent characteristic within 90 days MUST generate a council pattern signal to the Build-Time Council. |

---

## 9. Security Considerations

Learning packages carry significant influence over future agent behaviour. A compromised learning package can introduce systematic bias or vulnerabilities into the agent knowledge base across the entire deployment. Packages generated from council records MUST be stored with the same access controls as the council records from which they derive. The human approval gate is the critical control point — the human reviewer MUST be independent of the agent team whose agents would be affected by the package.

---

## 10. Operational Considerations

The feedback loop defined in this document is the mechanism through which ANIF deployments improve over time. Organisations that treat the council as a compliance requirement rather than a learning opportunity will find council escalation rates stable or increasing over time. Organisations that actively manage the learning feedback loop — reviewing council pattern signals, acting on policy recommendations, and approving quality learning packages — will see council escalation rates decline as agents develop better decision patterns.
