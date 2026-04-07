# ANIF-801: Agent Types, Roles & Human Counterparts

| Field        | Value                                              |
|--------------|----------------------------------------------------|
| Doc ID       | ANIF-801                                           |
| Series       | AI Agent Architecture                              |
| Version      | 0.1.0                                              |
| Status       | Draft                                              |
| Authors      | ANIF Working Group                                 |
| Reviewers    | —                                                  |
| Approved by  | —                                                  |
| Created      | 2026-04-07                                         |
| Last updated | 2026-04-07                                         |
| Replaces     | N/A                                                |
| Related docs | ANIF-800, ANIF-802, ANIF-808, ANIF-004             |

---

## Abstract

This document defines the complete catalogue of AI agent roles across all four tiers. Every agent role maps to a human counterpart. The human retains authority; the agent extends human capacity. No agent role exists without a corresponding human role — autonomous agents augment human teams, they do not replace them. Every deployed agent MUST be assigned exactly one role from this catalogue.

---

## 1. Introduction

### 1.1 Purpose

Role clarity prevents scope creep. An agent with an undefined role has undefined boundaries. An agent whose role is precisely defined — with a named human counterpart, a primary responsibility, and a clear scope — can be evaluated for appropriate capability, risk, and governance requirements during build-time council review.

### 1.2 Scope

This document covers:

- The complete role catalogue for all four tiers
- The human counterpart for each role
- The primary responsibility of each role
- The scope boundary: what the role covers and what it does not
- The human authority principle

### 1.3 Out of Scope

This document does not cover:

- Permissions granted to each role (see ANIF-802)
- How human and agent collaborate in practice (see ANIF-808)
- Agent lifecycle for each role (see ANIF-803)
- The communication paths between roles (see ANIF-804)

### 1.4 Intended Audience

- AI engineers building agents for specific roles
- Human operators understanding how their role relates to AI agents
- Build-time council members reviewing role-appropriateness of agent proposals
- HR and organisational design teams mapping AI roles to human roles

---

## 2. Normative References

- ANIF-800 — Agent Architecture Overview
- ANIF-004 — Roles and RACI
- ANIF-802 — Agent Capabilities and Permissions
- ANIF-808 — Human-Agent Collaboration Model
- RFC 2119 — Key words for use in RFCs to indicate requirement levels

---

## 3. Human Authority Principle

For every role in this catalogue, the human counterpart retains final authority. The agent extends the human's capacity — it does not replace the human's judgement or accountability.

Where an agent and its human counterpart reach different conclusions, the human's decision prevails. The human's override MUST be logged with the operator's identity, the agent's recommendation, the human's decision, and the reason for the override.

The frequency of overrides is a governance metric (ANIF-837). A high override rate indicates the agent's recommendations are not aligned with operator judgement and warrants investigation. A zero override rate over an extended period may indicate operators are not adequately reviewing agent recommendations.

---

## 4. Tier 0 — Management and Orchestration Roles

Tier 0 agents coordinate other agents and humans. They have no direct network access. They submit intents to the pipeline and manage the agent pool.

| Role | Human Counterpart | Primary Responsibility |
|---|---|---|
| NOC Manager Agent | NOC Manager / Shift Lead | Coordinates operational response across all agent tiers. Prioritises and queues intents. Escalates to human when automated response is insufficient |
| Change Manager Agent | Change Manager | Manages the change lifecycle from intent submission through execution and post-implementation review. Enforces change windows |
| Problem Manager Agent | Problem Manager | Tracks recurring incidents, identifies root causes, and coordinates resolution across operational agents |
| Project Manager Agent | Project Manager | Tracks network project delivery, flags timeline risks, and coordinates dependencies between project tasks and operational changes |
| Service Manager Agent | Service Manager / Service Owner | Monitors service health against SLA commitments. Coordinates recovery actions when service KPIs breach thresholds |
| Vendor Manager Agent | Vendor Manager | Tracks vendor-specific device health, firmware versions, and support contract status. Flags vendor-related risks |
| Configuration Manager Agent | Configuration Manager | Maintains configuration baseline accuracy. Detects configuration drift. Coordinates remediation |
| Knowledge Manager Agent | Knowledge Manager | Curates the operational knowledge base. Routes knowledge queries to relevant agents. Manages knowledge package approval workflow |
| Escalation Coordinator Agent | Escalation Manager / On-call Lead | Manages escalation paths when agents or automated processes cannot resolve an issue. Ensures the right human is engaged |
| Learning Agent | Knowledge Engineer / ML Engineer | Network knowledge broker. Collects lessons from incidents, problems, and changes. Routes approved knowledge updates to relevant agents |
| Intent Manager Agent | Intent Engineer | Manages the intent lifecycle across the pipeline. Detects intent conflicts. Flags quality issues with external intent sources |
| Agent Pool Controller | Platform Engineer / SRE | Manages agent instance counts, health, and resource allocation. Scales agent pool up or down within approved bounds |

---

## 5. Tier 1 — Monitor Roles

Tier 1 agents observe and report. They have read-only access to telemetry and canonical state. They publish observations to the observation bus.

| Role | Human Counterpart | Primary Responsibility |
|---|---|---|
| Network Observer | Network Analyst | Continuously monitors network telemetry for anomalies, performance degradation, and capacity trends. Publishes observations to Tier 2 advisors |
| Security Sentinel | Security Analyst | Monitors for security events: unauthorised access attempts, unusual traffic patterns, policy violations, and indicators of compromise |
| Compliance Watcher | Compliance Analyst | Monitors for compliance drift: configurations inconsistent with declared policy, data residency violations, audit trail gaps |
| Capacity Monitor | Capacity Planner | Tracks capacity utilisation trends across all segments. Flags segments approaching capacity thresholds before they breach |
| Service Health Monitor | Service Desk Analyst | Tracks service health metrics against SLA commitments in real time. Publishes health degradation signals before SLA breach |
| Ethics Sentinel | AI Ethics Officer | Monitors AI agent behaviour for ethics drift: bias signals, anomalous confidence patterns, unusual governance gate firing rates |

---

## 6. Tier 2 — Advisor Roles

Tier 2 agents reason and recommend. They may use LLM components. They publish recommendations to the recommendation bus. Their outputs are advisory until accepted by Tier 3.

| Role | Human Counterpart | Primary Responsibility |
|---|---|---|
| Intent Interpreter | Intent Engineer | Interprets ambiguous or underspecified intents. Produces clarified, validated intent proposals. Flags intents that cannot be interpreted without human input |
| Network Design Advisor | Network Architect | Produces network design recommendations given a set of constraints and objectives. Evaluates design alternatives against policy and risk criteria |
| Security Advisor | Security Architect | Analyses security implications of proposed changes. Recommends security-preserving alternatives when proposed actions introduce risk |
| Routing Advisor | Network Engineer (Routing) | Produces routing optimisation recommendations. Evaluates traffic engineering options against performance and policy constraints |
| Automation Advisor | Automation Engineer | Recommends automation strategies for recurring operational patterns. Identifies candidates for intent-based automation |
| Risk Analyst | Risk Manager | Produces risk assessments for proposed actions beyond the automated risk scoring. Provides nuanced risk analysis for complex or novel scenarios |
| Policy Advisor | Policy Architect | Advises on policy configuration. Identifies policy gaps and conflicts. Recommends policy updates when operational patterns expose coverage gaps |
| Incident Analyst | Incident Manager | Analyses active incidents: likely cause, blast radius, recommended response. Provides context to Tier 3 agents responding to incidents |
| Change Advisor | Change Analyst | Advises on change risk, sequencing, and rollback strategy. Reviews proposed changes against change calendar and freeze windows |
| Intent Engineer Agent | Intent Engineer | Analyses intent quality metrics from external sources. Produces correction templates for high-failure-rate intent sources. Recommends intent schema improvements |

---

## 7. Tier 3 — Decision Roles

Tier 3 agents select and execute bounded actions through the full pipeline containment contract. These are the most constrained roles in the architecture.

| Role | Human Counterpart | Primary Responsibility |
|---|---|---|
| Action Selector | Network Operations Engineer | Selects the appropriate bounded action (from the four-action enum) to address the current intent. Operates through the full ANIF pipeline |
| Rollback Coordinator | Change Manager / Operations Engineer | Executes rollback actions when a change produces adverse outcomes. Ensures rollback completes within the declared SLA |
| Incident Responder | Incident Response Engineer | Executes bounded actions in response to active network incidents. Operates under enhanced governance scrutiny due to time pressure |
| Provisioning Agent | Network Provisioning Engineer | Executes bounded provisioning actions for new service onboarding and capacity changes within declared policy bounds |

---

## 8. Role Assignment Rules

### 8.1 One Role Per Agent

Every deployed agent MUST be assigned exactly one role from this catalogue. An agent with multiple roles has an ambiguous scope that complicates build-time council review, governance reporting, and accountability chain reconstruction.

### 8.2 Role Determines Tier

The role assignment determines the agent's tier. An agent assigned as a Network Observer is a Tier 1 agent and MUST be deployed with Tier 1 credentials and capabilities. An agent that claims a Tier 2 role (Intent Interpreter) but requests Tier 3 execution endpoints at runtime is a reach-up attempt (ANIF-800 section 5.3).

### 8.3 New Roles

Roles not in this catalogue MUST be proposed to the ANIF Working Group and reviewed by the AI Ethics Officer before deployment. An agent deployed with an undeclared role has an undefined scope and MUST NOT be approved by the build-time council.

---

## 9. Conformance Requirements

Every deployed agent MUST be assigned exactly one role from this catalogue.

An agent MUST NOT be deployed without a declared role in its signed manifest.

The human counterpart for every deployed agent MUST be identified and their identity resolvable in the organisation's IAM system.

---

## 10. Security Considerations

Role clarity is a security control. An agent with a precisely defined role has a bounded scope of legitimate action. When an agent acts outside its role scope, that action is detectable as anomalous. An agent whose role is undefined has no anomaly baseline.

---

## 11. Operational Considerations

Human counterpart roles SHOULD be briefed on the capabilities and limitations of their corresponding AI agents during agent deployment. Operators who do not understand what their AI counterpart can and cannot do are less able to exercise appropriate oversight and override when needed.

---

## Appendix A: Change History

| Version | Date | Author | Changes |
|---|---|---|---|
| 0.1.0 | 2026-04-07 | ANIF Working Group | Initial draft |
