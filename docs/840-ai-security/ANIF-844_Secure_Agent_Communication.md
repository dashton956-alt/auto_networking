# ANIF-844: Secure Agent Communication

| Field        | Value                                              |
|--------------|----------------------------------------------------|
| Doc ID       | ANIF-844                                           |
| Series       | AI Security                                        |
| Version      | 0.1.0                                              |
| Status       | Draft                                              |
| Authors      | ANIF Working Group                                 |
| Reviewers    | —                                                  |
| Approved by  | —                                                  |
| Created      | 2026-04-08                                         |
| Last updated | 2026-04-08                                         |
| Replaces     | N/A                                                |
| Related docs | ANIF-804, ANIF-841, ANIF-843, ANIF-845             |

---

## Abstract

This document defines the normative security requirements for all inter-agent communication in an ANIF-conformant deployment. TLS 1.3 is mandatory for all inter-agent communication. All message bus messages MUST carry integrity signatures. Replay attacks MUST be prevented through nonce and timestamp validation with a 30-second replay window — messages older than 30 seconds MUST be rejected regardless of signature validity. Bus access controls MUST be enforced cryptographically. Plaintext inter-agent communication is a conformance violation.

---

## 1. Introduction

### 1.1 Purpose

Inter-agent communication is the nervous system of an ANIF deployment. Compromising this channel — through eavesdropping, message tampering, bus spoofing, or replay attacks — allows an attacker to observe agent behaviour, inject false messages, or replay valid past messages in invalid contexts. This document specifies the security controls that protect the communication layer.

### 1.2 Scope

This document covers:

- Transport security requirements for all inter-agent communication
- Message integrity requirements for bus messages
- Replay attack prevention
- Bus access controls
- Key management requirements

### 1.3 Out of Scope

This document does not cover:

- Agent authentication and identity (see ANIF-843)
- Agent communication protocol content (see ANIF-804)
- Infrastructure network security (see ANIF-205)

### 1.4 Intended Audience

- Platform engineers implementing the agent communication infrastructure
- Security engineers reviewing the communication security model
- Conformance assessors evaluating communication security claims

---

## 2. Normative References

| Reference | Title |
|---|---|
| ANIF-804 | Agent Communication Protocol |
| ANIF-841 | AI Threat Model |
| ANIF-843 | Agent Zero Trust and Authentication |
| ANIF-845 | AI Infrastructure Security |
| RFC 2119 | Key words for use in RFCs to Indicate Requirement Levels |
| RFC 8446 | The Transport Layer Security (TLS) Protocol Version 1.3 |

---

## 3. Terms and Definitions

| Term | Definition |
|---|---|
| Message integrity signature | A cryptographic signature applied to a message that allows the recipient to verify the message has not been modified in transit |
| Nonce | A unique value included in a message to prevent replay — the same nonce MUST NOT be accepted twice |
| Replay window | The time period within which a message with a valid timestamp and nonce is accepted; messages outside this window are rejected |
| Bus access control | A cryptographic mechanism that restricts which agents may publish to or subscribe from specific message bus topics |
| Mutual TLS | A TLS configuration where both the client and server present certificates, enabling both-way authentication |

---

## 4. Transport Security

### 4.1 TLS 1.3 Requirement

All inter-agent communication MUST use TLS 1.3 (RFC 8446). TLS 1.2 is not permitted for new deployments. Existing deployments MUST migrate to TLS 1.3 within 180 days of adopting this standard.

Plaintext communication between agents is a conformance violation. Any inter-agent connection that falls back to plaintext MUST be rejected and logged as a security event.

### 4.2 Mutual TLS

All inter-agent connections MUST use mutual TLS. Both the connecting agent (client) and the receiving component (server) MUST present certificates. The agent's certificate is the certificate issued by the build-time council per ANIF-843. Server-side certificates MUST be issued by the organisation's internal certificate authority.

### 4.3 TLS Configuration

TLS connections MUST be configured to:

- Use only TLS 1.3-approved cipher suites
- Reject certificate chains with SHA-1 or MD5 signatures
- Verify full certificate chains against the trust anchor
- Enforce certificate revocation checking

---

## 5. Message Integrity

### 5.1 Signature Requirement

Every message published to the agent message bus MUST carry a cryptographic integrity signature. The signature MUST be computed over:

- The full message body
- The message nonce
- The timestamp
- The publishing agent's `agent_id`

The signature algorithm MUST be ECDSA with P-256 or stronger.

### 5.2 Signature Verification

Every agent receiving a bus message MUST verify the message signature before processing the message content. A message that fails signature verification MUST be:

1. Rejected and not processed.
2. Logged as a security event with: `source_topic`, `publishing_agent_id`, `failure_reason`, `timestamp`.
3. The security team MUST be notified within 5 minutes if more than 5 signature failures occur from the same source within 10 minutes.

---

## 6. Replay Attack Prevention

### 6.1 Nonce Requirement

Every bus message MUST include a UUID v4 nonce generated at message creation time. The receiving component MUST maintain a nonce cache for the replay window period and MUST reject any message whose nonce appears in the cache.

### 6.2 Timestamp Requirement

Every bus message MUST include an ISO 8601 timestamp recording the message creation time. Receiving components MUST reject messages where:

- The timestamp is more than 30 seconds in the past
- The timestamp is more than 5 seconds in the future (clock skew allowance)

Messages older than 30 seconds MUST be rejected regardless of signature validity. The 30-second window is the authoritative replay prevention boundary.

### 6.3 Nonce Cache Management

The nonce cache MUST retain all nonces received within the 30-second replay window. Cache entries older than 35 seconds MAY be purged (the 5-second margin accounts for processing latency). The nonce cache MUST be shared across all instances of a receiving component — a replay attack that targets a different instance MUST be rejected.

---

## 7. Bus Access Controls

### 7.1 Cryptographic Access Control

Access to message bus topics MUST be enforced cryptographically. An agent MUST NOT be able to publish to a topic it does not have access rights for, regardless of network-level access.

Bus access rights are declared in the agent capability manifest (ANIF-802) and are enforced by the message bus broker, which verifies the publishing agent's certificate and checks the declared capability against the manifest.

### 7.2 Topic Classification

Message bus topics MUST be classified by the minimum tier required to publish:

| Topic Category | Publish Access | Subscribe Access |
|---|---|---|
| Intent coordination | Tier 0 | Tier 0 and above |
| Monitoring observations | Tier 1 | Tier 0 and above |
| Analysis recommendations | Tier 2 | Tier 2 and above |
| Execution commands | Tier 3 | Tier 3 only |
| Council messages | Council-role agents only | Council-role and Tier 0 |

### 7.3 Bus Spoofing Prevention

An agent that attempts to publish to a topic above its declared tier is committing a bus spoofing violation. The message MUST be rejected by the broker, and the attempt MUST be logged as a Severity 2 security event.

---

## 8. Key Management

### 8.1 Signing Key Storage

Agent message signing keys MUST be stored in HSM or equivalent tamper-resistant storage, consistent with the certificate private key requirements of ANIF-843.

### 8.2 Key Rotation

Message signing keys MUST be rotated in conjunction with certificate rotation (every 90 days minimum per ANIF-843). Key rotation MUST not cause message signature verification failures — the new signing key MUST be published to all receiving components before it is used for the first time.

---

## 9. Conformance Requirements

| ID | Requirement |
|---|---|
| CR-844-01 | All inter-agent communication MUST use TLS 1.3. Plaintext communication is a conformance violation. |
| CR-844-02 | All inter-agent connections MUST use mutual TLS. |
| CR-844-03 | Every bus message MUST carry a cryptographic integrity signature. |
| CR-844-04 | Signature verification failures MUST be logged and the security team notified per section 5.2. |
| CR-844-05 | Every bus message MUST include a nonce and timestamp. |
| CR-844-06 | Messages older than 30 seconds MUST be rejected regardless of signature validity. |
| CR-844-07 | The nonce cache MUST be shared across all instances of a receiving component. |
| CR-844-08 | Bus access controls MUST be enforced cryptographically by the message broker. |
| CR-844-09 | Bus spoofing attempts MUST be logged as Severity 2 security events. |
| CR-844-10 | Message signing keys MUST be rotated every 90 days. |

---

## 10. Security Considerations

The 30-second replay window is a security-availability trade-off. A longer window increases protection against delayed replay attacks but increases nonce cache size and latency sensitivity. A shorter window risks rejecting legitimate messages from components with clock synchronisation lag. The 30-second value MUST NOT be extended without governance committee approval and a documented risk assessment.

---

## 11. Operational Considerations

Clock synchronisation across all agent components is a dependency for replay attack prevention. All agent hosts MUST synchronise time via NTP from a trusted source. Clock drift exceeding 2 seconds MUST trigger an alert. Agents running on hosts with excessive clock drift risk having their legitimate messages rejected by the 30-second window.
