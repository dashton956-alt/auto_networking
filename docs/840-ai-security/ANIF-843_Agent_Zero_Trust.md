# ANIF-843: Agent Zero Trust and Authentication

| Field        | Value                                              |
|--------------|----------------------------------------------------|
| Doc ID       | ANIF-843                                           |
| Series       | AI Security                                        |
| Version      | 0.1.0                                              |
| Status       | Draft                                              |
| Authors      | ANIF Working Group                                 |
| Reviewers    | —                                                  |
| Approved by  | —                                                  |
| Created      | 2026-04-08                                         |
| Last updated | 2026-04-08                                         |
| Replaces     | N/A                                                |
| Related docs | ANIF-802, ANIF-841, ANIF-844, ANIF-903             |

---

## Abstract

This document defines the zero trust authentication model for ANIF agents. Every agent MUST hold a unique cryptographic certificate issued by the build-time council. Identity is verified on every API call — there is no session-based trust that can be hijacked. Tier boundary enforcement is cryptographic: the API gateway verifies that the agent's certificate tier declaration matches the endpoint being accessed. A compromised agent identity MUST trigger immediate certificate revocation, transition of the agent to UNTRUSTED lifecycle state, and a Severity 1 security incident. Certificates MUST be rotated every 90 days at minimum.

---

## 1. Introduction

### 1.1 Purpose

Traditional authentication models grant a session after initial authentication, after which all requests within the session are trusted. This model is inadequate for AI agents because a compromised session token grants persistent access. Zero trust authentication eliminates session-based trust: every request is independently authenticated and authorised, and a stolen credential is insufficient without the accompanying certificate.

### 1.2 Scope

This document covers:

- Agent certificate issuance and management
- Per-request authentication requirements
- Tier boundary enforcement at the API gateway
- Compromised identity handling
- Certificate rotation policy

### 1.3 Out of Scope

This document does not cover:

- Human operator authentication (governed by organisational IAM policy)
- Secure message transport (see ANIF-844)
- Agent capability and permission boundaries (see ANIF-802)

### 1.4 Intended Audience

- Security engineers implementing agent identity infrastructure
- Platform engineers building the API gateway
- Build-time council members issuing and managing certificates
- Conformance assessors evaluating zero trust claims

---

## 2. Normative References

| Reference | Title |
|---|---|
| ANIF-802 | Agent Capabilities and Permissions |
| ANIF-803 | Agent Lifecycle Management |
| ANIF-841 | AI Threat Model |
| ANIF-844 | Secure Agent Communication |
| ANIF-903 | Build-Time Council |
| RFC 2119 | Key words for use in RFCs to Indicate Requirement Levels |

---

## 3. Terms and Definitions

| Term | Definition |
|---|---|
| Agent certificate | A unique X.509 certificate issued to an agent instance by the build-time council, containing the agent's identity and tier declaration |
| Certificate authority | The build-time council's certificate authority, which issues, signs, and revokes agent certificates |
| Per-request authentication | The practice of verifying agent identity on every API call, not only at session establishment |
| Tier boundary | The architectural separation between agent tiers; crossing a tier boundary requires appropriate tier-level authorisation |
| UNTRUSTED state | An agent lifecycle state in which the agent is prevented from making any API calls pending security investigation |

---

## 4. Agent Certificate Requirements

### 4.1 Mandatory Certificate Fields

Every agent certificate MUST include:

| Field | Description |
|---|---|
| `agent_id` | The unique identifier of the agent instance |
| `agent_type` | The registered agent type |
| `tier` | The agent's declared tier (0, 1, 2, or 3) |
| `issuer` | The build-time council certificate authority |
| `valid_from` | Certificate validity start date |
| `valid_to` | Certificate expiry date (MUST NOT exceed 90 days from issue) |
| `capabilities_hash` | SHA-256 hash of the agent's approved capability manifest |

### 4.2 Certificate Issuance

Certificates MUST be issued by the build-time council certificate authority as part of the agent approval process (ANIF-903). No certificate MUST be issued without council approval of the corresponding capability manifest.

A single certificate MUST be issued per agent instance. Certificates MUST NOT be shared between agents.

### 4.3 Certificate Storage

Agent certificates and private keys MUST be stored in a hardware security module (HSM) or equivalent tamper-resistant storage. Private keys MUST NOT be stored in configuration files, environment variables, or code repositories.

---

## 5. Per-Request Authentication

### 5.1 Requirement

Every API call from an agent to any platform component MUST be authenticated with the agent's certificate. The API gateway MUST verify the certificate on every request. There is no session after initial authentication.

### 5.2 Authentication Verification Steps

On receipt of an API call, the API gateway MUST:

1. Verify the certificate is signed by the build-time council certificate authority.
2. Verify the certificate is within its validity period.
3. Verify the certificate is not on the revocation list.
4. Verify the `capabilities_hash` in the certificate matches the current approved manifest hash in the registry.
5. Verify the requested endpoint tier is permitted for the `tier` declared in the certificate.

If any verification step fails, the request MUST be rejected with an authentication failure response and the attempt MUST be logged as a security event.

### 5.3 No Session Tokens

Session tokens that persist across multiple requests MUST NOT be issued. An API call that presents a session token rather than a certificate MUST be rejected.

---

## 6. Tier Boundary Enforcement

### 6.1 Requirement

Tier boundaries MUST be enforced cryptographically at the API gateway. An agent with a certificate declaring `tier: 1` MUST NOT be permitted to call endpoints designated for Tier 3 agents, regardless of any other claims in the request.

### 6.2 Endpoint Tier Classification

Every platform API endpoint MUST be classified with the minimum tier required for access:

| Endpoint Category | Minimum Tier Required |
|---|---|
| Canonical state read | Tier 0 |
| Policy evaluation | Tier 1 |
| Risk scoring | Tier 2 |
| Execution API | Tier 3 |
| Council vote submission | Tier 0 (council-role only) |

### 6.3 Tier Boundary Violation

An agent that attempts to call an endpoint above its declared tier is committing a security violation. The attempt MUST be:

1. Rejected by the API gateway.
2. Logged as a Severity 2 security event.
3. Reported to the security team within 5 minutes.

Repeated tier boundary violations (three or more from the same agent within 24 hours) MUST escalate to a Severity 1 security incident.

---

## 7. Compromised Identity Handling

### 7.1 Compromise Indicators

A compromised agent identity is indicated by any of the following:

- Certificate private key known or suspected to be disclosed
- Certificate used from an unexpected network location
- Agent certificate presented alongside a token belonging to a different agent
- Authentication failure analysis revealing systematic forgery attempts

### 7.2 Response

On suspected or confirmed compromise:

1. The agent's certificate MUST be revoked by the build-time council certificate authority immediately. Revocation propagates to all API gateway instances within 60 seconds.
2. The agent MUST be transitioned to UNTRUSTED lifecycle state (ANIF-803).
3. A Severity 1 security incident MUST be raised.
4. All requests made by the agent since its last successful integrity verification MUST be reviewed.
5. A replacement certificate MUST NOT be issued until a full security investigation is complete and the build-time council has approved reissuance.

---

## 8. Certificate Rotation

### 8.1 Rotation Policy

Agent certificates MUST be rotated at a minimum interval of 90 days. A certificate that has not been rotated within 90 days is a conformance violation.

### 8.2 Rotation Process

Certificate rotation MUST follow the same issuance process as initial certificate issuance — the build-time council certificate authority issues the new certificate, the old certificate is revoked after a brief overlap window (maximum 24 hours) to allow in-flight requests to complete.

### 8.3 Rotation Monitoring

The platform MUST monitor certificate expiry dates and alert the build-time council 14 days before any certificate is due to expire. Certificates that expire without renewal MUST cause the associated agent to transition to SUSPENDED state.

---

## 9. Conformance Requirements

| ID | Requirement |
|---|---|
| CR-843-01 | Every agent MUST hold a unique certificate issued by the build-time council certificate authority. |
| CR-843-02 | Every API call MUST be authenticated with the agent's certificate. Session tokens MUST NOT be used. |
| CR-843-03 | The API gateway MUST verify all five authentication steps on every request. |
| CR-843-04 | Tier boundary violations MUST be rejected, logged, and reported within 5 minutes. |
| CR-843-05 | Suspected or confirmed identity compromise MUST trigger certificate revocation within 60 seconds. |
| CR-843-06 | Compromised agents MUST be transitioned to UNTRUSTED state and a Severity 1 incident raised. |
| CR-843-07 | Certificates MUST be rotated at a minimum interval of 90 days. |
| CR-843-08 | Certificate private keys MUST be stored in HSM or equivalent tamper-resistant storage. |

---

## 10. Security Considerations

The certificate authority is the root of trust for the entire agent identity system. Compromise of the certificate authority would allow an attacker to issue certificates for any agent at any tier. The certificate authority MUST be operated with the highest security controls in the deployment — air-gapped issuance, hardware security modules for CA key storage, and strict procedural controls for certificate issuance.

---

## 11. Operational Considerations

Certificate rotation at 90-day intervals requires operational planning. Build-time council members MUST have a defined process for rotating certificates in both scheduled and emergency scenarios. The 14-day expiry warning provides lead time for scheduled rotation; emergency rotation processes MUST be tested as part of the annual DR drill.
