# ANIF-848: Security Testing and Penetration Testing

| Field        | Value                                              |
|--------------|----------------------------------------------------|
| Doc ID       | ANIF-848                                           |
| Series       | AI Security                                        |
| Version      | 0.1.0                                              |
| Status       | Draft                                              |
| Authors      | ANIF Working Group                                 |
| Reviewers    | —                                                  |
| Approved by  | —                                                  |
| Created      | 2026-04-08                                         |
| Last updated | 2026-04-08                                         |
| Replaces     | N/A                                                |
| Related docs | ANIF-820, ANIF-841, ANIF-847, ANIF-903             |

---

## Abstract

This document defines the mandatory security testing cadence for ANIF-conformant deployments. Prompt injection tests MUST be conducted quarterly. Adversarial input testing MUST be conducted before every new agent deployment and after every model version change. Full penetration testing MUST be conducted annually. Red-team scope MUST include council manipulation attempts, ethics gate bypass attempts, and governance abuse scenarios. Critical findings from red-team or penetration testing MUST be resolved before any autonomy expansion. Red-team reports MUST be retained for three years.

---

## 1. Introduction

### 1.1 Purpose

ANIF-820 defines agent-level testing before deployment. This document defines the ongoing infrastructure and system-level security testing programme that continues throughout the operational lifetime of the deployment.

### 1.2 Scope

Mandatory testing cadence, red-team scope requirements, critical finding resolution requirements, and report retention.

### 1.3 Out of Scope

Agent pre-deployment testing types (see ANIF-820), ethics gate testing (covered within ANIF-820 red-team), and functional testing.

### 1.4 Intended Audience

- Security engineers planning and executing security testing
- Build-time council members reviewing test findings
- Governance committee members approving autonomy expansions
- Conformance assessors verifying security testing compliance

---

## 2. Normative References

| Reference | Title |
|---|---|
| ANIF-820 | AI Agent Testing and Red-Team Standards |
| ANIF-841 | AI Threat Model |
| ANIF-843 | Agent Zero Trust and Authentication |
| ANIF-847 | AI Security Incident Response |
| ANIF-903 | Build-Time Council |
| RFC 2119 | Key words for use in RFCs to Indicate Requirement Levels |

---

## 3. Quarterly Prompt Injection Testing

### 3.1 Requirement

Prompt injection tests MUST be conducted quarterly against the full deployed agent set. These tests supplement the pre-deployment testing of ANIF-820 by verifying that the operational injection defence remains effective as the threat landscape evolves and as agents evolve.

### 3.2 Scope

Quarterly injection tests MUST cover:

- All four injection attack types (ANIF-842): direct, indirect, jailbreak, and role confusion
- All external intent sources active in the deployment
- All external data sources inserted into agent context (ITSM, CMDB, monitoring)

### 3.3 Pass Criteria

All injection test cases MUST be blocked by the defence layers and logged as security events. Any test case that reaches the pipeline undetected is a critical finding.

---

## 4. Pre-Deployment and Post-Change Adversarial Input Testing

### 4.1 Requirement

Adversarial input testing MUST be conducted:

- Before every new agent type is deployed to production
- After every model version change for an existing agent
- After any change to the intent validation pipeline

### 4.2 Scope

Testing MUST cover the adversarial input test cases defined in ANIF-820 section 5, updated to reflect current deployment configuration (specific device IDs, intent types, and boundary values in use).

---

## 5. Annual Penetration Testing

### 5.1 Requirement

A full penetration test of the ANIF deployment MUST be conducted annually by a qualified external party. Annual penetration testing is separate from the red-team engagement defined in section 6.

### 5.2 Scope

The penetration test MUST cover:

- API gateway authentication and authorisation
- Message bus access controls and replay prevention
- Container escape opportunities
- Certificate management weaknesses
- Secrets management exposure
- Audit trail tampering

### 5.3 Finding Resolution

Critical findings (CVSS ≥ 9.0) MUST be resolved within 30 days. High findings (CVSS 7.0–8.9) MUST be resolved within 60 days. Open critical findings beyond 30 days MUST be reported to the governance committee.

---

## 6. Annual Red-Team Engagement

### 6.1 Requirement

An annual red-team engagement MUST be conducted by an authorised security team, as defined in ANIF-820 section 8. The infrastructure red-team augments the agent-level red-team by targeting governance structures and operational processes.

### 6.2 Mandatory Red-Team Scenarios

The infrastructure red-team MUST attempt at minimum:

| Scenario | Description |
|---|---|
| Council manipulation | Attempt to coordinate or impersonate governance committee or AI Council members to direct policy or decision outcomes |
| Ethics gate bypass | Attempt to bypass ethics evaluation through API manipulation, timing attacks, or permission escalation |
| Governance abuse | Attempt to invoke the emergency fast-track policy process without genuine emergency conditions |
| Audit suppression | Attempt to prevent security events from being written to the audit trail |
| Supply chain infiltration | Attempt to introduce a modified model or container image into the approved registry |

### 6.3 Critical Finding Resolution Requirement

Critical findings from red-team engagements MUST be resolved before any expansion of AI autonomy (Phase 3 step expansion or L5 claim). Unresolved Critical findings are a disqualifying condition for autonomy expansion regardless of business urgency.

---

## 7. Report Retention

All security test reports — prompt injection quarterly results, adversarial input test reports, penetration test reports, and red-team reports — MUST be retained for a minimum of three years. Reports MUST be available to the build-time council, governance committee, and external auditors during the retention period.

---

## 8. Testing Environment Requirements

All security testing MUST be conducted in a dedicated test environment that:

- Replicates the production architecture without using production network data
- Uses synthetic or anonymised network topology data
- Is isolated from production systems

Red-team engagements and penetration tests MUST NOT be conducted against production systems unless explicitly approved by the governance committee with documented risk acceptance.

---

## 9. Conformance Requirements

| ID | Requirement |
|---|---|
| CR-848-01 | Prompt injection testing MUST be conducted quarterly. |
| CR-848-02 | Adversarial input testing MUST be conducted before every new agent deployment and after every model version change. |
| CR-848-03 | Annual penetration testing MUST be conducted by a qualified external party. |
| CR-848-04 | Annual red-team engagements MUST cover all five mandatory scenarios in section 6.2. |
| CR-848-05 | Critical red-team findings MUST be resolved before any autonomy expansion. |
| CR-848-06 | Security testing reports MUST be retained for a minimum of three years. |

---

## 10. Security Considerations

Test reports describe the deployment's known vulnerabilities and testing methodology. Reports from red-team engagements that were not fully successful still provide an attacker with information about what was tested and how. Test reports MUST be classified as highly confidential and access restricted to the security team, build-time council, governance committee, and auditors.

---

## 11. Operational Considerations

Annual testing schedules MUST be planned and budgeted at the start of each financial year. Security testing capacity — both internal and external — must be secured in advance. Organisations that defer annual penetration testing due to "operational windows" invariably find that the deferral becomes indefinite.
