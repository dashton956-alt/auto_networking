# ANIF-840: AI Security Overview

| Field        | Value                                              |
|--------------|----------------------------------------------------|
| Doc ID       | ANIF-840                                           |
| Series       | AI Security                                        |
| Version      | 0.1.0                                              |
| Status       | Draft                                              |
| Authors      | ANIF Working Group                                 |
| Reviewers    | —                                                  |
| Approved by  | —                                                  |
| Created      | 2026-04-08                                         |
| Last updated | 2026-04-08                                         |
| Replaces     | N/A                                                |
| Related docs | ANIF-205, ANIF-720, ANIF-841, ANIF-830             |

---

## Abstract

This document defines the expanded attack surface that AI agents introduce into network infrastructure management and serves as the entry point for the ANIF-840 series. AI agents are not merely faster automation — they introduce qualitatively different vulnerabilities: probabilistic outputs that can be manipulated, natural language interfaces that can be exploited, model behaviour that can be poisoned at the supply chain level, and governance structures that can be abused by insiders. The ANIF-840 series extends the security architecture defined in ANIF-205 with AI-specific threat modelling, controls, monitoring, incident response, and compliance requirements. Security and ethics are complementary frameworks — security protects the integrity of the system, ethics governs its behaviour.

---

## 1. Introduction

### 1.1 Purpose

This document introduces the security threat landscape specific to AI-autonomous network management, explains how the ANIF-840 series addresses it, and establishes the relationship between AI security and the ethics safeguard framework. It is the mandatory entry point for the ANIF-840 series.

### 1.2 Scope

This document covers:

- The AI-expanded attack surface compared to deterministic automation
- Three threat categories: external, internal, and AI-specific
- The defence-in-depth model showing which ANIF documents address which layer
- The relationship between security controls and ethics safeguards

### 1.3 Out of Scope

This document does not cover:

- Network security architecture for the infrastructure being managed (see ANIF-205)
- Ethics safeguard technical implementation (see ANIF-720–725)
- General infrastructure security hardening

### 1.4 Intended Audience

- Security architects designing the ANIF deployment security model
- Security operations teams monitoring AI agent behaviour
- Governance officers understanding the security threat context
- Conformance assessors evaluating L5 security claims

---

## 2. Normative References

| Reference | Title |
|---|---|
| ANIF-205 | Security Architecture |
| ANIF-720 | Safeguard Architecture Overview |
| ANIF-724 | Ethics Audit Trail Requirements |
| ANIF-841 | AI Threat Model |
| ANIF-830 | AI Governance Overview |
| RFC 2119 | Key words for use in RFCs to Indicate Requirement Levels |

---

## 3. Terms and Definitions

| Term | Definition |
|---|---|
| Attack surface | The set of points in a system that an attacker can exploit to cause harm |
| Threat category | A grouping of related threats sharing a common origin or mechanism |
| Defence-in-depth | A security strategy where multiple independent controls each address part of the threat landscape, such that no single control failure compromises the system |
| AI-specific threat | A threat that exists only because of the probabilistic, language-model, or learning properties of AI agents — threats that do not apply to deterministic automation |

---

## 4. The AI-Expanded Attack Surface

Deterministic automation systems have a well-understood attack surface: code vulnerabilities, credential compromise, network intrusion, insider abuse. AI agents expand this surface in five material ways:

| Expansion | Description |
|---|---|
| Natural language interfaces | Intent authoring in natural language creates a surface for injection attacks that are impossible against binary command interfaces |
| Probabilistic outputs | Outputs that vary across invocations can be manipulated without breaking the system — the attacker does not need code execution, only the ability to shift probabilities |
| Model training dependencies | The model's behaviour is shaped by its training data; poisoning training data poisons behaviour without touching runtime code |
| Governance complexity | Multi-layer governance with council voting and human approval creates manipulation opportunities that purely technical systems do not have |
| Confidence and trust scores | Numeric scores that gate autonomous action can be gamed by crafting inputs that produce high confidence in incorrect outputs |

---

## 5. Three Threat Categories

### 5.1 External Threats

Threats originating from actors outside the organisation or the deployment boundary.

| Threat | Brief Description |
|---|---|
| Prompt injection | Malicious instructions embedded in inputs to hijack agent behaviour |
| Adversarial inputs | Inputs engineered to produce incorrect outputs |
| Model extraction | Repeated queries to reverse-engineer model behaviour or weights |
| Token denial of service | Flooding agents with high-token-cost requests to exhaust budget and trigger circuit breakers |
| Supply chain compromise | Poisoning models, dependencies, or training data at their source |

Full threat catalogue with attack vectors, impacts, and mitigating controls is defined in ANIF-841.

### 5.2 Internal Threats

Threats originating from actors with legitimate access to the deployment.

| Threat | Brief Description |
|---|---|
| Insider abuse | Authorised operators submitting malicious intents or approvals |
| Training data manipulation | Intentional introduction of biased or backdoored data into training pipelines |
| Audit tampering | Modification or deletion of audit records to conceal actions |
| Council manipulation | Coordinated insider action to direct council votes toward governance bypass |

### 5.3 AI-Specific Threats

Threats that exist only because of AI agent properties — not applicable to deterministic systems.

| Threat | Brief Description |
|---|---|
| Hallucination exploitation | Crafting inputs that trigger hallucination in predictable directions |
| Confidence manipulation | Inputs designed to produce artificially high or low confidence scores |
| Context poisoning | Injecting false information into agent context to alter downstream decisions |
| Trust score gaming | Manipulating the inputs that feed risk and trust scoring to produce incorrect scores |
| Strike evasion | Deliberately staying below ethics strike thresholds to avoid intervention |

---

## 6. Defence-in-Depth Model

| Defence Layer | What It Protects Against | ANIF Documents |
|---|---|---|
| Input validation and sanitisation | Prompt injection, adversarial inputs | ANIF-842 |
| Cryptographic agent identity | Impersonation, session hijacking, bus spoofing | ANIF-843 |
| Secure inter-agent communication | Replay attacks, eavesdropping, bus spoofing | ANIF-844 |
| Infrastructure hardening | Model tampering, container escape, key compromise | ANIF-845 |
| Security monitoring | Detection of active attacks, anomaly identification | ANIF-846 |
| Incident response | Containing and recovering from confirmed attacks | ANIF-847 |
| Security testing | Proactive identification of vulnerabilities before exploitation | ANIF-848 |
| Supply chain controls | Poisoned models, backdoored dependencies | ANIF-824 |
| Ethics safeguards | Behavioural constraints that hold even under attack | ANIF-720–725 |

---

## 7. Security and Ethics: Complementary Frameworks

Security controls and ethics safeguards are not redundant — they address different failure modes.

Security controls ask: is the system being attacked?
Ethics safeguards ask: is the system behaving correctly?

An agent can pass all security controls and still produce harmful outputs (model drift, training bias). An agent can satisfy all ethics checks and still be vulnerable to a prompt injection attack that has not yet been detected.

Both frameworks MUST be implemented. Neither replaces the other. Where they interact — for example, where an injection attempt triggers an ethics violation — the more restrictive control applies.

---

## 8. ANIF-840 Series Document Map

| Doc ID | Title | Purpose |
|---|---|---|
| ANIF-840 | AI Security Overview | Threat landscape and defence model (this document) |
| ANIF-841 | AI Threat Model | Full threat catalogue with controls |
| ANIF-842 | Prompt Injection and Adversarial Input Security | Input validation and injection defence |
| ANIF-843 | Agent Zero Trust and Authentication | Cryptographic identity, tier boundary enforcement |
| ANIF-844 | Secure Agent Communication | TLS, message integrity, replay prevention |
| ANIF-845 | AI Infrastructure Security | Container isolation, key management, signed images |
| ANIF-846 | Security Monitoring and Threat Detection | SIEM integration, AI-specific correlation rules |
| ANIF-847 | AI Security Incident Response | Four-level incident classification and response |
| ANIF-848 | Security Testing and Penetration Testing | Mandatory testing cadence, red-team scope |
| ANIF-849 | Security Compliance and Certification | EU AI Act, NIS2, ISO 27001, ISO 42001 security mapping |

---

## 9. Conformance Requirements

| ID | Requirement |
|---|---|
| CR-840-01 | All ANIF deployments claiming L5 conformance MUST implement all controls in ANIF-841 through ANIF-849. |
| CR-840-02 | Security controls MUST NOT be treated as alternatives to ethics safeguards. Both MUST be implemented. |
| CR-840-03 | The defence-in-depth model MUST be implemented such that no single control failure compromises the system. |

---

## 10. Security Considerations

The threat landscape for AI-autonomous systems is evolving rapidly. New attack techniques — particularly against LLMs — are published frequently. The ANIF-840 series reflects the threat landscape as of its authoring date. Organisations MUST establish a process for reviewing the series annually against published AI security research and updating controls where the threat landscape has materially changed.

---

## 11. Operational Considerations

Security controls impose operational overhead. Input sanitisation adds latency; cryptographic identity verification adds complexity; monitoring generates alert volume. These costs are inherent in deploying AI agents in critical infrastructure and MUST NOT be traded away for operational efficiency. Where security controls degrade performance below acceptable operational bounds, the correct response is to improve the implementation, not to weaken the control.
