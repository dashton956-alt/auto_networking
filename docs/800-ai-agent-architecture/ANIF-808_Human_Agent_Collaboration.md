# ANIF-808: Human-Agent Collaboration Model

| Field        | Value                                              |
|--------------|----------------------------------------------------|
| Doc ID       | ANIF-808                                           |
| Series       | AI Agent Architecture                              |
| Version      | 0.1.0                                              |
| Status       | Draft                                              |
| Authors      | ANIF Working Group                                 |
| Reviewers    | —                                                  |
| Approved by  | —                                                  |
| Created      | 2026-04-08                                         |
| Last updated | 2026-04-08                                         |
| Replaces     | N/A                                                |
| Related docs | ANIF-801, ANIF-815, ANIF-404, ANIF-838             |

---

## Abstract

This document defines the normative boundaries of authority and responsibility between human operators and AI agents within an ANIF-conformant implementation. For each of the five primary operational roles, this document specifies what the human MUST decide, what the agent MAY decide autonomously, and what requires joint action. Human authority is primary and non-negotiable: where agent recommendation and human judgement conflict, the human decision prevails and MUST be logged. Agent autonomy exists to extend human operational capacity, not to displace human accountability.

---

## 1. Introduction

### 1.1 Purpose

This document answers the operational question every network operator faces when deploying autonomous agents: what do I still own? It provides a role-by-role specification of the collaboration boundary, expressed as normative requirements. It ensures that the introduction of AI agents does not erode operator accountability or reduce meaningful human oversight below safe levels.

### 1.2 Scope

This document covers:

- Collaboration principles governing all human-agent interactions
- Role-by-role authority tables for the five primary operational roles
- Requirements for logging human overrides of agent recommendations
- Reporting obligations for override frequency

### 1.3 Out of Scope

This document does not cover:

- Human-in-loop workflow mechanics and approval queue specifications (see ANIF-404)
- The human interaction interface design (see ANIF-815)
- Escalation and exception policy (see ANIF-105)
- Agent lifecycle state transitions (see ANIF-803)

### 1.4 Intended Audience

- Network operations staff whose roles intersect with deployed agents
- Platform architects defining agent authority scopes
- Governance officers auditing human oversight levels
- Conformance assessors evaluating L5 human-oversight claims

---

## 2. Normative References

| Reference | Title |
|---|---|
| ANIF-004 | Roles and RACI |
| ANIF-105 | Escalation and Exception Policy |
| ANIF-404 | Human-in-Loop Controls |
| ANIF-801 | Agent Types, Roles and Human Counterparts |
| ANIF-815 | Human-Agent Interaction Model |
| ANIF-837 | Governance Reporting |
| ANIF-838 | Human Override Management |
| RFC 2119 | Key words for use in RFCs to Indicate Requirement Levels |

---

## 3. Terms and Definitions

| Term | Definition |
|---|---|
| Human authority | The exclusive right and obligation of a named human to make certain decisions. Authority cannot be delegated to an agent. |
| Autonomous decision | A decision made by an agent within declared policy bounds without requiring human approval. |
| Joint action | A decision that requires both an agent recommendation and explicit human approval before execution. |
| Override | A human decision to reject or modify an agent recommendation. The override supersedes the agent output regardless of agent confidence score. |
| Override logging | The mandatory recording of an override event including operator identity, agent recommendation, human decision, and justification. |

---

## 4. Collaboration Principles

### 4.1 Human Authority is Primary

Humans retain authority over all consequential network decisions. Agent autonomy exists to extend human capacity by handling routine decisions within well-defined policy bounds. No implementation MUST reduce human authority below the levels specified in this document.

### 4.2 Override is Unconditional

A human operator MUST be able to override any agent recommendation at any time, with immediate effect. The override mechanism MUST NOT require the agent's agreement, approval, or acknowledgement. Technical implementations that allow an agent to delay, dispute, or circumvent a human override are a conformance violation.

### 4.3 Disagreement Logging is Mandatory

When a human overrides an agent recommendation, the event MUST be logged. Override logging is not punitive — it provides the data required to identify cases where agent recommendations are systematically incorrect or where policy bounds require adjustment.

### 4.4 Efficiency Does Not Justify Oversight Reduction

Agent efficiency gains — reduced response times, increased throughput, improved consistency — do not justify reducing human oversight below the levels specified in section 5. Requests to relax oversight requirements on efficiency grounds MUST be referred to the governance committee (ANIF-830).

---

## 5. Role-by-Role Collaboration Tables

The following tables define the collaboration boundary for each primary operational role. All roles are as defined in ANIF-004 and ANIF-801.

### 5.1 NOC Manager

The NOC Manager holds overall responsibility for operational outcomes during a shift.

| Category | Human MUST Decide | Agent MAY Decide | Joint Action Required |
|---|---|---|---|
| Incident declaration | Declare a P1 or P2 incident | Raise an alert and recommend severity classification | Confirm P1 declaration when agent recommendation is P1 |
| Escalation | Escalate to vendor or senior engineering | Recommend escalation with supporting evidence | — |
| Communications | Issue customer-facing communications | Draft communications for human review | All outbound communications requiring human signature |
| Resource allocation | Authorise overtime or additional resource | Schedule routine monitoring tasks | Deploy additional tooling or agent capacity |
| Handover | Accept and sign off shift handover | Compile shift summary and open action list | — |

### 5.2 Network Architect

The Network Architect is responsible for topology, routing policy, and vendor selection decisions.

| Category | Human MUST Decide | Agent MAY Decide | Joint Action Required |
|---|---|---|---|
| Topology changes | Any change to physical or logical topology | Recommend topology optimisation within declared constraints | Any change affecting more than one domain |
| Routing policy | Define, modify, or delete routing policies | Apply QoS adjustments within existing policy bounds | Any change to carrier-grade or inter-AS segments |
| Vendor selection | Select or deselect network vendors | Provide comparative analysis of vendor options | — |
| Capacity planning | Approve capacity increase above declared thresholds | Recommend capacity adjustments within headroom bounds | Changes affecting SLA-bearing services |
| Change request approval | Approve all RFC submissions | Draft RFC with supporting data and impact analysis | — |

### 5.3 Security Engineer

The Security Engineer is responsible for threat response, access control, and security policy.

| Category | Human MUST Decide | Agent MAY Decide | Joint Action Required |
|---|---|---|---|
| Threat response | Declare a security incident and initiate response | Detect anomalies, raise alerts, recommend containment actions | Containment actions affecting production traffic |
| Access control | Grant, modify, or revoke privileged access | Report access anomalies and recommend review | Any change to agent permission scopes |
| Policy exceptions | Grant security policy exceptions | Flag policy exception requests with risk assessment | — |
| Forensic action | Initiate forensic collection | Preserve and tag potential evidence automatically | — |
| Agent quarantine | Authorise quarantine of a misbehaving agent | Recommend quarantine with supporting evidence | — |

### 5.4 Change Manager

The Change Manager governs the change management process and controls change scheduling.

| Category | Human MUST Decide | Agent MAY Decide | Joint Action Required |
|---|---|---|---|
| Change approval | Approve or reject all change requests | Assess change risk and recommend approval or deferral | Emergency changes where speed and governance both apply |
| Change scheduling | Set the maintenance window calendar | Recommend maintenance windows based on traffic patterns | Changes affecting multiple teams or domains |
| Rollback authorisation | Authorise rollback of an in-progress change | Detect rollback triggers and recommend rollback | — |
| Freeze enforcement | Declare and lift change freezes | Enforce freeze rules automatically and flag violations | — |
| Post-change review | Sign off post-implementation review | Compile post-change evidence and metrics | — |

### 5.5 Problem Manager

The Problem Manager is responsible for root cause analysis and permanent resolution of recurring incidents.

| Category | Human MUST Decide | Agent MAY Decide | Joint Action Required |
|---|---|---|---|
| Problem record creation | Create a problem record for a systemic issue | Detect recurrence patterns and recommend problem creation | — |
| Root cause determination | Determine and record root cause | Analyse logs and correlate events to propose root cause | Complex multi-domain root cause analysis |
| Known error declaration | Declare a known error and workaround | Suggest known error candidate with supporting evidence | — |
| Permanent fix approval | Approve permanent fix implementation | Recommend fix options with risk and effort estimates | Fixes requiring topology or architecture changes |
| Problem closure | Close a problem record | Verify fix effectiveness against recurrence data | — |

---

## 6. Override Logging Requirements

### 6.1 Mandatory Override Record

When a human operator overrides an agent recommendation, the following MUST be recorded in the audit trail (ANIF-724):

| Field | Type | Description |
|---|---|---|
| `override_id` | UUID v4 | Unique identifier for the override event |
| `operator_id` | string | Identity of the human operator |
| `agent_id` | string | Identity of the agent whose recommendation was overridden |
| `agent_recommendation` | object | The full agent recommendation as produced |
| `human_decision` | object | The decision the human made instead |
| `override_reason` | string | Free-text justification from the operator |
| `timestamp` | ISO 8601 | Time of the override |
| `intent_id` | UUID v4 | The intent associated with this recommendation |

The `override_reason` field MUST be completed by the operator. Systems MUST NOT permit override submission with an empty `override_reason`.

### 6.2 Override Frequency Reporting

Override frequency data MUST be aggregated and reported to the governance committee monthly (ANIF-837). The report MUST include:

- Total override count by agent
- Override count by role
- Most frequent override reasons (categorised)
- Agents with override rates exceeding 20% of their recommendations — these MUST be flagged for policy review

A sustained override rate above 20% for any agent indicates that the agent's policy bounds or decision logic are misaligned with operator intent and MUST trigger a policy review within 30 days.

---

## 7. Conformance Requirements

| ID | Requirement |
|---|---|
| CR-808-01 | A human operator MUST be able to override any agent recommendation at any time with immediate effect. |
| CR-808-02 | Technical implementations MUST NOT allow an agent to delay, dispute, or circumvent a human override. |
| CR-808-03 | When a human overrides an agent recommendation, the event MUST be logged with all fields defined in section 6.1. |
| CR-808-04 | Override submission MUST be blocked if `override_reason` is empty. |
| CR-808-05 | Override frequency data MUST be reported to the governance committee monthly. |
| CR-808-06 | Agents with override rates exceeding 20% of recommendations MUST be flagged for policy review. |
| CR-808-07 | Agent authority MUST NOT exceed the bounds defined in the role tables in section 5. |
| CR-808-08 | Human-authority boundaries MUST NOT be relaxed without governance committee approval per ANIF-830. |

---

## 8. Security Considerations

The override mechanism is a critical control surface. An attacker who can suppress override events, delay override execution, or forge override records can effectively remove human authority from the system. Override logging records MUST be treated with the same integrity protections as ethics audit trail records (ANIF-724) — they MUST be write-once and tamper-evident.

---

## 9. Operational Considerations

Override frequency metrics are a leading indicator of policy alignment. Operations teams SHOULD review override patterns quarterly rather than waiting for the threshold-based alert. Patterns that do not breach the 20% threshold but cluster around specific agent recommendations or shift conditions indicate policy gaps that are better resolved proactively.

Human operators SHOULD be trained on the authority boundaries defined in section 5 before being given access to agent management interfaces. Role confusion — where a human defers to agent recommendations in areas where they retain authority — is as much a risk as agents exceeding their bounds.
