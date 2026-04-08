# ANIF-835: AI Vendor and Model Governance

| Field        | Value                                              |
|--------------|----------------------------------------------------|
| Doc ID       | ANIF-835                                           |
| Series       | AI Governance                                      |
| Version      | 0.1.0                                              |
| Status       | Draft                                              |
| Authors      | ANIF Working Group                                 |
| Reviewers    | —                                                  |
| Approved by  | —                                                  |
| Created      | 2026-04-08                                         |
| Last updated | 2026-04-08                                         |
| Replaces     | N/A                                                |
| Related docs | ANIF-824, ANIF-807, ANIF-830, ANIF-903             |

---

## Abstract

This document defines the governance requirements for selecting, evaluating, approving, and managing AI model vendors and the models they supply. Vendor selection MUST be assessed against five criteria: security, compliance, transparency, support SLAs, and exit strategy readiness. Every model MUST pass an evaluation checklist before first deployment. The version approval process ensures that model updates do not introduce regression or supply chain risk. Exit strategy requirements protect the organisation from vendor lock-in and ensure continuity if a vendor is discontinued or compromised.

---

## 1. Introduction

### 1.1 Purpose

AI models are a critical dependency in ANIF deployments. Vendor relationships and model versions require the same governance rigour as any other critical infrastructure dependency. This document establishes the standards for vendor selection, ongoing due diligence, model version management, and exit planning.

### 1.2 Scope

This document covers vendor selection criteria, model evaluation checklist, version approval, due diligence standards, and exit strategy requirements. It applies to all LLM and ML model vendors whose models are used in ANIF deployments.

### 1.3 Out of Scope

This document does not cover supply chain security technical controls (see ANIF-824) or agent manifest version pinning (see ANIF-807).

### 1.4 Intended Audience

- Procurement and vendor management teams
- AI Risk Officers conducting due diligence
- Build-time council members approving model versions
- Governance committee members overseeing vendor relationships

---

## 2. Normative References

| Reference | Title |
|---|---|
| ANIF-807 | LLM Agent Specification |
| ANIF-824 | Agent Supply Chain Security |
| ANIF-830 | AI Governance Overview |
| ANIF-903 | Build-Time Council |
| RFC 2119 | Key words for use in RFCs to Indicate Requirement Levels |

---

## 3. Vendor Selection Criteria

Vendors MUST be assessed against all five of the following criteria before any model from that vendor is approved for deployment.

### 3.1 Security

| Criterion | Requirement |
|---|---|
| Vulnerability disclosure | Vendor MUST maintain a published vulnerability disclosure programme |
| Security assessments | Vendor MUST provide evidence of third-party security assessments (SOC 2 Type II or equivalent) conducted within the last 12 months |
| Incident response | Vendor MUST provide a documented AI-specific incident response process and commit to notification within 24 hours of a confirmed security incident affecting deployed models |
| Model integrity | Vendor MUST provide cryptographic model file hashes for all model versions used in ANIF deployments |

### 3.2 Compliance

| Criterion | Requirement |
|---|---|
| Data processing | Vendor MUST provide a data processing agreement (DPA) acceptable under applicable privacy law |
| Regulatory alignment | Vendor MUST demonstrate alignment with EU AI Act obligations for high-risk AI system providers |
| Export controls | Vendor MUST confirm that model export does not violate applicable export control regulations |

### 3.3 Transparency

| Criterion | Requirement |
|---|---|
| Training data disclosure | Vendor MUST disclose the categories of training data used and any known biases or limitations |
| Model card | Vendor MUST provide a model card documenting intended use, limitations, and known failure modes |
| Explainability | Vendor MUST describe the mechanism by which the model's outputs can be explained to the degree required by ANIF-402 |

### 3.4 Support SLAs

| Criterion | Requirement |
|---|---|
| Version support | Vendor MUST commit to a minimum 12-month support lifecycle for each model version |
| Deprecation notice | Vendor MUST provide minimum 6 months' notice before deprecating a model version used in production |
| Incident support | Vendor MUST provide a support SLA committing to a response within 4 hours for Severity 1 production incidents |

### 3.5 Exit Strategy Readiness

| Criterion | Requirement |
|---|---|
| Data portability | Vendor MUST confirm that all inference logs and model outputs can be exported in a standard format |
| Transition period | Vendor MUST agree to provide a minimum 90-day transition period following contract termination during which API access remains available |
| Documentation | Vendor MUST provide documentation sufficient to replace their model with an equivalent from another vendor |

---

## 4. Model Evaluation Checklist

Before a model version is approved for the first time, the build-time council MUST complete the following evaluation:

| Check | Pass Criteria |
|---|---|
| Model card reviewed | Model card reviewed and limitations documented |
| Training data provenance | Provenance record completed per ANIF-824 |
| Poisoning detection | Statistical test passed per ANIF-824 |
| Red-team | Red-team engagement completed with no Critical findings |
| Ethics alignment | Model outputs assessed against ANIF-701 values; no systematic violations identified |
| Deterministic shadow | A companion deterministic shadow has been developed and tested |
| Capability declaration | Agent manifest completed with all required LLM fields per ANIF-807 |
| Vendor SLA | Vendor SLA confirmed as meeting section 3.4 requirements |

All checks MUST pass. A single failed check blocks model approval.

---

## 5. Version Approval Process

When a vendor releases a new model version:

1. The build-time council is notified.
2. The model evaluation checklist is re-run for the new version (full evaluation, not a delta).
3. The deterministic shadow is re-validated against the new version to confirm divergence rates remain acceptable.
4. The governance committee is informed of the version upgrade and its assessed impact.
5. The old version's support lifecycle is confirmed with the vendor.

Model version upgrades MUST NOT be deployed without completing all five steps.

---

## 6. Due Diligence Standards

### 6.1 Initial Due Diligence

Full due diligence against all five criteria MUST be conducted before a vendor is approved. Due diligence evidence MUST be documented and retained.

### 6.2 Annual Review

Vendor due diligence MUST be refreshed annually. Changes in vendor security posture, compliance status, or support commitments MUST be assessed against the selection criteria. A vendor that no longer meets any criterion MUST be placed on probation and a remediation timeline agreed within 30 days.

### 6.3 Material Change Review

Any material change in the vendor relationship — acquisition, change of ownership, significant product change — MUST trigger an immediate due diligence review.

---

## 7. Exit Strategy Requirements

### 7.1 Mandatory Exit Plan

For every vendor providing models used in production, a documented exit plan MUST exist and be reviewed annually. The exit plan MUST address:

- Identification of alternative models capable of replacing the vendor's model
- Timeline and steps to migrate to an alternative
- Data migration requirements
- Impact assessment on ANIF-conformant operations during transition

### 7.2 Exit Trigger Conditions

The exit plan MUST be activated if any of the following occur:

- Vendor confirms discontinuation of the model version in use
- A supply chain compromise is confirmed (ANIF-824)
- The vendor fails due diligence review and does not remediate within 60 days
- The vendor is acquired by an entity the governance committee determines poses an unacceptable risk

---

## 8. Conformance Requirements

| ID | Requirement |
|---|---|
| CR-835-01 | All five vendor selection criteria MUST be assessed before a vendor is approved. |
| CR-835-02 | The model evaluation checklist MUST be completed in full before any model version is approved for first deployment. |
| CR-835-03 | Model version upgrades MUST complete all five steps in section 5 before deployment. |
| CR-835-04 | Vendor due diligence MUST be refreshed annually. |
| CR-835-05 | A documented exit plan MUST exist for every production model vendor. |
| CR-835-06 | The exit plan MUST be activated within 5 business days of any exit trigger condition being met. |

---

## 9. Security Considerations

Vendor relationships are a supply chain security dependency. A vendor acquired by a hostile actor or a vendor whose staff have been compromised can introduce malicious model updates that pass all automated checks. The combination of integrity hashing (ANIF-824), red-team evaluation (ANIF-820), and governance committee oversight of vendor relationships provides defence in depth against this scenario.

---

## 10. Operational Considerations

Vendor due diligence cadence should be co-ordinated with contract renewal cycles where possible, reducing the operational overhead of separate governance reviews. Organisations SHOULD establish a vendor calendar that schedules due diligence reviews, contract renewals, and version support expiry monitoring in a single governance view.
