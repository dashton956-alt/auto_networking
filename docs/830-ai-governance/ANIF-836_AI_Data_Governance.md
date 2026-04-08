# ANIF-836: AI Data Governance

| Field        | Value                                              |
|--------------|----------------------------------------------------|
| Doc ID       | ANIF-836                                           |
| Series       | AI Governance                                      |
| Version      | 0.1.0                                              |
| Status       | Draft                                              |
| Authors      | ANIF Working Group                                 |
| Reviewers    | —                                                  |
| Approved by  | —                                                  |
| Created      | 2026-04-08                                         |
| Last updated | 2026-04-08                                         |
| Replaces     | N/A                                                |
| Related docs | ANIF-106, ANIF-202, ANIF-714, ANIF-824             |

---

## Abstract

This document defines the data governance requirements specific to AI systems within an ANIF-conformant deployment. Training data MUST meet defined quality standards for completeness, freshness, diversity, and bias detection. Every training dataset MUST have a lineage record traceable to its original source. Consent and privacy governance applies to network telemetry used in training. Retention governance for AI-related data is defined separately from general operational data retention and MUST be applied in addition to it.

---

## 1. Introduction

### 1.1 Purpose

AI systems are data-dependent in ways that general IT systems are not. The quality, origin, and governance of training data directly determines model behaviour. Poor data governance produces biased, unreliable, or privacy-non-compliant models. This document establishes the normative data governance requirements that underpin reliable, compliant AI deployment.

### 1.2 Scope

Training data quality standards, lineage requirements, privacy governance for network telemetry, and AI-specific data retention requirements.

### 1.3 Out of Scope

General operational data retention (see ANIF-107), data architecture (see ANIF-202), and privacy and data ethics policy (see ANIF-714).

### 1.4 Intended Audience

- Data engineers building training pipelines
- Data Protection Officers advising on privacy compliance
- AI Risk Officers managing data governance risk
- Conformance assessors evaluating data governance claims

---

## 2. Normative References

| Reference | Title |
|---|---|
| ANIF-106 | Data Residency and Compliance Policy |
| ANIF-202 | Data Architecture |
| ANIF-714 | Privacy and Data Ethics Policy |
| ANIF-824 | Agent Supply Chain Security |
| RFC 2119 | Key words for use in RFCs to Indicate Requirement Levels |

---

## 3. Training Data Quality Standards

### 3.1 Completeness

Training datasets MUST be assessed for completeness before use. Completeness is defined as: the proportion of expected data fields that are populated with valid values. Datasets with completeness below 85% MUST NOT be used without documented justification and governance committee approval.

### 3.2 Freshness

Training data MUST be assessed for temporal relevance. For network pattern and operational knowledge, data older than 24 months MUST be excluded or flagged for assessment of continued relevance. The currency of training data MUST be documented in the provenance record (ANIF-824).

### 3.3 Diversity

Training datasets MUST be assessed for representativeness. A dataset is considered insufficiently diverse if it is dominated by data from a single:

- Time period (e.g., only holiday traffic patterns)
- Network domain (e.g., only data centre traffic)
- Incident type (e.g., only link failure scenarios)

Insufficient diversity MUST be documented in the provenance record and the model card MUST declare the known gap.

### 3.4 Bias Detection

Every training dataset MUST undergo bias detection before use. Bias detection MUST assess:

- Systematic under-representation of specific network topologies, device types, or service classes
- Skew toward outcomes that favour specific vendors or configurations
- Historical bias that may perpetuate past suboptimal operational patterns

Detected biases MUST be documented. Biases that cannot be corrected before training MUST be disclosed in the model card.

---

## 4. Data Lineage Requirements

### 4.1 Lineage Record Requirement

Every training dataset MUST have a lineage record that is maintained alongside the training data provenance record (ANIF-824). The lineage record MUST be traceable from the final training dataset back to each original source.

### 4.2 Lineage Record Contents

| Field | Description |
|---|---|
| `source_system` | The system from which the data was collected |
| `collection_method` | How the data was collected (API export, direct query, file transfer) |
| `collection_date` | Date the data was collected |
| `transformations_applied` | List of transformations from raw data to training format |
| `anonymisation_applied` | Whether and how personally identifiable or sensitive data was anonymised |
| `approved_by` | Named governance approver |

### 4.3 Lineage Gap Policy

Any gap in the lineage — any data that cannot be traced to its source — MUST result in that data being excluded from the training dataset. Lineage-incomplete datasets MUST NOT be approved for model training.

---

## 5. Privacy Governance for Network Telemetry

### 5.1 Applicability

Network telemetry used in model training may contain personal data where telemetry includes user-identifiable information such as: device identifiers linkable to individuals, location data, or traffic content.

### 5.2 Requirements

Where network telemetry may contain personal data:

- A Data Protection Impact Assessment (DPIA) MUST be conducted before the telemetry is used in training.
- The DPO MUST sign off on the DPIA before training data preparation begins.
- Anonymisation MUST be applied to remove or irreversibly pseudonymise personal data before training.
- The anonymisation method MUST be documented in the provenance record.

Telemetry that has not been assessed for personal data content MUST be treated as containing personal data until assessed otherwise.

---

## 6. AI-Specific Data Retention

### 6.1 Retention Categories

AI data retention requirements apply to categories that are distinct from general operational data and MUST be applied in addition to ANIF-107 requirements:

| Data Category | Minimum Retention Period |
|---|---|
| Training datasets (approved versions) | 5 years from model retirement |
| Training data provenance records | 5 years from model retirement |
| Data lineage records | 5 years from model retirement |
| Model evaluation records (bias checks, quality assessments) | 5 years from model retirement |
| Inference logs (inputs and outputs, sanitised) | 2 years |
| Knowledge package records (ANIF-812) | 3 years |

### 6.2 Retention Independence

AI data retention schedules MUST be managed independently of general operational data retention. An operational data purge MUST NOT delete data that is still within its AI-specific retention period.

### 6.3 Deletion on Retirement

When a model is permanently retired and its retention period expires, associated training data and provenance records MAY be deleted. Deletion MUST be recorded in an audit log.

---

## 7. Conformance Requirements

| ID | Requirement |
|---|---|
| CR-836-01 | Training datasets with completeness below 85% MUST NOT be used without governance committee approval. |
| CR-836-02 | Training data older than 24 months MUST be excluded or formally assessed for continued relevance. |
| CR-836-03 | Bias detection MUST be conducted on every training dataset before use. |
| CR-836-04 | Every training dataset MUST have a complete lineage record. Lineage-incomplete datasets MUST NOT be approved. |
| CR-836-05 | Network telemetry that may contain personal data MUST undergo DPIA and DPO sign-off before training use. |
| CR-836-06 | AI-specific retention periods MUST be maintained independently from general operational data retention. |

---

## 8. Security Considerations

Training data is a high-value target. Its modification can persistently alter model behaviour. Access to training data storage MUST be restricted to authorised training pipeline processes. All access MUST be logged. Lineage records are equally sensitive — they describe the attack surface for training data poisoning.

---

## 9. Operational Considerations

Training data governance overhead grows with the number of models in deployment. Organisations with multiple agent types SHOULD establish a centralised data governance function rather than managing training data governance independently per model. A centralised function also simplifies regulatory audit responses.
