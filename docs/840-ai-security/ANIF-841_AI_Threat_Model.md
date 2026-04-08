# ANIF-841: AI Threat Model

| Field        | Value                                              |
|--------------|----------------------------------------------------|
| Doc ID       | ANIF-841                                           |
| Series       | AI Security                                        |
| Version      | 0.1.0                                              |
| Status       | Draft                                              |
| Authors      | ANIF Working Group                                 |
| Reviewers    | —                                                  |
| Approved by  | —                                                  |
| Created      | 2026-04-08                                         |
| Last updated | 2026-04-08                                         |
| Replaces     | N/A                                                |
| Related docs | ANIF-840, ANIF-842, ANIF-843, ANIF-844, ANIF-824  |

---

## Abstract

This document defines the full threat catalogue for ANIF-conformant AI agent deployments across three categories: external threats, internal threats, and AI-specific threats. For each threat, this document identifies the attack vector, the potential impact, and the mitigating control with a reference to the ANIF document that specifies it. Implementers MUST consult this document when designing security controls to ensure no threat category is unaddressed. This threat model is not exhaustive — the AI threat landscape evolves continuously — but it establishes the baseline set of threats that every ANIF deployment MUST mitigate.

---

## 1. Introduction

### 1.1 Purpose

A threat model is the foundation of a security programme. Without a structured catalogue of threats, security controls are chosen ad hoc and gaps are discovered only after exploitation. This document provides the structured threat catalogue from which all ANIF security control requirements derive.

### 1.2 Scope

This document covers all threats specific to AI agent deployments. It does not duplicate the general network infrastructure threat model defined in ANIF-205.

### 1.3 Out of Scope

This document does not cover:

- Network infrastructure threats not related to AI agents (see ANIF-205)
- Physical security threats
- Social engineering attacks on human personnel

### 1.4 Intended Audience

- Security architects designing the ANIF deployment security model
- Security engineers implementing mitigating controls
- Red-team practitioners designing engagement scenarios
- Conformance assessors verifying threat coverage

---

## 2. Normative References

| Reference | Title |
|---|---|
| ANIF-205 | Security Architecture |
| ANIF-724 | Ethics Audit Trail Requirements |
| ANIF-820 | AI Agent Testing and Red-Team Standards |
| ANIF-824 | Agent Supply Chain Security |
| ANIF-842 | Prompt Injection and Adversarial Input Security |
| ANIF-843 | Agent Zero Trust and Authentication |
| ANIF-844 | Secure Agent Communication |
| ANIF-845 | AI Infrastructure Security |
| ANIF-846 | Security Monitoring and Threat Detection |
| RFC 2119 | Key words for use in RFCs to Indicate Requirement Levels |

---

## 3. Terms and Definitions

| Term | Definition |
|---|---|
| Attack vector | The path or mechanism through which a threat actor exploits a vulnerability |
| Impact | The consequence of a successful exploit, assessed across: confidentiality, integrity, availability, and safety |
| Mitigating control | A technical or governance measure that reduces the likelihood or impact of a threat |
| Threat actor | An individual or group with the motive and capability to exploit a vulnerability |

---

## 4. External Threat Catalogue

### 4.1 Prompt Injection

| Field | Detail |
|---|---|
| Attack vector | Malicious instructions embedded in intent payload fields, external data sources, or tool outputs |
| Impact | Agent behaviour altered; ethics gates bypassed; unauthorised network actions executed |
| Mitigating control | Input sanitisation and pattern detection (ANIF-842); schema validation (ANIF-301) |

### 4.2 Adversarial Inputs

| Field | Detail |
|---|---|
| Attack vector | Carefully crafted inputs designed to cause the agent to produce incorrect outputs through boundary exploitation or statistical manipulation |
| Impact | Incorrect risk scores; wrong policy evaluation outcomes; misrouted intents |
| Mitigating control | Adversarial input testing (ANIF-820); deterministic shadow comparison (ANIF-807) |

### 4.3 Model Extraction

| Field | Detail |
|---|---|
| Attack vector | Systematic querying of the agent to reverse-engineer model behaviour, decision boundaries, or parameter approximations |
| Impact | Attacker gains detailed knowledge of agent decision logic enabling more targeted attacks |
| Mitigating control | Rate limiting (ANIF-813, ANIF-817); monitoring for systematic probing patterns (ANIF-846) |

### 4.4 Token Denial of Service

| Field | Detail |
|---|---|
| Attack vector | Flooding the system with intents designed to maximise LLM token consumption, exhausting the cost circuit breaker |
| Impact | Cost circuit breaker triggered; autonomous operation degraded or halted |
| Mitigating control | Rate limiting at intent submission (ANIF-813); cost circuit breaker (ANIF-817); monitoring for token spikes (ANIF-822) |

### 4.5 Supply Chain Compromise

| Field | Detail |
|---|---|
| Attack vector | Poisoning model weights, training data, or software dependencies at their source before deployment |
| Impact | Persistent malicious behaviour embedded in deployed agents; detection is extremely difficult post-deployment |
| Mitigating control | Model integrity hashing (ANIF-824); training data provenance (ANIF-824); dependency scanning (ANIF-824) |

### 4.6 Session Hijacking and Token Theft

| Field | Detail |
|---|---|
| Attack vector | Attacker steals an authenticated agent session token to impersonate the agent on the message bus or at the API gateway |
| Impact | Attacker can submit messages as a trusted agent, potentially submitting actions outside that agent's tier or role |
| Mitigating control | Cryptographic identity per request — no session-based trust (ANIF-843). A stolen session token is insufficient without the agent's certificate. |

---

## 5. Internal Threat Catalogue

### 5.1 Insider Abuse

| Field | Detail |
|---|---|
| Attack vector | Authorised operator submits malicious intents, approves harmful recommendations, or uses override authority to direct the system toward harmful outcomes |
| Impact | Network disruption; data exfiltration; suppression of legitimate network operations |
| Mitigating control | Override logging (ANIF-808); approval audit trail (ANIF-724); separation of duties (ANIF-004) |

### 5.2 Training Data Manipulation

| Field | Detail |
|---|---|
| Attack vector | Insider with access to training pipelines injects biased, backdoored, or false data into training datasets |
| Impact | Persistent model behaviour modification; may not surface until a specific trigger condition is encountered |
| Mitigating control | Training data provenance and access controls (ANIF-824, ANIF-836); build-time council review of training data (ANIF-824) |

### 5.3 Audit Tampering

| Field | Detail |
|---|---|
| Attack vector | Insider modifies or deletes audit records to conceal unauthorised actions |
| Impact | Loss of audit trail integrity; inability to reconstruct events for forensic investigation or regulatory compliance |
| Mitigating control | Write-once, tamper-evident audit log (ANIF-107, ANIF-724); separate write and read access controls for audit storage |

### 5.4 Council Manipulation

| Field | Detail |
|---|---|
| Attack vector | Coordinated insider action by multiple council members to direct council votes toward governance bypass outcomes |
| Impact | Governance controls circumvented through legitimate-appearing process; technical safeguards remain but policy constraints removed |
| Mitigating control | Independence requirements (ANIF-831, ANIF-900); unusual voting pattern monitoring (ANIF-846); governance committee oversight of council decisions |

---

## 6. AI-Specific Threat Catalogue

### 6.1 Hallucination Exploitation

| Field | Detail |
|---|---|
| Attack vector | Attacker crafts inputs designed to trigger hallucination in predictable directions — for example, constructing a scenario that causes the agent to believe a non-existent network element exists |
| Impact | Agent makes decisions based on false information; incorrect recommendations or actions follow |
| Mitigating control | Canonical state grounding (ANIF-307); hallucination rejection (ANIF-722); hallucination stress testing (ANIF-820) |

### 6.2 Confidence Manipulation

| Field | Detail |
|---|---|
| Attack vector | Inputs designed to produce artificially high confidence scores in incorrect recommendations, bypassing the threshold for automatic approval |
| Impact | Incorrect actions auto-approved without human review |
| Mitigating control | Deterministic shadow comparison (ANIF-807); confidence score trend monitoring (ANIF-822) |

### 6.3 Context Poisoning

| Field | Detail |
|---|---|
| Attack vector | Injecting false information into the data sources that populate agent context — CMDB records, monitoring data, ITSM records — to alter downstream decisions |
| Impact | Agent reasons from false premises and produces outputs aligned with attacker goals |
| Mitigating control | Context sanitisation before insertion (ANIF-816); canonical state integrity (ANIF-307); adapter read-only boundaries (ANIF-810) |

### 6.4 Trust Score Gaming

| Field | Detail |
|---|---|
| Attack vector | Manipulating the inputs that feed the risk and trust scoring algorithm (ANIF-304) to produce scores that incorrectly enable or block autonomous action |
| Impact | High-risk actions approved without human review; or low-risk actions incorrectly blocked, degrading operational throughput |
| Mitigating control | Deterministic risk scoring algorithm (ANIF-304); scoring input validation; monitoring for anomalous score distributions (ANIF-822) |

### 6.5 Strike Evasion

| Field | Detail |
|---|---|
| Attack vector | An attacker with knowledge of the ethics strike system (ANIF-716) deliberately structures malicious actions to stay below strike thresholds — for example, spacing harmful actions to avoid the three-strikes window |
| Impact | Progressive intervention does not trigger; harmful behaviour continues undetected |
| Mitigating control | Monitoring for patterns below thresholds (ANIF-846); governance reporting on ethics event frequency (ANIF-837); red-team testing for evasion (ANIF-820) |

### 6.6 Bus Spoofing

| Field | Detail |
|---|---|
| Attack vector | A compromised process or agent publishes messages to a message bus topic it does not have access rights for — for example, a Tier 1 Monitoring Agent publishing to the Recommendation Bus |
| Impact | Unauthorised recommendations or instructions injected into the pipeline as if from a trusted source |
| Mitigating control | Cryptographic bus access controls (ANIF-844); tier boundary enforcement at API gateway (ANIF-843) |

### 6.7 Replay Attacks on the Recommendation Bus

| Field | Detail |
|---|---|
| Attack vector | A previously valid recommendation message is re-submitted to the Recommendation Bus to trigger a decision that has already been actioned or is no longer valid — for example, re-triggering a high-risk approval that was granted hours earlier |
| Impact | Stale or already-executed actions re-triggered, potentially causing duplicate or contradictory network changes |
| Mitigating control | Message nonce and timestamp validation with a 30-second replay window (ANIF-844). Messages older than 30 seconds MUST be rejected regardless of signature validity. |

---

## 7. Threat Coverage Matrix

| Threat | Primary Control | Secondary Control |
|---|---|---|
| Prompt injection | ANIF-842 | ANIF-820 (testing) |
| Adversarial inputs | ANIF-820 | ANIF-807 (shadow) |
| Model extraction | ANIF-817 (rate limit) | ANIF-846 (monitoring) |
| Token DoS | ANIF-817 | ANIF-813 |
| Supply chain | ANIF-824 | ANIF-820 (red-team) |
| Session hijacking | ANIF-843 | — |
| Insider abuse | ANIF-808 | ANIF-724 |
| Training data manipulation | ANIF-824 | ANIF-836 |
| Audit tampering | ANIF-107 | ANIF-724 |
| Council manipulation | ANIF-831 | ANIF-846 |
| Hallucination exploitation | ANIF-722 | ANIF-820 |
| Confidence manipulation | ANIF-807 | ANIF-822 |
| Context poisoning | ANIF-816 | ANIF-307 |
| Trust score gaming | ANIF-304 | ANIF-822 |
| Strike evasion | ANIF-846 | ANIF-837 |
| Bus spoofing | ANIF-844 | ANIF-843 |
| Replay attacks | ANIF-844 | — |

---

## 8. Conformance Requirements

| ID | Requirement |
|---|---|
| CR-841-01 | Every threat listed in sections 4–6 MUST have at least one implemented mitigating control. |
| CR-841-02 | Red-team engagements (ANIF-820) MUST attempt to exploit at least one threat from each of the three categories. |
| CR-841-03 | This threat model MUST be reviewed annually and updated to reflect the current threat landscape. |

---

## 9. Security Considerations

This threat catalogue is necessarily public — it is part of the ANIF specification. Adversaries with knowledge of this document understand the controls they must evade. The defence-in-depth approach ensures that no single control failure is sufficient for a successful attack. Organisations MUST NOT rely on this document being obscure; they MUST assume adversaries have read it.

---

## 10. Operational Considerations

Threat models require active maintenance. The AI threat landscape is advancing rapidly — new attack techniques against LLMs, new supply chain attack patterns, and new governance manipulation strategies are published regularly. Organisations SHOULD assign a named threat intelligence function to track developments and propose updates to this document through the policy lifecycle process (ANIF-833).
