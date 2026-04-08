# ANIF-807: LLM Agent Specification

| Field        | Value                                              |
|--------------|----------------------------------------------------|
| Doc ID       | ANIF-807                                           |
| Series       | AI Agent Architecture                              |
| Version      | 0.1.0                                              |
| Status       | Draft                                              |
| Authors      | ANIF Working Group                                 |
| Reviewers    | —                                                  |
| Approved by  | —                                                  |
| Created      | 2026-04-08                                         |
| Last updated | 2026-04-08                                         |
| Replaces     | N/A                                                |
| Related docs | ANIF-705, ANIF-722, ANIF-800, ANIF-806, ANIF-824  |

---

## Abstract

This document defines normative requirements for any agent component that uses a Large Language Model (LLM). Every LLM agent MUST declare its non-deterministic nature in its capability manifest, operate a deterministic shadow in parallel, pin the LLM model version, and specify fallback behaviour for LLM unavailability. LLM components MUST NOT occupy Tier 3 decision positions without a co-located deterministic validator. These requirements exist because LLM outputs are probabilistic — the same input may produce different outputs across invocations — and probabilistic behaviour in critical infrastructure MUST be bounded by deterministic constraints.

---

## 1. Introduction

### 1.1 Purpose

This document specifies the mandatory requirements that govern any ANIF agent component whose output is produced by a Large Language Model. The requirements address manifest declaration, deterministic shadowing, tier placement restrictions, model version management, and fallback behaviour.

### 1.2 Scope

This document covers:

- Mandatory capability manifest declarations for LLM agents
- The deterministic shadow requirement and divergence handling
- Tier placement restrictions for LLM components
- Model version pinning and upgrade governance
- LLM unavailability handling

### 1.3 Out of Scope

This document does not cover:

- LLM output validation rules (see ANIF-722)
- LLM-specific ethics principles (see ANIF-705)
- LLM guardrails and prompt injection prevention (see ANIF-713)
- Agent testing and red-team standards for LLM agents (see ANIF-820)

### 1.4 Intended Audience

- AI engineers designing and implementing LLM-backed agents
- Platform architects placing agents within the four-tier model
- Build-time council members reviewing LLM component deployments
- Conformance assessors evaluating L5 claims

---

## 2. Normative References

| Reference | Title |
|---|---|
| ANIF-705 | LLM-Specific Ethics Principles |
| ANIF-713 | LLM Guardrails Policy |
| ANIF-722 | LLM Output Validation |
| ANIF-800 | Agent Architecture Overview |
| ANIF-806 | Agent Observability Standard |
| ANIF-824 | Agent Supply Chain Security |
| RFC 2119 | Key words for use in RFCs to Indicate Requirement Levels |

---

## 3. Terms and Definitions

| Term | Definition |
|---|---|
| LLM agent | Any agent component that calls an external or embedded Large Language Model to generate part or all of its output |
| Deterministic shadow | A rule-based component that computes the same logical task as the LLM agent without using probabilistic inference |
| Divergence | A condition where the LLM output and the deterministic shadow output differ beyond the declared tolerance threshold |
| Model version | The exact identifier of the LLM model, including provider, model family, and version tag (e.g., `claude-sonnet-4-6`) |
| Confidence score | A normalised value between 0.0 and 1.0 representing the LLM agent's self-assessed certainty in its output |
| Fallback behaviour | The action taken when the LLM component is unavailable or produces output below the confidence threshold |

---

## 4. Mandatory Manifest Declarations

Every LLM agent MUST declare the following fields in its capability manifest (as defined in ANIF-802):

| Manifest Field | Type | Requirement |
|---|---|---|
| `deterministic` | boolean | MUST be set to `false` |
| `llm_model_id` | string | MUST be the exact model version identifier (e.g., `claude-sonnet-4-6`) |
| `llm_provider` | string | MUST be the provider name (e.g., `anthropic`, `openai`, `mistral`) |
| `confidence_threshold` | float (0.0–1.0) | MUST specify the minimum acceptable confidence score below which output is suppressed |
| `fallback_behaviour` | enum | MUST be one of `block` or `use_deterministic_only` |
| `deterministic_shadow` | string | MUST identify the companion deterministic component by agent_id |

An LLM agent manifest that omits any of these six fields MUST be rejected at registration time. The agent MUST NOT be permitted to transition to ACTIVE state with an incomplete manifest.

### 4.1 Deterministic Flag

The `deterministic: false` flag signals to all consuming components — including the decision engine (ANIF-305), the policy engine (ANIF-302), and the governance audit system (ANIF-831) — that outputs from this agent carry probabilistic uncertainty. Components consuming LLM agent output MUST treat it accordingly and MUST NOT apply deterministic guarantees to LLM-sourced values.

---

## 5. Deterministic Shadow Requirement

### 5.1 Mandatory Co-execution

Every LLM agent MUST operate a deterministic shadow running in parallel. The shadow computes the same logical task using rule-based logic without invoking the LLM. Both components receive the same input at the same time.

The deterministic shadow MUST be identified in the manifest `deterministic_shadow` field. The shadow MUST be a registered agent with `deterministic: true` in its own manifest.

### 5.2 Divergence Detection

The LLM agent MUST compare its output to the deterministic shadow output after every invocation. Divergence is defined as any of the following:

- Output category differs (e.g., LLM recommends `scale_up`, shadow recommends `scale_down`)
- Risk classification differs by more than one severity level
- Confidence score from the LLM is below the declared `confidence_threshold`

### 5.3 Divergence Handling

When divergence is detected:

1. The LLM output MUST be suppressed from downstream processing.
2. The deterministic shadow output MUST be used in its place, labelled as `shadow_substitution: true` in the action record.
3. A divergence event MUST be emitted to the audit trail (ANIF-724) with: `llm_output`, `shadow_output`, `divergence_reason`, `timestamp`, `agent_id`.
4. Repeated divergence — defined as more than three divergence events within any 24-hour window for the same agent — MUST trigger automatic escalation to the governance committee via the progressive intervention mechanism (ANIF-716).

---

## 6. Tier Placement Restrictions

### 6.1 Tier 3 Restriction

An LLM component MUST NOT occupy a Tier 3 decision position without a deterministic validator in the same pipeline stage. Specifically:

- LLM-only Tier 3 decisions — where no deterministic validator co-exists in the same stage — are a conformance violation.
- The deterministic validator MUST have veto power: if the validator rejects the LLM recommendation, the action MUST NOT proceed.

### 6.2 Permitted Tier Placements

| Tier | LLM Component Permitted? | Condition |
|---|---|---|
| Tier 0 (Coordination) | Yes | No restrictions beyond manifest compliance |
| Tier 1 (Monitoring) | Yes | No restrictions beyond manifest compliance |
| Tier 2 (Analysis) | Yes | No restrictions beyond manifest compliance |
| Tier 3 (Execution) | Conditionally | Only with co-located deterministic validator with veto power |

---

## 7. Model Version Management

### 7.1 Version Pinning

The model version declared in `llm_model_id` MUST be pinned to an exact version. Floating version identifiers (e.g., `claude-latest`, `gpt-4-turbo`) are not permitted. An agent registered with a floating version identifier MUST be rejected at registration.

### 7.2 Upgrade Process

Upgrading an LLM agent's model version requires the following process:

1. The new model version MUST be tested against the full test suite defined for the agent (ANIF-820).
2. The deterministic shadow comparison MUST be re-validated against the new model version to confirm divergence rates remain within acceptable bounds.
3. The build-time council (ANIF-901) MUST review and approve the version change before deployment.
4. The manifest MUST be updated with the new `llm_model_id` and re-signed.

Upgrading an LLM model version without completing all four steps is a Severity 2 governance violation.

---

## 8. LLM Unavailability Handling

### 8.1 Fallback Behaviour

When the LLM component is unavailable — whether due to provider outage, network failure, or timeout — the agent MUST apply the declared `fallback_behaviour`:

| Value | Behaviour |
|---|---|
| `block` | The agent MUST halt processing, return an error state, and escalate to the human-in-loop queue (ANIF-404). The intent MUST NOT proceed. |
| `use_deterministic_only` | The agent MUST route to the deterministic shadow for the remainder of the session. All outputs from this session MUST be labelled `llm_degraded: true`. |

### 8.2 Silent Degradation Prohibition

Silent fallback — where the agent continues operating without the LLM but does not declare the degradation — is a conformance violation. All consuming components and governance systems MUST be notified when an LLM agent is operating in fallback mode.

### 8.3 Timeout Definition

An LLM invocation that does not return within 10 seconds MUST be treated as unavailable. The timeout value MUST be declared in the agent manifest as `llm_timeout_seconds`. If not declared, the default of 10 seconds applies.

---

## 9. Conformance Requirements

| ID | Requirement |
|---|---|
| CR-807-01 | Every LLM agent MUST declare `deterministic: false` in its capability manifest. |
| CR-807-02 | Every LLM agent MUST declare `llm_model_id`, `llm_provider`, `confidence_threshold`, `fallback_behaviour`, and `deterministic_shadow` in its manifest. |
| CR-807-03 | An LLM agent with an incomplete manifest MUST be rejected at registration and MUST NOT transition to ACTIVE state. |
| CR-807-04 | Every LLM agent MUST operate a deterministic shadow in parallel. |
| CR-807-05 | When divergence is detected, the LLM output MUST be suppressed and the shadow output MUST be used. |
| CR-807-06 | Divergence events MUST be logged to the audit trail with the fields defined in section 5.3. |
| CR-807-07 | More than three divergence events within any 24-hour window MUST trigger escalation via ANIF-716. |
| CR-807-08 | LLM components MUST NOT occupy Tier 3 positions without a co-located deterministic validator with veto power. |
| CR-807-09 | Model version identifiers MUST be pinned to exact versions. Floating identifiers MUST be rejected at registration. |
| CR-807-10 | Model version upgrades MUST complete all four steps in section 7.2 before deployment. |
| CR-807-11 | An LLM invocation exceeding `llm_timeout_seconds` MUST be treated as unavailable. |
| CR-807-12 | Silent fallback without declared degradation is a conformance violation. |

---

## 10. Security Considerations

LLM agents are adversarial attack surfaces. Prompt injection (ANIF-713), model poisoning (ANIF-824), and output manipulation (ANIF-722) all specifically target LLM components. The deterministic shadow provides a compensating control: even if an LLM is successfully manipulated, the shadow constrains the blast radius by blocking divergent outputs.

Model version pinning limits exposure to supply chain attacks where a model update introduces malicious behaviour. The council review requirement (section 7.2) ensures human oversight of every model change.

---

## 11. Operational Considerations

Operators MUST monitor divergence rates as a leading indicator of LLM component degradation. A rising divergence rate — even if below the 3-per-24-hour threshold — indicates model drift or environmental change that warrants investigation before the threshold is breached.

LLM provider outages are operationally predictable events. Operators SHOULD pre-test the `block` or `use_deterministic_only` fallback path under non-incident conditions to verify it functions correctly before an actual outage.

---

## Appendix A: LLM Agent Manifest Example

```yaml
agent_id: intent-classifier-llm-01
deterministic: false
tier: 2
llm_model_id: claude-sonnet-4-6
llm_provider: anthropic
confidence_threshold: 0.85
fallback_behaviour: use_deterministic_only
deterministic_shadow: intent-classifier-rule-01
llm_timeout_seconds: 10
capabilities:
  - intent_classification
  - ambiguity_detection
permissions:
  - read:intent
  - write:classification_result
```
