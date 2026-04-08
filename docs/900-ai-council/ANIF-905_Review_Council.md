# ANIF-905: Review Council

| Field        | Value                                              |
|--------------|----------------------------------------------------|
| Doc ID       | ANIF-905                                           |
| Series       | AI Council                                         |
| Version      | 0.1.0                                              |
| Status       | Draft                                              |
| Authors      | ANIF Working Group                                 |
| Reviewers    | —                                                  |
| Approved by  | —                                                  |
| Created      | 2026-04-08                                         |
| Last updated | 2026-04-08                                         |
| Replaces     | N/A                                                |
| Related docs | ANIF-715, ANIF-812, ANIF-847, ANIF-900, ANIF-901, ANIF-906, ANIF-908 |

---

## Abstract

This document defines the Review Council: its trigger conditions, mandatory deliberation model, three mandatory outputs, and reporting requirements. The Review Council convenes after every Severity 1 ethics incident and every Level 3 or Level 4 security incident. It always uses the adversarial deliberation model, which requires all seven seats and the longest deliberation window. The Review Council MUST produce three outputs: an accountability determination identifying which accountability layer bears primary responsibility, policy change recommendations citing specific ANIF requirements to be modified, and learning packages for submission to the Learning Agent. The full review report MUST be submitted to the governance committee within 72 hours of the triggering incident.

---

## 1. Introduction

### 1.1 Purpose

When serious incidents occur — ethics violations at Severity 1 or security incidents at Level 3 or above — the organisation requires a structured post-incident process that goes beyond incident closure. The Review Council provides accountability determination, prevents recurrence through policy change, and integrates lessons learned into agent knowledge. Without this body, incidents close and their lessons are lost.

### 1.2 Scope

Review Council trigger conditions, the adversarial deliberation model requirement, three mandatory outputs, and the 72-hour reporting requirement.

### 1.3 Out of Scope

Council composition and quorum requirements (see ANIF-901), mode selection logic (see ANIF-902 — Review Council always uses adversarial model), Build-Time Council procedures (see ANIF-903), Runtime Council procedures (see ANIF-904), deliberation time limits (see ANIF-906), Learning Agent integration (see ANIF-908).

### 1.4 Intended Audience

- Governance committee members receiving Review Council reports
- Council seat holders participating in post-incident review
- AI Ethics Officer and AI Risk Officer responsible for acting on recommendations
- Conformance assessors verifying Review Council operation

---

## 2. Normative References

| Reference | Title |
|---|---|
| ANIF-715 | Ethics Incident Response Policy |
| ANIF-724 | Ethics Audit Trail Requirements |
| ANIF-812 | Learning Agent |
| ANIF-831 | AI Governance Structure and Accountability |
| ANIF-833 | AI Policy Lifecycle Management |
| ANIF-839 | AI Governance Compliance and Audit |
| ANIF-847 | AI Security Incident Response |
| ANIF-900 | AI Council Overview |
| ANIF-901 | AI Council Composition and Roles |
| ANIF-906 | Council Deliberation Standards |
| ANIF-907 | Council Audit and Accountability |
| ANIF-908 | Council and Learning Agent Integration |
| RFC 2119 | Key words for use in RFCs to Indicate Requirement Levels |

---

## 3. Trigger Conditions

The Review Council MUST be convened following:

| Trigger | Definition |
|---|---|
| Severity 1 ethics incident | An ethics incident classified at Severity 1 per ANIF-715 |
| Level 3 security incident | An AI security incident at Level 3 per ANIF-847 |
| Level 4 security incident | An AI security incident at Level 4 per ANIF-847 |

The Review Council convenes after the immediate incident response is complete — it is a post-incident body, not a concurrent response body. The ethics incident response (ANIF-715) and security incident response (ANIF-847) procedures take precedence during the active incident. The Review Council is convened once the incident is stabilised and closed.

The Review Council MUST be convened within 5 business days of incident closure. If an incident is not closed within 30 calendar days, the Review Council MUST convene on the available evidence without waiting for full closure.

---

## 4. Deliberation Model

The Review Council MUST always use the adversarial deliberation model. No other model is permitted for Review Council sessions. The adversarial model requires:

- All seven seats present (see ANIF-901 quorum requirements)
- Explicit challenge and counter-challenge of proposed accountability determinations
- Separate votes on each of the three mandatory outputs
- Full recording of dissenting positions

The adversarial model is mandatory because post-incident accountability determination requires that every proposed conclusion be challenged. A council that reaches easy consensus on accountability has likely failed to examine the incident with sufficient rigour.

---

## 5. Mandatory Outputs

The Review Council MUST produce all three of the following outputs. A council that produces fewer than three outputs has not completed its review.

### 5.1 Accountability Determination

The accountability determination MUST identify which accountability layer (ANIF-831) bears primary responsibility for the incident and why. The determination MUST:

- Name the specific accountability layer: agent, pipeline, governance, or human operator
- Cite the specific failure that caused or permitted the incident
- Assess whether the failure was a policy gap, a configuration error, a testing failure, or a governance failure
- Where multiple layers contributed, rank them by degree of contribution

The accountability determination MUST NOT be used punitively against individual seat holders or operators. Its purpose is systemic improvement, not individual sanction.

### 5.2 Policy Change Recommendations

Policy change recommendations MUST cite specific ANIF documents and requirements that are to be changed, added, or removed. Recommendations MUST:

- Reference the specific ANIF-NNN document and section to be modified
- State the proposed change precisely enough that it can be submitted directly to the policy lifecycle (ANIF-833)
- Explain why the change would prevent recurrence of the incident
- Assess whether the change creates new risks that require separate treatment

Vague recommendations ("improve monitoring", "tighten access controls") are not valid policy change recommendations. Each recommendation MUST be specific enough to be independently actionable.

### 5.3 Learning Packages

Learning packages are structured knowledge artefacts submitted to the Learning Agent (ANIF-812) for human approval and incorporation into the agent knowledge base. Each learning package MUST:

- Describe the scenario that caused the incident in terms an agent can evaluate at inference time
- Specify the correct behaviour that should have been taken (or avoided)
- Classify the package as a positive example (behaviour to repeat) or negative example (behaviour to avoid)
- Include the council record reference for traceability

Learning packages MUST be submitted to the Learning Agent within 10 business days of the Review Council completing its session. They are subject to the human approval requirement in ANIF-812 before any agent knowledge is updated.

---

## 6. Reporting Requirements

The Review Council MUST submit a written report to the governance committee within 72 hours of the triggering incident closure. The report MUST include all three mandatory outputs. Partial reports — reports containing fewer than three outputs — are not accepted as complete. The governance committee MUST acknowledge receipt of the report and record the acknowledgement in governance committee minutes.

The report MUST be retained as part of the incident record for a minimum of 5 years. For Level 4 incidents, the report MUST be retained for a minimum of 10 years.

---

## 7. Conformance Requirements

| ID | Requirement |
|---|---|
| CR-905-01 | The Review Council MUST be convened within 5 business days of every Severity 1 ethics incident or Level 3+ security incident closure. |
| CR-905-02 | The Review Council MUST always use the adversarial deliberation model. |
| CR-905-03 | The Review Council MUST produce all three mandatory outputs: accountability determination, policy change recommendations, and learning packages. |
| CR-905-04 | Policy change recommendations MUST cite specific ANIF documents and sections. |
| CR-905-05 | The full review report MUST be submitted to the governance committee within 72 hours of incident closure. |
| CR-905-06 | Learning packages MUST be submitted to the Learning Agent within 10 business days of the Review Council session. |

---

## 8. Security Considerations

Review Council reports describe the organisation's governance weaknesses as exposed by the incident. They MUST be classified as highly confidential and access restricted to the governance committee, council seat holders, and external auditors. Reports MUST NOT be shared externally without governance committee approval. Where a report contains details of specific vulnerabilities that remain unresolved, distribution MUST be further restricted until remediation is confirmed.

---

## 9. Operational Considerations

Review Council sessions are emotionally and politically sensitive. The accountability determination process may implicate functions or individuals with organisational authority. The adversarial deliberation model is specifically designed to resist the social pressure toward comfortable conclusions. Council seat holders MUST be briefed before their first Review Council session on the distinction between systemic accountability determination (the council's purpose) and individual blame (outside the council's scope).
