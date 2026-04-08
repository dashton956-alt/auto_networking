# ANIF-824: Agent Supply Chain Security

| Field        | Value                                              |
|--------------|----------------------------------------------------|
| Doc ID       | ANIF-824                                           |
| Series       | AI Agent Architecture                              |
| Version      | 0.1.0                                              |
| Status       | Draft                                              |
| Authors      | ANIF Working Group                                 |
| Reviewers    | —                                                  |
| Approved by  | —                                                  |
| Created      | 2026-04-08                                         |
| Last updated | 2026-04-08                                         |
| Replaces     | N/A                                                |
| Related docs | ANIF-807, ANIF-841, ANIF-845, ANIF-835             |

---

## Abstract

This document defines five normative controls for securing the AI agent supply chain — the chain of models, training data, dependencies, and deployment artefacts that constitute a deployed agent. The five controls are: model integrity hashing, training data provenance, dependency security, model poisoning detection, and provenance guarantee. No model MUST be deployed without a complete provenance chain traceable to governance-approved sources. Build-time council review is required before any new model is added to the approved model registry. Supply chain compromise is a Severity 1 security incident.

---

## 1. Introduction

### 1.1 Purpose

An agent that passes all functional and ethics tests can still be compromised at the supply chain level: through a poisoned model, a backdoored dependency, untraceable training data, or a tampered deployment artefact. This document specifies the controls that protect the integrity of everything that goes into a deployed agent before it processes its first intent.

### 1.2 Scope

This document covers:

- Model integrity verification at load time
- Training data provenance requirements
- Dependency pinning and scanning
- Model poisoning detection
- The provenance guarantee requirement for all deployed models
- Build-time council review of new model approvals

### 1.3 Out of Scope

This document does not cover:

- Runtime adversarial attack detection (see ANIF-848)
- Tool dependency security for agent tool integrations (see ANIF-845)
- Agent lifecycle state management (see ANIF-803)
- LLM agent manifest requirements (see ANIF-807)

### 1.4 Intended Audience

- AI engineers responsible for model deployment
- Security engineers managing the agent supply chain
- Build-time council members reviewing model approvals
- Conformance assessors evaluating supply chain security claims

---

## 2. Normative References

| Reference | Title |
|---|---|
| ANIF-807 | LLM Agent Specification |
| ANIF-820 | AI Agent Testing and Red-Team Standards |
| ANIF-835 | Security Monitoring and Alerting |
| ANIF-841 | AI Security Threat Model |
| ANIF-845 | Agent Supply Chain — Tool Dependencies |
| ANIF-901 | AI Council Overview |
| ANIF-903 | Build-Time Council |
| RFC 2119 | Key words for use in RFCs to Indicate Requirement Levels |

---

## 3. Terms and Definitions

| Term | Definition |
|---|---|
| Supply chain | The complete set of models, training data, dependencies, and deployment artefacts used to produce and deploy an agent |
| Model integrity hash | A SHA-256 cryptographic hash of a model file, used to verify that the file has not been modified since approval |
| Training data provenance | A documented record of data sources, collection dates, preprocessing steps, and anonymisation procedures for a training dataset |
| Poisoned model | A model that has been deliberately modified to exhibit malicious behaviour under specific trigger conditions |
| Dependency | A software library, framework, or package required by an agent's runtime environment |
| Provenance chain | A complete, unbroken record tracing a deployed model back to its governance-approved sources |
| Approved model registry | The governance-authorised list of model versions approved for deployment in ANIF environments |

---

## 4. Control 1 — Model Integrity Hashing

### 4.1 Requirement

A SHA-256 hash MUST be computed for every model file at the time of governance approval. The hash MUST be stored in the approved model registry by the build-time council.

At every load event — initial deployment, restart, or failover — the deployed model's hash MUST be computed and compared against the registry entry. A mismatch MUST halt the load process and MUST be treated as a Severity 1 security incident.

### 4.2 Hash Verification Process

1. The platform computes the SHA-256 hash of the model file being loaded.
2. The platform queries the approved model registry for the expected hash for the declared `llm_model_id`.
3. The hashes are compared.
4. If the hashes match, loading proceeds.
5. If the hashes do not match, loading is aborted, a security incident is raised, and the deployment is quarantined pending investigation.

### 4.3 Registry Integrity

The approved model registry itself MUST be stored with tamper-evident controls. The registry MUST be accessible to the platform in read-only mode. Write access to the registry MUST require build-time council authorisation and MUST be logged.

---

## 5. Control 2 — Training Data Provenance

### 5.1 Requirement

For every model in the approved model registry, a training data provenance record MUST exist and MUST be reviewed by the build-time council before the model is approved.

### 5.2 Provenance Record Schema

```yaml
model_id: string
provenance_record_id: UUID v4
data_sources:
  - source_name: string
    source_type: enum [public_dataset | licensed_dataset | proprietary | operational_data]
    collection_date_range: string (e.g., "2023-01 to 2024-06")
    url_or_reference: string
preprocessing_steps:
  - step: string
    description: string
anonymisation_applied: boolean
anonymisation_description: string
known_biases: string
data_exclusions: string
approved_by: string (build-time council member identity)
approval_date: ISO 8601
```

### 5.3 Operational Data Restriction

If operational network data (real topology, real traffic patterns, real incident data) was used in training, the provenance record MUST explicitly state:

- The anonymisation procedures applied
- The approval obtained from the data owning organisation
- The specific types of operational data included

Models trained on operational data without documented anonymisation MUST NOT be approved.

---

## 6. Control 3 — Dependency Security

### 6.1 Pinning Requirement

All software dependencies required by an agent's runtime MUST be pinned to exact versions. Floating version ranges (e.g., `>=1.2.0`, `^3.4`) are not permitted in agent dependency manifests.

### 6.2 Scanning Requirement

Before any agent deployment and after any dependency update, all dependencies MUST be scanned against:

- The National Vulnerability Database (NVD) for known CVEs
- The build-time council's internal exclusion list of known vulnerable packages

Dependencies with Critical (CVSS ≥ 9.0) or High (CVSS 7.0–8.9) severity CVEs MUST be updated or replaced before deployment. Deployment with unresolved Critical vulnerabilities is a conformance violation.

### 6.3 Software Bill of Materials

A Software Bill of Materials (SBOM) MUST be generated for every agent deployment and retained for the life of the deployment. The SBOM MUST list every dependency with its exact version and the build-time council's approval status.

---

## 7. Control 4 — Model Poisoning Detection

### 7.1 Requirement

Before approving a model for the registry, and after any model version update, the build-time council MUST conduct a model poisoning detection test.

### 7.2 Detection Method

Model poisoning detection MUST use a statistical comparison method that tests the candidate model's output distribution against a known-clean reference model of the same type. The test MUST:

1. Submit a representative set of at least 500 test inputs covering the model's intended use cases.
2. Compare the output distribution of the candidate model against the reference model using a statistical distance metric (Jensen-Shannon divergence or equivalent).
3. Record any outputs where the candidate model exhibits qualitatively different behaviour from the reference — categorised as anomalous outputs.

### 7.3 Pass Criteria

A model MUST be considered to have passed poisoning detection if:

- The statistical distance score is below 0.15
- The anomalous output rate is below 1%

A model that fails either criterion MUST be rejected from the approved model registry and MUST NOT be deployed.

### 7.4 Trigger-Based Poisoning

Standard statistical testing cannot detect trigger-based poisoning attacks where the model behaves normally except when a specific trigger input is present. Red-team testing (ANIF-820) provides a complementary control targeting trigger-based attacks. Both controls MUST be applied.

---

## 8. Control 5 — Provenance Guarantee

### 8.1 Requirement

No model MUST be deployed in a production ANIF environment without a complete provenance chain. A complete provenance chain means that every element of the model's origin is documented and has been reviewed by the build-time council:

- The model architecture and base training are documented
- All fine-tuning or adaptation steps are documented with data provenance records (section 5)
- The model file integrity hash is in the approved registry (section 4)
- All dependencies have passed security scanning (section 6)
- Poisoning detection has been conducted and passed (section 7)

### 8.2 Provenance Gap

Any gap in the provenance chain — any step where origin cannot be verified — MUST result in the model being classified as unverifiable. Unverifiable models MUST NOT be deployed.

### 8.3 Build-Time Council Approval

Before any model is added to the approved registry, the build-time council MUST conduct a formal review covering all five supply chain controls. The review outcome MUST be recorded as a signed council decision. Approval by a single council member is not sufficient — a quorum vote is required per ANIF-903.

---

## 9. Supply Chain Incident Response

### 9.1 Incident Classification

Supply chain compromise is classified as a Severity 1 security incident. Indicators of supply chain compromise include:

- Model integrity hash mismatch at load time
- Discovery of a backdoored dependency post-deployment
- Anomalous output pattern consistent with trigger-based poisoning
- Training data provenance record found to contain false information

### 9.2 Immediate Response

Upon detection of any supply chain compromise indicator:

1. The affected agent MUST be quarantined immediately (transition to QUARANTINED lifecycle state per ANIF-803).
2. The approved model registry entry for the affected model MUST be revoked.
3. The build-time council and AI Council MUST be notified within 1 hour.
4. All intents processed by the affected agent since its last successful integrity verification MUST be flagged for review.

---

## 10. Conformance Requirements

| ID | Requirement |
|---|---|
| CR-824-01 | A SHA-256 hash MUST be computed and stored in the approved model registry for every approved model version. |
| CR-824-02 | Hash verification MUST occur at every model load event. Hash mismatch MUST trigger a Severity 1 security incident. |
| CR-824-03 | A training data provenance record MUST exist for every model in the approved registry. |
| CR-824-04 | Models trained on operational data without documented anonymisation MUST NOT be approved. |
| CR-824-05 | All agent dependencies MUST be pinned to exact versions. |
| CR-824-06 | Deployment with unresolved Critical CVSS CVEs in dependencies is a conformance violation. |
| CR-824-07 | A poisoning detection test MUST be conducted before any model is approved or after any version update. |
| CR-824-08 | No model with a gap in its provenance chain MUST be deployed. |
| CR-824-09 | Build-time council approval requires a quorum vote, not single-member sign-off. |
| CR-824-10 | Supply chain compromise MUST result in immediate agent quarantine and registry revocation. |

---

## 11. Security Considerations

Supply chain attacks are increasingly sophisticated. The controls in this document address known attack vectors but cannot guarantee against novel techniques. The build-time council SHOULD maintain awareness of emerging supply chain attack patterns (e.g., new model poisoning techniques, novel dependency confusion attacks) and update these requirements accordingly.

---

## 12. Operational Considerations

The build-time council review process for new model approvals can be a bottleneck if not resourced adequately. Organisations SHOULD establish a standing council meeting cadence for model approvals and SHOULD plan model updates well in advance to avoid operational pressure to shortcut the review process.
