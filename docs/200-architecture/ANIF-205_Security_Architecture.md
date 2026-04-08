# ANIF-205: Security Architecture

| Field        | Value                              |
|--------------|------------------------------------|
| Doc ID       | ANIF-205                           |
| Series       | Architecture                       |
| Version      | 0.1.0                              |
| Status       | Draft                              |
| Authors      | ANIF Working Group                 |
| Reviewers    | —                                  |
| Approved by  | —                                  |
| Created      | 2026-04-07                         |
| Last updated | 2026-04-07                         |
| Replaces     | N/A                                |
| Related docs | ANIF-103, ANIF-106, ANIF-404       |

---

## Abstract

This document defines the Security Architecture for the Autonomous Networking & Infrastructure
Framework (ANIF). It specifies the authentication model, role-based access control (RBAC)
framework, least privilege enforcement, approval ticket security, audit log integrity, input
validation security, API security, transport security, plugin security, and secrets management.
All ANIF implementations MUST satisfy the controls defined herein before operating in any
environment that affects real network infrastructure.

---

## 1. Introduction

### 1.1 Purpose

This document establishes the security controls that protect the ANIF platform, its data, and
the network infrastructure it governs. Security controls are distributed across all pipeline
stages and all architectural layers. This document provides the authoritative reference for
security-relevant design decisions throughout the ANIF 200-series.

### 1.2 Scope

This document covers:

- Authentication model for the prototype and production paths
- RBAC: roles, permissions, and enforcement points
- Governance gate role checks
- Least privilege enforcement (P-05)
- Approval ticket security: expiry, state transitions, integrity
- Audit log integrity controls
- Input validation security
- API security: error handling, trace correlation
- Transport security requirements
- Plugin security isolation model
- Secrets management

### 1.3 Out of Scope

- Network device authentication and authorisation
- Physical security controls
- Security incident response procedures (see 400-series)
- Penetration testing methodology
- Cryptographic algorithm selection beyond minimum TLS version

### 1.4 Intended Audience

- Security architects and engineers reviewing ANIF deployments
- Core contributors implementing authentication and authorisation
- Compliance officers verifying security control coverage
- DevOps engineers configuring secrets and transport security
- Plugin authors understanding security boundaries

---

## 2. Normative References

- RFC 2119: Key words for use in RFCs to Indicate Requirement Levels
- RFC 6749: The OAuth 2.0 Authorization Framework
- RFC 8705: OAuth 2.0 Mutual-TLS Client Authentication
- NIST SP 800-207: Zero Trust Architecture
- NIST CSF 2.0: Cybersecurity Framework
- ANIF-000: Framework Constitution
- ANIF-103: Governance Principles
- ANIF-106: Security Principles
- ANIF-200: Reference Architecture
- ANIF-202: Data Architecture (audit record integrity)
- ANIF-404: Security Operations Procedures
- OWASP API Security Top 10

---

## 3. Terms and Definitions

| Term                  | Definition                                                                                     |
|-----------------------|------------------------------------------------------------------------------------------------|
| Authentication        | The process of verifying the identity of a caller or system.                                   |
| Authorisation         | The process of determining whether an authenticated identity has permission to perform an action.|
| RBAC                  | Role-Based Access Control — permissions assigned to roles, roles assigned to identities.       |
| Principal             | An authenticated entity (human user or machine agent) interacting with ANIF.                  |
| Capability            | A named permission that a plugin must declare to access a specific ANIF operation.             |
| Approval Ticket       | A time-bound governance record requiring human review before an action can proceed.            |
| mTLS                  | Mutual TLS — both client and server present certificates for authentication.                   |
| Trace ID              | A UUID4 included in all responses to correlate errors without exposing internal state.         |
| Append-Only           | A storage constraint preventing modification or deletion of existing records.                  |

---

## 4. Security Architecture

### 4.1 Authentication

#### 4.1.1 Prototype: Static API Key

The prototype MUST use a static API key passed as an HTTP header for authentication.

```
Header: X-ANIF-API-Key: <key-value>
```

Requirements:
1. The API key MUST be configured via the `ANIF_API_KEY` environment variable.
2. The API key MUST NOT appear in source code, configuration files committed to version control,
   or log output.
3. All API endpoints MUST require the API key header. Requests missing the header MUST return
   HTTP 401 Unauthorized.
4. Requests with an invalid API key MUST return HTTP 401 Unauthorized. The response MUST NOT
   indicate whether the key format is valid or invalid (to prevent enumeration).
5. The API key MUST be at least 32 characters of cryptographically random data.

#### 4.1.2 Production: OAuth 2.0 / mTLS

In production, the static API key MUST be replaced with one of the following authentication
mechanisms:

| Mechanism      | Use Case                                         | Standard    |
|----------------|--------------------------------------------------|-------------|
| OAuth 2.0 + JWT| Human operators using interactive clients        | RFC 6749    |
| mTLS           | Machine-to-machine (automation agents, adapters) | RFC 8705    |
| API Gateway    | External consumers proxied through an API gateway| Varies      |

The authentication mechanism MUST be configurable without code changes. The `ANIF_AUTH_MODE`
environment variable MUST control the active mechanism: `api_key | oauth2 | mtls`.

#### 4.1.3 Identity Propagation

Once authenticated, the principal's identity and role MUST be attached to the request context
and propagated through all pipeline stages. The identity MUST be recorded in every `AuditRecord`
and `ApprovalTicket` written during that request.

### 4.2 Authorisation: RBAC Model

ANIF defines five RBAC roles. Every authenticated principal MUST be assigned exactly one
primary role. Roles MUST NOT be combined at runtime; a principal cannot hold multiple roles
simultaneously.

#### 4.2.1 Role Definitions

| Role                   | Code                    | Description                                                      |
|------------------------|-------------------------|------------------------------------------------------------------|
| Network Engineer       | `network_engineer`      | Human operator who submits and monitors intents.                 |
| Senior Engineer        | `senior_engineer`       | Experienced operator authorised to approve high-risk actions.    |
| Automation Agent       | `automation_agent`      | Machine principal submitting intents programmatically.           |
| Policy Administrator   | `policy_administrator`  | Manages policy sets, reviews and accepts feedback suggestions.   |
| Compliance Officer     | `compliance_officer`    | Read-only access to audit records; no operational permissions.   |

#### 4.2.2 Permission Matrix

The following matrix defines which operations each role MAY perform. All other operations are
implicitly DENIED.

| Operation                              | network_engineer | senior_engineer | automation_agent | policy_administrator | compliance_officer |
|----------------------------------------|:----------------:|:---------------:|:----------------:|:--------------------:|:-----------------:|
| POST /validate-intent                  | YES              | YES             | YES              | NO                   | NO                |
| GET /intent/{intent_id}                | YES              | YES             | YES              | NO                   | NO                |
| POST /evaluate-policy                  | YES              | YES             | YES              | YES                  | NO                |
| POST /score-risk                       | YES              | YES             | YES              | NO                   | NO                |
| POST /decide                           | YES              | YES             | YES              | NO                   | NO                |
| POST /governance/check                 | YES              | YES             | YES              | NO                   | NO                |
| POST /governance/approve/{ticket_id}   | NO               | YES             | NO               | NO                   | NO                |
| POST /governance/reject/{ticket_id}    | NO               | YES             | NO               | NO                   | NO                |
| POST /execute                          | YES              | YES             | YES              | NO                   | NO                |
| POST /rollback/{intent_id}             | YES              | YES             | NO               | NO                   | NO                |
| GET /execution/{execution_id}          | YES              | YES             | YES              | NO                   | YES               |
| GET /audit/{intent_id}                 | YES              | YES             | NO               | YES                  | YES               |
| GET /audit/{intent_id}/why             | YES              | YES             | NO               | YES                  | YES               |
| GET /audit                             | NO               | YES             | NO               | YES                  | YES               |
| POST /orchestrate                      | YES              | YES             | YES              | NO                   | NO                |
| GET /orchestrate/{intent_id}/status    | YES              | YES             | YES              | NO                   | NO                |
| GET /feedback/analysis                 | NO               | YES             | NO               | YES                  | NO                |
| POST /feedback/accept/{suggestion_id}  | NO               | NO              | NO               | YES                  | NO                |
| POST /feedback/reject/{suggestion_id}  | NO               | NO              | NO               | YES                  | NO                |

#### 4.2.3 RBAC Enforcement Points

RBAC MUST be enforced at the following locations:

1. **API Layer**: Every request handler MUST validate the principal's role against the
   permission matrix before processing. Role validation MUST occur BEFORE any business logic.
2. **Governance Gate**: The governance gate MUST independently verify that the operator role
   present in the request context satisfies the governance mode requirements (see Section 4.3).
3. **Approval Workflow**: The approval and rejection endpoints MUST verify that the caller
   holds the `senior_engineer` role before processing the ticket.

RBAC enforcement MUST NOT be implemented only at the API layer. The Governance Gate and
Approval Workflow MUST enforce their own role checks as defence-in-depth.

### 4.3 Governance Gate Role Checks

The Governance Gate applies the following role-based rules:

1. **Operator Role Requirement**: The `Intent.requestor_role` MUST be one of `network_engineer`
   or `automation_agent` for the pipeline to proceed. Any other role submitted as the requestor
   MUST result in a `block` governance outcome.

2. **Approval Authority**: Only principals with the `senior_engineer` role MUST be permitted
   to call `POST /governance/approve/{ticket_id}` or `POST /governance/reject/{ticket_id}`.
   Attempts by any other role MUST return HTTP 403 Forbidden.

3. **Self-Approval Prohibition**: An `automation_agent` MUST NOT approve its own submitted
   intent. This is enforced by the role model: `automation_agent` has no approval permission.
   Implementations MUST additionally verify that the approver's identity differs from the
   intent requestor's identity.

4. **Policy Administrator Exclusion**: `policy_administrator` principals MUST NOT be permitted
   to submit intents or approve tickets. Their scope is confined to policy and feedback
   management.

```
Governance Gate Role Validation Flow:

Incoming Decision + Operator Context
         │
         ▼
  Is requestor_role in {network_engineer, automation_agent}?
         │
    NO ──┴──► BLOCK (403)
         │
        YES
         │
         ▼
  Compute mode from risk_score and configuration
         │
   ┌─────┴──────────────┬───────────────┐
   ▼                    ▼               ▼
  auto            manual_review       block
   │                    │
   │            Create ApprovalTicket
   │            Notify senior_engineer
   │                    │
   │          (senior_engineer approves/rejects)
   │                    │
   └────────────────────┘
              │
              ▼
         Proceed to Execution
```

### 4.4 Least Privilege Enforcement (P-05)

Least privilege is applied at three levels:

#### 4.4.1 RBAC Least Privilege

Role permissions are the minimum required for the role's function. No role has blanket
access to all endpoints. The Compliance Officer role has read-only access and no operational
permissions.

#### 4.4.2 Action Executor Scoping

Action Executors MUST be scoped to the capabilities declared at registration. An executor
MUST NOT perform an action type that is not in its declared capabilities.

The `isolate_segment` action type has an additional privilege requirement: the adapter
MUST explicitly declare the `action:isolate_segment` capability. An adapter that does not
declare this capability MUST NOT be invoked for `isolate_segment` actions even if it
handles other action types.

```python
# Enforcement at execution time (illustrative)
def execute(decision: Decision) -> ExecutionRecord:
    """Execute the decision using the registered adapter."""
    adapter = registry.get_adapter_for_action(decision.action_type)
    # Raises CapabilityError if adapter does not declare the capability
    registry.assert_capability(adapter, f"action:{decision.action_type.value}")
    return adapter.execute(decision.parameters)
```

#### 4.4.3 Plugin Least Privilege

Plugins MUST operate within their declared capabilities. A plugin MUST NOT:

- Access the Audit Service write path directly
- Call the Governance Gate or modify governance decisions
- Access other plugins' internal state
- Escalate its own capabilities at runtime

Plugins that attempt operations outside their declared capabilities MUST have those calls
rejected with a `CapabilityError` that is logged and included in the audit record.

### 4.5 Approval Ticket Security

Approval tickets govern the `manual_review` governance flow. The following rules MUST be enforced:

#### 4.5.1 Ticket Creation

1. Tickets MUST be created with a unique `ticket_id` (UUID4).
2. `expires_at` MUST be set to `created_at + 15 minutes`. This value MUST NOT be configurable
   per-ticket by the caller; it is a system constant (configurable globally via `ANIF_TICKET_EXPIRY_MINUTES`).
3. Initial status MUST be `pending`.
4. Tickets MUST be associated with exactly one `Decision` (via `decision_id`).

#### 4.5.2 Ticket Expiry

1. At the time of any approval or rejection call, the system MUST check `expires_at` against
   the current UTC time.
2. If the ticket has expired, the approval call MUST return HTTP 410 Gone. The ticket status
   MUST be transitioned to `expired`.
3. An expired ticket MUST NOT be re-opened or extended. The intent MUST be resubmitted.
4. The system SHOULD proactively expire tickets via a background check on the `manual_review`
   queue. Notification to the approver SHOULD be sent before expiry.

#### 4.5.3 Ticket State Machine

```
            PENDING
           /       \
          /         \
    APPROVED       REJECTED
                              \
                               EXPIRED (on timeout)
```

Terminal states: `approved`, `rejected`, `expired`. Once in a terminal state, a ticket
MUST NOT transition to any other state. Attempts to approve or reject a non-pending ticket
MUST return HTTP 409 Conflict.

#### 4.5.4 Ticket Integrity

In production, the ticket payload MUST be signed or hash-chained to prevent tampering.
Approved tickets that fail integrity verification MUST NOT be honoured; the intent MUST
be treated as blocked.

### 4.6 Audit Log Integrity

The audit log is the primary evidence record for compliance and forensic investigation.
Its integrity MUST be protected by the following controls:

1. **No DELETE endpoint**: The Audit Service MUST NOT expose any endpoint that deletes or
   modifies audit records. `GET` and `POST` (write) are the only permitted operations.
2. **No UPDATE endpoint**: Audit records are immutable after creation. There is no update
   operation.
3. **Append-Only Storage**: In production, the audit log MUST be backed by an append-only
   storage mechanism at the storage layer (not only enforced at the application layer).
4. **Hash Chaining (RECOMMENDED for production)**: Each `AuditRecord` SHOULD include a
   `previous_hash` field containing the SHA-256 hash of the immediately preceding record's
   canonical JSON serialisation. This enables detection of record insertion, deletion, or
   reordering.
5. **Access Control**: Write access to the audit log MUST be restricted to internal ANIF
   components via internal function calls or service-to-service calls. External principals
   (including `compliance_officer`) have read-only access only.
6. **Audit of Audit Access**: Access to audit records by external principals SHOULD itself
   be logged (at INFO level) to detect unusual access patterns.

### 4.7 Input Validation Security

All external input MUST be validated before any business logic is executed. This prevents
injection attacks, malformed data from propagating through the pipeline, and unexpected
behaviour from untrusted input.

1. All API request bodies MUST be validated against Pydantic v2 schemas before reaching
   any module function.
2. Validation failures MUST return HTTP 422 Unprocessable Entity. Implementations MUST NOT
   return HTTP 500 for client-supplied invalid data.
3. The 422 response MUST include structured error details (field name, error type, message)
   sufficient for the caller to correct the request, but MUST NOT include internal state,
   file paths, or stack traces.
4. Enum fields MUST only accept defined enum values. Unknown values MUST be rejected with 422.
5. String fields with defined maximum lengths MUST enforce those limits. Strings exceeding
   maximum length MUST be rejected with 422, not silently truncated.
6. `intent_id` and `trace_id` fields MUST be validated as UUID4 format. Invalid UUIDs MUST
   be rejected with 422.
7. The `dry_run` field in the Intent MUST be treated as a binary boolean. Any other value
   MUST be rejected.
8. Intent constraints dict MUST be validated against the allowed keys for the declared action
   type. Unknown constraint keys SHOULD be rejected or at minimum logged as a warning.

### 4.8 API Security

#### 4.8.1 Error Response Security

API error responses MUST NOT expose internal system state to external callers. The following
rules govern error responses:

1. HTTP 500 responses MUST return a generic message: `"An internal error occurred."` The
   actual error detail MUST be logged server-side and correlated via `trace_id`.
2. Error responses MUST include a `trace_id` so the caller can reference the incident.
3. Stack traces MUST NOT appear in API responses under any circumstances.
4. Internal file paths, module names, or variable names MUST NOT appear in API responses.
5. The distinction between "resource not found" and "resource exists but access denied" MUST
   be carefully considered. For sensitive resources, returning 404 for both cases is
   RECOMMENDED to prevent enumeration.

#### 4.8.2 Rate Limiting

In production, the API layer SHOULD enforce rate limits per API key or per principal.
Rate limiting protects against:

- Unintentional automation loops submitting excessive intents
- Denial-of-service via repeated pipeline invocations

Rate limit responses MUST use HTTP 429 Too Many Requests with a `Retry-After` header.

#### 4.8.3 Trace ID Usage

Every response MUST include a `trace_id`. For error responses, the `trace_id` enables
support personnel to look up the full server-side error without requiring the caller to
describe the error in detail.

```json
{
  "status": "error",
  "data": {},
  "errors": [
    {
      "code": "INTENT_VALIDATION_FAILED",
      "message": "Field 'action' must be one of: reroute_traffic, apply_qos, scale_bandwidth, isolate_segment"
    }
  ],
  "trace_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
}
```

### 4.9 Transport Security

1. In production deployments, all API traffic MUST use HTTPS with TLS 1.2 as the minimum
   version. TLS 1.3 is RECOMMENDED.
2. TLS certificates MUST be issued by a trusted Certificate Authority.
3. HTTP (non-TLS) endpoints MUST be disabled in production. The API server MUST redirect
   HTTP requests to HTTPS or reject them with a 400 Bad Request response.
4. For machine-to-machine communication between ANIF services in production, mTLS SHOULD
   be used to authenticate both sides of the connection.
5. TLS certificate validity MUST be monitored. Expired certificates MUST NOT be permitted
   in production.
6. The prototype MAY operate over HTTP for development purposes only. Any documentation or
   deployment guide MUST clearly note that HTTP is not suitable for production.

### 4.10 Plugin Security

Plugins extend ANIF and therefore represent a potential attack surface. The following
controls MUST be applied to all plugins:

1. **Manifest Validation**: Plugin manifests MUST be validated against the manifest schema
   at registration time. Malformed manifests MUST cause registration failure.
2. **Entry Point Validation**: Plugin entry points MUST be importable Python paths. Any
   `ImportError` or `AttributeError` during entry point loading MUST cause registration failure.
3. **Capability Scoping**: Plugins MUST only access operations covered by their declared
   capabilities. Runtime capability checks MUST be enforced by the module registry.
4. **Audit Write Isolation**: Plugins MUST NOT call the Audit Service write path directly.
   All audit records written as a result of plugin activity MUST be written by the owning
   module (Actions or Policy) through the standard audit write interface.
5. **No Governance Access**: Plugins MUST NOT call the Governance Gate or influence
   governance mode decisions.
6. **Process Isolation (Production)**: In production, plugins from untrusted sources SHOULD
   be executed in a subprocess or container with restricted OS-level permissions (e.g.,
   no network access beyond declared endpoints, read-only filesystem access).
7. **Plugin Source Trust**: Only plugins from declared trusted sources (configured via
   `ANIF_TRUSTED_PLUGIN_SOURCES`) SHOULD be loaded at startup. Loading untrusted plugins
   MUST require explicit operator approval.

### 4.11 Secrets Management

1. No secrets MUST appear in source code.
2. No secrets MUST appear in YAML schema files (`schemas/` directory).
3. No secrets MUST appear in `pyproject.toml` or any configuration file committed to
   version control.
4. All secrets MUST be provided via environment variables at runtime.
5. `.env` files containing real secrets MUST be listed in `.gitignore` and MUST NOT be
   committed to version control.
6. In production, secrets MUST be injected via the container orchestrator's native secrets
   mechanism (Docker Secrets, Kubernetes Secrets, HashiCorp Vault, or equivalent).
7. The structured logging framework MUST be configured to redact known secret field names
   (e.g., `api_key`, `password`, `token`, `secret`) from log output.
8. Secrets MUST be rotated when a principal with knowledge of the secret is removed from
   the system or when a compromise is suspected.

---

## 5. Conformance Requirements

1. All API endpoints MUST require authentication. Unauthenticated requests MUST return HTTP 401.
2. All role-permission checks in the Permission Matrix (Section 4.2.2) MUST be enforced.
3. The Governance Gate MUST independently verify role requirements as defined in Section 4.3.
4. `isolate_segment` actions MUST require explicit capability declaration from the adapter.
5. Approval tickets MUST expire after 15 minutes. Expired tickets MUST NOT be honoured.
6. The Audit Service MUST NOT expose any delete or update endpoint for audit records.
7. All API inputs MUST be validated with Pydantic before processing; validation failures MUST return HTTP 422.
8. HTTP 500 responses MUST NOT include stack traces or internal state.
9. Production deployments MUST use TLS 1.2 or higher.
10. No secrets MUST appear in code, configuration files, or log output.
11. Plugins MUST NOT access the audit write path directly.
12. Self-approval of intents by automation agents is PROHIBITED.

---

## 6. Security Considerations

This entire document constitutes security guidance. Implementers are additionally advised to:

- Review the OWASP API Security Top 10 and verify ANIF controls address each risk.
- Conduct a threat model of the deployment using STRIDE or equivalent methodology.
- Review audit logs regularly for anomalous patterns (excessive blocks, repeated 401s,
  unusual approval patterns).
- Test rollback handlers as part of security drills to verify recovery capability.

---

## 7. Operational Considerations

- API key rotation procedures MUST be documented and tested before production deployment.
- Approval ticket expiry notifications SHOULD be tested end-to-end in staging.
- Audit log integrity verification (hash chain checking) SHOULD be run as a scheduled
  operational task, not only on demand.
- Plugin source trust lists MUST be reviewed when adding new integration partners.
- TLS certificate expiry monitoring MUST be configured before production go-live.

---

## Appendix A: Examples

### A.1 API Key Authentication Header

```http
POST /validate-intent HTTP/1.1
Host: anif.example.com
X-ANIF-API-Key: Xk9mP2rQ8vL4nJ7wT1uY3cZ6dF0hA5sE
Content-Type: application/json

{
  "action": "reroute_traffic",
  "target": "segment-east-01",
  ...
}
```

### A.2 403 Forbidden Response (Role Violation)

```json
{
  "status": "error",
  "data": {},
  "errors": [
    {
      "code": "INSUFFICIENT_ROLE",
      "message": "This operation requires the senior_engineer role."
    }
  ],
  "trace_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
}
```

### A.3 Expired Ticket Response

```json
{
  "status": "error",
  "data": {},
  "errors": [
    {
      "code": "TICKET_EXPIRED",
      "message": "Approval ticket has expired. Please resubmit the intent."
    }
  ],
  "trace_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
}
```

### A.4 Security Control Summary Matrix

| Control Area        | Prototype Mechanism              | Production Mechanism                |
|---------------------|----------------------------------|-------------------------------------|
| Authentication      | Static API Key (header)          | OAuth 2.0 JWT or mTLS               |
| Authorisation       | RBAC (in-process)                | RBAC + API Gateway policy           |
| Transport           | HTTP (dev only)                  | HTTPS TLS 1.2+, mTLS service mesh   |
| Audit Integrity     | Append-only list (in-memory)     | Append-only store + hash chaining   |
| Plugin Isolation    | In-process capability checks     | Subprocess/container isolation      |
| Secrets             | Environment variables            | Vault / orchestrator secrets        |
| Input Validation    | Pydantic v2 (422 on failure)     | Same                                |
| Ticket Expiry       | 15-minute TTL enforced in code   | Same + background expiry sweep      |

---

## Appendix B: Change History

| Version | Date       | Author             | Summary                  |
|---------|------------|--------------------|--------------------------|
| 0.1.0   | 2026-04-07 | ANIF Working Group | Initial draft            |
