# ANIF-846: Security Monitoring and Threat Detection

| Field        | Value                                              |
|--------------|----------------------------------------------------|
| Doc ID       | ANIF-846                                           |
| Series       | AI Security                                        |
| Version      | 0.1.0                                              |
| Status       | Draft                                              |
| Authors      | ANIF Working Group                                 |
| Reviewers    | —                                                  |
| Approved by  | —                                                  |
| Created      | 2026-04-08                                         |
| Last updated | 2026-04-08                                         |
| Replaces     | N/A                                                |
| Related docs | ANIF-401, ANIF-841, ANIF-847, ANIF-837             |

---

## Abstract

This document defines the mandatory security monitoring events, SIEM integration requirements, AI-specific threat detection correlation rules, and alert thresholds for ANIF-conformant deployments. Security monitoring MUST detect not only conventional threats but also AI-specific patterns including governance abuse signals such as unusual council voting patterns or repeated override attempts. All alert conditions MUST have defined escalation paths to the security incident response process (ANIF-847).

---

## 1. Introduction

### 1.1 Purpose

Detection is the prerequisite for response. Without defined monitoring events and correlation rules, AI-specific attacks — particularly those that exploit probabilistic behaviour, governance structures, and the long timescales of strike evasion — will not be detected until they have caused harm. This document establishes the monitoring baseline that every ANIF deployment MUST implement.

### 1.2 Scope

This document covers mandatory monitoring events, SIEM integration, AI-specific correlation rules, alert thresholds, and escalation paths.

### 1.3 Out of Scope

This document does not cover general infrastructure monitoring (see ANIF-401) or the incident response process triggered by alerts (see ANIF-847).

### 1.4 Intended Audience

- Security operations engineers implementing monitoring
- SIEM engineers building AI-specific detection rules
- Security architects designing the monitoring architecture
- Conformance assessors evaluating security monitoring claims

---

## 2. Normative References

| Reference | Title |
|---|---|
| ANIF-401 | Observability Standard |
| ANIF-724 | Ethics Audit Trail Requirements |
| ANIF-841 | AI Threat Model |
| ANIF-847 | AI Security Incident Response |
| ANIF-837 | AI Governance Reporting and Metrics |
| RFC 2119 | Key words for use in RFCs to Indicate Requirement Levels |

---

## 3. Mandatory Monitoring Events

The following event types MUST be collected and forwarded to the SIEM. Events that are not collected cannot generate alerts.

| Event Category | Event Type | Source |
|---|---|---|
| Authentication | Failed agent certificate authentication | API gateway |
| Authentication | Tier boundary violation attempt | API gateway |
| Authentication | Certificate presented from unexpected source IP | API gateway |
| Injection defence | Injection pattern detected and flagged | Intent validation pipeline |
| Injection defence | Semantic manipulation score above threshold | Intent validation pipeline |
| Intent processing | Intent flagged and blocked by security layer | Intent pipeline |
| Bus security | Signature verification failure on bus message | Message bus broker |
| Bus security | Bus spoofing attempt (unauthorised topic publish) | Message bus broker |
| Bus security | Replay attack detected (expired nonce/timestamp) | Message bus broker |
| Governance | Override submitted with unusual frequency | Override logging system |
| Governance | Council vote pattern anomaly | AI Council |
| Governance | Emergency fast-track policy change invoked | Policy management system |
| AI model health | Token usage spike (> 3 std dev above baseline) | Cost monitoring (ANIF-817) |
| AI model health | Hallucination rejection rate above 3% | Output validation (ANIF-722) |
| AI model health | Model drift score above 0.21 | Observability layer (ANIF-822) |
| Supply chain | Model integrity hash mismatch | Infrastructure security (ANIF-845) |
| Supply chain | Unsigned container image deployment attempt | Container runtime |
| Ethics | Critical ethics violation recorded | Ethics audit trail (ANIF-724) |
| Ethics | Three ethics strikes triggered for same agent | Progressive intervention (ANIF-716) |

---

## 4. SIEM Integration Requirements

### 4.1 Mandatory Integration

All mandatory monitoring events listed in section 3 MUST be forwarded to the organisation's SIEM in real time (maximum 30-second lag). Batch forwarding is not sufficient for security monitoring.

### 4.2 Event Format

Events forwarded to the SIEM MUST conform to a structured format containing at minimum:

| Field | Description |
|---|---|
| `event_id` | UUID v4 unique to the event |
| `event_category` | From the category column in section 3 |
| `event_type` | Specific event type |
| `source_component` | The ANIF component that generated the event |
| `agent_id` | The agent involved (where applicable) |
| `severity` | One of: informational, low, medium, high, critical |
| `timestamp` | ISO 8601 event time |
| `details` | Structured additional context |

### 4.3 Availability of Historical Events

SIEM event storage MUST retain AI security events for a minimum of 12 months to support investigation of long-duration attacks such as strike evasion.

---

## 5. AI-Specific Correlation Rules

The following correlation rules MUST be implemented in the SIEM. Each rule generates an alert when its condition is met.

| Rule ID | Rule Name | Condition | Alert Severity |
|---|---|---|---|
| CR-SEC-01 | Repeated injection attempts | More than 5 injection flags from the same `source_id` within 60 minutes | High |
| CR-SEC-02 | Tier boundary probing | More than 3 tier boundary violations from the same `agent_id` within 24 hours | High |
| CR-SEC-03 | Systematic model probing | Token usage from a single source exceeds 5× daily baseline for 3 consecutive days | Medium |
| CR-SEC-04 | Strike evasion pattern | Ethics events from the same `agent_id` consistently at severity below strike threshold, frequency increasing over 7 days | High |
| CR-SEC-05 | Council voting anomaly | Same council seat votes to override ethics gates in more than 50% of council sessions within 30 days | Critical |
| CR-SEC-06 | Override frequency spike | Override rate for a single operator exceeds 3× their 30-day baseline within 24 hours | Medium |
| CR-SEC-07 | Governance abuse | Emergency fast-track invoked twice within 14 days without a declared security incident | High |
| CR-SEC-08 | Bus spoofing cluster | More than 3 bus spoofing attempts within 10 minutes | Critical |
| CR-SEC-09 | Replay attack cluster | More than 10 replay attack detections within 5 minutes | Critical |
| CR-SEC-10 | Supply chain alert | Any model integrity hash mismatch | Critical |

---

## 6. Alert Thresholds and Escalation

| Alert Severity | Initial Response Time | Escalation Path |
|---|---|---|
| Informational | No automated alert; captured in daily log review | — |
| Low | Review within 1 business day | Security analyst review |
| Medium | Review within 4 hours | Security team; escalate to ANIF-847 Level 1 if confirmed |
| High | Review within 1 hour; security team paged | ANIF-847 Level 2 if confirmed |
| Critical | Immediate page; security team on-call activated | ANIF-847 Level 3 process initiated immediately |

---

## 7. Security Monitoring Reporting

Security monitoring summaries MUST be included in the monthly governance report (ANIF-837). The monthly summary MUST include:

- Count of events by category and severity
- Alert counts by rule
- Incidents initiated from monitoring (cross-referenced to ANIF-847 records)
- Any new patterns not covered by existing correlation rules

---

## 8. Conformance Requirements

| ID | Requirement |
|---|---|
| CR-846-01 | All mandatory monitoring events in section 3 MUST be collected and forwarded to the SIEM. |
| CR-846-02 | Event forwarding latency MUST NOT exceed 30 seconds. |
| CR-846-03 | All AI-specific correlation rules in section 5 MUST be implemented in the SIEM. |
| CR-846-04 | SIEM event storage for AI security events MUST cover a minimum of 12 months. |
| CR-846-05 | Critical alerts MUST initiate the ANIF-847 Level 3 process immediately. |
| CR-846-06 | Security monitoring summaries MUST be included in monthly governance reports. |

---

## 9. Security Considerations

Security monitoring data is itself sensitive — it reveals what the security team is looking for and what they are not. Access to correlation rules and alert configurations MUST be restricted to the security team. An adversary with knowledge of the correlation rules can structure attacks to stay below alert thresholds (rule CR-SEC-04 addresses the pattern-based version of this; the human security review layer addresses the rest).

---

## 10. Operational Considerations

Alert fatigue degrades security monitoring effectiveness. Correlation rules that generate frequent false positive alerts SHOULD be tuned. However, tuning MUST be done through a documented review process, not through unilateral threshold adjustment. Any change to a correlation rule threshold MUST be reviewed by the security team and recorded.
