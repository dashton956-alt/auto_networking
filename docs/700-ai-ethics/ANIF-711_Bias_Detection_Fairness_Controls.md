# ANIF-711: Bias Detection & Fairness Controls

| Field        | Value                                              |
|--------------|----------------------------------------------------|
| Doc ID       | ANIF-711                                           |
| Series       | AI Ethics                                          |
| Version      | 0.1.0                                              |
| Status       | Draft                                              |
| Authors      | ANIF Working Group                                 |
| Reviewers    | —                                                  |
| Approved by  | —                                                  |
| Created      | 2026-04-07                                         |
| Last updated | 2026-04-07                                         |
| Replaces     | N/A                                                |
| Related docs | ANIF-703, ANIF-710, ANIF-723, ANIF-304, ANIF-307  |

---

## Abstract

This document defines the operational policy for detecting and responding to the four bias types defined in ANIF-703, and specifies the canonical state freshness gate that blocks decisions based on stale ground truth data. Detection methods are defined per bias type with explicit alert thresholds. Policy responses specify the minimum action required when detection fires. The technical enforcement of fairness at decision time is defined in ANIF-723.

---

## 1. Introduction

### 1.1 Purpose

Detecting bias in AI systems requires different methods for different bias types. A statistical distribution check that detects resource allocation bias does not detect LLM reasoning bias. This document provides a concrete detection method and policy response for each of the four bias types in ANIF-703, along with the canonical state freshness gate that addresses ground process bias at its source.

### 1.2 Scope

This document covers:

- Detection method and alert threshold for each of the four bias types
- The canonical state freshness gate specification
- Minimum policy responses when detection fires
- Cadence requirements for each detection method
- Integration with governance reporting

### 1.3 Out of Scope

This document does not cover:

- The principles underlying bias and fairness (see ANIF-703)
- Technical enforcement of fairness at decision time (see ANIF-723)
- Training data governance (see ANIF-836)
- Statistical methodology beyond what is defined here

### 1.4 Intended Audience

- AI platform engineers implementing bias detection pipelines
- Data scientists calibrating detection thresholds
- Ethics officers reviewing bias detection results
- Governance committee members receiving quarterly reports

---

## 2. Normative References

- ANIF-703 — Bias and Fairness Principles
- ANIF-307 — Distributed Source of Truth
- ANIF-304 — Risk and Trust Quantification
- ANIF-723 — Fairness Enforcement Controls
- ANIF-836 — AI Data Governance
- ANIF-837 — AI Governance Reporting and Metrics
- RFC 2119 — Key words for use in RFCs to indicate requirement levels

---

## 3. Terms and Definitions

**Rolling window:** A time-based sliding window over which statistical metrics are computed. The window moves forward in time as new data arrives. Window sizes are specified per detection method.

**SLA-weighted baseline:** The expected distribution of resource allocation outcomes when each service receives resources proportional to its declared SLA tier. Used as the reference point for resource allocation bias detection.

**Freshness score:** A metric indicating how recently a canonical state data source was successfully read. Defined in ANIF-603. Range: 0.0 (never read or read indefinitely long ago) to 1.0 (read within the freshness window).

**Detection signal:** A metric value that exceeds the defined alert threshold for a bias type, indicating that investigation is required. A detection signal does not require proof of causation — it requires a response.

---

## 4. Bias Detection Methods

### 4.1 Resource Allocation Bias Detection

**What it detects:** Systematic preference for certain network segments, regions, or services in resource allocation decisions, inconsistent with SLA-weighted entitlements.

**Method:** Statistical distribution check comparing actual resource allocation outcomes against the SLA-weighted baseline over a rolling 24-hour window.

For each resource allocation action in the window:
1. Compute the SLA-weighted expected allocation for each affected service
2. Compute the actual allocation outcome
3. Compute the deviation: `deviation = |actual_allocation - expected_allocation| / expected_allocation`
4. Aggregate deviations per service tier over the window

**Alert threshold:** If the mean deviation for any SLA tier exceeds 15% over the 24-hour window, a detection signal MUST be raised.

**Cadence:** Continuous. The rolling window recalculates with every new resource allocation action.

**Data requirement:** SLA tier metadata for all services MUST be present in canonical state. Services without declared SLA tiers MUST be flagged for classification before their allocation decisions are included in detection.

---

### 4.2 Training Data Bias Detection

**What it detects:** Agent recommendations that reflect historical human operator preferences rather than objectively optimal network decisions.

**Method:** Comparison of agent recommendation distribution against operator-approved baseline decisions over a rolling 7-day window, controlling for network state inputs.

For each agent recommendation in the window:
1. Record the recommended action, target, and the network state inputs that produced it
2. Compare the recommendation distribution against the approved baseline for similar network states
3. Compute the divergence score: proportion of recommendations that differ from baseline for matched network states

**Alert threshold:** If the divergence score exceeds 10% over the 7-day window, a detection signal MUST be raised.

**Cadence:** Weekly review minimum. Continuous monitoring where compute permits.

**Baseline maintenance:** The operator-approved baseline MUST be reviewed and updated at least quarterly. A stale baseline (older than 90 days without review) reduces the validity of this detection method and MUST be flagged in governance reports.

---

### 4.3 LLM Reasoning Bias Detection

**What it detects:** LLM components producing outputs skewed by training corpus patterns irrelevant to the network management context.

**Method:** Output diversity check and canonical state grounding check.

**Output diversity check:** If an LLM produces outputs with identical or near-identical reasoning (cosine similarity > 0.95) for two inputs that differ meaningfully in network state, a detection signal MUST be raised. Identical reasoning for different inputs indicates the LLM is not using the input to discriminate — it is applying a fixed pattern.

**Canonical state grounding check:** LLM outputs that reference network protocols, device types, or configuration patterns not present in canonical state MUST be flagged. References to non-existent elements are an indicator of training corpus bias overriding ground truth.

**Alert threshold:** Three identical-reasoning events within a 1-hour window, or two canonical state grounding failures within a 1-hour window.

**Cadence:** Continuous during LLM-involved pipeline executions.

---

### 4.4 Ground Process Bias Detection

**What it detects:** Canonical state that is systematically skewed due to data source coverage gaps, causing decisions to be made on an unrepresentative picture of the network.

**Method:** Data source coverage check against the registered device inventory.

For each decision:
1. Identify all canonical state sources contributing to the decision
2. Check coverage: what percentage of registered devices in the affected segments are represented in the contributing sources
3. Check vendor and region distribution: are all vendor types and regions proportionally represented

**Alert threshold:** If fewer than 90% of registered devices in the affected segment are represented in canonical state, or if any single vendor or region accounts for more than 60% of contributing data points when the network has more balanced topology, a detection signal MUST be raised.

**Cadence:** Per-decision check as part of the canonical state freshness gate (section 5).

---

## 5. Canonical State Freshness Gate

The freshness gate is a mandatory blocking check that runs before any decision that uses canonical state. It addresses ground process bias at its source by refusing to make decisions on stale data.

### 5.1 Gate Specification

Before any decision-time use of canonical state data:

1. Compute the freshness score for every canonical state source that contributes to the decision
2. Identify sources with a freshness score below 0.6
3. If any contributing source has a freshness score below 0.6: block the decision and route to `manual_review`
4. If insufficient fresh sources remain to support a complete decision: block the decision and route to `manual_review`
5. If all contributing sources have freshness scores ≥ 0.6: proceed

### 5.2 Gate Behaviour

The freshness gate MUST block — it does not warn. A decision that proceeds with a stale source has no protection against ground process bias. The gate is non-configurable. An organisation MUST NOT modify the 0.6 threshold to a lower value.

An organisation MAY configure a stricter threshold (higher than 0.6) for specific segments or environments. Carrier-grade segments SHOULD use a freshness threshold of 0.8 or higher.

### 5.3 Stale Source Logging

Every blocked decision MUST log: the source identifier, the freshness score, the decision that was blocked, and the intent_id. This log feeds governance reporting (ANIF-837) to identify systematic data collection issues.

### 5.4 Gate Position

The freshness gate runs after intent validation and before policy check. Position in pipeline: see ANIF-720 safeguard architecture.

---

## 6. Policy Responses

When a detection signal fires for any bias type, the following minimum responses apply. Organisations MAY implement stricter responses.

| Bias Type | Detection Signal | Minimum Response |
|---|---|---|
| Resource allocation bias | Mean deviation > 15% over 24h | Suspend automated resource allocation decisions for affected segment. Notify governance committee. Human review required before resuming |
| Training data bias | Divergence > 10% over 7 days | Flag agent for build-time council review. Human oversight required for all recommendations from flagged agent until council clears it |
| LLM reasoning bias | Threshold events within window | Route to `manual_review` for all subsequent decisions from the LLM component within the current window. Log as potential Severity 3 ethics drift |
| Ground process bias | Coverage < 90% or distribution skew | Block the specific decision via freshness gate. Flag data collection gap to the data governance function (ANIF-836) |

---

## 7. Governance Reporting Integration

Bias detection results MUST feed the monthly governance committee report (ANIF-837). Each report MUST include:

- Count of detection signals per bias type over the reporting period
- Number of decisions blocked by the freshness gate
- Agent-level summary of training data bias divergence scores
- Status of baseline maintenance (date of last baseline review)
- Open investigations resulting from detection signals

---

## 8. Conformance Requirements

An implementation MUST run the canonical state freshness gate before every decision. The freshness threshold of 0.6 MUST NOT be lowered by configuration.

An implementation MUST run resource allocation bias detection continuously with a maximum 24-hour rolling window.

An implementation MUST NOT allow a detection signal to be dismissed without a logged human decision and reason.

Bias detection results MUST be included in monthly governance reports.

---

## 9. Security Considerations

The canonical state freshness gate can be attacked by suppressing telemetry from specific devices, causing their freshness scores to drop and triggering gate failures. Systematic freshness gate failures concentrated on specific device types or regions SHOULD be treated as a potential active attack and escalated to the security monitoring function per ANIF-846.

---

## 10. Operational Considerations

Detection thresholds SHOULD be calibrated for the specific network environment during the initial deployment period. A threshold that produces too many false positives will be suppressed in practice; one that is too permissive will miss real bias. The AI Ethics Officer (ANIF-838) SHOULD review threshold calibration during the first 90 days of production operation and annually thereafter.

---

## Appendix A: Change History

| Version | Date | Author | Changes |
|---|---|---|---|
| 0.1.0 | 2026-04-07 | ANIF Working Group | Initial draft |
