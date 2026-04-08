# ANIF-822: AI Observability and Model Health

| Field        | Value                                              |
|--------------|----------------------------------------------------|
| Doc ID       | ANIF-822                                           |
| Series       | AI Agent Architecture                              |
| Version      | 0.1.0                                              |
| Status       | Draft                                              |
| Authors      | ANIF Working Group                                 |
| Reviewers    | —                                                  |
| Approved by  | —                                                  |
| Created      | 2026-04-08                                         |
| Last updated | 2026-04-08                                         |
| Replaces     | N/A                                                |
| Related docs | ANIF-401, ANIF-402, ANIF-817, ANIF-837             |

---

## Abstract

This document defines five AI-specific observability metrics that MUST be collected and monitored in addition to the general observability requirements of ANIF-401. The five metrics — model drift score, hallucination rejection rate, confidence score trend, token usage anomalies, and recommendation acceptance rate — address failure modes specific to LLM-backed agents that general infrastructure monitoring cannot detect. Thresholds for each metric are defined. Alert conditions MUST be reported to the governance committee via the monthly AI governance report (ANIF-837).

---

## 1. Introduction

### 1.1 Purpose

General observability (ANIF-401) monitors whether agents are running and processing intents. AI-specific observability monitors whether agents are reasoning correctly. An agent can be operationally healthy — processing intents, emitting health signals, meeting latency SLAs — while its underlying model has drifted, its confidence is declining, or it is producing outputs that are systematically rejected. This document defines the metrics that detect those conditions.

### 1.2 Scope

This document covers:

- Five AI-specific observability metrics and their measurement definitions
- Alert thresholds for each metric
- Metric data flows to governance reporting
- Interaction with the general observability layer (ANIF-401)

### 1.3 Out of Scope

This document does not cover:

- General agent health signals and metrics (see ANIF-401)
- Explainability output format and API (see ANIF-402)
- AI cost metrics (see ANIF-817)
- Ethics audit trail metrics (see ANIF-724)

### 1.4 Intended Audience

- Platform engineers implementing AI-specific monitoring
- AI engineers interpreting model health signals
- Governance officers reviewing monthly AI health reports
- Conformance assessors evaluating AI observability claims

---

## 2. Normative References

| Reference | Title |
|---|---|
| ANIF-401 | Observability Standard |
| ANIF-722 | LLM Output Validation |
| ANIF-806 | Agent Observability Standard |
| ANIF-817 | AI Cost Optimisation and Governance |
| ANIF-837 | AI Governance Reporting |
| RFC 2119 | Key words for use in RFCs to Indicate Requirement Levels |

---

## 3. Terms and Definitions

| Term | Definition |
|---|---|
| Model drift | A gradual change in an LLM's output distribution relative to its baseline, indicating that the model's effective behaviour has shifted |
| Hallucination rejection rate | The proportion of LLM outputs that are rejected by the output validation stage (ANIF-722) due to fabricated content |
| Confidence score trend | The 7-day rolling average of the agent's self-reported confidence scores |
| Token usage anomaly | A token consumption event that deviates significantly from the agent's historical baseline |
| Recommendation acceptance rate | The proportion of Tier 2 agent recommendations that are accepted by the Tier 3 decision stage |
| Baseline period | The 30-day window of operation following initial deployment, used to establish normal behaviour benchmarks |

---

## 4. Metric 1 — Model Drift Score

### 4.1 Definition

The model drift score measures the rolling divergence between an agent's current output distribution and its established baseline distribution. It is expressed as a value between 0.0 (no drift) and 1.0 (complete divergence).

### 4.2 Measurement Method

Model drift is measured using a statistical distance metric (Jensen-Shannon divergence or equivalent) applied to the distribution of output categories over a rolling 7-day window compared to the baseline 30-day window.

Deployments MUST establish a baseline during the first 30 days of operation for each agent role. The baseline MUST be approved by the build-time council before drift monitoring begins.

### 4.3 Alert Thresholds

| Score | Status | Action |
|---|---|---|
| 0.00–0.10 | Normal | No action |
| 0.11–0.20 | Watch | Log for trend monitoring |
| 0.21–0.30 | Elevated | Notify AI engineering team for investigation |
| > 0.30 | Critical | Notify governance committee; consider model version review |

---

## 5. Metric 2 — Hallucination Rejection Rate

### 5.1 Definition

The hallucination rejection rate is the percentage of LLM outputs that are rejected by the output validation stage (ANIF-722) specifically due to references to non-existent network elements, fabricated policy clauses, or invented historical events.

### 5.2 Measurement Period

The rate MUST be calculated on a rolling 24-hour window per agent.

### 5.3 Alert Thresholds

| Rate | Status | Action |
|---|---|---|
| 0.0–1.0% | Normal | No action |
| 1.1–3.0% | Watch | Log; monitor for trend |
| 3.1–5.0% | Elevated | Notify AI engineering team; review recent model behaviour |
| > 5.0% | Critical | Notify governance committee; consider fallback to deterministic shadow |

A sustained rejection rate above 5% indicates a model in significant distress. The agent SHOULD be moved to deterministic shadow operation until the cause is determined.

---

## 6. Metric 3 — Confidence Score Trend

### 6.1 Definition

The confidence score trend is the 7-day rolling average of the LLM agent's self-reported confidence scores across all invocations.

### 6.2 Interpretation

A declining confidence score trend indicates that the model is encountering inputs outside its effective operating envelope more frequently. This may be caused by network environment changes that the model has not been updated to handle, or by model drift.

Both very high (> 0.95) and very low (< 0.60) sustained averages warrant investigation:

- A sustained average above 0.95 may indicate overconfidence and SHOULD be cross-checked against the deterministic shadow divergence rate.
- A sustained average below 0.60 indicates the model is consistently uncertain and the deployment SHOULD review whether the model tier is appropriate for the task.

### 6.3 Alert Thresholds

| 7-Day Average | Status | Action |
|---|---|---|
| 0.75–0.94 | Normal | No action |
| 0.60–0.74 | Watch | Monitor; review task complexity vs model tier |
| < 0.60 | Elevated | Notify AI engineering; consider model tier upgrade |
| > 0.95 (sustained 3+ days) | Watch | Cross-check against shadow divergence rate |

---

## 7. Metric 4 — Token Usage Anomalies

### 7.1 Definition

A token usage anomaly occurs when a single agent's token consumption within a 1-hour window exceeds 3 standard deviations above its historical mean for that window duration.

### 7.2 Significance

Abnormal token consumption may indicate:

- Adversarial probing — an attacker submitting intents designed to maximise LLM computation
- Runaway inference — a feedback loop causing the agent to invoke the LLM repeatedly
- Context management failure — context not being isolated per intent, causing accumulation

### 7.3 Alert Thresholds

| Deviation | Status | Action |
|---|---|---|
| < 2 std dev | Normal | No action |
| 2–3 std dev | Watch | Log; monitor for pattern |
| > 3 std dev | Alert | Notify AI engineering and security team; investigate cause |
| > 5 std dev | Critical | Notify governance committee; consider agent suspension pending investigation |

---

## 8. Metric 5 — Recommendation Acceptance Rate

### 8.1 Definition

The recommendation acceptance rate is the proportion of Tier 2 agent recommendations that proceed to execution (either auto-approved or human-approved) versus those that are rejected, modified, or cancelled.

### 8.2 Interpretation

Both very high and very low acceptance rates are signals that warrant investigation:

- A rate above 98% may indicate that human reviewers are rubber-stamping recommendations without substantive review, or that the risk scoring threshold for manual review is set too high.
- A rate below 60% indicates that Tier 2 recommendations are frequently wrong or misaligned with operator intent — the agent's policy bounds or decision logic SHOULD be reviewed.

### 8.3 Alert Thresholds

| Rate | Status | Action |
|---|---|---|
| 75–97% | Normal | No action |
| 60–74% | Watch | Log; review with AI engineering |
| < 60% | Elevated | Notify governance committee; trigger policy review |
| > 98% (sustained 7+ days) | Watch | Audit human review quality; verify reviewers are engaging substantively |

---

## 9. Metric Collection and Reporting

### 9.1 Collection Frequency

All five metrics MUST be collected and updated at a minimum interval of 5 minutes.

### 9.2 Observability Integration

All five metrics MUST be emitted to the general observability layer (ANIF-401) using the same metric emission protocol as standard agent health metrics, with `metric_category: ai_model_health` to distinguish them from operational metrics.

### 9.3 Governance Reporting

Monthly AI governance reports (ANIF-837) MUST include all five metrics with:

- 30-day trend chart per metric
- Count of alert threshold breaches per metric
- Actions taken in response to breaches
- Agent-level breakdown where multiple agent types are deployed

---

## 10. Conformance Requirements

| ID | Requirement |
|---|---|
| CR-822-01 | All five AI-specific observability metrics MUST be collected at a minimum interval of 5 minutes. |
| CR-822-02 | A baseline period of 30 days MUST be established for each agent role before drift monitoring begins. |
| CR-822-03 | All five metrics MUST be emitted to the general observability layer with `metric_category: ai_model_health`. |
| CR-822-04 | Critical threshold breaches MUST result in governance committee notification. |
| CR-822-05 | Monthly AI governance reports MUST include all five metrics per the requirements of section 9.3. |

---

## 11. Security Considerations

Model health metrics themselves can be used by an attacker to understand the system's current state and calibrate attacks to stay below alert thresholds. Access to real-time model health dashboards MUST be restricted to authorised personnel. Aggregate trend data for governance reporting is appropriate for wider distribution, but real-time metric streams SHOULD be treated as operational security data.

---

## 12. Operational Considerations

The five metrics defined here require a 30-day baseline period to be meaningful. Deployments that have not completed the baseline period MUST NOT suppress alerts on the grounds that thresholds are not yet calibrated — they SHOULD apply conservative default thresholds during the baseline period and refine them once the baseline is established.
