# ANIF-823: Migration and Adoption Roadmap

| Field        | Value                                              |
|--------------|----------------------------------------------------|
| Doc ID       | ANIF-823                                           |
| Series       | AI Agent Architecture                              |
| Version      | 0.1.0                                              |
| Status       | Draft                                              |
| Authors      | ANIF Working Group                                 |
| Reviewers    | —                                                  |
| Approved by  | —                                                  |
| Created      | 2026-04-08                                         |
| Last updated | 2026-04-08                                         |
| Replaces     | N/A                                                |
| Related docs | ANIF-500, ANIF-501, ANIF-700, ANIF-819             |

---

## Abstract

This document defines the three-phase migration path from L1–L4 conformance to L5 (AI-Native) conformance. The three phases are: parallel running, validation, and progressive autonomy. Each phase has defined entry criteria, exit criteria, and minimum duration requirements. The minimum viable L5 implementation — the set of ANIF documents and safeguards that constitute the minimum to claim L5 — is specified. No organisation MUST claim L5 without completing all three phases, regardless of implementation quality. L5 is a governed state that requires demonstrated operational evidence, not merely technical capability.

---

## 1. Introduction

### 1.1 Purpose

L5 conformance introduces AI autonomous operation into critical network infrastructure. This cannot safely be achieved by switching from L4 to L5 in a single step. The three-phase migration path defined in this document ensures that AI agents are introduced incrementally, with each phase providing operational evidence that the agents are ready for greater autonomy before it is granted.

### 1.2 Scope

This document covers:

- Entry and exit criteria for each migration phase
- Minimum duration requirements per phase
- The minimum viable L5 implementation specification
- Governance approvals required to progress between phases

### 1.3 Out of Scope

This document does not cover:

- Conformance level definitions (see ANIF-501)
- Certification process (see ANIF-502)
- Disaster recovery and degradation levels (see ANIF-819)
- AI Council composition and deliberation (see ANIF-900)

### 1.4 Intended Audience

- Network operations executives planning AI adoption
- Platform engineers implementing the ANIF framework
- Governance officers approving phase progression
- Conformance assessors verifying L5 readiness

---

## 2. Normative References

| Reference | Title |
|---|---|
| ANIF-500 | Conformance Overview |
| ANIF-501 | Conformance Level Definitions |
| ANIF-502 | Certification Process |
| ANIF-700 | AI Ethics Framework Overview |
| ANIF-819 | Disaster Recovery and Resilience |
| ANIF-900 | AI Council Overview |
| ANIF-903 | Build-Time Council |
| RFC 2119 | Key words for use in RFCs to Indicate Requirement Levels |

---

## 3. Terms and Definitions

| Term | Definition |
|---|---|
| Parallel running | A migration phase in which AI agents operate alongside deterministic systems, producing recommendations that are logged but not acted upon |
| Validation phase | A migration phase in which AI agent outputs are validated against a deterministic baseline before any autonomous action is taken |
| Progressive autonomy | A migration phase in which AI agents are permitted to act autonomously on a progressively wider scope, starting with the lowest-risk, most reversible actions |
| Minimum viable L5 | The minimum set of ANIF documents, safeguards, and operational evidence required to claim L5 conformance |
| Shadow mode | Operation in which an agent produces outputs that are recorded but not executed |

---

## 4. Pre-Migration Requirements

Before beginning Phase 1, the following MUST be complete:

1. The organisation MUST hold L1–L4 conformance for the systems that the AI agents will manage.
2. The minimum viable L5 implementation (section 7) MUST be deployed in the test environment.
3. The AI Council (ANIF-900) and Build-Time Council (ANIF-903) MUST be formally chartered and their members confirmed.
4. All agents intended for Phase 1 deployment MUST have passed all deployment gates defined in ANIF-820.
5. The organisation MUST have completed the ANIF-819 Level 2 DR drill at least once in the test environment.

---

## 5. Phase 1 — Parallel Running

### 5.1 Description

In Phase 1, AI agents operate in shadow mode alongside the existing deterministic systems. Agent outputs are logged and are visible to operators but are not executed. Operators compare agent recommendations to their own decisions without any obligation to follow the agent recommendations.

### 5.2 Entry Criteria

- All pre-migration requirements (section 4) satisfied
- Governance committee approval documented
- Shadow mode operation technically verified: agent outputs are confirmed to be write-only to logs, not to execution pipeline

### 5.3 What MUST Happen During Phase 1

- Agents MUST produce recommendations for all intents processed during the phase
- All agent recommendations MUST be logged alongside the actual human decisions taken
- The difference between agent recommendations and human decisions MUST be tracked as the "alignment gap"
- Operators MUST provide structured feedback on recommendations they would have rejected, with reasons

### 5.4 Minimum Duration

Phase 1 MUST run for a minimum of 30 calendar days covering at least 500 processed intents. If 500 intents are not reached within 30 days, Phase 1 MUST continue until both conditions are met.

### 5.5 Exit Criteria

Phase 1 may exit to Phase 2 only when:

- The alignment gap is below 15% (agent recommendations align with human decisions in more than 85% of cases)
- No Critical or High red-team findings are open
- The governance committee has reviewed Phase 1 results and approved progression
- The AI Council has voted to approve Phase 2 entry

---

## 6. Phase 2 — Validation

### 6.1 Description

In Phase 2, AI agents produce outputs that are validated against a deterministic baseline before any autonomous action. No action executes unless both the AI agent and the deterministic baseline agree the action is appropriate. Disagreements are escalated to the human-in-loop queue.

### 6.2 Entry Criteria

- Phase 1 exit criteria satisfied and governance committee approval documented
- AI Council Phase 2 entry vote recorded
- Deterministic validation layer technically verified and tested

### 6.3 What MUST Happen During Phase 2

- Every AI agent output MUST be compared against the deterministic baseline before execution
- Only outputs where both agree MUST proceed to auto-execution
- Disagreements MUST enter PENDING_APPROVAL state for human decision
- Disagreement rate MUST be tracked per agent role per week

### 6.4 Minimum Duration

Phase 2 MUST run for a minimum of 30 calendar days covering at least 1,000 processed intents across at least three distinct intent types.

### 6.5 Exit Criteria

Phase 2 may exit to Phase 3 only when:

- The disagreement rate between AI agent and deterministic baseline is below 10% for each agent role
- Zero Critical governance violations have occurred during Phase 2
- The ANIF-819 Level 2 DR drill has been conducted in the production environment and passed
- The governance committee has reviewed Phase 2 results and approved progression
- The AI Council has voted to approve Phase 3 entry

---

## 7. Phase 3 — Progressive Autonomy

### 7.1 Description

In Phase 3, AI agents are permitted to take autonomous action on a progressively wider scope. Autonomy is expanded in defined steps, each requiring governance approval before the next step begins.

### 7.2 Entry Criteria

- Phase 2 exit criteria satisfied and governance committee approval documented
- AI Council Phase 3 entry vote recorded

### 7.3 Autonomy Expansion Steps

Autonomous action MUST be introduced in the following order. Each step MUST be stable for a minimum of 14 days before the next step is approved.

| Step | Scope Permitted for Autonomous Action |
|---|---|
| Step 1 | Low-risk (risk score < 30), fully reversible, non-carrier-grade, single-domain intents only |
| Step 2 | Medium-risk (risk score 30–50), reversible, non-carrier-grade intents |
| Step 3 | Medium-risk, multi-domain intents (still non-carrier-grade) |
| Step 4 | Carrier-grade segments with risk score < 30 (low-risk only) |
| Step 5 | Full scope within policy bounds — equivalent to full L5 operation |

Each step beyond Step 1 MUST be approved by the AI Council before activation.

### 7.4 Exit Criteria (L5 Claim)

An organisation MAY claim L5 conformance when:

- Phase 3 Step 5 has been stable for 30 calendar days
- Zero Critical governance violations have occurred since entering Phase 3
- The annual ANIF-819 Level 4 manual operation drill has been completed and passed
- Third-party conformance assessment has been completed per ANIF-502
- The AI Council has confirmed L5 readiness

---

## 8. Minimum Viable L5 Implementation

The following represents the minimum set of ANIF requirements that MUST be implemented before an organisation may begin Phase 1 migration. Organisations claiming L5 MUST satisfy all requirements, not merely this minimum set.

| Category | Minimum Requirements |
|---|---|
| Ethics | ANIF-700–725 fully implemented |
| Agent Architecture | ANIF-800–809 fully implemented |
| Human oversight | ANIF-404, ANIF-808, ANIF-815 implemented |
| Audit trail | ANIF-107, ANIF-724 implemented with full retention |
| Containment | ANIF-725 implemented |
| Testing | ANIF-820 — all five testing types completed for each agent |
| Disaster recovery | ANIF-819 Level 2 drill completed |
| Governance | ANIF-830–831 implemented; AI Council chartered (ANIF-900) |
| Observability | ANIF-806, ANIF-822 implemented |

---

## 9. Governance Approval Requirements

| Milestone | Approving Body |
|---|---|
| Phase 1 entry | Governance committee |
| Phase 2 entry | Governance committee + AI Council vote |
| Phase 3 entry | Governance committee + AI Council vote |
| Phase 3 Step 2 and above | AI Council vote |
| L5 claim | Third-party assessor + AI Council confirmation |

All approvals MUST be recorded and retained as evidence artefacts for conformance assessment.

---

## 10. Conformance Requirements

| ID | Requirement |
|---|---|
| CR-823-01 | All pre-migration requirements (section 4) MUST be satisfied before Phase 1 begins. |
| CR-823-02 | Phase 1 MUST run for a minimum of 30 days and 500 intents. |
| CR-823-03 | Phase 2 MUST run for a minimum of 30 days and 1,000 intents. |
| CR-823-04 | Each Phase 3 autonomy step MUST be stable for 14 days before the next step is approved. |
| CR-823-05 | L5 conformance MUST NOT be claimed without third-party conformance assessment per ANIF-502. |
| CR-823-06 | All phase progression approvals MUST be recorded as evidence artefacts. |

---

## 11. Security Considerations

Parallel running and validation phases are lower-risk than full autonomy, but they are not risk-free. Even in shadow mode, agents receive real network topology data and produce recommendations that, if exposed, could assist an attacker in understanding the network. Phase 1 and Phase 2 deployments MUST be secured with the same access controls as Phase 3 production deployments.

---

## 12. Operational Considerations

Migration timelines in this document are minimums. Organisations with complex, high-criticality networks SHOULD extend each phase beyond the minimum until their governance committee is satisfied with the evidence. The minimum durations are designed to ensure sufficient evidence is gathered, not to pressure organisations into early progression.
