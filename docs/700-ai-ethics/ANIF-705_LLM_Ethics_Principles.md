# ANIF-705: LLM-Specific Ethics Principles

| Field        | Value                                              |
|--------------|----------------------------------------------------|
| Doc ID       | ANIF-705                                           |
| Series       | AI Ethics                                          |
| Version      | 0.1.0                                              |
| Status       | Draft                                              |
| Authors      | ANIF Working Group                                 |
| Reviewers    | —                                                  |
| Approved by  | —                                                  |
| Created      | 2026-04-07                                         |
| Last updated | 2026-04-07                                         |
| Replaces     | N/A                                                |
| Related docs | ANIF-701, ANIF-713, ANIF-722, ANIF-807             |

---

## Abstract

Large Language Models introduce ethical obligations that do not apply to deterministic automation components. This document defines four principles specific to LLM components within ANIF: hallucination accountability, prompt integrity, confidence calibration, and non-determinism disclosure. These principles establish where accountability lies when an LLM produces a wrong output, what records must be kept of what was submitted to the LLM, how confidence must be measured, and what must be declared when a non-deterministic component is used. The operational controls enforcing these principles are defined in ANIF-713 and ANIF-722.

---

## 1. Introduction

### 1.1 Purpose

LLMs behave differently from deterministic components in ways that are ethically significant. They can produce outputs that are confidently wrong. They can behave differently for identical inputs. They can be manipulated through the content of their inputs. They operate without transparency into their internal reasoning.

These properties require specific ethical obligations that do not exist in the deterministic parts of the ANIF framework. The nine core values in ANIF-701 apply to all agents — this document applies specifically and additionally to any component that uses an LLM.

### 1.2 Scope

This document covers:

- Hallucination accountability: where responsibility lies for LLM hallucinations
- Prompt integrity: what records must be kept and why
- Confidence calibration: how confidence must be measured, not self-reported
- Non-determinism disclosure: what must be declared in agent manifests
- LLM uncertainty propagation: how LLM uncertainty affects downstream risk scoring

### 1.3 Out of Scope

This document does not cover:

- The technical output validation pipeline (see ANIF-722)
- LLM guardrails policy (see ANIF-713)
- Agent manifest structure and declaration format (see ANIF-807)
- LLM selection, training, or fine-tuning methodology

### 1.4 Intended Audience

- AI engineers building or integrating LLM components into ANIF agents
- Ethics officers reviewing LLM deployments
- Build-time council members evaluating LLM-based agent proposals
- Auditors verifying LLM governance obligations are met

---

## 2. Normative References

- ANIF-701 — Ethics Constitution and Core Values
- ANIF-304 — Risk and Trust Quantification
- ANIF-713 — LLM Guardrails Policy
- ANIF-722 — LLM Output Validation
- ANIF-807 — LLM Agent Specification
- RFC 2119 — Key words for use in RFCs to indicate requirement levels

---

## 3. Terms and Definitions

**Hallucination:** An LLM output that asserts a fact as true when that fact contradicts the canonical state of the network, or asserts the existence of network elements that do not exist in canonical state.

**Prompt:** The input submitted to an LLM component, including system instructions, context injected from canonical state, and the specific query derived from the current intent.

**Prompt hash:** A SHA-256 cryptographic hash of the complete prompt submitted to an LLM, written to the audit record before submission. The hash enables post-incident verification that the prompt was not modified between logging and submission.

**Calibrated confidence:** A confidence score that has been validated against actual accuracy — meaning the declared confidence correlates with real-world accuracy over a test distribution. A confidence score that is self-reported by the LLM without external calibration is not calibrated.

**Deterministic shadow:** A deterministic computation that runs in parallel with an LLM component and produces the same type of output using rule-based logic. The shadow enables the reproducibility check defined in ANIF-723.

**Non-determinism declaration:** The `deterministic: false` flag in an agent manifest, indicating that the agent contains a non-deterministic component and that its outputs may vary for identical inputs.

---

## 4. Hallucination Accountability

### 4.1 Where Accountability Lies

When an LLM produces a hallucinated output that passes undetected into the pipeline and contributes to an adverse action, accountability lies with the designer layer (ANIF-702) — not with the LLM itself. The LLM is a component. The engineer who deployed it without adequate validation controls is accountable for the absence of those controls.

This principle is not punitive — it is structural. It ensures that the organisation cannot attribute incidents to "the AI" without a named human at the designer layer bearing accountability for the deployment decision.

### 4.2 Undetected Hallucinations

A hallucination that passes through validation and reaches execution is a designer-layer accountability failure. Validation controls exist to prevent this. If they fail to catch a hallucination, the question is: were the validation controls adequate for the risk level of the deployment? This determination is made during incident review (ANIF-905) using the build-time council record (ANIF-903) as evidence of what was known at deployment time.

### 4.3 Hallucination Is Not Agent Failure

A hallucination that is detected and blocked by the validation pipeline (ANIF-722) is the system working correctly. It is not a strike event unless the agent produces hallucinations at a frequency that triggers the circuit breaker defined in ANIF-713. Occasional hallucination is an expected property of LLM components — the obligation is to detect and block it, not to achieve zero hallucination rate.

---

## 5. Prompt Integrity

### 5.1 Why Prompt Integrity Matters

Prompt injection attacks (ANIF-842) work by introducing content into the LLM's input that alters its behaviour in ways the operator did not intend. If the prompt that was actually submitted to the LLM is not recorded, it is impossible to determine after the fact whether an agent's unexpected behaviour was caused by an injection attack or by a legitimate input.

Prompt integrity records provide the forensic basis for post-incident investigation.

### 5.2 Prompt Hash Requirement

The SHA-256 hash of the complete prompt MUST be computed and written to the audit record before the prompt is submitted to the LLM. The sequence is:

```
1. Construct prompt
2. Compute SHA-256 hash of prompt
3. Write hash to audit record (ANIF-724)
4. Submit prompt to LLM
```

Reversing steps 3 and 4 — submitting to the LLM before logging the hash — invalidates the integrity guarantee. An implementation that logs the hash after submission is non-conformant.

### 5.3 Hash Verification

During validation (ANIF-722 stage 4), the hash computed from the submitted prompt MUST be compared against the hash stored in the audit record. A mismatch indicates that the prompt was modified between the time it was logged and the time it was submitted. This MUST be treated as a security incident (ANIF-847) with Severity 1 classification.

### 5.4 Prompt Content Retention

The full prompt content MUST NOT be retained beyond the audit record retention period for the associated intent. Prompts that contain network topology data or operational details are sensitive and MUST be handled under the data residency obligations defined in ANIF-106 and ANIF-714.

---

## 6. Confidence Calibration

### 6.1 Self-Reported Confidence Is Not Sufficient

LLMs can produce confidence-sounding outputs even when the underlying output is wrong. An LLM that states "I am confident that..." is not providing a calibrated confidence score — it is producing text that resembles confident output.

Calibrated confidence means: the declared confidence score correlates with real-world accuracy over a representative test distribution. A confidence score of 0.90 should mean the output is correct approximately 90% of the time across the test set.

### 6.2 Calibration Requirement

LLM confidence scores used in ANIF decision-making MUST be calibrated using a method external to the LLM itself. Acceptable calibration methods include: held-out test set comparison, Platt scaling, isotonic regression, or another method that maps LLM output distributions to empirical accuracy rates.

An uncalibrated confidence score MUST be treated as a confidence score of zero for the purposes of the tier thresholds defined in ANIF-713.

### 6.3 Calibration Maintenance

Confidence calibration degrades when the model is updated or when the distribution of inputs shifts. Calibration MUST be re-validated whenever the LLM model version is updated, and at least every 90 days in production. Calibration failures MUST be reported to the build-time council.

---

## 7. Non-Determinism Disclosure

### 7.1 Declaration Obligation

Every agent that incorporates an LLM component MUST declare `deterministic: false` in its agent manifest. This declaration is a statement of fact about the agent's behaviour — LLMs produce different outputs for identical inputs across runs, temperature settings, and model updates. Declaring `deterministic: true` for an agent that uses an LLM without a deterministic shadow that fully determines the output is a misrepresentation and a conformance violation.

### 7.2 Effect on Risk Scoring

The non-determinism declaration has a direct effect on risk scoring. An agent that declares `deterministic: false` has its risk score increased by a factor defined in ANIF-304. This increase reflects the additional uncertainty introduced by non-deterministic components. The factor is not configurable — it is a framework-level constant applied uniformly to all non-deterministic agents.

### 7.3 Non-Determinism and Tier 3

An agent that declares `deterministic: false` MUST NOT be placed in Tier 3 (Decision Agent role) without a deterministic validator running in the same pipeline stage. A non-deterministic Tier 3 agent without a deterministic validator is a conformance violation. The deterministic validator constrains the action space — the LLM selects within it, but the validator ensures the selection is within the bounded action enum (ANIF-721).

---

## 8. LLM Uncertainty Propagation

### 8.1 Uncertainty Must Not Be Absorbed

When an LLM produces an output with a confidence score below the applicable threshold, that uncertainty MUST NOT be silently absorbed by the pipeline. It MUST propagate to the risk scoring stage, which uses it as an input to increase the risk score.

An implementation that proceeds with LLM outputs regardless of confidence score — without propagating the low confidence to risk scoring — is non-conformant.

### 8.2 Propagation Mechanism

If the LLM returns a confidence score below the tier-appropriate threshold defined in ANIF-713, the risk score for the intent MUST be increased to at least the `warn` threshold, regardless of all other risk factors. This ensures that low-confidence LLM outputs always receive increased human scrutiny.

### 8.3 LLM Unavailability

If an LLM component is unavailable and the agent's declared `fallback_behaviour` is `block`, the pipeline MUST halt and escalate. If the fallback is `use_deterministic_only`, the pipeline proceeds on the deterministic shadow output alone, and this substitution MUST be recorded in the audit record.

Silent degradation — where the LLM is unavailable and the pipeline proceeds without declaring the degradation — is a non-determinism disclosure violation.

---

## 9. Conformance Requirements

Every agent incorporating an LLM component MUST declare `deterministic: false` in its agent manifest.

LLM confidence scores used in ANIF decision-making MUST be calibrated using a method external to the LLM. Uncalibrated scores MUST be treated as zero.

The SHA-256 hash of every prompt MUST be written to the audit record before submission to the LLM. Post-submission hash logging is non-conformant.

An LLM component MUST NOT be used in Tier 3 decision making without a deterministic validator in the same pipeline stage.

LLM unavailability MUST be declared in the audit record. Silent fallback to degraded operation without declaration is non-conformant.

---

## 10. Security Considerations

The prompt integrity requirement is a security control as much as an ethics one. The SHA-256 hash prevents undetected prompt modification between logging and submission. Monitoring for prompt hash mismatches is a security signal indicating potential prompt injection or man-in-the-middle tampering within the pipeline. Hash mismatch events MUST be escalated to the security team as Severity 1 incidents (ANIF-847).

---

## 11. Operational Considerations

LLM model updates require re-validation of confidence calibration and re-review by the build-time council before the new model version is placed in production. Organisations MUST NOT update LLM model versions in production without completing this process. The risk of silent model behaviour changes between versions is a specific property of LLM components that has no equivalent in deterministic systems.

---

## Appendix A: Change History

| Version | Date | Author | Changes |
|---|---|---|---|
| 0.1.0 | 2026-04-07 | ANIF Working Group | Initial draft |
