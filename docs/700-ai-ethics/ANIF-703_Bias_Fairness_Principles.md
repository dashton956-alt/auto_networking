# ANIF-703: Bias & Fairness Principles

| Field        | Value                                              |
|--------------|----------------------------------------------------|
| Doc ID       | ANIF-703                                           |
| Series       | AI Ethics                                          |
| Version      | 0.1.0                                              |
| Status       | Draft                                              |
| Authors      | ANIF Working Group                                 |
| Reviewers    | —                                                  |
| Approved by  | —                                                  |
| Created      | 2026-04-07                                         |
| Last updated | 2026-04-07                                         |
| Replaces     | N/A                                                |
| Related docs | ANIF-701, ANIF-711, ANIF-723, ANIF-836             |

---

## Abstract

This document defines the four bias types that AI agents in autonomous networking environments are susceptible to, establishes the ANIF definition of fairness in networking contexts, and sets the principle that fairness means proportional to declared SLA obligations — not equal allocation. The operational controls that enforce these principles are defined in ANIF-711 and ANIF-723.

---

## 1. Introduction

### 1.1 Purpose

Bias in AI systems is well-documented in general AI literature. In networking contexts, bias takes specific forms that general frameworks do not address. An AI agent that consistently routes traffic sub-optimally for one region, or that makes recommendations based on training data that over-represents certain network conditions, causes real service degradation for real users.

This document provides the conceptual foundation for the bias detection and fairness enforcement controls that follow in ANIF-711 and ANIF-723.

### 1.2 Scope

This document covers:

- The ANIF definition of fairness in networking contexts
- The four bias types applicable to autonomous networking AI
- The principle that fairness is SLA-proportional, not equal
- The obligation to audit resource allocation decisions for bias
- The relationship between fairness and the Justice value in ANIF-701

### 1.3 Out of Scope

This document does not cover:

- Bias detection methods or algorithms (see ANIF-711)
- Technical enforcement of fairness at decision time (see ANIF-723)
- Training data governance for AI models (see ANIF-836)
- Statistical methods for bias measurement

### 1.4 Intended Audience

- AI engineers building agents that make resource allocation decisions
- Ethics officers and governance reviewers
- Build-time council members reviewing agent designs (ANIF-903)
- Auditors verifying fairness compliance

---

## 2. Normative References

- ANIF-701 — Ethics Constitution and Core Values
- ANIF-711 — Bias Detection and Fairness Controls
- ANIF-723 — Fairness Enforcement Controls
- ANIF-836 — AI Data Governance
- RFC 2119 — Key words for use in RFCs to indicate requirement levels

---

## 3. Terms and Definitions

**Fairness (ANIF definition):** Resource allocation and action selection that is proportional to the SLA tier declared for each service. Equal allocation across services of different SLA tiers is not fair — it under-serves high-tier services and over-serves low-tier ones relative to their commitments.

**SLA floor:** The minimum resource allocation a service MUST receive, derived from its declared `availability_percent` constraint. The SLA floor is defined as 80% of the declared availability target.

**Systematic bias:** A consistent pattern of deviation in agent outputs that advantages or disadvantages specific network segments, services, or tenants in a manner inconsistent with their declared SLA tiers.

**Ground truth:** The canonical state of the network as maintained by the distributed source-of-truth system defined in ANIF-307. Decisions made on stale or partial ground truth are susceptible to ground process bias.

---

## 4. ANIF Definition of Fairness

Fairness in networking is not equality. Two services with different SLA commitments have different entitlements. Treating them equally would breach the higher-tier service's SLA while over-provisioning the lower-tier one.

Fairness in ANIF means: **every service receives resources and priority proportional to its declared SLA tier.**

An agent that allocates resources equally across all services, regardless of SLA tier, is not fair — it is indifferent. An agent that allocates resources proportionally to declared SLA tiers, such that every service meets its committed availability target, is fair.

This definition has two consequences:

1. Fairness checks MUST use SLA tier as the reference point, not raw resource counts.
2. An agent that improves overall network efficiency while causing one high-tier service to fall below its SLA floor has violated the Justice value (ANIF-701) regardless of the aggregate outcome.

---

## 5. Four Bias Types

### 5.1 Resource Allocation Bias

**Definition:** Systematic preference for certain network segments, regions, or services in resource allocation decisions, regardless of SLA weight.

**Example:** An agent consistently routes high-bandwidth traffic through one regional hub, starving other regions of equal or higher SLA tier of the capacity they are entitled to. The agent may be optimising for a metric (total throughput) that is not aligned with SLA-weighted allocation.

**Detection signal:** Statistical distribution of resource allocation across SLA tiers deviating from the SLA-weighted baseline over a rolling window.

**Root causes:** Training data that over-represents certain topologies; objective functions that do not incorporate SLA weighting; canonical state that does not include accurate SLA tier metadata.

### 5.2 Training Data Bias

**Definition:** Historical data used to train agents reflects past human decisions that were themselves biased, causing the agent to inherit and perpetuate those biases.

**Example:** An agent trained on historical NOC decisions inherits operator preferences for certain vendors, certain protocols, or certain network paths — not because those are objectively better, but because past operators happened to favour them. The agent treats historical preference as ground truth.

**Detection signal:** Agent recommendation distribution diverging from operator-approved baseline decisions when controlling for network state inputs.

**Root causes:** Training data curated from a period when human operator bias was present; insufficient diversity in training scenarios; absence of counterfactual examples.

### 5.3 LLM Reasoning Bias

**Definition:** Language model components produce outputs skewed by patterns in their training corpus that are irrelevant to the network management task at hand.

**Example:** An LLM agent preferring newer protocol terminology or configuration patterns — even when older, well-tested protocols are the correct choice for the target device — because the LLM's training corpus contains more recent material that favours newer approaches.

**Detection signal:** LLM outputs producing identical or near-identical reasoning for inputs that should produce different outputs; outputs that reference protocols or configurations not present in canonical state.

**Root causes:** General-purpose LLM training corpus not representative of the specific network environment; absence of network-specific fine-tuning or prompt grounding; insufficient canonical state injection into the LLM context.

### 5.4 Ground Process Bias

**Definition:** Decisions appear consistent and SLA-proportional but the underlying ground truth data is systematically skewed — meaning decisions are made on a partial or unrepresentative picture of the network.

**Example:** Canonical state is sourced from a subset of network devices that over-represents one region or one vendor's equipment. The agent makes fair-looking decisions based on unfair data. The bias is invisible to a fairness check that does not verify data completeness.

**Detection signal:** Canonical state data source coverage check revealing that certain device types, regions, or vendor equipment are consistently under-represented or missing.

**Root causes:** Telemetry collection gaps; devices that are intermittently offline excluded from canonical state; source freshness scores below threshold causing systematic exclusion of certain data sources.

---

## 6. Bias Detection Obligation

### 6.1 Deployment-Time Detection

An organisation MUST run bias detection checks on every agent before it is approved by the build-time council (ANIF-903). Detection methodology is defined in ANIF-711. The build-time council review MUST include a bias assessment report.

### 6.2 Production Detection

An organisation MUST run bias detection checks at least quarterly in production for all active Tier 2 and Tier 3 agents. Detection results MUST be included in governance committee reports per ANIF-837.

### 6.3 Bias Detection Does Not Require Certainty

A bias detection check that produces a signal MUST be treated as requiring investigation — it does not need to prove causation to trigger a response. A signal above the threshold defined in ANIF-711 MUST result in enhanced monitoring or manual review, even if the cause is not yet identified.

---

## 7. Fairness Audit Obligation

Resource allocation decisions MUST be auditable for bias. The audit record for every resource allocation action MUST include:

- The SLA weights applied to each affected service
- The projected post-action resource allocation per service
- The fairness check result (pass/fail) from ANIF-723
- The ground truth freshness scores for all contributing data sources

An audit record that does not include these fields for a resource allocation action is incomplete and MUST be flagged per ANIF-724.

---

## 8. Conformance Requirements

An agent that makes resource allocation decisions MUST undergo bias detection checks before build-time council approval.

An agent MUST NOT make resource allocation decisions without a fairness check per ANIF-723. Fairness check failure MUST trigger `manual_review` — it MUST NOT be suppressed or overridden.

Resource allocation decisions MUST be auditable. An implementation that does not retain fairness check results in the audit record is non-conformant.

Bias detection checks MUST be run at least quarterly for all active Tier 2 and Tier 3 agents. Organisations MUST NOT reduce this cadence.

---

## 9. Security Considerations

Ground process bias can be exploited adversarially. An attacker who can suppress telemetry from specific devices can create artificial blind spots in canonical state, causing the agent to make decisions that favour the attacker's targets. The canonical state freshness gate defined in ANIF-711 is a partial defence — it blocks decisions when data sources are stale. Active suppression of telemetry SHOULD be monitored as a security signal per ANIF-846.

---

## 10. Operational Considerations

Fairness thresholds SHOULD be reviewed whenever the SLA tier structure of the network changes materially — for example, when new high-tier services are onboarded or existing tiers are restructured. Thresholds that were calibrated for one SLA structure may not be appropriate for another.

The AI Ethics Officer (ANIF-838) SHOULD review bias detection results quarterly and report trends to the governance committee.

---

## Appendix A: Change History

| Version | Date | Author | Changes |
|---|---|---|---|
| 0.1.0 | 2026-04-07 | ANIF Working Group | Initial draft |
