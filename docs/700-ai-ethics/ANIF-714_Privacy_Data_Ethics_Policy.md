# ANIF-714: Privacy & Data Ethics Policy

| Field        | Value                                              |
|--------------|----------------------------------------------------|
| Doc ID       | ANIF-714                                           |
| Series       | AI Ethics                                          |
| Version      | 0.1.0                                              |
| Status       | Draft                                              |
| Authors      | ANIF Working Group                                 |
| Reviewers    | —                                                  |
| Approved by  | —                                                  |
| Created      | 2026-04-07                                         |
| Last updated | 2026-04-07                                         |
| Replaces     | N/A                                                |
| Related docs | ANIF-106, ANIF-710, ANIF-806, ANIF-816, ANIF-836, ANIF-851 |

---

## Abstract

This document governs privacy obligations for network telemetry processed by AI components. It defines anonymisation requirements, data residency enforcement for AI training and inference, PII retention prohibitions, and purpose limitation for operational data. These obligations apply in addition to the data residency policy in ANIF-106 and the data governance requirements in ANIF-836. Compliance mappings to GDPR, HIPAA, and CCPA are in ANIF-851.

---

## 1. Introduction

### 1.1 Purpose

AI systems that process network telemetry have access to data that can indirectly reveal information about individual users, devices, and organisational behaviour. Network flow data, DNS queries, and application traffic patterns are not inherently personal data — but they can become so when correlated, retained, or used in contexts beyond their original collection purpose.

This document establishes the privacy obligations that apply specifically to AI components processing network telemetry. It does not replace general data protection obligations — it adds AI-specific obligations on top of them.

### 1.2 Scope

This document covers:

- Telemetry anonymisation requirements before AI processing
- Data residency enforcement for AI training and inference workloads
- PII retention prohibition in AI memory and training data
- Purpose limitation for operational telemetry
- Cross-region data transfer governance

### 1.3 Out of Scope

This document does not cover:

- General data residency policy for non-AI workloads (see ANIF-106)
- Training data quality standards (see ANIF-836)
- Agent memory isolation (see ANIF-806)
- Context window data handling (see ANIF-816)
- Regulatory compliance specifics (see ANIF-851)

### 1.4 Intended Audience

- AI engineers handling network telemetry in training and inference pipelines
- Data protection officers reviewing AI data practices
- Compliance officers mapping obligations to GDPR, HIPAA, and CCPA
- Platform architects designing telemetry collection and processing pipelines

---

## 2. Normative References

- ANIF-106 — Data Residency and Compliance Policy
- ANIF-806 — Agent Memory and State
- ANIF-816 — Context Window Management
- ANIF-836 — AI Data Governance
- ANIF-851 — Industry Compliance Framework Mapping
- RFC 2119 — Key words for use in RFCs to indicate requirement levels

---

## 3. Terms and Definitions

**Network telemetry:** Data collected from network infrastructure including flow records, packet samples, device metrics, routing state, and application traffic metadata.

**PII-adjacent data:** Network telemetry that does not directly identify an individual but that, when combined with other available data, could enable identification. Examples: persistent device identifiers, MAC addresses, user-agent strings, application session tokens.

**Anonymisation:** The irreversible transformation of data such that individuals cannot be re-identified from the anonymised data or from a combination of the anonymised data with other reasonably available information.

**Pseudonymisation:** The replacement of identifying fields with artificial identifiers (tokens or hashes). Pseudonymised data remains personal data because re-identification is possible with the mapping key. Pseudonymisation does not satisfy the anonymisation requirement in this document.

**Purpose limitation:** The principle that data collected for one purpose MUST NOT be used for a different purpose without explicit governance approval.

---

## 4. Telemetry Anonymisation

### 4.1 Anonymisation Requirement

Network telemetry MUST be anonymised before it is ingested into any AI training pipeline or used in any AI inference context where it would be retained beyond the scope of a single intent.

Anonymisation MUST occur at the collection point — not post-collection, not at the point of ingestion into the AI pipeline. Retaining unanonymised telemetry and anonymising it before model training does not satisfy this requirement if the unanonymised data is retained in a form accessible to AI components.

### 4.2 Required Anonymisation Steps

Anonymisation MUST remove or irreversibly transform the following fields:

| Field Category | Examples | Transformation Required |
|---|---|---|
| IP addresses | Source IP, destination IP, next-hop IP | Replace with zone identifier or hash. Original MUST NOT be recoverable |
| MAC addresses | Source MAC, destination MAC | Replace with anonymised device identifier |
| Device hostnames | Router names, server FQDNs, management names | Replace with anonymised device identifier |
| User identifiers | Username in flow metadata, Active Directory identifiers | Remove entirely |
| Session tokens | Application session IDs, authentication tokens | Remove entirely |
| Application identifiers | Application names in DPI data, process identifiers | Replace with category identifier (e.g., "video-streaming") |

### 4.3 Anonymisation Is Not Pseudonymisation

Replacing an IP address with a consistent hash of that IP address is pseudonymisation, not anonymisation. A consistent hash allows correlation across records and can be reversed given the original IP. Anonymisation requires that the mapping between the original value and the transformed value be destroyed or made practically unrecoverable.

Where correlation across records is required for AI training (for example, to train on traffic flow sequences), a session-scoped token MUST be used: a token generated fresh for each collection session, without a persistent mapping to any original identifier.

### 4.4 Anonymisation Verification

Anonymisation processes MUST be verified at implementation and re-verified whenever the telemetry collection pipeline changes. Verification confirms that: (a) all required fields are transformed, and (b) the transformation is not reversible using data available to AI components.

---

## 5. Data Residency Enforcement

### 5.1 Training Data Residency

AI training data derived from network telemetry MUST be processed in the region declared in the `allowed_zones` constraint of the originating intent. Training workloads MUST NOT process data from a region in a different zone.

Where network telemetry is collected globally but training is conducted in a specific region, only telemetry collected within that region's declared zones MAY be used in the regional training pipeline.

### 5.2 Inference Data Residency

Real-time telemetry used in AI inference (for example, canonical state injected into an LLM prompt context) MUST NOT be transferred to a processing region that is not permitted under the `allowed_zones` constraint for the active intent.

### 5.3 Cross-Region Transfer

Cross-region transfer of AI training data is prohibited unless:

1. Explicit governance approval has been obtained from the governance committee
2. The transfer is documented in the AI data governance register (ANIF-836)
3. Appropriate data transfer mechanisms are in place (e.g., Standard Contractual Clauses for EU data)
4. The transfer is logged with the approver identity, transfer date, destination region, and data description

Cross-region transfers that are not approved and logged are a conformance violation and MUST be treated as a data incident.

---

## 6. PII Retention Prohibition

### 6.1 No PII in AI Memory

PII and PII-adjacent data MUST NOT be retained in any AI agent memory store — working memory, episodic memory, or knowledge base — beyond the scope of the intent that caused its collection.

The intent scope ends when the intent reaches a terminal state (COMPLETED, FAILED, or CANCELLED). After this point, any working memory containing PII MUST be cleared. This requirement aligns with the working memory clearing obligation in ANIF-806.

### 6.2 No PII in Training Data

PII and PII-adjacent data MUST NOT appear in AI training datasets after anonymisation has been applied. Training datasets MUST be verified as PII-free before use. Verification MUST include automated scanning for known PII patterns and a human review sample for datasets above 1 million records.

### 6.3 Detection and Response

If PII is detected in an AI memory store or training dataset:

1. The affected memory or dataset MUST be quarantined immediately
2. The incident MUST be reported to the Data Protection Officer within 24 hours
3. If the PII relates to EU data subjects and a breach is confirmed: the incident MUST be reported per the GDPR breach notification obligations in ANIF-851
4. The root cause (how PII entered the AI pipeline despite anonymisation) MUST be investigated

---

## 7. Purpose Limitation

### 7.1 Network Management Only

Telemetry collected for network management MUST NOT be used for any purpose beyond network management without explicit governance approval. Uses beyond network management include but are not limited to:

- Training general-purpose AI models not specific to network management
- Providing telemetry data to third parties for commercial purposes
- Using network telemetry to infer user behaviour patterns for non-network purposes
- Building user profiles from network traffic data

### 7.2 Approval Process

Use of operational network telemetry for a purpose beyond network management MUST be approved by:

1. The Data Protection Officer
2. The governance committee (ANIF-831)
3. The AI Ethics Officer (ANIF-838)

The approval MUST be documented with the purpose, data scope, retention period, and any conditions applied.

### 7.3 Telemetry Shared with LLM Providers

Where network telemetry is injected into prompts submitted to an LLM provider's API, the data MUST be anonymised before submission. The LLM provider's data retention and training policies MUST be reviewed as part of vendor governance (ANIF-835) to ensure that submitted prompt data is not retained for provider model training without consent.

---

## 8. Conformance Requirements

Telemetry MUST be anonymised before ingestion into AI training pipelines. Anonymisation MUST occur at the collection point.

Cross-region transfers of AI training data MUST be governance-approved and logged.

PII MUST NOT be present in AI agent memory stores after intent completion.

Purpose limitation violations — using network telemetry for non-network-management purposes without approval — are a Severity 2 ethics incident.

---

## 9. Security Considerations

Unanonymised network telemetry in an AI pipeline is a high-value target for adversaries seeking to identify network topology, user behaviour, or organisational structure. Anonymisation reduces the value of any data breach. Data residency enforcement reduces cross-border legal exposure. Both also reduce the harm from insider threats with access to AI training infrastructure.

---

## 10. Operational Considerations

Data Protection Officers SHOULD be involved in the review of any new AI data pipeline that processes network telemetry. Annual privacy impact assessments SHOULD be conducted for all AI components that process telemetry, with particular attention to anonymisation effectiveness and purpose limitation adherence.

---

## Appendix A: Change History

| Version | Date | Author | Changes |
|---|---|---|---|
| 0.1.0 | 2026-04-07 | ANIF Working Group | Initial draft |
