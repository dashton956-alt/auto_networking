# ANIF-804: Agent Communication Protocol

| Field        | Value                                              |
|--------------|----------------------------------------------------|
| Doc ID       | ANIF-804                                           |
| Series       | AI Agent Architecture                              |
| Version      | 0.1.0                                              |
| Status       | Draft                                              |
| Authors      | ANIF Working Group                                 |
| Reviewers    | —                                                  |
| Approved by  | —                                                  |
| Created      | 2026-04-07                                         |
| Last updated | 2026-04-07                                         |
| Replaces     | N/A                                                |
| Related docs | ANIF-800, ANIF-802, ANIF-841, ANIF-843             |

---

## Abstract

This document specifies the three communication buses used by ANIF agents: the observation bus (Tier 1 → Tier 2), the recommendation bus (Tier 2 → Tier 3), and the management bus (Tier 0 → all tiers). Every message on every bus MUST carry a signed envelope. Agents MUST NOT communicate outside the bus architecture. Direct agent-to-agent calls are prohibited.

---

## 1. Introduction

### 1.1 Purpose

The communication architecture is the primary mechanism for enforcing tier separation at runtime. If agents could communicate freely — calling each other directly, sharing state via side channels — tier boundaries would become policy constraints rather than architectural ones. The bus model prevents direct inter-agent communication: every message goes through a bus that the agent's tier is permitted to access.

### 1.2 Scope

This document covers:

- The three bus definitions and their permitted publishers and subscribers
- The signed message envelope required on all buses
- Message routing and addressing
- Bus access control requirements
- Prohibited communication patterns

### 1.3 Out of Scope

This document does not cover:

- The content schema of observation or recommendation payloads (see ANIF-811 and ANIF-812)
- The management bus message schema for specific coordination operations (see ANIF-809)
- Bus infrastructure implementation (message broker technology selection)
- Bus security and threat model (see ANIF-841)

### 1.4 Intended Audience

- Platform engineers implementing bus infrastructure
- AI engineers building agents that publish or subscribe to buses
- Security engineers verifying bus access controls
- Build-time council members reviewing agent communication claims

---

## 2. Normative References

- ANIF-800 — Agent Architecture Overview
- ANIF-802 — Agent Capabilities and Permissions
- ANIF-841 — Agent Security Threat Model
- ANIF-843 — Agent Zero Trust and Authentication
- RFC 2119 — Key words for use in RFCs to indicate requirement levels

---

## 3. Terms and Definitions

**Bus:** A message routing component that accepts publications from permitted publishers and delivers them to permitted subscribers. Publishers and subscribers are identified by signed agent identity.

**Signed envelope:** A wrapper around every bus message that includes the publisher's identity, the message timestamp, a message UUID, and a cryptographic signature over the envelope fields and payload hash.

**Direct agent-to-agent call:** Any communication between two agents that does not pass through a bus. Direct calls are prohibited at all tiers.

**Bus access claim:** A capability declared in an agent's signed manifest specifying which buses the agent may publish to or subscribe from.

---

## 4. Three-Bus Architecture

### 4.1 Observation Bus

**Purpose:** Carries observations from Tier 1 monitor agents to Tier 2 advisor agents.

**Permitted publishers:** Tier 1 agents only.

**Permitted subscribers:** Tier 2 agents only.

**Message content:** Structured observations about network state, anomalies, security events, and capacity trends. The observation schema is defined in ANIF-811.

**Direction:** One-directional — from Tier 1 to Tier 2. Tier 2 agents MUST NOT publish to the observation bus.

### 4.2 Recommendation Bus

**Purpose:** Carries recommendations from Tier 2 advisor agents to Tier 3 decision agents.

**Permitted publishers:** Tier 2 agents only.

**Permitted subscribers:** Tier 3 agents only.

**Message content:** Structured recommendations including the recommended action, the reasoning chain, confidence score, and relevant risk factors. The recommendation schema is defined in ANIF-812.

**Direction:** One-directional — from Tier 2 to Tier 3. Tier 3 agents MUST NOT publish to the recommendation bus.

### 4.3 Management Bus

**Purpose:** Carries coordination signals from Tier 0 to all other tiers, and status reports from all tiers to Tier 0.

**Permitted publishers:** Tier 0 agents and all tiers (for status reports to Tier 0).

**Permitted subscribers:** All tiers.

**Message content:** Intent routing signals, agent pool management commands, escalation notifications, operational status reports.

**Direction:** Bidirectional between Tier 0 and other tiers. Non-Tier-0 agents MUST NOT publish management bus messages addressed to other non-Tier-0 agents. A Tier 1 agent MUST NOT send a management bus message to a Tier 3 agent.

---

## 5. Signed Message Envelope

### 5.1 Requirement

Every message published to any bus MUST be wrapped in a signed envelope. A message without a valid signed envelope MUST be rejected by the bus before delivery to any subscriber.

### 5.2 Mandatory Envelope Fields

| Field | Type | Description |
|---|---|---|
| `message_id` | UUID | Unique message identifier |
| `publisher_id` | UUID | Agent identity UUID of the publisher |
| `publisher_tier` | enum: 0/1/2/3 | Tier of the publishing agent |
| `bus_name` | enum | observation / recommendation / management |
| `published_at` | ISO 8601 timestamp | Publication timestamp |
| `payload_hash` | SHA-256 | Hash of the message payload |
| `signature` | string | Cryptographic signature over all envelope fields and payload hash |

### 5.3 Signature Verification

The bus MUST verify the publisher's signature before accepting the message for delivery. A message with an invalid signature MUST be rejected and the rejection MUST be logged as a security event (ANIF-847 Level 2).

Subscribers SHOULD verify the signature on each received message. Signature verification at the subscriber is a defence-in-depth measure against bus compromise.

### 5.4 Replay Prevention

The `message_id` and `published_at` fields together provide replay prevention. A bus MUST NOT deliver a message whose `message_id` has already been delivered within the replay window (default: 5 minutes). A duplicate `message_id` MUST be logged as a security event.

---

## 6. Bus Access Control

### 6.1 Manifest Declaration

An agent's signed manifest MUST declare:

- Which buses it is permitted to publish to
- Which buses it is permitted to subscribe from

The API gateway enforces these declarations on every publish and subscribe request.

### 6.2 Tier-Based Enforcement

The bus access control MUST enforce tier boundaries in addition to manifest claims:

- Even if a Tier 3 agent's manifest claims publish access to the observation bus, the bus MUST reject the request because Tier 3 agents are not permitted publishers of the observation bus.
- Tier enforcement takes precedence over manifest claims where they conflict.

### 6.3 Cross-Bus Prohibition

An agent MUST NOT forward messages between buses. A Tier 2 agent that receives a message from the observation bus MUST NOT re-publish that message to the recommendation bus without transforming it into a recommendation produced by the agent's own reasoning. Forwarding raw observations to the recommendation bus would allow Tier 1 content to bypass Tier 2 reasoning.

---

## 7. Prohibited Communication Patterns

The following communication patterns are prohibited at all times:

**Direct agent-to-agent calls:** An agent MUST NOT invoke another agent's API endpoint directly. All communication MUST go through a bus.

**Out-of-band signalling:** An agent MUST NOT communicate with another agent through shared memory, shared file systems, shared databases, or environment variables. These are side channels that bypass bus access controls.

**Bus bridge:** An agent MUST NOT act as a bridge between two buses it is not permitted to access on both sides. Creating a bridge between the observation bus and the execution layer is a Severity 1 security incident.

**Anonymous publishing:** An agent MUST NOT publish to a bus without including its authenticated identity in the signed envelope.

A detected violation of any of these patterns MUST be treated as a security incident and MUST trigger progressive intervention against the responsible agent (ANIF-716).

---

## 8. Conformance Requirements

All inter-agent communication MUST go through the three-bus architecture. Direct agent-to-agent calls are not conformant.

Every bus message MUST carry a signed envelope with all mandatory fields populated.

Bus access MUST be enforced using the publisher's signed manifest claims and the tier-based hard limits.

Replay prevention MUST be implemented. A duplicate `message_id` within the replay window MUST be rejected.

---

## 9. Security Considerations

The bus architecture ensures that every inter-agent communication is observable, attributable, and auditable. A compromised agent cannot communicate with another agent without leaving a signed trace on the bus. The signed envelope prevents message forgery — an attacker who cannot obtain the publisher's signing key cannot inject messages as that agent. Bus access control prevents tier bypass — a compromised Tier 1 agent cannot publish to the recommendation bus to inject false recommendations.

---

## 10. Operational Considerations

Bus message volume monitoring SHOULD be implemented as part of the standard observability stack. Anomalous bus message volumes — significantly more or fewer messages than expected from a given agent — are an operational signal that warrants investigation. The observation bus carrying no messages from a Tier 1 agent that should be monitoring indicates a monitoring failure. The recommendation bus carrying messages at an unusual rate from a Tier 2 agent may indicate a runaway recommendation loop.

---

## Appendix A: Change History

| Version | Date | Author | Changes |
|---|---|---|---|
| 0.1.0 | 2026-04-07 | ANIF Working Group | Initial draft |
