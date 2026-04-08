# ANIF-845: AI Infrastructure Security

| Field        | Value                                              |
|--------------|----------------------------------------------------|
| Doc ID       | ANIF-845                                           |
| Series       | AI Security                                        |
| Version      | 0.1.0                                              |
| Status       | Draft                                              |
| Authors      | ANIF Working Group                                 |
| Reviewers    | —                                                  |
| Approved by  | —                                                  |
| Created      | 2026-04-08                                         |
| Last updated | 2026-04-08                                         |
| Replaces     | N/A                                                |
| Related docs | ANIF-824, ANIF-843, ANIF-844, ANIF-846             |

---

## Abstract

This document defines five normative controls for securing the infrastructure on which ANIF agents run. The five controls are: model file integrity hashing at load time, isolated container runtime with no shared process namespace, signed container images, LLM API key rotation, and per-agent resource limits. Training data MUST be encrypted at rest using organisation-controlled keys. These controls ensure that even if a higher-level control is bypassed, the infrastructure layer provides a defence-in-depth backstop.

---

## 1. Introduction

### 1.1 Purpose

Agent security depends on the security of the infrastructure it runs on. A compromised container host, an unsigned image, or a leaked API key can undermine all higher-level controls. This document specifies the infrastructure-level security controls that form the foundation of the ANIF security stack.

### 1.2 Scope

This document covers model integrity hashing, container isolation, signed images, API key management, resource limits, and training data encryption at rest.

### 1.3 Out of Scope

This document does not cover supply chain integrity of models (see ANIF-824), inter-agent transport security (see ANIF-844), or agent identity (see ANIF-843).

### 1.4 Intended Audience

- Platform engineers deploying and managing agent infrastructure
- Security engineers reviewing the infrastructure security model
- Conformance assessors evaluating infrastructure security claims

---

## 2. Normative References

| Reference | Title |
|---|---|
| ANIF-824 | Agent Supply Chain Security |
| ANIF-843 | Agent Zero Trust and Authentication |
| ANIF-844 | Secure Agent Communication |
| ANIF-846 | Security Monitoring and Threat Detection |
| RFC 2119 | Key words for use in RFCs to Indicate Requirement Levels |

---

## 3. Control 1 — Model File Integrity Hashing at Load Time

At every model load event — initial deployment, restart, container recreation, or failover — the SHA-256 hash of the model file MUST be computed and compared against the approved model registry (ANIF-824).

A hash mismatch MUST:

1. Abort the load process.
2. Raise a Severity 1 security incident.
3. Place the affected agent in UNTRUSTED lifecycle state.

The hash verification MUST occur before the model is made available to any agent process. Agents MUST NOT start processing intents until hash verification has completed successfully.

---

## 4. Control 2 — Isolated Container Runtime

### 4.1 Requirement

Every agent MUST run in its own isolated container. Container configurations MUST enforce:

- No shared process namespace between agent containers
- No shared IPC namespace between agent containers
- No privileged mode
- Read-only root filesystem (with explicit writable mounts only for declared working directories)
- No capability elevation beyond the minimum required for the agent's declared function

### 4.2 Network Isolation

Agent containers MUST communicate only through the declared interfaces in their manifest (the message bus and declared API endpoints). Direct container-to-container network connections not routed through the message bus or API gateway are prohibited.

### 4.3 Host Access Restriction

Agent containers MUST NOT have access to host-level resources including: host network namespace, host PID namespace, host device files, or host file systems outside declared volume mounts.

---

## 5. Control 3 — Signed Container Images

### 5.1 Requirement

All agent container images MUST be signed by the build-time council before deployment. Container images without a valid build-time council signature MUST NOT be deployed.

### 5.2 Signature Verification

The container runtime MUST verify the image signature before starting any container. Signature verification MUST:

- Confirm the signature is from the build-time council signing key
- Confirm the image digest matches the signed manifest
- Reject images whose signatures have been revoked

### 5.3 Image Registry

All approved agent images MUST be stored in a private, access-controlled image registry. Public registry images MUST NOT be deployed as agent containers without first being evaluated and signed by the build-time council.

---

## 6. Control 4 — LLM API Key Management

### 6.1 Rotation Requirement

All LLM API keys MUST be rotated at a minimum interval of 30 days. API keys that have not been rotated within 30 days are a conformance violation.

### 6.2 Storage Requirement

LLM API keys MUST be stored in a secrets management system (e.g., HashiCorp Vault, AWS Secrets Manager, or equivalent). API keys MUST NOT be stored in:

- Agent container images
- Environment variables embedded in container definitions
- Configuration files in source code repositories
- Agent manifest files

### 6.3 Access Control

API key retrieval MUST require authenticated access. Each agent retrieves its API key at runtime from the secrets management system using its agent certificate (ANIF-843) as the authentication credential. API key access MUST be logged.

### 6.4 Compromised Key Response

If an API key is suspected or confirmed compromised:

1. The key MUST be revoked immediately.
2. A new key MUST be provisioned from the secrets management system.
3. All API calls made with the compromised key since the last rotation MUST be reviewed.
4. A security incident MUST be raised.

---

## 7. Control 5 — Per-Agent Resource Limits

Every agent container MUST have CPU, memory, and network I/O limits declared and enforced by the container runtime.

| Resource | Limit Requirement |
|---|---|
| CPU | Maximum CPU allocation declared in agent manifest; container MUST be throttled if limit is exceeded |
| Memory | Maximum memory allocation declared in agent manifest; container MUST be terminated (OOM killed) if limit is exceeded by more than 10% |
| Network I/O | Maximum outbound network bandwidth per agent; excess traffic MUST be throttled |

Resource limit values MUST be declared in the agent's capability manifest. Agents that consistently operate near their resource limits MUST be flagged for manifest review — limits set too close to normal operation increase the risk of legitimate requests being throttled.

---

## 8. Training Data Encryption at Rest

Training data used for AI models deployed in ANIF environments MUST be encrypted at rest using organisation-controlled encryption keys. Specifically:

- Encryption keys MUST be managed by the organisation, not delegated to the model vendor or cloud provider
- Key management MUST use a dedicated key management service with HSM-backed key storage
- Training data MUST NOT be stored unencrypted on any storage medium, including backups
- Access to decryption keys MUST be restricted to authorised training pipeline processes and audited

---

## 9. Conformance Requirements

| ID | Requirement |
|---|---|
| CR-845-01 | Model file integrity MUST be verified at every load event. Hash mismatch is a Severity 1 incident. |
| CR-845-02 | Every agent MUST run in an isolated container with no shared process or IPC namespace. |
| CR-845-03 | Container images MUST be signed by the build-time council. Unsigned images MUST NOT be deployed. |
| CR-845-04 | LLM API keys MUST be rotated every 30 days. Keys exceeding 30 days without rotation are a conformance violation. |
| CR-845-05 | API keys MUST be stored in a secrets management system. Storage in images, environment variables, or config files is prohibited. |
| CR-845-06 | Per-agent CPU, memory, and network limits MUST be declared and enforced. |
| CR-845-07 | Training data MUST be encrypted at rest with organisation-controlled keys. |

---

## 10. Security Considerations

Container isolation is a meaningful but not absolute control. Container escape vulnerabilities do exist in container runtimes. Organisations SHOULD maintain container runtime patches on a regular cadence and SHOULD subscribe to CVE feeds for their container runtime platform. The no-shared-namespace requirement limits the blast radius of a successful container escape.

---

## 11. Operational Considerations

Resource limits that are set too conservatively cause agent throttling and operational disruption. Limits set too generously allow runaway resource consumption. Operators SHOULD baseline resource usage over 30 days after initial deployment and set limits at 150% of the observed 95th percentile to provide headroom without enabling unbounded consumption.
