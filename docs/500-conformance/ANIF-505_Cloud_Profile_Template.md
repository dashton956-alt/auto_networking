# ANIF-505: Cloud Provider Profile Template

| Field        | Value                                              |
|--------------|----------------------------------------------------|
| Doc ID       | ANIF-505                                           |
| Series       | Conformance                                        |
| Version      | 0.1.0                                              |
| Status       | Draft                                              |
| Authors      | ANIF Working Group                                 |
| Reviewers    | —                                                  |
| Approved by  | —                                                  |
| Created      | 2026-04-07                                         |
| Last updated | 2026-04-07                                         |
| Replaces     | N/A                                                |
| Related docs | ANIF-504, ANIF-101                                 |

---

## Abstract

This document defines the cloud provider conformance profile template, which extends the base vendor profile template defined in ANIF-504 with cloud-specific additions. A completed cloud provider profile documents how ANIF action types map to cloud-native primitives, how cloud regions map to the ANIF region enumeration, how cloud IAM/RBAC roles map to ANIF roles, how cloud audit logs integrate with the ANIF audit trail, and which cloud compliance certifications are relevant to ANIF-101 data residency requirements.

---

## 1. Introduction

### 1.1 Purpose

Cloud providers offering infrastructure-as-a-service, platform-as-a-service, or networking-as-a-service that supports ANIF-based autonomous operations MUST complete both the base vendor profile (ANIF-504) and this cloud-specific extension. The cloud profile ensures that organisations deploying ANIF on cloud platforms can understand precisely how ANIF abstractions map to cloud-provider specifics.

### 1.2 Scope

This document applies to:

- Public cloud providers (e.g., hyperscalers, regional cloud providers)
- Private cloud platforms declaring ANIF support
- Managed network service providers whose infrastructure is cloud-based

### 1.3 Out of Scope

This document does not cover:

- On-premises networking equipment (see ANIF-504)
- Telecommunications network domains (see ANIF-506)
- Application-layer concerns beyond those relevant to intent-driven network operations

### 1.4 Intended Audience

Cloud provider engineering and product teams preparing cloud profiles; enterprise architects selecting cloud platforms for ANIF deployments; operators configuring ANIF pipelines on cloud infrastructure.

---

## 2. Normative References

| Document  | Title                                    |
|-----------|------------------------------------------|
| ANIF-101  | Policy Schema (including region enum)    |
| ANIF-103  | Audit Requirements                       |
| ANIF-104  | Role and Permission Model                |
| ANIF-106  | Data Residency Policy                    |
| ANIF-504  | Vendor Profile Template                  |
| RFC 2119  | Key words for use in RFCs to indicate requirement levels |

---

## 3. Terms and Definitions

**Cloud-native primitive**: A cloud provider service or API that implements a network function (e.g., a load balancer, route table, security group).

**Region mapping**: The association between a cloud provider's geographic region identifiers and the ANIF region enumeration values (EU, US, APAC).

**IAM role**: An Identity and Access Management role defined in the cloud provider's access control system.

**ANIF role**: A role defined in the ANIF role and permission model (ANIF-104).

**Audit integration**: The mechanism by which a cloud provider's native audit/logging service produces records that satisfy the ANIF audit trail requirements defined in ANIF-103.

---

## 4. Cloud Profile Requirements

### 4.1 Relationship to Base Vendor Profile

A cloud provider MUST complete the full ANIF-504 vendor profile in addition to this cloud-specific extension. The base vendor profile fields (header, action type support, deviations, certification status) MUST be present and complete. The sections in this document are additive to those defined in ANIF-504.

### 4.2 Action Mapping Completeness

For each supported ANIF action type, the cloud provider MUST:

- Identify the specific cloud-native service(s) used to implement the action
- Document the API calls or service configuration changes made
- Note any limitations (e.g., region availability, account-type restrictions)

### 4.3 Region Mapping

The cloud provider MUST provide an exhaustive mapping from all of its geographic regions to the ANIF region enumeration. Regions that cannot be unambiguously mapped to EU, US, or APAC MUST be documented with a proposed handling (e.g., classified as non-conformant for data residency purposes, or provisionally mapped with stated reasoning).

### 4.4 Compliance Certification Relevance

The cloud provider SHOULD declare which of its held compliance certifications are relevant to ANIF-106 (data residency) and ANIF-101 (policy schema, particularly `pci_compliant` and zone constraint fields). Certification claims MUST reference publicly verifiable compliance reports.

---

## 5. Cloud Provider Profile Template

Cloud providers MUST complete the ANIF-504 base template and append the following sections.

---

```markdown
# ANIF Cloud Provider Conformance Profile

## [Include all sections from ANIF-504 Vendor Profile Template]

---

## Cloud-Specific Additions

### Section C1: Cloud-Native Action Mappings

For each supported ANIF action type, document the cloud-native implementation.

#### reroute_traffic

| Field                        | Value                                                        |
|------------------------------|--------------------------------------------------------------|
| Cloud service(s) used        | [e.g., Route53 weighted routing, ALB target group weights, Traffic Manager profiles] |
| Implementation mechanism     | [How the action translates to cloud API calls]              |
| Scope                        | [Global / Regional / Zone-level]                            |
| Rollback mechanism           | [How the cloud service supports ANIF rollback for this action] |
| Limitations                  | [Any restrictions, e.g., DNS TTL propagation delay]         |

#### apply_qos

| Field                        | Value                                                        |
|------------------------------|--------------------------------------------------------------|
| Cloud service(s) used        | [e.g., VPC Traffic Mirroring, Network Policy, QoS queues]   |
| Implementation mechanism     | [Description]                                               |
| Granularity                  | [Flow-level / Service-level / Subnet-level]                 |
| Rollback mechanism           | [Description]                                               |
| Limitations                  | [e.g., not supported in all regions]                        |

#### scale_bandwidth

| Field                        | Value                                                        |
|------------------------------|--------------------------------------------------------------|
| Cloud service(s) used        | [e.g., Direct Connect bandwidth tiers, ExpressRoute circuits, Transit Gateway bandwidth] |
| Implementation mechanism     | [Description]                                               |
| Minimum scale increment      | [e.g., 100 Mbps]                                            |
| Rollback mechanism           | [Description]                                               |
| Limitations                  | [e.g., scaling down may require hours due to provider SLA] |

#### isolate_segment

| Field                        | Value                                                        |
|------------------------------|--------------------------------------------------------------|
| Cloud service(s) used        | [e.g., Security Groups, Network ACLs, VPC isolation, firewall rules] |
| Implementation mechanism     | [Description]                                               |
| Isolation scope              | [Instance / Subnet / VPC / Account boundary]                |
| Rollback mechanism           | [Description]                                               |
| Limitations                  | [e.g., inter-account isolation requires additional IAM setup] |

---

### Section C2: Region and Zone Mapping

#### ANIF Region to Cloud Region Mapping

| ANIF Region | Cloud Provider Regions Included                              | Notes                                |
|-------------|--------------------------------------------------------------|--------------------------------------|
| EU          | [List of cloud region identifiers, e.g., eu-west-1, eu-central-1] | [Any exclusions or provisos]    |
| US          | [List of cloud region identifiers, e.g., us-east-1, us-west-2] | [Any exclusions or provisos]       |
| APAC        | [List of cloud region identifiers, e.g., ap-southeast-1, ap-northeast-1] | [Any exclusions or provisos] |

#### Unmapped Regions

| Cloud Region | Reason not mapped | Proposed handling                     |
|--------------|-------------------|---------------------------------------|
| [region-id]  | [e.g., sovereign cloud, government region] | [Classification for data residency purposes] |

#### Availability Zone Granularity

| Capability                              | Supported | Notes                              |
|-----------------------------------------|-----------|-----------------------------------|
| Zone-aware intent targeting             | [Yes / No] | [Description]                   |
| Multi-zone redundancy enforcement       | [Yes / No] | [e.g., for 99.99% availability intents] |
| Zone failover via reroute_traffic       | [Yes / No] | [Description]                   |

---

### Section C3: IAM / RBAC Role Mapping

#### Mapping Cloud Provider Roles to ANIF Roles

The following table maps the cloud provider's IAM roles to the ANIF role model defined in ANIF-104.

| ANIF Role              | Cloud Provider Role(s) / Permission Set                          | Notes                              |
|------------------------|------------------------------------------------------------------|------------------------------------|
| intent.submit          | [e.g., NetworkOperator, custom policy: anif:intent:write]       | [Minimum required permissions]     |
| intent.approve         | [e.g., NetworkAdmin, custom policy: anif:intent:approve]        | [May require MFA enforcement]      |
| policy.manage          | [e.g., SecurityAdmin, custom policy: anif:policy:write]         | [Description]                      |
| audit.read             | [e.g., AuditViewer, CloudTrailReadOnly]                         | [Description]                      |
| rollback.execute       | [e.g., NetworkOperator, custom policy: anif:rollback:execute]   | [Description]                      |
| admin                  | [e.g., NetworkAdmin with full ANIF permissions]                 | [Should be restricted; require justification for grant] |

#### Least Privilege Implementation Notes

[Document how the cloud provider's IAM system enforces ANIF principle P-05 (Least Privilege). Include notes on permission boundaries, service control policies, or other guardrails.]

---

### Section C4: Audit Integration

#### Audit Service Mapping

| ANIF Audit Requirement           | Cloud Provider Audit Service         | Integration mechanism              |
|----------------------------------|--------------------------------------|------------------------------------|
| Pipeline stage audit records     | [e.g., CloudTrail, Activity Log]     | [How ANIF audit writes to cloud service] |
| Append-only enforcement          | [e.g., S3 Object Lock, immutable log storage] | [Description of enforcement mechanism] |
| Audit record retrieval API       | [e.g., CloudTrail Lake queries, Log Analytics] | [API or query interface used] |
| Audit export format              | [e.g., JSON to S3, Azure Monitor SIEM connector] | [Format and delivery mechanism] |
| Retention period                 | [Minimum retention configured]       | [How to configure longer retention] |

#### ANIF-103 Compliance Notes

[Describe any gaps between the cloud provider's native audit capabilities and the ANIF-103 audit requirements. List any additional configuration required to achieve full compliance.]

#### Cross-Region Audit Aggregation

| Capability                                   | Supported | Notes                            |
|----------------------------------------------|-----------|----------------------------------|
| Single audit trail spanning multiple regions | [Yes / No] | [Description]                  |
| Cross-region audit query API                 | [Yes / No] | [Description]                  |
| Audit trail integrity verification           | [Yes / No] | [e.g., hash chaining, signing]  |

---

### Section C5: Data Residency and Compliance

#### Relevant Compliance Certifications

| Certification          | Scope                                | Publicly verifiable report location  |
|------------------------|--------------------------------------|--------------------------------------|
| ISO 27001              | [Regions/services in scope]          | [URL or report reference]            |
| SOC 2 Type II          | [Regions/services in scope]          | [URL or report reference]            |
| PCI DSS Level 1        | [Regions/services in scope]          | [URL or report reference]            |
| GDPR / Data Processing Agreement | [Regions]               | [URL or DPA reference]               |
| [Additional certifications as applicable] | — | —                           |

#### Data Residency Controls Relevant to ANIF-106

| Control                                     | Available | Notes                               |
|---------------------------------------------|-----------|-------------------------------------|
| Data residency guarantee per region         | [Yes / No] | [Contractual or technical guarantee] |
| Cross-border data transfer controls         | [Yes / No] | [How ANIF-106 zone constraints are enforced at the platform level] |
| Sovereign/restricted region designation     | [Yes / No] | [e.g., EU sovereign cloud offering] |
| Customer-managed encryption keys            | [Yes / No] | [Relevant to ANIF constraints.encryption] |

---

### Section C6: Example Cloud Provider Profile (Placeholder)

The following example illustrates a completed cloud provider profile for a generic provider. All values are illustrative placeholders.

```
Vendor name: Generic Cloud Provider Ltd
Product name: Cloud Networking Services
Product version: 2026Q1
ANIF version: 0.1.0
Declared conformance level: L3 — Conformant
Verification method: Self-assessment

ANIF Region EU → Regions: eu-west-1, eu-west-2, eu-central-1, eu-north-1
ANIF Region US → Regions: us-east-1, us-east-2, us-west-1, us-west-2
ANIF Region APAC → Regions: ap-southeast-1, ap-southeast-2, ap-northeast-1, ap-northeast-2

reroute_traffic → Route53 weighted routing + ALB target group weight adjustment
apply_qos → VPC Traffic Shaping policies + DSCP marking at instance level
scale_bandwidth → Direct Connect hosted connection tier upgrade API
isolate_segment → Security Group rule replacement + Network ACL quarantine ruleset

IAM: ANIF operator role mapped to NetworkOperator managed policy
IAM: ANIF approver role mapped to NetworkAdmin + ANIF:Approve custom permission

Audit: All pipeline events written to CloudTrail; S3 Object Lock enforces append-only
Audit: Cross-region aggregation via CloudTrail Lake; query latency < 5 minutes
Audit: Retention minimum 13 months (configurable to 7 years)

Compliance: ISO 27001 (all commercial regions), SOC 2 Type II, PCI DSS Level 1 (us-east-1, eu-west-1)
Data residency: EU data processing guarantee available; contractual DPA references §12

Deviations: None
```
```

---

## 6. Security Considerations

Cloud providers MUST NOT include in their profile:

- Customer account identifiers or tenancy details used in testing
- Internal network topology details that could assist adversarial mapping

Cloud profiles SHOULD note whether the cloud platform supports network-level isolation of the ANIF control plane from the data plane, as this is relevant to the security posture of an ANIF deployment.

---

## 7. Operational Considerations

- Cloud providers SHOULD publish profiles per major cloud service API version, not per product release, as cloud API versioning is typically decoupled from product versioning
- Cloud providers SHOULD provide a machine-readable region mapping file (JSON) alongside the profile, to allow ANIF orchestrators to automatically validate zone constraint compliance
- Profiles SHOULD include a link to the cloud provider's service health dashboard, as service health directly affects ANIF risk scoring inputs

---

## Appendix A: ANIF Region Enumeration Reference

The ANIF region enumeration as defined in ANIF-101 is:

| ANIF Region Value | Geographic scope                                       |
|-------------------|--------------------------------------------------------|
| EU                | European Union member states and associated territories |
| US                | United States of America and territories               |
| APAC              | Asia-Pacific region                                    |

Cloud providers with regions outside these three designations (e.g., Middle East, Africa, South America) MUST document how those regions are handled for data residency purposes in Section C2 of their profile.

---

## Appendix B: Change History

| Version | Date       | Author             | Description   |
|---------|------------|--------------------|---------------|
| 0.1.0   | 2026-04-07 | ANIF Working Group | Initial draft |
