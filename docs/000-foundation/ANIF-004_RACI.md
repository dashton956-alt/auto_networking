# ANIF-004: Roles, Responsibilities and RACI

| Field        | Value                                    |
|--------------|------------------------------------------|
| Doc ID       | ANIF-004                                 |
| Series       | Foundation                               |
| Version      | 0.1.0                                    |
| Status       | Draft                                    |
| Authors      | ANIF Working Group                       |
| Reviewers    | —                                        |
| Approved by  | —                                        |
| Created      | 2026-04-07                               |
| Last updated | 2026-04-07                               |
| Replaces     | N/A                                      |
| Related docs | ANIF-001, ANIF-100, ANIF-404, ANIF-406   |

---

## Abstract

This document defines all roles within the ANIF ecosystem, their responsibilities, and the RACI (Responsible, Accountable, Consulted, Informed) matrix for all key activities in the ANIF pipeline and governance process. Role definitions in this document are normative: any ANIF-conformant implementation MUST enforce the responsibilities and permission boundaries described herein. The RACI matrix provides the authoritative assignment of accountability for every key activity from intent submission to framework governance.

---

## 1. Introduction

### 1.1 Purpose

Autonomous systems require clarity about who is responsible for each decision, action, and escalation. Without explicit role definitions and accountability assignments, autonomous operations create ambiguity about authority and responsibility — particularly when actions have unintended consequences. This document provides the normative role structure that ANIF implementations MUST enforce.

### 1.2 Scope

This document covers:

- Definitions and responsibilities for all ANIF roles (human and automated)
- Permission boundaries for each role
- The RACI matrix for all key ANIF activities
- Role assignment requirements and governance
- Escalation paths between roles

### 1.3 Out of Scope

- Organisation-specific job titles or HR classifications
- How organisations map their existing roles to ANIF roles
- Specific identity provider or authentication mechanism implementations
- Compensation, reporting lines, or non-technical organisational concerns

### 1.4 Intended Audience

- IT and network operations managers designing ANIF operating models
- Security and compliance teams establishing access controls
- Platform engineers implementing ANIF authentication and authorisation
- ANIF Working Group members governing framework documents

---

## 2. Normative References

- RFC 2119 — Key words for use in RFCs to indicate requirement levels
- ANIF-001 — Charter and Scope
- ANIF-002 — Framework Design Principles (P-05 Least Privilege, P-06 Human Override)
- ANIF-003 — Terms and Definitions
- ANIF-100 — Governance and Policy Model
- ANIF-404 — Action Execution Specification (referenced for executor role requirements)
- ANIF-406 — Incident Response Specification (referenced for incident role requirements)

---

## 3. Terms and Definitions

See ANIF-003 for the full glossary. Key terms used in this document:

| Term | Definition |
|---|---|
| Role | A named set of permissions and responsibilities assigned to a human operator or automation agent within the ANIF system |
| Permission | An authorised capability to perform a specific operation (e.g., submit intent, approve governance ticket, invoke rollback) |
| Capability Manifest | The versioned document that defines what action types an automation agent or action executor is permitted to perform |
| Governance Ticket | A work item in the governance queue requiring human review and approval before an action proceeds |
| Escalation | Routing an event or decision to a higher-authority role for resolution |
| RACI | Responsible, Accountable, Consulted, Informed — a matrix model for assigning roles to activities |

---

## 4. Role Definitions

### 4.1 Role Summary

The following table summarises all ANIF roles. Detailed definitions follow in Sections 4.2–4.8.

| Role ID | Role Name | Actor Type | Description |
|---|---|---|---|
| R-01 | Network Engineer | Human | Submits intents, reviews and approves standard governance tickets |
| R-02 | Senior Engineer | Human | Final approval authority for high-risk actions; override authority |
| R-03 | Automation Agent | Automated | Programmatic intent submission; no human review authority |
| R-04 | Policy Administrator | Human | Manages policy sets; approves policy change proposals |
| R-05 | Compliance Officer | Human | Audit log review; compliance queries; no action authority |
| R-06 | System Operator | Human | System health monitoring; adapter management; incident escalation |
| R-07 | ANIF Working Group | Human (collective) | Framework governance; document management; specification approval |

---

### 4.2 R-01: Network Engineer

**Description:**
The Network Engineer is the primary human role for day-to-day autonomous operations. Network Engineers interact with the ANIF system by submitting intents, monitoring pipeline status, and reviewing governance tickets routed to them for manual review.

**Responsibilities:**
- Submit intents to the ANIF pipeline via the intent submission API or approved tooling
- Monitor the status of submitted intents through the pipeline
- Review and action `manual_review` governance tickets assigned to their queue within defined SLA
- Approve or reject governance tickets for actions within their authority level (standard risk threshold)
- Respond to escalation notifications from the ANIF system
- Invoke rollback for actions within their authority level when instructed or when adverse outcomes are detected
- Review and acknowledge audit notifications for actions they have submitted or approved

**Permissions:**

| Permission | Granted | Notes |
|---|---|---|
| Submit intent | Yes | All intent types within their team scope |
| View intent status | Yes | Own intents and team intents |
| View governance queue | Yes | Tickets assigned to Network Engineer role |
| Approve governance ticket (standard risk) | Yes | Risk score below high-risk threshold (defined in ANIF-100) |
| Approve governance ticket (high risk) | No | Requires R-02 Senior Engineer |
| Override governance decision | No | Requires R-02 Senior Engineer |
| Invoke rollback (own actions) | Yes | For actions they submitted or approved |
| Invoke emergency halt | No | Requires R-02 Senior Engineer or R-06 System Operator |
| View audit records | Yes | Own and team audit records |
| Modify policy sets | No | Requires R-04 Policy Administrator |
| Manage adapters | No | Requires R-06 System Operator |

**Reporting and accountability:**
Network Engineers are accountable for intents they submit and governance tickets they approve. Approval of a governance ticket constitutes formal authorisation of the associated action. Network Engineers MUST NOT approve governance tickets for actions outside their team scope without explicit delegation from a Senior Engineer.

**Authority escalation:**
A Network Engineer MUST escalate to a Senior Engineer when:
- A governance ticket is classified as high risk
- An action has produced an unexpected outcome and rollback is insufficient
- A pattern of escalations suggests a systemic policy or configuration issue

---

### 4.3 R-02: Senior Engineer

**Description:**
The Senior Engineer holds final approval authority for high-risk actions and has the ability to override governance decisions. This role is the primary human override mechanism as required by P-06 (Human Override). Senior Engineer status MUST be granted only to individuals with demonstrated expertise and explicit organisational authority.

**Responsibilities:**
- Review and approve or reject governance tickets for high-risk actions
- Override governance decisions when operational circumstances require it (with mandatory logging and justification)
- Invoke the emergency halt mechanism to suspend all autonomous actions
- Authorise rollback of any action regardless of who submitted it
- Perform post-incident reviews of override actions and document outcomes
- Delegate authority to Network Engineers for specific time-bounded scenarios
- Participate in post-mortem analysis of incidents involving autonomous actions
- Review and sign off on new policy sets before they are activated in production

**Permissions:**

| Permission | Granted | Notes |
|---|---|---|
| All Network Engineer permissions | Yes | Senior Engineer is a superset of Network Engineer |
| Approve governance ticket (high risk) | Yes | All risk levels |
| Override governance decision | Yes | MUST be logged with mandatory justification field |
| Invoke emergency halt | Yes | Suspends all in-flight autonomous actions |
| Invoke rollback (any action) | Yes | Any action regardless of submitter |
| Delegate authority to Network Engineer | Yes | Time-bounded; recorded in audit log |
| View all audit records | Yes | Organisation-wide |
| Approve new policy set activation | Yes | Required before production activation |

**Override requirements:**
When a Senior Engineer invokes an override, the system MUST:
1. Record the override in the audit log with: engineer identity, timestamp, the decision being overridden, the justification provided, and the action taken.
2. Notify the Compliance Officer and relevant System Operator.
3. Create a post-action review ticket within 24 hours.

A Senior Engineer MUST NOT override a `block` decision for an action that violates a data residency constraint (P-11) without approval from the Compliance Officer.

---

### 4.4 R-03: Automation Agent

**Description:**
The Automation Agent is a non-human principal — a software process, pipeline runner, or bot — that submits intents to the ANIF pipeline programmatically. Automation Agents represent the primary source of intent volume in mature ANIF deployments. Every Automation Agent MUST be individually identified, authenticated, and assigned a capability manifest.

**Responsibilities:**
- Submit well-formed intents conforming to the ANIF Intent Schema
- Include all required context fields in submitted intents (including `data_residency` where applicable)
- Respond to pipeline feedback (e.g., validation errors) by correcting and resubmitting intents
- Operate within the action types defined in its capability manifest
- Not attempt to bypass the governance pipeline

**Permissions:**

| Permission | Granted | Notes |
|---|---|---|
| Submit intent | Yes | Only action types in capability manifest |
| View own intent status | Yes | Intents submitted by this agent |
| View governance queue | No | Human review is not an Automation Agent function |
| Approve governance ticket | No | Automation Agents MUST NOT approve their own actions |
| Invoke rollback | No | Rollback initiation requires human authority |
| View audit records | No | Audit access requires Compliance Officer role |
| Any human review or approval action | No | Strictly prohibited |

**Registration requirements:**
An Automation Agent MUST be registered in the ANIF system before it can submit intents. Registration requires:
1. A unique agent identity (e.g., service account identifier)
2. A signed capability manifest, approved by a Policy Administrator
3. Authentication credentials (certificate or token) issued by the organisation's identity provider
4. Assignment of the `automation_agent` role

**Capability manifest governance:**
An Automation Agent's capability manifest MUST be reviewed by a Policy Administrator before the agent is activated. Changes to a capability manifest MUST follow the policy lifecycle (version increment, approval, audit record). An agent MUST operate within its current, approved capability manifest. Requests for expanded capabilities MUST be submitted as governance tickets for Policy Administrator review.

**Trust score:**
Automation Agents are assigned a Trust Score based on their operational history (action outcomes, error rates, policy compliance). Trust Scores are evaluated by the Policy Engine and may affect governance mode assignments. An agent with a low Trust Score MAY have otherwise `auto` actions routed to `manual_review`.

---

### 4.5 R-04: Policy Administrator

**Description:**
The Policy Administrator is responsible for the full lifecycle of ANIF policy sets — creation, versioning, activation, and retirement. The Policy Administrator is the gatekeeper for all changes to the policy store, including policy proposals from the continuous learning feedback loop.

**Responsibilities:**
- Create, version, and manage policy sets in the ANIF policy store
- Review and resolve policy conflicts identified during policy evaluation
- Review policy change proposals submitted by the learning feedback loop
- Accept or reject feedback-derived policy proposals via the governance ticket process
- Ensure all active policy sets are consistent, non-conflicting, and have current test coverage
- Maintain the capability manifest registry for all registered Automation Agents
- Coordinate with Senior Engineers on policy set activation for production
- Ensure policy sets satisfy applicable data residency (P-11) and compliance requirements

**Permissions:**

| Permission | Granted | Notes |
|---|---|---|
| Create policy set | Yes | Draft state only; requires Senior Engineer approval for production |
| Update policy set | Yes | Increments version; requires test suite update |
| Activate policy set | Yes | Only after Senior Engineer sign-off |
| Retire policy set | Yes | With audit record |
| Manage capability manifests | Yes | Create, update, approve |
| Review learning proposals | Yes | Approve or reject via governance ticket |
| View all audit records | Yes | Read-only |
| Submit intents | No | Policy Administrators do not submit operational intents |
| Approve action governance tickets | No | Policy Administrators govern policy, not operational actions |
| Override governance decisions | No | Requires Senior Engineer |

**Policy lifecycle requirements:**
Every policy set change MUST:
1. Increment the policy set version number.
2. Include an updated or new test case covering the changed rule.
3. Be reviewed by a second Policy Administrator (four-eyes principle) for changes to high-impact policies.
4. Produce an audit record.

---

### 4.6 R-05: Compliance Officer

**Description:**
The Compliance Officer has read-only access to the ANIF audit trail for regulatory review, compliance assessment, and forensic investigation purposes. The Compliance Officer does not have operational authority over actions, policies, or governance decisions, but MUST be consulted before Senior Engineers override data residency or compliance-related `block` decisions.

**Responsibilities:**
- Review audit logs for compliance with regulatory requirements
- Query `/audit` and `/audit/{id}/why` endpoints for investigations
- Assess ANIF conformance posture against applicable regulations
- Review and provide input on data residency policy configurations
- Be consulted by Senior Engineers before overriding data residency `block` decisions
- Provide compliance sign-off for new policy sets that affect regulated data or jurisdictions
- Participate in post-incident reviews for compliance-relevant events

**Permissions:**

| Permission | Granted | Notes |
|---|---|---|
| View all audit records | Yes | Full read access; no write or delete |
| Query `/audit` endpoint | Yes | All filters available |
| Query `/audit/{id}/why` endpoint | Yes | For any audit record within retention period |
| View governance tickets | Yes | Read-only; for compliance review |
| View policy sets | Yes | Read-only |
| Submit intents | No | |
| Approve governance tickets | No | |
| Modify policy sets | No | |
| Override governance decisions | No | |
| Invoke rollback or halt | No | |

**Data access controls:**
Audit records containing PII or sensitive regulated data MUST be accessible to the Compliance Officer only via the API (not direct database access). The Compliance Officer's access to audit records MUST itself be logged.

---

### 4.7 R-06: System Operator

**Description:**
The System Operator is responsible for the operational health of the ANIF platform itself — not the network actions it takes, but the system's availability, adapter health, and incident response. System Operators are the first responders to platform-level incidents and have the authority to invoke the emergency halt if the system is behaving unexpectedly.

**Responsibilities:**
- Monitor ANIF system health dashboards and alerting
- Manage adapter configurations and lifecycle (deploy, update, retire adapters)
- Investigate and escalate platform-level incidents
- Invoke emergency halt if autonomous actions are producing unexpected or harmful outcomes at scale
- Ensure audit store availability and integrity monitoring
- Manage system configuration parameters (not policy content)
- Coordinate with Network Engineers and Senior Engineers during operational incidents
- Maintain the ANIF deployment and upgrade runbooks

**Permissions:**

| Permission | Granted | Notes |
|---|---|---|
| View system health APIs | Yes | Full access |
| Manage adapters | Yes | Deploy, configure, retire |
| Invoke emergency halt | Yes | System-level authority |
| View all audit records | Yes | For incident investigation (read-only) |
| View all governance tickets | Yes | For situational awareness during incidents |
| Submit intents | No | System Operators manage the platform, not network actions |
| Approve governance tickets | No | |
| Override governance decisions | No | Requires Senior Engineer |
| Modify policy sets | No | Requires Policy Administrator |

**Emergency halt authority:**
The System Operator's emergency halt authority is granted specifically for scenarios where the ANIF platform itself is malfunctioning (e.g., a bug causing incorrect governance mode assignments, or an adapter producing malformed actions). System Operators MUST NOT use emergency halt as a substitute for governance ticket rejection for individual operational decisions.

---

### 4.8 R-07: ANIF Working Group

**Description:**
The ANIF Working Group (WG) is the collective governing body for all ANIF framework documents. The WG does not have operational authority within an ANIF deployment — its authority is over the specification itself. The WG operates according to the governance rules in ANIF-001.

**Responsibilities:**
- Govern all ANIF normative documents (series 000–500)
- Assign ANIF document IDs and track document lifecycle states
- Review, debate, and vote on specification changes
- Approve new document series and conformance level changes
- Maintain the public ANIF document repository
- Manage the CLA process for contributors
- Publish WG meeting minutes within 14 days of each meeting

**Authority:**
The WG's authority is limited to the ANIF specification. It does not govern deployments or implementations. Implementing organisations are responsible for their own operational governance.

---

## 5. RACI Matrix

The RACI matrix below assigns each role a designation for each key ANIF activity:

- **R** — Responsible: Does the work
- **A** — Accountable: Owns the outcome; the person who answers for whether the activity is done correctly (only one A per activity)
- **C** — Consulted: Provides input before or during the activity
- **I** — Informed: Notified of the outcome

### 5.1 Key to Role Abbreviations

| Abbreviation | Role |
|---|---|
| NE | R-01 Network Engineer |
| SE | R-02 Senior Engineer |
| AA | R-03 Automation Agent |
| PA | R-04 Policy Administrator |
| CO | R-05 Compliance Officer |
| SO | R-06 System Operator |
| WG | R-07 ANIF Working Group |

### 5.2 RACI Matrix

| Activity | NE | SE | AA | PA | CO | SO | WG | Notes |
|---|---|---|---|---|---|---|---|---|
| **Intent submission (human)** | R/A | C | — | — | — | I | — | NE is both responsible and accountable for their own submissions |
| **Intent submission (automated)** | — | I | R/A | — | — | I | — | AA is responsible; accountable for its own submissions |
| **Intent validation** | I | I | I | — | — | I | — | Automated pipeline stage; no human actor is R or A |
| **Policy evaluation** | I | I | I | C | — | I | — | Automated; PA consulted on rule interpretation disputes |
| **Risk scoring** | I | I | I | C | — | I | — | Automated; PA consulted on scoring model questions |
| **Governance gate decision** | I | I | I | — | — | I | — | Automated; no human actor is R or A |
| **Governance ticket review (standard risk)** | R/A | I | — | — | — | I | — | NE is accountable for approvals within their authority |
| **Governance ticket review (high risk)** | C | R/A | — | C | C | I | — | SE is accountable; NE and PA consulted; CO consulted if compliance-relevant |
| **Governance decision override** | — | R/A | — | C | C | I | — | SE accountable; override MUST be justified and logged |
| **Action execution** | I | I | I | — | — | I | — | Automated pipeline stage |
| **Rollback initiation (own action)** | R | A | — | — | — | I | — | NE responsible for own rollback; SE accountable |
| **Rollback initiation (any action)** | — | R/A | — | — | — | I | — | SE has authority for any action rollback |
| **Emergency halt** | — | R/A | — | — | — | R | — | SE and SO both have R; SE is A |
| **Audit record creation** | — | — | — | — | — | — | — | Automated; no human actor |
| **Audit log review** | — | I | — | — | R/A | I | — | CO is accountable for compliance audit review |
| **Policy set creation and update** | C | C | — | R/A | C | — | — | PA accountable; SE and CO consulted for significant changes |
| **Policy set activation (production)** | — | A | — | R | C | — | — | PA responsible for preparation; SE accountable for go/no-go |
| **Capability manifest management** | C | C | — | R/A | — | — | — | PA accountable for manifest governance |
| **Policy tuning (manual)** | C | C | — | R/A | C | — | — | PA accountable; CO consulted on compliance impact |
| **Learning proposal review** | — | I | — | R/A | C | — | — | PA accountable for accepting/rejecting proposals |
| **Adapter deployment** | — | C | — | — | — | R/A | — | SO accountable for adapter lifecycle |
| **Adapter configuration** | C | C | — | — | — | R/A | — | SO accountable; NE and SE consulted |
| **Incident response (platform)** | I | C | — | — | — | R/A | — | SO leads platform incidents; SE consulted |
| **Incident response (action outcome)** | R | A | — | C | I | I | — | NE leads remediation; SE accountable; PA consulted on policy implications |
| **Post-incident review** | R | A | — | C | C | C | — | SE accountable; all relevant roles contribute |
| **Automation agent registration** | — | C | — | R/A | — | — | — | PA accountable for agent onboarding |
| **Trust score monitoring** | I | I | — | R/A | — | I | — | PA responsible for trust score governance |
| **Framework document authoring** | — | — | — | — | — | — | R/A | WG accountable for all specification content |
| **Document ID assignment** | — | — | — | — | — | — | R/A | WG accountable |
| **Specification change approval** | — | — | — | — | — | — | R/A | WG accountable per ANIF-001 governance rules |
| **Conformance test development** | C | C | — | C | — | — | R/A | WG accountable; operational roles consulted |
| **Charter amendment** | — | — | — | — | — | — | R/A | WG accountable; supermajority vote required |

---

## 6. Escalation Paths

The following table defines the required escalation paths between roles:

| Trigger | From Role | To Role | SLA | Notes |
|---|---|---|---|---|
| High-risk governance ticket | System (auto-route) | R-02 Senior Engineer | Defined in ANIF-100 | System routes automatically based on risk threshold |
| NE approves ticket outside authority | R-01 Network Engineer | R-02 Senior Engineer | Immediate | NE MUST escalate if uncertain about authority level |
| Data residency `block` override request | R-02 Senior Engineer | R-05 Compliance Officer | Before override | SE MUST obtain CO sign-off |
| Platform incident affecting > N actions | R-06 System Operator | R-02 Senior Engineer | 15 minutes | N defined in deployment-specific SLA |
| Policy conflict detected | R-04 Policy Administrator | R-02 Senior Engineer | 1 business day | For conflicts affecting production policy |
| Audit anomaly detected | R-05 Compliance Officer | R-02 Senior Engineer | Per regulatory requirement | CO initiates investigation; SE has operational authority |
| Agent trust score falls below threshold | System (auto-route) | R-04 Policy Administrator | 4 hours | PA reviews agent behaviour |
| Learning proposal with significant policy impact | System (auto-route) | R-04 Policy Administrator + R-02 Senior Engineer | 1 business day | Both roles MUST review jointly |

---

## 7. Conformance Requirements

An ANIF-conformant implementation MUST:

1. Implement all seven roles defined in Section 4 (R-01 through R-07) as distinct, enforceable access control groups.
2. Enforce the permission boundaries defined for each role. No role MUST have permissions beyond those specified in this document without explicit policy justification reviewed by a Policy Administrator.
3. Enforce the principle that Automation Agents (R-03) MUST NOT be granted any human review or approval permissions.
4. Implement the RACI assignments in Section 5.2 such that accountability (A) designations are enforced — only accountable roles can formally approve, authorise, or override activities assigned to them.
5. Log all role-based permission checks as audit records.
6. Implement the escalation paths defined in Section 6 with at minimum alerting mechanisms for each trigger condition.
7. Maintain a current role assignment register (who holds each role) accessible to Senior Engineers and Compliance Officers.

---

## 8. Security Considerations

- Role assignments MUST be protected by the organisation's identity and access management system. Role changes MUST be audited.
- The Senior Engineer override capability (R-02) is a high-value target. Access to this role MUST be governed by strong authentication (MFA at minimum) and SHOULD be reviewed quarterly.
- Automation Agent credentials (R-03) MUST be rotated on a schedule defined by the organisation's security policy. Credential rotation MUST not require changes to the capability manifest.
- Segregation of duties MUST be enforced: the same individual MUST NOT hold both the R-03 Automation Agent identity for a specific agent and the R-02 Senior Engineer role that would approve that agent's high-risk actions.
- The Compliance Officer role (R-05) MUST be assigned to an individual with no operational action authority, to maintain the independence of compliance review.

---

## 9. Operational Considerations

- Role assignments SHOULD be reviewed at minimum annually and whenever an individual changes job function.
- Organisations with small teams MAY assign multiple roles to one individual, subject to the segregation of duties constraint in Section 8.
- Temporary role grants (e.g., for incident response) MUST be time-bounded and MUST produce an audit record. All temporary grants MUST expire automatically.
- The role assignment register MUST be available to on-call engineers during incident response so that escalation paths can be executed without delay.
- Organisations SHOULD conduct tabletop exercises for high-severity scenarios (e.g., emergency halt, mass rollback) to verify that role holders can execute their responsibilities under pressure.

---

## Appendix A: Examples

### A.1 Intent Submission and Governance Flow

**Scenario**: An Automation Agent (R-03) submits an intent to reconfigure BGP policy on 12 edge routers. The risk scoring engine returns a score of 0.72. The organisation's high-risk threshold is 0.70.

**Flow**:
1. AA submits intent — R-03 is Responsible and Accountable for submission quality.
2. Intent Validator, Policy Engine, Risk Scorer execute — automated pipeline stages.
3. Governance Gate produces `manual_review` at risk 0.72 — ticket created.
4. Ticket is classified as high-risk — auto-routed to R-02 Senior Engineer queue.
5. NE (R-01) is Consulted (may provide operational context) but MUST NOT approve.
6. SE (R-02) reviews the reasoning chain, consults with NE if needed, and approves or rejects.
7. If approved: Action Executor proceeds; SE is Accountable for the approval decision.
8. Audit record created for every step; CO (R-05) can review at any time.

### A.2 Emergency Halt Scenario

**Scenario**: The System Operator (R-06) notices that the ANIF action executor is producing malformed configurations due to an adapter bug. 47 actions have been queued.

**Flow**:
1. SO (R-06) invokes emergency halt — all 47 queued actions are suspended.
2. SO notifies SE (R-02) immediately per the escalation path in Section 6.
3. SE (R-02) is Accountable for the response decision.
4. SO (R-06) investigates the adapter issue and proposes a fix.
5. SE (R-02) and PA (R-04) review the fix (if policy implications exist).
6. SE (R-02) authorises re-enabling the pipeline after the fix is validated.
7. All halt, investigation, and re-enable events are recorded in the audit log.
8. CO (R-05) is Informed; will review audit log.
9. Post-incident review conducted within 48 hours.

### A.3 Policy Change from Learning Feedback

**Scenario**: The continuous learning system proposes lowering the risk weight for "BGP policy reconfiguration on maintenance-window intents" based on 90 days of consistently successful outcomes.

**Flow**:
1. System creates a governance ticket for the proposal — automatically assigned to R-04 Policy Administrator.
2. PA reviews the evidence (outcome data, current risk weight, proposed weight).
3. PA consults SE (R-02) because the change affects high-risk threshold routing.
4. CO (R-05) is consulted because BGP changes may have compliance implications in regulated environments.
5. PA approves the proposal and creates a new version of the affected policy set.
6. SE (R-02) signs off on production activation.
7. PA activates the updated policy set — audit record created.
8. All WG members are Informed of significant policy changes via the change log.

---

## Appendix B: Change History

| Version | Date | Author | Changes |
|---|---|---|---|
| 0.1.0 | 2026-04-07 | ANIF Working Group | Initial draft |
