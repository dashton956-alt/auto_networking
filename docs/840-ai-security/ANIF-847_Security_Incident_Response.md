# ANIF-847: AI Security Incident Response

| Field        | Value                                              |
|--------------|----------------------------------------------------|
| Doc ID       | ANIF-847                                           |
| Series       | AI Security                                        |
| Version      | 0.1.0                                              |
| Status       | Draft                                              |
| Authors      | ANIF Working Group                                 |
| Reviewers    | —                                                  |
| Approved by  | —                                                  |
| Created      | 2026-04-08                                         |
| Last updated | 2026-04-08                                         |
| Replaces     | N/A                                                |
| Related docs | ANIF-819, ANIF-841, ANIF-846, ANIF-724             |

---

## Abstract

This document defines the four-level AI security incident classification and the normative response requirements for each level. Level 1 is suspicious activity requiring investigation. Level 2 is a confirmed security event requiring agent isolation. Level 3 is an active incident requiring full manual operation per ANIF-819 Level 4 and governance notification. Level 4 is a critical infrastructure attack requiring all Level 3 actions plus regulatory notification within required timeframes. Every level has defined recovery requirements that MUST be satisfied before returning to AI-assisted operation.

---

## 1. Introduction

### 1.1 Purpose

Security incidents in AI deployments require response procedures that are distinct from general IT security incident response. Agent isolation, audit trail preservation, and the transition to manual operation are all AI-specific response actions. This document defines the normative classification and response requirements for AI security incidents.

### 1.2 Scope

Four-level incident classification, response requirements per level, and recovery requirements before returning to AI-assisted operation.

### 1.3 Out of Scope

This document does not cover general IT security incident response procedures (which remain in the organisation's existing CSIRT process) or ethics incident response (see ANIF-715).

### 1.4 Intended Audience

- Security operations teams responding to AI incidents
- Governance officers notified of Level 3 and 4 incidents
- Platform engineers executing agent isolation and recovery
- Conformance assessors evaluating incident response capability

---

## 2. Normative References

| Reference | Title |
|---|---|
| ANIF-715 | Ethics Incident Response Policy |
| ANIF-724 | Ethics Audit Trail Requirements |
| ANIF-803 | Agent Lifecycle Management |
| ANIF-819 | Disaster Recovery and Resilience |
| ANIF-846 | Security Monitoring and Threat Detection |
| RFC 2119 | Key words for use in RFCs to Indicate Requirement Levels |

---

## 3. Incident Level Classification

| Level | Classification | Examples |
|---|---|---|
| Level 1 | Suspicious activity | Repeated injection attempts, unusual token usage, single tier boundary violation |
| Level 2 | Confirmed security event | Confirmed injection exploit, agent certificate compromise, bus spoofing confirmed |
| Level 3 | Active incident | Active exploitation causing incorrect agent behaviour, audit tampering confirmed, multiple agents compromised |
| Level 4 | Critical infrastructure attack | Confirmed attacker control over network operations; service disruption caused by AI system; supply chain compromise affecting production |

---

## 4. Level 1 Response — Suspicious Activity

### 4.1 Trigger

A Level 1 incident is raised when monitoring (ANIF-846) generates a High-severity alert that has not been attributed to a known benign cause.

### 4.2 Response Actions

1. Assign to a named security analyst within 1 hour.
2. Begin investigation: collect relevant audit log entries, agent observability data, and monitoring events.
3. Implement enhanced monitoring on the suspected component: increase monitoring event frequency and add targeted correlation rules.
4. Document findings in the incident record within 4 hours of assignment.

### 4.3 Level Escalation Trigger

Escalate to Level 2 if investigation confirms malicious intent or a control was successfully bypassed, even partially.

---

## 5. Level 2 Response — Confirmed Security Event

### 5.1 Trigger

A Level 2 incident is raised when a security event is confirmed — a threat actor has successfully exploited a vulnerability, even if the impact is contained.

### 5.2 Response Actions

1. Isolate the affected agent immediately: transition to UNTRUSTED or SUSPENDED lifecycle state (ANIF-803).
2. Revoke the affected agent's certificate (ANIF-843).
3. Notify the security team lead within 30 minutes.
4. Preserve all audit log entries related to the affected agent since the estimated compromise time — mark as evidence, do not purge.
5. Block the attack vector: apply mitigating controls from ANIF-841 if not already in place for this vector.
6. Assess lateral movement: determine whether the confirmed event has enabled access to other agents or data.

### 5.3 Level Escalation Trigger

Escalate to Level 3 if: multiple agents are affected, the attack is ongoing, incorrect network actions have been executed, or audit integrity is in doubt.

---

## 6. Level 3 Response — Active Incident

### 6.1 Trigger

A Level 3 incident is raised when an active attack is causing or has caused incorrect autonomous behaviour, or when the scope of compromise is sufficiently broad to require full operational response.

### 6.2 Response Actions

1. Halt all AI autonomous operations: transition the deployment to ANIF-819 Level 4 (full manual operation). This MUST occur within 15 minutes of Level 3 declaration.
2. Isolate all potentially affected agents — err toward broader isolation to prevent further harm.
3. Notify the governance committee within 1 hour.
4. Notify the build-time council within 1 hour — they are responsible for certificate revocation and forensic access to build artefacts.
5. Assign an incident commander from the security team.
6. Initiate forensic investigation using audit log records.
7. Brief NOC management on manual operation procedures within 15 minutes of Level 4 activation.

### 6.3 Communication

Internal stakeholders MUST be notified per the organisation's major incident communication plan. AI-related Level 3 incidents SHOULD be communicated to network operations customers if their services have been or may be affected.

---

## 7. Level 4 Response — Critical Infrastructure Attack

### 7.1 Trigger

A Level 4 incident is raised when a Level 3 incident has caused confirmed harm to network infrastructure or services, or when there is confirmed evidence of a state-level or sophisticated targeted attack.

### 7.2 Response Actions

Level 4 response includes all Level 3 actions plus:

1. Notify the executive sponsor and board within 2 hours.
2. Notify relevant regulatory authorities within the timeframes required by applicable law:
   - NIS2 (EU): initial notification within 24 hours; detailed report within 72 hours
   - Applicable national cybersecurity authority: per national requirements
3. Engage external security incident response specialists if internal capability is insufficient.
4. Preserve all evidence in a forensically sound manner — implement evidence hold on all relevant storage systems.
5. Issue a formal incident report to the governance committee within 5 business days.

---

## 8. Recovery Requirements

Recovery from each incident level requires the following conditions to be met before returning to AI-assisted operation.

| Level | Recovery Requirements |
|---|---|
| Level 1 | Investigation closed with root cause identified; enhanced monitoring confirmed effective |
| Level 2 | Affected agent re-evaluated (ANIF-820 testing re-run); new certificate issued; attack vector mitigated and tested |
| Level 3 | All Level 2 requirements for each affected agent; full audit log review confirming scope of impact; governance committee approval to resume AI operations; ANIF-819 Level 0 recovery process followed |
| Level 4 | All Level 3 requirements; regulatory authority confirmation (where required) that recovery is approved; board-level authorisation to resume autonomous operation; independent security assessment confirming the attack vector is closed |

---

## 9. Conformance Requirements

| ID | Requirement |
|---|---|
| CR-847-01 | Level 1 incidents MUST be assigned to a named analyst within 1 hour. |
| CR-847-02 | Level 2: affected agent MUST be isolated immediately upon confirmation. |
| CR-847-03 | Level 3: full manual operation (ANIF-819 Level 4) MUST be activated within 15 minutes of declaration. |
| CR-847-04 | Level 3: governance committee MUST be notified within 1 hour. |
| CR-847-05 | Level 4: regulatory notifications MUST be submitted within applicable legal timeframes. |
| CR-847-06 | Recovery requirements for each level MUST be satisfied before returning to AI-assisted operation. |

---

## 10. Security Considerations

Incident response procedures are themselves an attack target. An attacker who knows the Level 3 response procedure — specifically, that it triggers full manual operation — may use Level 3 incident conditions as a denial-of-service strategy to force the network into manual operation during a subsequent attack. Recovery procedures MUST verify that the triggering condition has been genuinely resolved and not merely suppressed.

---

## 11. Operational Considerations

Level 3 incident response requires NOC staff to operate in full manual mode, possibly for extended periods. NOC staff must maintain proficiency in manual operation through regular drills (ANIF-819). An organisation whose staff cannot competently operate the network in manual mode is not ready to deploy AI autonomous systems.
