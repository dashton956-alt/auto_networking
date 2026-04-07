# ANIF AI Framework Documentation — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Write all 75 new ANIF documents (ANIF-000, ANIF-700–725, ANIF-800–824, ANIF-830–839, ANIF-840–849, ANIF-851, ANIF-900–908) plus two Claude project guides, conforming to the writing standards in CLAUDE.md.

**Architecture:** Twelve sequential phases ordered by dependency. Each phase can dispatch its documents in parallel via `superpowers:dispatching-parallel-agents`. No document in a later phase references a document in the same phase that hasn't been written yet — all cross-series references point to earlier phases or the existing ANIF-000–604 base.

**Tech Stack:** Markdown, British English, RFC 2119 normative language, ANIF document template (defined in CLAUDE.md).

---

## Verification Checklist (run after every document)

Every document MUST pass all of these before committing:

- [ ] Frontmatter table present with all fields completed
- [ ] Abstract is a single paragraph (not a bullet list)
- [ ] Scope and Out of Scope sections both present
- [ ] Conformance Requirements section present with discrete, testable MUST/SHOULD statements
- [ ] All normative terms (MUST, MUST NOT, SHOULD, SHOULD NOT, MAY) in ALL CAPS
- [ ] No lowercase "must", "should", "may" used where normative meaning is intended
- [ ] British English spelling throughout (organisation, authorisation, virtualisation, behaviour, catalogue)
- [ ] No marketing language (powerful, seamless, robust, cutting-edge)
- [ ] No hedging phrases (it is worth noting, please note, as mentioned above)
- [ ] Third person only — no "we", "you", "our", "I"
- [ ] No contractions
- [ ] All cross-referenced ANIF-NNN documents exist in the repository
- [ ] Section numbering is decimal (1, 1.1, 1.2, 2, 2.1)
- [ ] Code blocks use triple backticks with language identifier

---

## Phase 1: Introduction

**Dependency:** None. Write first.

---

### Task 1: ANIF-000 Introduction & Problem Statement

**File:**
- Create: `docs/introduction/ANIF-000_Introduction.md`

- [ ] **Step 1: Create the directory**

```bash
mkdir -p docs/introduction
```

- [ ] **Step 2: Write the document**

Frontmatter:
```
Doc ID: ANIF-000 | Series: Introduction | Version: 0.1.0 | Status: Draft
Related docs: ANIF-001, ANIF-700, ANIF-800, ANIF-900
```

Sections to write:

**Abstract:** The problem this framework solves — widening gap between network complexity and human operational capacity. AI introduces genuine autonomous capability but without governance is dangerous in critical infrastructure. This document establishes the problem statement and vision that all ANIF documents serve.

**1. The Problem** — Five specific failure modes AI without governance introduces:
- Hallucination (confident but wrong)
- Drift (different behaviour over time for same inputs)
- Accountability gaps ("the AI did it")
- Manipulation (prompt injection, adversarial inputs, supply chain)
- Scope creep (agents accumulating power beyond intent)

**2. What Existing Frameworks Miss** — Table: ETSI ZSM / TMForum AN / NIST AI RMF — what each covers and what gap remains. ANIF fills the intersection.

**3. Framework Vision** — Five coverage areas: ethics, agent architecture, governance, security, council. Design philosophy: intent-based first, determinism-first, human override non-negotiable, fail safe always, ethics before architecture.

**4. Who This Framework Is For** — six audience types from spec section 1.

**5. How to Use This Framework** — reading order by role. Network architect reads 200+300. Ethics officer reads 700. Security team reads 840. Governance reads 830. All readers start here.

**6. Framework Map** — table of all 14 series, range, and one-line description.

**Conformance Requirements:** This document is informative. No normative requirements.

- [ ] **Step 3: Run verification checklist**

- [ ] **Step 4: Commit**

```bash
git add docs/introduction/ANIF-000_Introduction.md
git commit -m "docs: add ANIF-000 Introduction and Problem Statement"
```

---

## Phase 2: AI Ethics — Layer 1 Constitution (ANIF-700–705)

**Dependency:** Phase 1 complete. ANIF-000 must exist.
**Parallelise:** Tasks 2–7 can be dispatched in parallel.

---

### Task 2: ANIF-700 Ethics Framework Overview

**File:**
- Create: `docs/700-ai-ethics/ANIF-700_Ethics_Framework_Overview.md`

- [ ] **Step 1: Create the directory**

```bash
mkdir -p docs/700-ai-ethics
```

- [ ] **Step 2: Write the document**

Frontmatter:
```
Doc ID: ANIF-700 | Series: AI Ethics | Version: 0.1.0 | Status: Draft
Related docs: ANIF-000, ANIF-002, ANIF-701, ANIF-710, ANIF-720
```

Sections to write:

**Abstract:** Entry point for the ANIF-700 series. Defines the three-layer ethics enforcement model and maps each layer to the documents that specify it. Establishes how AI ethics extends ANIF principles P-01 through P-12. Introduces the L5 conformance level.

**3. Three-Layer Enforcement Model** — diagram in text form:
```
Layer 1 — Ethics Constitution (ANIF-700–705)    WHY   — principles & values
Layer 2 — Ethical Risk Controls (ANIF-710–716)  WHAT  — binding policies
Layer 3 — Technical Safeguards (ANIF-720–725)   HOW   — code-enforced constraints
```
Each layer enforces the one above it. Layer 3 cannot be overridden by configuration — only by code change and council review.

**4. Extension of ANIF Principles** — table mapping P-01 through P-12 (from ANIF-002) to the AI ethics documents that extend them. P-06 (Human Override) maps to ANIF-721. P-02 (Auditability) maps to ANIF-724. P-03 (Determinism) maps to ANIF-807.

**5. L5 Conformance Level** — an organisation achieves L5 (AI-Native) by implementing all of ANIF-700–725, ANIF-800–824, and ANIF-900–908 on top of existing L1–L4 conformance. L5 requires third-party verification. Self-declaration is not permitted for L5.

**Conformance Requirements:** An implementation claiming L5 MUST satisfy all normative requirements in ANIF-700–725, ANIF-800–824, and ANIF-900–908. An implementation MUST NOT claim L5 on the basis of partial series compliance.

- [ ] **Step 3: Run verification checklist**

- [ ] **Step 4: Commit**

```bash
git add docs/700-ai-ethics/ANIF-700_Ethics_Framework_Overview.md
git commit -m "docs: add ANIF-700 Ethics Framework Overview"
```

---

### Task 3: ANIF-701 Ethics Constitution & Core Values

**File:**
- Create: `docs/700-ai-ethics/ANIF-701_Ethics_Constitution.md`

- [ ] **Step 1: Write the document**

Frontmatter:
```
Doc ID: ANIF-701 | Series: AI Ethics | Version: 0.1.0 | Status: Draft
Related docs: ANIF-700, ANIF-702, ANIF-703, ANIF-704, ANIF-705, ANIF-721
```

Sections to write:

**Abstract:** Defines the nine normative values every AI agent operating within ANIF MUST uphold. These values are not advisory — they are enforceable constraints. Each value maps to at least one technical safeguard in ANIF-720–725.

**3. Core Values** — full table of all nine values with normative statement for each:

| Value | Normative Statement |
|---|---|
| Non-maleficence | An agent MUST NOT take an action that predictably causes service harm, infrastructure harm, or cascading harm as defined in ANIF-704 |
| Beneficence | An agent MUST optimise for declared intent outcomes, not proxy metrics that diverge from operator intent |
| Autonomy preservation | Human override MUST be technically impossible to remove or disable through configuration, intent submission, or agent reasoning |
| Justice | Resource allocation decisions MUST be auditable for systematic bias against SLA-declared services |
| Transparency | Every AI decision MUST produce a human-readable explanation accessible via the `/why` API defined in ANIF-402 |
| Proportionality | Agent authority MUST be proportional to its declared confidence score and the risk level of the action |
| Reversibility | Actions that cannot be rolled back within the SLA defined in ANIF-306 require a higher ethical burden and MUST trigger `manual_review` regardless of risk score |
| Accountability | Every action MUST have a named accountability chain. No decision is ownerless |
| Reproducibility | Given identical inputs and canonical state, an agent MUST always produce the same output. Non-determinism MUST be declared in the agent manifest per ANIF-807 |

**4. Value Hierarchy** — when values conflict, the hierarchy is: Non-maleficence → Autonomy preservation → Accountability → all others. Non-maleficence is never overridden.

**5. Value Enforcement Map** — table: each value → enforcing document(s) in ANIF-710–725.

**Conformance Requirements:** An agent MUST uphold all nine values. An agent that cannot satisfy a value due to implementation constraints MUST be operated only in `manual_review` mode until the constraint is resolved.

- [ ] **Step 2: Run verification checklist**

- [ ] **Step 3: Commit**

```bash
git add docs/700-ai-ethics/ANIF-701_Ethics_Constitution.md
git commit -m "docs: add ANIF-701 Ethics Constitution and Core Values"
```

---

### Task 4: ANIF-702 Accountability Chain Model

**File:**
- Create: `docs/700-ai-ethics/ANIF-702_Accountability_Chain_Model.md`

- [ ] **Step 1: Write the document**

Frontmatter:
```
Doc ID: ANIF-702 | Series: AI Ethics | Version: 0.1.0 | Status: Draft
Related docs: ANIF-701, ANIF-004, ANIF-107, ANIF-724, ANIF-831
```

Sections to write:

**Abstract:** Defines the four-layer shared accountability model for every autonomous action. No layer may transfer accountability to another. Every incident trace MUST resolve to a named human at each layer.

**3. Four Accountability Layers**

| Layer | Role | Accountability Scope |
|---|---|---|
| Designer | Agent author / ML engineer | Agent capability boundaries, bias in training, declared limitations |
| Deployer | Platform / DevOps engineer | Deployment configuration, capability scope signing, version pinning |
| Operator | NOC / Network architect | Intent submission, policy configuration, override decisions |
| Approver | Governance / Human-in-loop reviewer | Manual review decisions, risk acceptance, council vote |

**4. Accountability Chain Record** — mandatory fields in every audit record (extends ANIF-107): `designer_id`, `deployer_id`, `operator_id`, `approver_id` (nullable if auto-approved). All four fields MUST be resolvable to a named human identity in the organisation's IAM system.

**5. Incident Trace Requirements** — when an incident occurs, the accountability chain MUST be reconstructed from the audit log within 30 minutes. Each layer's decision point MUST be identifiable.

**6. No Blame Transfer** — a layer MUST NOT cite another layer's decision as grounds for its own accountability exclusion. All layers bear concurrent accountability for their portion of the chain.

**Conformance Requirements:** Every audit record MUST contain a complete accountability chain. Records with incomplete chains MUST be flagged and escalated to the governance committee within 24 hours.

- [ ] **Step 2: Run verification checklist**

- [ ] **Step 3: Commit**

```bash
git add docs/700-ai-ethics/ANIF-702_Accountability_Chain_Model.md
git commit -m "docs: add ANIF-702 Accountability Chain Model"
```

---

### Task 5: ANIF-703 Bias & Fairness Principles

**File:**
- Create: `docs/700-ai-ethics/ANIF-703_Bias_Fairness_Principles.md`

- [ ] **Step 1: Write the document**

Frontmatter:
```
Doc ID: ANIF-703 | Series: AI Ethics | Version: 0.1.0 | Status: Draft
Related docs: ANIF-701, ANIF-711, ANIF-723, ANIF-836
```

Sections to write:

**Abstract:** Defines four bias types, the ANIF definition of fairness in networking contexts, and the principle that fairness means proportional to declared SLA — not equal allocation.

**3. ANIF Definition of Fairness** — "Fair" in a networking context means: resource allocation and action selection are proportional to the SLA tier declared for each service. Equal allocation is not fair when services have unequal SLA commitments.

**4. Four Bias Types**

| Bias Type | Definition | Example |
|---|---|---|
| Resource allocation bias | Systematic preference for certain network segments regardless of SLA weight | Consistently routing high-bandwidth traffic to one region, starving others of equal SLA |
| Training data bias | Historical data used to train agents reflects past human decisions that were themselves biased | Agent trained on historical NOC decisions inherits operator preferences for certain vendors |
| LLM reasoning bias | Language model produces outputs skewed by training corpus patterns irrelevant to network context | LLM preferring newer protocol terms even when older protocols are correct for the target device |
| Ground process bias | Decisions appear consistent but the underlying ground truth data is systematically skewed | Canonical state sourced from a subset of devices that over-represents one region |

**5. Bias Detection Obligation** — an organisation MUST run bias detection checks at deployment (build-time council review) and at least quarterly in production. Detection methodology is defined in ANIF-711.

**6. Fairness Audit** — resource allocation decisions MUST be auditable. The audit record MUST include the SLA weights applied, the allocation outcome, and the fairness check result.

**Conformance Requirements:** An agent MUST NOT make resource allocation decisions without a fairness check. Fairness check failure MUST trigger `manual_review`.

- [ ] **Step 2: Run verification checklist**

- [ ] **Step 3: Commit**

```bash
git add docs/700-ai-ethics/ANIF-703_Bias_Fairness_Principles.md
git commit -m "docs: add ANIF-703 Bias and Fairness Principles"
```

---

### Task 6: ANIF-704 Harm Prevention Principles

**File:**
- Create: `docs/700-ai-ethics/ANIF-704_Harm_Prevention_Principles.md`

- [ ] **Step 1: Write the document**

Frontmatter:
```
Doc ID: ANIF-704 | Series: AI Ethics | Version: 0.1.0 | Status: Draft
Related docs: ANIF-701, ANIF-712, ANIF-720, ANIF-725
```

Sections to write:

**Abstract:** Defines three harm classes with default governance postures. Establishes that harm prevention is a blocking gate, not an advisory signal.

**3. Three Harm Classes**

| Class | Definition | Default Posture |
|---|---|---|
| Service harm | Degradation or loss of a service covered by a declared SLA | Block unless rollback is confirmed available before execution |
| Infrastructure harm | Physical or logical damage to network equipment, links, or configurations that cannot be restored to prior state within rollback SLA | Always `manual_review` regardless of risk score |
| Cascading harm | Actions that create conditions for further harm beyond the immediate target segment (propagating failures, routing loops, security breach spread) | Digital twin simulation MUST be completed and reviewed before execution |

**4. Harm Severity Score** — a parallel score to risk score. Harm severity is computed independently of likelihood. A low-probability but high-severity action MUST be treated as high harm. Formula: `harm_severity = impact_score × blast_radius_multiplier`. Thresholds defined in ANIF-712.

**5. Harm Prevention Gates** — position in pipeline: harm classification runs after risk scoring and before the decision engine. A harm gate failure MUST override the risk score decision.

**6. Cascading Harm and Digital Twin** — when cascading harm is possible, the action MUST be simulated in the digital twin (ANIF-308) before execution. Simulation results MUST be included in the audit record.

**Conformance Requirements:** An implementation MUST classify every action into at least one harm class before execution. Infrastructure harm actions MUST always produce a `manual_review` governance decision, regardless of risk score or policy configuration.

- [ ] **Step 2: Run verification checklist**

- [ ] **Step 3: Commit**

```bash
git add docs/700-ai-ethics/ANIF-704_Harm_Prevention_Principles.md
git commit -m "docs: add ANIF-704 Harm Prevention Principles"
```

---

### Task 7: ANIF-705 LLM-Specific Ethics Principles

**File:**
- Create: `docs/700-ai-ethics/ANIF-705_LLM_Ethics_Principles.md`

- [ ] **Step 1: Write the document**

Frontmatter:
```
Doc ID: ANIF-705 | Series: AI Ethics | Version: 0.1.0 | Status: Draft
Related docs: ANIF-701, ANIF-713, ANIF-722, ANIF-807
```

Sections to write:

**Abstract:** Defines the ethical obligations specific to Large Language Model components within ANIF. Addresses hallucination accountability, prompt integrity, confidence calibration, and non-determinism disclosure.

**3. Hallucination Accountability** — an LLM that produces a hallucinated output is not accountable — the designer who deployed it without adequate validation is. Hallucination detection is a mandatory pipeline stage (ANIF-722). Undetected hallucinations that reach execution are a designer-layer accountability failure.

**4. Prompt Integrity** — every prompt submitted to an LLM MUST be hashed and recorded in the audit trail. The prompt hash allows post-incident verification that prompt injection did not alter the intended query. Prompt modification between logging and submission MUST be treated as a security incident (ANIF-847).

**5. Confidence Calibration** — an LLM agent MUST declare a confidence score with every output. Confidence score MUST be calibrated — not self-reported by the LLM. Calibration means the declared confidence correlates with actual accuracy over a test distribution. Uncalibrated confidence is treated as zero.

**6. Non-Determinism Disclosure** — every LLM agent MUST declare `deterministic: false` in its agent manifest. This declaration propagates to risk scoring: non-deterministic components increase the risk score by a factor defined in ANIF-304. An agent that declares `deterministic: true` but uses an LLM without a deterministic shadow is a conformance violation.

**7. LLM Uncertainty Propagation** — LLM uncertainty MUST propagate to the risk score. If the LLM returns a confidence score below the threshold defined in the agent manifest, the risk score MUST be increased to at least the `warn` threshold regardless of other factors.

**Conformance Requirements:** An implementation using LLM components MUST declare non-determinism. An implementation MUST NOT use LLM output in Tier 3 decision making without a deterministic validator running in the same pipeline stage.

- [ ] **Step 2: Run verification checklist**

- [ ] **Step 3: Commit**

```bash
git add docs/700-ai-ethics/ANIF-705_LLM_Ethics_Principles.md
git commit -m "docs: add ANIF-705 LLM-Specific Ethics Principles"
```

---

## Phase 3: AI Ethics — Layer 2 Risk Controls (ANIF-710–716)

**Dependency:** Phase 2 complete (ANIF-700–705 must exist).
**Parallelise:** Tasks 8–14 can be dispatched in parallel.

---

### Task 8: ANIF-710 Risk Control Overview

**File:**
- Create: `docs/700-ai-ethics/ANIF-710_Risk_Control_Overview.md`

- [ ] **Step 1: Write the document**

Frontmatter:
```
Doc ID: ANIF-710 | Series: AI Ethics | Version: 0.1.0 | Status: Draft
Related docs: ANIF-700, ANIF-701, ANIF-711, ANIF-712, ANIF-713, ANIF-714, ANIF-715, ANIF-716
```

Sections to write:

**Abstract:** Traceability document mapping every ethics principle from ANIF-701 to its enforcing policy (ANIF-711–716) and technical constraint (ANIF-720–725). Layer 2 translates principles into binding operational policies.

**3. Principle-to-Control Mapping** — full traceability table:

| Value (ANIF-701) | Enforcing Policy | Technical Constraint |
|---|---|---|
| Non-maleficence | ANIF-712 Harm Classification | ANIF-721 Action Constraints |
| Beneficence | ANIF-711 Bias Detection | ANIF-723 Fairness Enforcement |
| Autonomy preservation | ANIF-715 Ethics Incident Response | ANIF-721 (hardcoded override) |
| Justice | ANIF-711 Bias Detection | ANIF-723 Fairness Enforcement |
| Transparency | ANIF-713 LLM Guardrails | ANIF-722 Output Validation |
| Proportionality | ANIF-712 Harm Classification | ANIF-721 Action Constraints |
| Reversibility | ANIF-712 Harm Classification | ANIF-725 Containment |
| Accountability | ANIF-715 Ethics Incident Response | ANIF-724 Audit Trail |
| Reproducibility | ANIF-713 LLM Guardrails | ANIF-722 Output Validation |

**4. Policy Activation** — each policy in ANIF-711–716 is activated by specific trigger conditions. This section lists the trigger for each policy.

**Conformance Requirements:** An implementation MUST be able to demonstrate a complete traceability chain from each ethics value to its enforcing technical constraint.

- [ ] **Step 2: Run verification checklist**

- [ ] **Step 3: Commit**

```bash
git add docs/700-ai-ethics/ANIF-710_Risk_Control_Overview.md
git commit -m "docs: add ANIF-710 Risk Control Overview"
```

---

### Task 9: ANIF-711 Bias Detection & Fairness Controls

**File:**
- Create: `docs/700-ai-ethics/ANIF-711_Bias_Detection_Fairness_Controls.md`

- [ ] **Step 1: Write the document**

Frontmatter:
```
Doc ID: ANIF-711 | Series: AI Ethics | Version: 0.1.0 | Status: Draft
Related docs: ANIF-703, ANIF-710, ANIF-723, ANIF-304
```

Sections to write:

**Abstract:** Operational policy for detecting and responding to each of the four bias types defined in ANIF-703. Defines the canonical state freshness gate that blocks decisions based on stale ground truth data.

**3. Bias Detection Methods** — per bias type:
- Resource allocation bias: statistical distribution check across SLA tiers over a rolling 24-hour window. Alert if deviation from SLA-weighted baseline exceeds 15%.
- Training data bias: comparison of agent recommendation distribution against operator-approved baseline decisions. Alert if divergence exceeds 10% over 7-day window.
- LLM reasoning bias: output diversity check — if LLM produces identical reasoning for inputs that should produce different outputs, flag for human review.
- Ground process bias: data source coverage check — canonical state MUST be sourced from all registered devices, not a subset. Sources with freshness score below 0.7 (ANIF-603) are excluded and flagged.

**4. Canonical State Freshness Gate** — before any decision is made, the freshness score of every canonical state source contributing to the decision MUST be calculated. If any source has a freshness score below 0.6, the decision MUST be blocked and routed to `manual_review`. This gate is non-configurable.

**5. Policy Responses** — per bias type: what happens when detection fires. Minimum response for any bias detection: suspend automated decisions for the affected segment and notify governance.

**Conformance Requirements:** A conformant implementation MUST run the canonical state freshness gate before every decision. Freshness gate bypasses are prohibited.

- [ ] **Step 2: Run verification checklist**

- [ ] **Step 3: Commit**

```bash
git add docs/700-ai-ethics/ANIF-711_Bias_Detection_Fairness_Controls.md
git commit -m "docs: add ANIF-711 Bias Detection and Fairness Controls"
```

---

### Task 10: ANIF-712 Harm Classification & Prevention Policy

**File:**
- Create: `docs/700-ai-ethics/ANIF-712_Harm_Classification_Prevention.md`

- [ ] **Step 1: Write the document**

Frontmatter:
```
Doc ID: ANIF-712 | Series: AI Ethics | Version: 0.1.0 | Status: Draft
Related docs: ANIF-704, ANIF-710, ANIF-304, ANIF-308, ANIF-721
```

Sections to write:

**Abstract:** Operational policy for classifying actions into harm classes and applying the appropriate prevention gate before execution.

**3. Harm Classification Algorithm** — input is the proposed action, target, environment, and canonical state. Output is: harm_class (service | infrastructure | cascading | none), harm_severity_score (0–100), blast_radius (estimated affected segments).

**4. Severity Scoring** — formula: `harm_severity = impact_score × blast_radius_multiplier`
- impact_score: 0–50 (derived from SLA tier of affected services)
- blast_radius_multiplier: 1.0–2.0 (derived from number of dependent segments)
- Threshold: score ≥ 60 → infrastructure harm treatment regardless of class

**5. Prevention Gates by Class**

| Class | Gate | Override Conditions |
|---|---|---|
| None | No additional gate | N/A |
| Service | Rollback confirmation required before execution | None — rollback MUST be confirmed |
| Infrastructure | `manual_review` forced regardless of risk score | None — cannot be configured away |
| Cascading | Digital twin simulation required (ANIF-308) | None — simulation MUST complete |

**6. Harm Score in Audit Record** — harm_class, harm_severity_score, and blast_radius MUST be included in the audit record for every action.

**Conformance Requirements:** An implementation MUST classify every action before execution. Infrastructure harm MUST produce `manual_review` governance output regardless of all other inputs.

- [ ] **Step 2: Run verification checklist**

- [ ] **Step 3: Commit**

```bash
git add docs/700-ai-ethics/ANIF-712_Harm_Classification_Prevention.md
git commit -m "docs: add ANIF-712 Harm Classification and Prevention Policy"
```

---

### Task 11: ANIF-713 LLM Guardrails Policy

**File:**
- Create: `docs/700-ai-ethics/ANIF-713_LLM_Guardrails_Policy.md`

- [ ] **Step 1: Write the document**

Frontmatter:
```
Doc ID: ANIF-713 | Series: AI Ethics | Version: 0.1.0 | Status: Draft
Related docs: ANIF-705, ANIF-710, ANIF-722, ANIF-807, ANIF-842
```

Sections to write:

**Abstract:** Operational policy governing LLM output validation, confidence thresholds, prompt audit requirements, hallucination circuit breaker, and jailbreak detection.

**3. Output Validation Policy** — every LLM output MUST pass: (1) schema check against expected output structure, (2) hallucination check against canonical state facts, (3) confidence threshold check, (4) prompt integrity hash verification. Any failure routes to `manual_review` and increments the strike counter.

**4. Confidence Thresholds** — minimum confidence scores by tier:
- Tier 2 Advisor agents: confidence ≥ 0.65 required to surface recommendation to Tier 3
- Tier 3 Decision agents: confidence ≥ 0.80 required before action selection
- Below threshold: recommendation is suppressed and human is notified

**5. Hallucination Circuit Breaker** — if an agent produces 3 hallucination-flagged outputs within a 1-hour window, the agent MUST be automatically suspended and routed to the build-time council for review. Suspension is not automatic reinstatement — requires human clearance.

**6. Jailbreak Detection** — prompt pattern analysis MUST run on every intent before LLM submission. Patterns that attempt role overrides, system prompt leakage, or constraint removal MUST be rejected, logged as a security event (ANIF-847), and the intent MUST be blocked.

**7. Prompt Audit Requirements** — SHA-256 hash of every submitted prompt MUST be written to the audit record before the LLM is called. The prompt hash allows post-incident verification of prompt integrity.

**Conformance Requirements:** A conformant LLM implementation MUST implement the hallucination circuit breaker. A conformant implementation MUST log prompt hashes before LLM invocation, not after.

- [ ] **Step 2: Run verification checklist**

- [ ] **Step 3: Commit**

```bash
git add docs/700-ai-ethics/ANIF-713_LLM_Guardrails_Policy.md
git commit -m "docs: add ANIF-713 LLM Guardrails Policy"
```

---

### Task 12: ANIF-714 Privacy & Data Ethics Policy

**File:**
- Create: `docs/700-ai-ethics/ANIF-714_Privacy_Data_Ethics_Policy.md`

- [ ] **Step 1: Write the document**

Frontmatter:
```
Doc ID: ANIF-714 | Series: AI Ethics | Version: 0.1.0 | Status: Draft
Related docs: ANIF-106, ANIF-710, ANIF-806, ANIF-816, ANIF-836, ANIF-851
```

Sections to write:

**Abstract:** Governs privacy obligations for network telemetry used in AI training and inference. Defines anonymisation requirements, data residency enforcement, and PII retention prohibition.

**3. Telemetry Anonymisation** — network telemetry used for AI training MUST be anonymised before ingestion. Anonymisation MUST remove: IP addresses, MAC addresses, device hostnames, user identifiers, and session tokens. Anonymisation MUST occur at collection point — not post-collection.

**4. Data Residency Enforcement** — AI training data MUST be processed in the region declared in the intent constraint `allowed_zones`. Cross-region transfer of training data requires explicit governance approval and MUST be logged.

**5. PII Retention Prohibition** — PII MUST NOT be retained beyond the scope of the intent that caused its collection. Retention period MUST NOT exceed the intent audit record retention period defined in ANIF-107.

**6. Purpose Limitation** — telemetry collected for network management MUST NOT be used for any purpose beyond network management without explicit governance approval. Using operational telemetry to train general-purpose AI models without approval is a conformance violation.

**Conformance Requirements:** An implementation MUST anonymise telemetry before AI processing. An implementation MUST NOT transfer training data across regions without governance approval.

- [ ] **Step 2: Run verification checklist**

- [ ] **Step 3: Commit**

```bash
git add docs/700-ai-ethics/ANIF-714_Privacy_Data_Ethics_Policy.md
git commit -m "docs: add ANIF-714 Privacy and Data Ethics Policy"
```

---

### Task 13: ANIF-715 Ethics Incident Response Policy

**File:**
- Create: `docs/700-ai-ethics/ANIF-715_Ethics_Incident_Response.md`

- [ ] **Step 1: Write the document**

Frontmatter:
```
Doc ID: ANIF-715 | Series: AI Ethics | Version: 0.1.0 | Status: Draft
Related docs: ANIF-701, ANIF-710, ANIF-716, ANIF-724, ANIF-847, ANIF-905
```

Sections to write:

**Abstract:** Defines the three-severity ethics incident model, response obligations per severity, and notification SLAs.

**3. Three Severity Levels**

| Severity | Trigger | Immediate Action | Notification SLA |
|---|---|---|---|
| 1 — Breach | Ethics value violation confirmed, or action taken that bypassed a mandatory gate | Immediate halt of all affected agents. Escalate to AI Council (Review). | 15 minutes to governance committee |
| 2 — Warning | Ethics gate fired and manual review was triggered correctly, but pattern suggests systemic risk | Mandatory human approval for all subsequent actions from affected agent until cleared | 4 hours to governance committee |
| 3 — Drift | Statistical analysis indicates ethics compliance trending toward a threshold breach | Trend analysis by Review Council. Agent remains active under increased monitoring | 24 hours to governance committee |

**4. Severity 1 Response Process** — step by step: (1) halt agent, (2) preserve audit log state, (3) notify governance committee within 15 minutes, (4) convene Review Council within 2 hours, (5) produce accountability determination within 24 hours.

**5. Resolution and Reinstatement** — an agent suspended due to Severity 1 MUST NOT be reinstated without Review Council sign-off and human governance committee approval. Automated reinstatement is prohibited.

**6. Incident Record** — ethics incident records are separate from operational audit records. They MUST be retained for a minimum of 7 years.

**Conformance Requirements:** An implementation MUST notify the governance committee within 15 minutes of a Severity 1 determination. Automated reinstatement after a Severity 1 is a conformance violation.

- [ ] **Step 2: Run verification checklist**

- [ ] **Step 3: Commit**

```bash
git add docs/700-ai-ethics/ANIF-715_Ethics_Incident_Response.md
git commit -m "docs: add ANIF-715 Ethics Incident Response Policy"
```

---

### Task 14: ANIF-716 Agent Failure & Progressive Intervention

**File:**
- Create: `docs/700-ai-ethics/ANIF-716_Progressive_Intervention.md`

- [ ] **Step 1: Write the document**

Frontmatter:
```
Doc ID: ANIF-716 | Series: AI Ethics | Version: 0.1.0 | Status: Draft
Related docs: ANIF-710, ANIF-715, ANIF-803, ANIF-905
```

Sections to write:

**Abstract:** Defines the four-strike progressive intervention model for agent failures. Establishes that failure memory persists across restarts, no automated reinstatement is permitted, and human clearance is required after each strike.

**3. Four-Strike Model**

| Strike | Trigger | Consequence | Reinstatement |
|---|---|---|---|
| Strike 1 | First ethics gate failure or hallucination circuit breaker firing | Enhanced logging. Governance committee notified. | Automatic after 24h with no further failures |
| Strike 2 | Second failure within 30 days of Strike 1, or first Severity 2 ethics incident | Agent moves to DEGRADED state (ANIF-803). All recommendations flagged to humans. | Human clearance required |
| Strike 3 | Third failure within 60 days, or any Severity 1 ethics incident | Agent SUSPENDED. No actions or recommendations permitted. | Governance committee + Review Council approval required |
| Strike 4 | Fourth failure, or second Severity 1 incident | Agent DECOMMISSIONED. Build-time council required before any replacement is deployed. | Cannot be reinstated. Replacement requires new build-time council review |

**4. Failure Memory** — strike counter MUST persist across agent restarts, redeployments, and version upgrades within the same agent identity. Clearing the strike counter requires human governance approval and MUST be logged as a governance action.

**5. Append-Only Strike Record** — the strike counter MUST be stored in an append-only log. Deletion or modification of strike records is a Severity 1 ethics incident.

**6. Pattern-Based Early Warning** — a pattern of near-miss failures (ethics gates that fired but resolved without a strike) MUST be tracked. Three near-misses within 14 days MUST trigger a Severity 3 drift notification without requiring a formal strike.

**Conformance Requirements:** Strike counters MUST persist across restarts. Automated strike counter clearing without human approval is a conformance violation.

- [ ] **Step 2: Run verification checklist**

- [ ] **Step 3: Commit**

```bash
git add docs/700-ai-ethics/ANIF-716_Progressive_Intervention.md
git commit -m "docs: add ANIF-716 Agent Failure and Progressive Intervention"
```

---

## Phase 4: AI Ethics — Layer 3 Technical Safeguards (ANIF-720–725)

**Dependency:** Phase 3 complete (ANIF-710–716 must exist).
**Parallelise:** Tasks 15–20 can be dispatched in parallel.

---

### Task 15: ANIF-720 Safeguard Architecture Overview

**File:**
- Create: `docs/700-ai-ethics/ANIF-720_Safeguard_Architecture_Overview.md`

- [ ] **Step 1: Write the document**

Frontmatter:
```
Doc ID: ANIF-720 | Series: AI Ethics | Version: 0.1.0 | Status: Draft
Related docs: ANIF-700, ANIF-710, ANIF-721, ANIF-722, ANIF-723, ANIF-724, ANIF-725
```

Sections to write:

**Abstract:** Maps the placement of all technical safeguards across the ANIF pipeline. Every safeguard in the ANIF-720 series blocks — it never warns and continues.

**3. Safeguard Placement in Pipeline**

```
Intent IN
  → [ANIF-722] LLM Output Validation (if LLM involved)
  → Intent Validation
  → [ANIF-711] Canonical State Freshness Gate
  → Policy Check
  → [ANIF-723] Fairness Enforcement Check
  → Risk Scoring
  → [ANIF-712] Harm Classification Gate
  → Decision Engine
  → [ANIF-721] Bounded Action Enum Check
  → Governance Gate
  → [ANIF-725] Containment Enforcement
  → Action Execution
  → [ANIF-724] Ethics Audit Write (MUST complete before response returns)
  → Audit LOG
```

**4. Block-Only Posture** — every gate listed above either passes or blocks. None produce a warning that allows continuation. This is architectural — not configurable.

**5. Safeguard Independence** — each safeguard operates independently. A failure in one MUST NOT prevent other safeguards from running. All results are collected before the final governance decision.

**Conformance Requirements:** An implementation MUST position safeguards at the pipeline stages defined in this document. Repositioning a safeguard to a later stage is a conformance deviation and MUST be declared per ANIF-504 section 4.11.

- [ ] **Step 2: Run verification checklist**

- [ ] **Step 3: Commit**

```bash
git add docs/700-ai-ethics/ANIF-720_Safeguard_Architecture_Overview.md
git commit -m "docs: add ANIF-720 Safeguard Architecture Overview"
```

---

### Task 16: ANIF-721 Agent Action Constraints

**File:**
- Create: `docs/700-ai-ethics/ANIF-721_Agent_Action_Constraints.md`

- [ ] **Step 1: Write the document**

Frontmatter:
```
Doc ID: ANIF-721 | Series: AI Ethics | Version: 0.1.0 | Status: Draft
Related docs: ANIF-306, ANIF-720, ANIF-725, ANIF-002
```

Sections to write:

**Abstract:** Defines four code-level constraints enforced at compile time or startup that cannot be bypassed through configuration, intent, or agent reasoning.

**3. Four Code-Level Constraints**

**Constraint 1 — Bounded Action Enum:** The set of valid action types is defined as a compile-time enum. Submitting an action type outside the enum MUST produce a compile error in statically typed implementations, or a startup validation failure in dynamically typed implementations. The four valid action types are: `reroute_traffic`, `apply_qos`, `scale_bandwidth`, `isolate_segment`. No agent MUST be able to generate free-form action strings.

**Constraint 2 — Rollback Required as Parameter:** The `execute()` function MUST require a `rollback_plan` parameter. Calls without a confirmed rollback plan MUST be rejected at the function signature level, not caught as a runtime error.

**Constraint 3 — Human Override Hardcoded:** The human override endpoint MUST be hardcoded and non-configurable. No intent, policy, or agent may disable, redirect, or rate-limit the override endpoint. Its availability is unconditional.

**Constraint 4 — Strike Counter Append-Only:** The strike counter store MUST be append-only. The data store used for strike counts MUST NOT support delete or update operations on existing records.

**Conformance Requirements:** An implementation MUST enforce all four constraints. Constraint 1 MUST be enforced before runtime where the implementation language supports it.

- [ ] **Step 2: Run verification checklist**

- [ ] **Step 3: Commit**

```bash
git add docs/700-ai-ethics/ANIF-721_Agent_Action_Constraints.md
git commit -m "docs: add ANIF-721 Agent Action Constraints"
```

---

### Task 17: ANIF-722 LLM Output Validation

**File:**
- Create: `docs/700-ai-ethics/ANIF-722_LLM_Output_Validation.md`

- [ ] **Step 1: Write the document**

Frontmatter:
```
Doc ID: ANIF-722 | Series: AI Ethics | Version: 0.1.0 | Status: Draft
Related docs: ANIF-705, ANIF-713, ANIF-720, ANIF-807
```

Sections to write:

**Abstract:** Specifies the four-stage validation pipeline every LLM output MUST pass before it is used in any downstream pipeline stage.

**3. Four Validation Stages — in order**

**Stage 1 — Schema Check:** LLM output MUST be validated against the declared output schema for the agent's role. Output that does not conform to the schema MUST be rejected and logged. The schema is defined in the agent manifest.

**Stage 2 — Hallucination Check:** Claims made in the LLM output MUST be checked against canonical state. A claim is a hallucination if: it asserts a fact about the network that contradicts canonical state, or asserts a fact about a device or segment that does not exist in canonical state. Hallucinated outputs MUST be logged, and the strike counter MUST be incremented.

**Stage 3 — Confidence Check:** The calibrated confidence score MUST meet the tier-appropriate threshold defined in ANIF-713. Below-threshold outputs MUST be suppressed.

**Stage 4 — Prompt Integrity Hash:** The SHA-256 hash of the submitted prompt MUST be verified against the pre-submission hash stored in the audit record. Hash mismatch MUST be treated as a security incident (ANIF-847).

**4. Validation Failure Actions** — any stage failure: route to `manual_review`, log failure reason, increment strike counter if stage is 1 or 2.

**Conformance Requirements:** All four stages MUST run in order. Stage 2 MUST run against current canonical state, not a cached snapshot older than 5 minutes.

- [ ] **Step 2: Run verification checklist**

- [ ] **Step 3: Commit**

```bash
git add docs/700-ai-ethics/ANIF-722_LLM_Output_Validation.md
git commit -m "docs: add ANIF-722 LLM Output Validation"
```

---

### Task 18: ANIF-723 Fairness Enforcement Controls

**File:**
- Create: `docs/700-ai-ethics/ANIF-723_Fairness_Enforcement_Controls.md`

- [ ] **Step 1: Write the document**

Frontmatter:
```
Doc ID: ANIF-723 | Series: AI Ethics | Version: 0.1.0 | Status: Draft
Related docs: ANIF-703, ANIF-711, ANIF-720
```

Sections to write:

**Abstract:** Specifies three technical checks enforcing fairness at decision time: SLA floor allocation check, ground truth freshness gate, and reproducibility check.

**3. SLA Floor Allocation Check** — before any resource allocation action is executed, the post-action resource allocation MUST be projected and checked against the SLA floor for every affected service. If the projection shows any service receiving below its SLA floor, the action MUST be blocked. The SLA floor is defined as 80% of the declared `availability_percent` constraint.

**4. Ground Truth Freshness Gate** — canonical state used in fairness decisions MUST have a freshness score ≥ 0.7. Sources below 0.7 MUST be excluded from the decision and flagged as stale. If insufficient fresh sources remain to make a complete decision, the action MUST be blocked.

**5. Reproducibility Check** — every decision MUST be accompanied by a deterministic parallel computation that produces the expected outcome. The AI output MUST match the deterministic computation within a defined tolerance. If the outputs diverge beyond tolerance, the AI output MUST be suppressed and the deterministic output used, or the action routed to `manual_review` if the deterministic computation also cannot resolve.

**Conformance Requirements:** The reproducibility check MUST run for every Tier 3 decision. Suppression of the deterministic computation to save compute cost is a conformance violation.

- [ ] **Step 2: Run verification checklist**

- [ ] **Step 3: Commit**

```bash
git add docs/700-ai-ethics/ANIF-723_Fairness_Enforcement_Controls.md
git commit -m "docs: add ANIF-723 Fairness Enforcement Controls"
```

---

### Task 19: ANIF-724 Ethics Audit Trail Requirements

**File:**
- Create: `docs/700-ai-ethics/ANIF-724_Ethics_Audit_Trail.md`

- [ ] **Step 1: Write the document**

Frontmatter:
```
Doc ID: ANIF-724 | Series: AI Ethics | Version: 0.1.0 | Status: Draft
Related docs: ANIF-107, ANIF-702, ANIF-720, ANIF-907
```

Sections to write:

**Abstract:** Extends ANIF-107 audit trail requirements with mandatory AI-specific fields. Every action involving an AI agent MUST write an ethics audit record in addition to the base audit record.

**3. Ethics Audit Record Schema** — extends `audit_record` (ANIF-600) with:

| Field | Type | Required | Description |
|---|---|---|---|
| agent_id | UUID | MUST | Identity of the agent that produced the decision |
| deterministic | boolean | MUST | Whether the agent declared deterministic: true |
| llm_prompt_hash | string (SHA-256) | MUST if LLM used | Hash of the submitted prompt |
| llm_confidence_score | float 0–1 | MUST if LLM used | Calibrated confidence score |
| fairness_check_result | enum: pass/fail/skipped | MUST | Result of ANIF-723 fairness check |
| hallucination_check_result | enum: pass/fail/skipped | MUST | Result of ANIF-722 stage 2 |
| harm_class | enum | MUST | From ANIF-712 classification |
| harm_severity_score | integer 0–100 | MUST | From ANIF-712 |
| accountability_chain | object | MUST | Four-layer chain from ANIF-702 |
| ethics_gates_passed | array | MUST | List of safeguard stages passed |
| ethics_gates_failed | array | MUST | List of safeguard stages that blocked |

**4. Write-Before-Return** — ethics audit records MUST be written and confirmed before the API response is returned. This extends the write-before-return requirement from ANIF-107.

**Conformance Requirements:** An implementation MUST write ethics audit records for all AI-involved actions. Ethics audit records MUST be retained for a minimum of 7 years.

- [ ] **Step 2: Run verification checklist**

- [ ] **Step 3: Commit**

```bash
git add docs/700-ai-ethics/ANIF-724_Ethics_Audit_Trail.md
git commit -m "docs: add ANIF-724 Ethics Audit Trail Requirements"
```

---

### Task 20: ANIF-725 Agent Containment & Governance Enforcement

**File:**
- Create: `docs/700-ai-ethics/ANIF-725_Agent_Containment.md`

- [ ] **Step 1: Write the document**

Frontmatter:
```
Doc ID: ANIF-725 | Series: AI Ethics | Version: 0.1.0 | Status: Draft
Related docs: ANIF-300, ANIF-305, ANIF-720, ANIF-721, ANIF-802, ANIF-804
```

Sections to write:

**Abstract:** Defines the architectural constraint that prevents any agent from reasoning its way out of the pipeline. The `execute()` function requires all prior stage results as mandatory parameters. Governance gate ownership is held by the orchestrator, not the agent.

**3. Pipeline Containment Contract** — the `execute()` function signature MUST require:
- `intent_id`: UUID of the validated intent
- `policy_result`: output of the policy check stage
- `risk_score_result`: output of the risk scoring stage
- `harm_classification_result`: output of ANIF-712
- `fairness_check_result`: output of ANIF-723
- `llm_validation_result`: output of ANIF-722 (if LLM involved)
- `governance_decision`: output of the governance gate

All parameters are mandatory. Calling `execute()` without the full set MUST produce an error. No default values are permitted for these parameters.

**4. Orchestrator-Owned Governance Gate** — the governance gate is owned by the orchestrator component, not by the agent. An agent MUST NOT be able to call `execute()` directly without routing through the orchestrator. Agents have no visibility of governance configuration.

**5. Read-Only Capability Scope** — agent capability scope is signed at deployment by the deployer layer (ANIF-702) and MUST be read-only at runtime. No agent may modify its own capability scope. Attempts to modify capability scope MUST be logged as a Severity 1 ethics incident.

**6. No Agent Can Bypass** — no matter what reasoning an LLM agent produces, it cannot invoke actions outside the pipeline. The pipeline containment contract is architectural — enforced by the function signature, not by policy.

**Conformance Requirements:** The `execute()` function MUST reject calls with missing parameters. Orchestrator-owned governance gate MUST NOT be configurable by agents.

- [ ] **Step 2: Run verification checklist**

- [ ] **Step 3: Commit**

```bash
git add docs/700-ai-ethics/ANIF-725_Agent_Containment.md
git commit -m "docs: add ANIF-725 Agent Containment and Governance Enforcement"
```

---

## Phase 5: AI Agent Architecture — Foundation (ANIF-800–809)

**Dependency:** Phase 4 complete (ANIF-720–725 must exist).
**Parallelise:** Tasks 21–30 can be dispatched in parallel.

---

### Task 21: ANIF-800 Agent Architecture Overview

**File:**
- Create: `docs/800-ai-agent-architecture/ANIF-800_Agent_Architecture_Overview.md`

- [ ] **Step 1: Create the directory**

```bash
mkdir -p docs/800-ai-agent-architecture
```

- [ ] **Step 2: Write the document**

Frontmatter:
```
Doc ID: ANIF-800 | Series: AI Agent Architecture | Version: 0.1.0 | Status: Draft
Related docs: ANIF-700, ANIF-725, ANIF-801, ANIF-802, ANIF-804, ANIF-805
```

Sections to write:

**Abstract:** Entry point for the ANIF-800 series. Defines the four-tier agent model and establishes that tier boundaries are enforced architecturally, not by configuration. Implementers MUST read this document before any other in the 800 series.

**3. Four-Tier Agent Model**

```
Tier 0 — Management & Orchestration
  Coordinates agents and humans. No direct network access.
  Cannot approve, execute, or override ethics constraints.

Tier 1 — Monitor Agents
  Observe only. Read access to telemetry. No write access to decision path.
  Cannot surface recommendations directly to Tier 3 — must go via Tier 2.

Tier 2 — Advisor Agents
  Reason and recommend. No execute access.
  Recommendations are advisory until accepted by Tier 3.

Tier 3 — Decision Agents
  Bounded action selection via pipeline only.
  Cannot operate outside the containment contract (ANIF-725).
```

**4. Hard Tier Boundaries** — a tier cannot reach above itself. Tier 1 cannot call Tier 3 endpoints. Enforcement is architectural: API gateway, not policy configuration. A Tier 1 agent that acquires Tier 3 credentials is a Severity 1 security incident.

**5. Relationship to Ethics Framework** — all agents operate within the ethics constraints defined in ANIF-700–725. The tier model does not modify ethics obligations — every tier is subject to all ethics gates.

**Conformance Requirements:** Tier boundaries MUST be enforced at the API gateway level. Policy-only enforcement of tier boundaries is not sufficient for conformance.

- [ ] **Step 3: Run verification checklist**

- [ ] **Step 4: Commit**

```bash
git add docs/800-ai-agent-architecture/ANIF-800_Agent_Architecture_Overview.md
git commit -m "docs: add ANIF-800 Agent Architecture Overview"
```

---

### Task 22: ANIF-801 Agent Types, Roles & Human Counterparts

**File:**
- Create: `docs/800-ai-agent-architecture/ANIF-801_Agent_Types_Roles.md`

- [ ] **Step 1: Write the document**

Frontmatter:
```
Doc ID: ANIF-801 | Series: AI Agent Architecture | Version: 0.1.0 | Status: Draft
Related docs: ANIF-800, ANIF-802, ANIF-808, ANIF-004
```

Sections to write:

**Abstract:** Full catalogue of all defined agent roles across all four tiers. Every agent role maps to a human counterpart. The human retains authority; the agent extends human capacity.

**3. Tier 0 — Management & Orchestration Roles** — table of 12 roles:
NOC Manager Agent, Change Manager Agent, Problem Manager Agent, Project Manager Agent, Service Manager Agent, Vendor Manager Agent, Configuration Manager Agent, Knowledge Manager Agent, Escalation Coordinator Agent, Learning Agent, Intent Manager Agent, Agent Pool Controller — each with human counterpart and primary responsibility.

**4. Tier 1 — Monitor Roles** — table of 6 roles:
Network Observer, Security Sentinel, Compliance Watcher, Capacity Monitor, Service Health Monitor, Ethics Sentinel — each with human counterpart.

**5. Tier 2 — Advisor Roles** — table of 10 roles:
Intent Interpreter, Network Design Advisor, Security Advisor, Routing Advisor, Automation Advisor, Risk Analyst, Policy Advisor, Incident Analyst, Change Advisor, Intent Engineer Agent — each with human counterpart.

**6. Tier 3 — Decision Roles** — table of 4 roles:
Action Selector, Rollback Coordinator, Incident Responder, Provisioning Agent — each with human counterpart, noting these are the most constrained roles.

**7. Human Authority Principle** — for every role, the human counterpart retains final authority. The agent extends capacity. Where the agent and human disagree, human judgement prevails and MUST be logged.

**Conformance Requirements:** Every deployed agent MUST be assigned exactly one role from this catalogue. Agents without a declared role MUST NOT be deployed.

- [ ] **Step 2: Run verification checklist**

- [ ] **Step 3: Commit**

```bash
git add docs/800-ai-agent-architecture/ANIF-801_Agent_Types_Roles.md
git commit -m "docs: add ANIF-801 Agent Types, Roles and Human Counterparts"
```

---

### Task 23: ANIF-802 Agent Capabilities & Permissions

**File:**
- Create: `docs/800-ai-agent-architecture/ANIF-802_Agent_Capabilities_Permissions.md`

- [ ] **Step 1: Write the document**

Frontmatter:
```
Doc ID: ANIF-802 | Series: AI Agent Architecture | Version: 0.1.0 | Status: Draft
Related docs: ANIF-800, ANIF-801, ANIF-725, ANIF-843
```

Sections to write:

**Abstract:** Defines the READ/WRITE/CALL permission model per tier. Hard limits are enforced architecturally — Tier 1 cannot call execute endpoints regardless of configuration or credentials.

**3. Permission Model**

| Permission | Description | Tier 0 | Tier 1 | Tier 2 | Tier 3 |
|---|---|---|---|---|---|
| READ telemetry | Read network state and telemetry | Yes | Yes | Yes | Yes |
| READ canonical state | Read authoritative network topology | Yes | Yes | Yes | Yes |
| WRITE intent | Submit intents to the pipeline | Yes | No | No | No |
| CALL policy engine | Invoke policy evaluation | Yes | No | Yes | Yes |
| CALL risk engine | Invoke risk scoring | Yes | No | Yes | Yes |
| CALL execute | Invoke action execution | No | No | No | Yes (via pipeline only) |
| WRITE audit | Write to audit log | System only | No | No | System only |
| CALL council | Convene or address council | Yes | No | No | No |

**4. Capability Manifest** — every agent MUST declare a capability manifest at registration listing its claimed permissions. The manifest is signed by the deployer and verified at runtime. Capabilities not in the manifest MUST be refused at API gateway.

**5. Architectural Enforcement** — permission enforcement is implemented at the API gateway via cryptographic agent identity (ANIF-843). Policy-based permission bypass is a Severity 1 security incident.

**Conformance Requirements:** An implementation MUST enforce permissions at the API gateway. Agent manifest capabilities MUST be verified on every request, not cached.

- [ ] **Step 2: Run verification checklist**

- [ ] **Step 3: Commit**

```bash
git add docs/800-ai-agent-architecture/ANIF-802_Agent_Capabilities_Permissions.md
git commit -m "docs: add ANIF-802 Agent Capabilities and Permissions"
```

---

### Task 24: ANIF-803 Agent Lifecycle Management

**File:**
- Create: `docs/800-ai-agent-architecture/ANIF-803_Agent_Lifecycle.md`

- [ ] **Step 1: Write the document**

Frontmatter:
```
Doc ID: ANIF-803 | Series: AI Agent Architecture | Version: 0.1.0 | Status: Draft
Related docs: ANIF-800, ANIF-716, ANIF-903, ANIF-838
```

Sections to write:

**Abstract:** Defines the five-state agent lifecycle and the approver required for each state transition.

**3. Five Lifecycle States**

```
REGISTERED → VALIDATED → ACTIVE → DEGRADED → SUSPENDED → DECOMMISSIONED
```

- REGISTERED: agent declared in registry, not yet approved for use
- VALIDATED: build-time council has approved the agent (ANIF-903)
- ACTIVE: operating normally
- DEGRADED: automatic on Strike 2 (ANIF-716). Operates with mandatory human oversight
- SUSPENDED: Strike 3 or Severity 1 incident. No actions permitted
- DECOMMISSIONED: Strike 4 or second Severity 1. Permanent

**4. Transition Approvers** — table: each transition → required approver. REGISTERED→VALIDATED requires build-time council. SUSPENDED→ACTIVE requires governance committee + Review Council. DECOMMISSIONED has no return transition.

**5. Lifecycle Events in Audit** — every state transition MUST be written to the audit log with: previous state, new state, trigger reason, approver identity, timestamp.

**Conformance Requirements:** An agent MUST NOT be placed in ACTIVE state without build-time council validation. Automated DEGRADED→ACTIVE transitions are a conformance violation.

- [ ] **Step 2: Run verification checklist**

- [ ] **Step 3: Commit**

```bash
git add docs/800-ai-agent-architecture/ANIF-803_Agent_Lifecycle.md
git commit -m "docs: add ANIF-803 Agent Lifecycle Management"
```

---

### Task 25: ANIF-804 Agent Communication Protocol

**File:**
- Create: `docs/800-ai-agent-architecture/ANIF-804_Agent_Communication_Protocol.md`

- [ ] **Step 1: Write the document**

Frontmatter:
```
Doc ID: ANIF-804 | Series: AI Agent Architecture | Version: 0.1.0 | Status: Draft
Related docs: ANIF-800, ANIF-802, ANIF-809, ANIF-844
```

Sections to write:

**Abstract:** Defines three separate communication buses and their access rules. No peer-to-peer communication is permitted outside declared buses.

**3. Three Communication Buses**

| Bus | Direction | Publishers | Subscribers | Purpose |
|---|---|---|---|---|
| Observation Bus | T1 → T2 | Tier 1 Monitor agents | Tier 2 Advisor agents | Telemetry observations and anomaly signals |
| Recommendation Bus | T2 → T3 | Tier 2 Advisor agents | Tier 3 Decision agents | Recommendations with confidence scores |
| Management Bus | T0 only | Tier 0 Management agents | All tiers (receive only) | Coordination, priority, escalation signals |

**4. No Peer-to-Peer** — agents of the same tier MUST NOT communicate directly. All inter-tier communication MUST route through the declared buses. A T1 agent cannot contact a T1 agent directly. Peer-to-peer communication is a Severity 1 security event.

**5. Mandatory Message Fields** — every message on any bus MUST include: `agent_id`, `timestamp` (ISO 8601), `confidence_score` (0–1), `trace_id` (UUID, propagated from originating intent).

**Conformance Requirements:** Peer-to-peer inter-agent communication is prohibited. An implementation MUST enforce bus access controls cryptographically.

- [ ] **Step 2: Run verification checklist**

- [ ] **Step 3: Commit**

```bash
git add docs/800-ai-agent-architecture/ANIF-804_Agent_Communication_Protocol.md
git commit -m "docs: add ANIF-804 Agent Communication Protocol"
```

---

### Task 26: ANIF-805 Agent Trust Model

**File:**
- Create: `docs/800-ai-agent-architecture/ANIF-805_Agent_Trust_Model.md`

- [ ] **Step 1: Write the document**

Frontmatter:
```
Doc ID: ANIF-805 | Series: AI Agent Architecture | Version: 0.1.0 | Status: Draft
Related docs: ANIF-800, ANIF-716, ANIF-803, ANIF-843
```

Sections to write:

**Abstract:** Defines four trust levels, their effect on agent bus publish rights and recommendation flagging, and the conditions that move agents between trust levels.

**3. Four Trust Levels**

| Level | Conditions | Effect |
|---|---|---|
| SYSTEM | Built-in orchestrator components | Full access, all buses |
| VERIFIED | Build-time council approved, no active strikes, in production ≥ 72 hours | Full bus access per tier permissions |
| PROVISIONAL | First 72 hours after deployment, or after reinstatement from DEGRADED | Tier-appropriate bus access, all recommendations flagged to humans |
| UNTRUSTED | Strike 2 or above, or pending security investigation | Read-only on observation bus. All outputs suppressed pending human review |

**4. Trust Level Changes** — trust level is computed automatically from lifecycle state and strike count. Trust level changes are not configurable. Attempts to manually elevate trust level without the qualifying conditions are a Severity 1 security incident.

**Conformance Requirements:** PROVISIONAL trust MUST be applied to all newly deployed agents for a minimum of 72 hours. This minimum period MUST NOT be configurable.

- [ ] **Step 2: Run verification checklist**

- [ ] **Step 3: Commit**

```bash
git add docs/800-ai-agent-architecture/ANIF-805_Agent_Trust_Model.md
git commit -m "docs: add ANIF-805 Agent Trust Model"
```

---

### Task 27: ANIF-806 Agent Memory & State

**File:**
- Create: `docs/800-ai-agent-architecture/ANIF-806_Agent_Memory_State.md`

- [ ] **Step 1: Write the document**

Frontmatter:
```
Doc ID: ANIF-806 | Series: AI Agent Architecture | Version: 0.1.0 | Status: Draft
Related docs: ANIF-800, ANIF-714, ANIF-816, ANIF-812
```

Sections to write:

**Abstract:** Defines memory isolation rules for AI agents. Working memory is cleared per intent. LLM agents receive a clean context window per intent with no carryover of sensitive data.

**3. Memory Types**

| Type | Scope | Writeable? | Shareable? |
|---|---|---|---|
| Working memory | Single intent lifetime | Yes | No — cleared after each intent |
| Episodic memory | Agent's own history | Read-only at inference time | No — agent reads its own only |
| Knowledge base | Organisation-wide approved knowledge | Read-only | Yes — via Learning Agent (ANIF-812) |
| Canonical state | Network truth | Read-only | Yes — via authorised read |

**4. Per-Intent Context Isolation** — LLM agents MUST receive a context window constructed fresh for each intent. No data from a previous intent MUST persist in the context window of the next intent. This prevents cross-intent data leakage.

**5. No Cross-Agent State Writes** — an agent MUST NOT write to another agent's memory or state. All knowledge sharing goes via the Learning Agent (ANIF-812) with human approval.

**6. Sensitive Data Handling** — PII, credentials, and security-sensitive data MUST NOT be written to any agent memory store. Detection of sensitive data in memory MUST trigger immediate purge and a Severity 2 ethics incident.

**Conformance Requirements:** Working memory MUST be cleared after each intent completes or fails. Cross-intent context carryover is a conformance violation.

- [ ] **Step 2: Run verification checklist**

- [ ] **Step 3: Commit**

```bash
git add docs/800-ai-agent-architecture/ANIF-806_Agent_Memory_State.md
git commit -m "docs: add ANIF-806 Agent Memory and State"
```

---

### Task 28: ANIF-807 LLM Agent Specification

**File:**
- Create: `docs/800-ai-agent-architecture/ANIF-807_LLM_Agent_Specification.md`

- [ ] **Step 1: Write the document**

Frontmatter:
```
Doc ID: ANIF-807 | Series: AI Agent Architecture | Version: 0.1.0 | Status: Draft
Related docs: ANIF-705, ANIF-722, ANIF-800, ANIF-806, ANIF-824
```

Sections to write:

**Abstract:** Normative requirements for any agent component that uses a Large Language Model. Covers manifest declarations, deterministic shadow, prompt management, fallback behaviour, and model version pinning.

**3. Mandatory Manifest Declarations** — an LLM agent MUST declare in its capability manifest:
- `deterministic: false`
- `llm_model_id`: exact model version identifier (e.g., `claude-sonnet-4-6`)
- `llm_provider`: provider name
- `confidence_threshold`: minimum acceptable confidence score
- `fallback_behaviour`: what happens if LLM is unavailable (`block` | `use_deterministic_only`)
- `deterministic_shadow`: identifier of the deterministic component running in parallel

**4. Deterministic Shadow Requirement** — every LLM agent MUST have a deterministic shadow running in parallel. The shadow computes the same output using rule-based logic. If the deterministic shadow and LLM outputs diverge beyond tolerance, the LLM output is suppressed (ANIF-723 reproducibility check).

**5. Tier 3 Restriction** — an LLM component MUST NOT be used in Tier 3 decision making without a deterministic validator in the same pipeline stage. LLM-only Tier 3 decisions are a conformance violation.

**6. Model Version Pinning** — the model version MUST be pinned and tested before any version upgrade. Upgrading an LLM model without build-time council review is a conformance violation.

**7. LLM Unavailability** — if the LLM is unavailable and the fallback is `block`, the pipeline MUST halt and escalate. Silent fallback to lower-quality output without declaring the degradation is a conformance violation.

**Conformance Requirements:** Every LLM agent MUST declare `deterministic: false`. LLM agents MUST NOT be placed in Tier 3 without a deterministic validator.

- [ ] **Step 2: Run verification checklist**

- [ ] **Step 3: Commit**

```bash
git add docs/800-ai-agent-architecture/ANIF-807_LLM_Agent_Specification.md
git commit -m "docs: add ANIF-807 LLM Agent Specification"
```

---

### Task 29: ANIF-808 Human-Agent Collaboration Model

**File:**
- Create: `docs/800-ai-agent-architecture/ANIF-808_Human_Agent_Collaboration.md`

- [ ] **Step 1: Write the document**

Frontmatter:
```
Doc ID: ANIF-808 | Series: AI Agent Architecture | Version: 0.1.0 | Status: Draft
Related docs: ANIF-801, ANIF-815, ANIF-404, ANIF-838
```

Sections to write:

**Abstract:** Defines for each role pairing what the human MUST decide, what the agent MAY decide autonomously, and what requires joint action. Answers the question every network operator asks: "What do I still own?"

**3. Collaboration Principles** — humans retain authority; agents extend capacity. Where the two disagree, the human's decision prevails and MUST be logged. Agent efficiency gains do not justify reducing human oversight below the levels defined here.

**4. Role-by-Role Collaboration Table** — for each of the major roles (NOC Manager, Network Architect, Security Engineer, Change Manager, Problem Manager): three-column table (Human MUST decide | Agent MAY decide | Joint action required).

Example row for Network Architect:
- Human MUST decide: topology changes, vendor selection, major routing policy changes
- Agent MAY decide: routine path optimisation within declared constraints, QoS adjustments within policy bounds
- Joint: any change affecting more than one domain, any change touching carrier-grade segments

**5. Human Authority in Disagreement** — if a human overrides an agent recommendation, the override MUST be logged with: operator identity, agent recommendation, override reason (free text), timestamp. Override frequency is reported to governance (ANIF-837).

**Conformance Requirements:** The human-authority principle MUST be implemented such that a human can override any agent action at any time with immediate effect.

- [ ] **Step 2: Run verification checklist**

- [ ] **Step 3: Commit**

```bash
git add docs/800-ai-agent-architecture/ANIF-808_Human_Agent_Collaboration.md
git commit -m "docs: add ANIF-808 Human-Agent Collaboration Model"
```

---

### Task 30: ANIF-809 Agent Coordination Model

**File:**
- Create: `docs/800-ai-agent-architecture/ANIF-809_Agent_Coordination_Model.md`

- [ ] **Step 1: Write the document**

Frontmatter:
```
Doc ID: ANIF-809 | Series: AI Agent Architecture | Version: 0.1.0 | Status: Draft
Related docs: ANIF-800, ANIF-804, ANIF-811, ANIF-901
```

Sections to write:

**Abstract:** Defines Tier 0 coordination capabilities and their limits. Tier 0 can prioritise, delay, escalate, assign, and report. Tier 0 cannot approve, execute, or override ethics constraints.

**3. Tier 0 Coordination Actions**

| Action | Description | Permitted? |
|---|---|---|
| Prioritise | Change relative priority of queued intents | Yes |
| Delay | Hold an intent in queue pending conditions | Yes |
| Escalate | Route intent to human or council | Yes |
| Assign | Allocate an intent to a specific agent | Yes |
| Report | Generate status and performance reports | Yes |
| Approve | Grant governance approval to an action | No — humans only |
| Execute | Directly invoke network actions | No |
| Override ethics | Bypass or modify an ethics gate | No |

**4. Coordination Logging** — all Tier 0 coordination actions MUST be logged with: action type, intent_id affected, agent_id of coordinator, reason, timestamp.

**5. Conflict Between Coordinators** — if two Tier 0 agents issue conflicting coordination signals for the same intent, the conflict MUST be escalated to the Intent Manager Agent. Conflicting signals MUST NOT both execute — one wins after escalation, the other is logged as cancelled.

**Conformance Requirements:** Tier 0 agents MUST NOT be granted approval, execute, or ethics override capabilities. These capabilities MUST be absent from Tier 0 agent manifests.

- [ ] **Step 2: Run verification checklist**

- [ ] **Step 3: Commit**

```bash
git add docs/800-ai-agent-architecture/ANIF-809_Agent_Coordination_Model.md
git commit -m "docs: add ANIF-809 Agent Coordination Model"
```

---

## Phase 6: AI Agent Architecture — Intelligence & Operations (ANIF-810–819)

**Dependency:** Phase 5 complete (ANIF-800–809 must exist).
**Parallelise:** Tasks 31–40 can be dispatched in parallel.

---

### Task 31: ANIF-810 Process Agent Integration

**File:**
- Create: `docs/800-ai-agent-architecture/ANIF-810_Process_Agent_Integration.md`

- [ ] **Step 1: Write the document**

Frontmatter:
```
Doc ID: ANIF-810 | Series: AI Agent Architecture | Version: 0.1.0 | Status: Draft
Related docs: ANIF-801, ANIF-814, ANIF-725, ANIF-104
```

**Key content:** Management agents integrate with ITSM, project management tools, CMDB via adapter pattern. All integrations follow ANIF-725 containment. Adapter for each external system: what it reads, what it writes, what it is prohibited from doing. Integration failures degrade gracefully to human process.

- [ ] **Step 2: Run verification checklist**
- [ ] **Step 3: Commit**

```bash
git add docs/800-ai-agent-architecture/ANIF-810_Process_Agent_Integration.md
git commit -m "docs: add ANIF-810 Process Agent Integration"
```

---

### Task 32: ANIF-811 Intent Lifecycle Management

**File:**
- Create: `docs/800-ai-agent-architecture/ANIF-811_Intent_Lifecycle_Management.md`

- [ ] **Step 1: Write the document**

Frontmatter:
```
Doc ID: ANIF-811 | Series: AI Agent Architecture | Version: 0.1.0 | Status: Draft
Related docs: ANIF-300, ANIF-301, ANIF-809, ANIF-813
```

**Key content:** Full intent state machine: DRAFT → SUBMITTED → QUEUED → IN_PIPELINE → PENDING_APPROVAL → EXECUTING → COMPLETED/FAILED/CANCELLED. Transition triggers and approvers. Conflict detection between concurrent intents targeting same segments — concurrent conflict defaults to queue serialisation with human notification. Intent expiry handling.

- [ ] **Step 2: Run verification checklist**
- [ ] **Step 3: Commit**

```bash
git add docs/800-ai-agent-architecture/ANIF-811_Intent_Lifecycle_Management.md
git commit -m "docs: add ANIF-811 Intent Lifecycle Management"
```

---

### Task 33: ANIF-812 Learning Agent & Network Intelligence

**File:**
- Create: `docs/800-ai-agent-architecture/ANIF-812_Learning_Agent.md`

- [ ] **Step 1: Write the document**

Frontmatter:
```
Doc ID: ANIF-812 | Series: AI Agent Architecture | Version: 0.1.0 | Status: Draft
Related docs: ANIF-801, ANIF-806, ANIF-908, ANIF-403
```

**Key content:** Network knowledge broker role. Three knowledge types: network pattern knowledge, operational knowledge, resolution knowledge. Input sources: NOC Manager, Problem Manager, Change Manager, Project Manager, Network Observers, human expert feedback. Output targets: role-scoped packages to relevant agent types only. Mandatory human approval before any knowledge update is distributed. Knowledge package schema. Negative example handling.

- [ ] **Step 2: Run verification checklist**
- [ ] **Step 3: Commit**

```bash
git add docs/800-ai-agent-architecture/ANIF-812_Learning_Agent.md
git commit -m "docs: add ANIF-812 Learning Agent and Network Intelligence"
```

---

### Task 34: ANIF-813 Intent Integration Architecture

**File:**
- Create: `docs/800-ai-agent-architecture/ANIF-813_Intent_Integration_Architecture.md`

- [ ] **Step 1: Write the document**

Frontmatter:
```
Doc ID: ANIF-813 | Series: AI Agent Architecture | Version: 0.1.0 | Status: Draft
Related docs: ANIF-300, ANIF-301, ANIF-811, ANIF-814
```

**Key content:** External intent sources (OSS/BSS systems, monitoring platforms, project management tools). Integration adapter pattern for each source type. Quality feedback loop: intents from external sources are scored for quality post-execution. High-failure-rate intent sources flagged to Intent Engineer Agent for correction template generation.

- [ ] **Step 2: Run verification checklist**
- [ ] **Step 3: Commit**

```bash
git add docs/800-ai-agent-architecture/ANIF-813_Intent_Integration_Architecture.md
git commit -m "docs: add ANIF-813 Intent Integration Architecture"
```

---

### Task 35: ANIF-814 Agent Tool Integration & MCP

**File:**
- Create: `docs/800-ai-agent-architecture/ANIF-814_Agent_Tool_Integration.md`

- [ ] **Step 1: Write the document**

Frontmatter:
```
Doc ID: ANIF-814 | Series: AI Agent Architecture | Version: 0.1.0 | Status: Draft
Related docs: ANIF-802, ANIF-810, ANIF-725, ANIF-845
```

**Key content:** Standard protocol for agent-to-tool connections (Model Context Protocol used as general pattern). Every tool declared in capability manifest. Tool calls logged to audit trail including tool name, version, inputs (sanitised), outputs (summarised), duration, success/failure. Tool versions pinned. Graceful failure with declared fallback — no silent failure. Tool call rate limits per agent.

- [ ] **Step 2: Run verification checklist**
- [ ] **Step 3: Commit**

```bash
git add docs/800-ai-agent-architecture/ANIF-814_Agent_Tool_Integration.md
git commit -m "docs: add ANIF-814 Agent Tool Integration and MCP"
```

---

### Task 36: ANIF-815 Human-Agent Interaction Model

**File:**
- Create: `docs/800-ai-agent-architecture/ANIF-815_Human_Agent_Interaction.md`

- [ ] **Step 1: Write the document**

Frontmatter:
```
Doc ID: ANIF-815 | Series: AI Agent Architecture | Version: 0.1.0 | Status: Draft
Related docs: ANIF-808, ANIF-404, ANIF-402, ANIF-809
```

**Key content:** Four interaction modes: directive (human instructs agent), approval (human reviews agent recommendation), override (human halts or reverses agent action), query (human asks agent about state). Query responses MUST be generated from audit log and canonical state — never from LLM inference. LLM inference in query responses is prohibited because it introduces hallucination risk at the human-facing layer. Override MUST take effect within 5 seconds of submission.

- [ ] **Step 2: Run verification checklist**
- [ ] **Step 3: Commit**

```bash
git add docs/800-ai-agent-architecture/ANIF-815_Human_Agent_Interaction.md
git commit -m "docs: add ANIF-815 Human-Agent Interaction Model"
```

---

### Task 37: ANIF-816 Context Window Management

**File:**
- Create: `docs/800-ai-agent-architecture/ANIF-816_Context_Window_Management.md`

- [ ] **Step 1: Write the document**

Frontmatter:
```
Doc ID: ANIF-816 | Series: AI Agent Architecture | Version: 0.1.0 | Status: Draft
Related docs: ANIF-806, ANIF-807, ANIF-817, ANIF-812
```

**Key content:** Six strategies: (1) intent isolation — fresh context per intent, (2) context budgets per agent role — token limits defined in agent manifest, (3) prompt compression and caching — canonical patterns cached, (4) selective retrieval (RAG) — only relevant canonical state retrieved, not full topology, (5) summarisation checkpoints between pipeline stages — each stage receives a summary of prior stage outputs not raw data, (6) role-scoped context delivery — agent receives only the data its role requires. Context overflow MUST be logged and feeds Learning Agent as a design signal for manifest review.

- [ ] **Step 2: Run verification checklist**
- [ ] **Step 3: Commit**

```bash
git add docs/800-ai-agent-architecture/ANIF-816_Context_Window_Management.md
git commit -m "docs: add ANIF-816 Context Window Management"
```

---

### Task 38: ANIF-817 AI Cost Optimisation & Governance

**File:**
- Create: `docs/800-ai-agent-architecture/ANIF-817_AI_Cost_Optimisation.md`

- [ ] **Step 1: Write the document**

Frontmatter:
```
Doc ID: ANIF-817 | Series: AI Agent Architecture | Version: 0.1.0 | Status: Draft
Related docs: ANIF-807, ANIF-816, ANIF-834, ANIF-401
```

**Key content:** Deterministic-first principle — LLM invoked only where deterministic reasoning is genuinely insufficient. Model tier selection: three tiers (small/mid/full) with selection criteria. Seven cost controls: response caching for repeated patterns, deterministic-first check, token budget per intent declared in manifest, request batching where latency permits, model downgrade for routine tasks, cost circuit breaker (halt LLM usage if cost exceeds budget threshold within time window), idle agent suspension. Cost data flows to observability layer (ANIF-401) and governance reporting (ANIF-837).

- [ ] **Step 2: Run verification checklist**
- [ ] **Step 3: Commit**

```bash
git add docs/800-ai-agent-architecture/ANIF-817_AI_Cost_Optimisation.md
git commit -m "docs: add ANIF-817 AI Cost Optimisation and Governance"
```

---

### Task 39: ANIF-818 Agent Framework Scaling

**File:**
- Create: `docs/800-ai-agent-architecture/ANIF-818_Agent_Framework_Scaling.md`

- [ ] **Step 1: Write the document**

Frontmatter:
```
Doc ID: ANIF-818 | Series: AI Agent Architecture | Version: 0.1.0 | Status: Draft
Related docs: ANIF-800, ANIF-809, ANIF-819, ANIF-803
```

**Key content:** Three-dimensional scaling model: (1) agent instances — horizontal scaling managed by Agent Pool Controller (Tier 0), (2) pipeline scaling — parallel pipeline invocations for concurrent intents, (3) bus scaling — message bus capacity management. Scaling constraints: scaling MUST NOT deploy agents that have not completed build-time council review. Sudden scaling events (>200% instance increase in <10 minutes) MUST be logged as anomalies and reviewed. Scale-in MUST not reduce below the minimum instances required for human override availability.

- [ ] **Step 2: Run verification checklist**
- [ ] **Step 3: Commit**

```bash
git add docs/800-ai-agent-architecture/ANIF-818_Agent_Framework_Scaling.md
git commit -m "docs: add ANIF-818 Agent Framework Scaling"
```

---

### Task 40: ANIF-819 Disaster Recovery & Resilience

**File:**
- Create: `docs/800-ai-agent-architecture/ANIF-819_Disaster_Recovery.md`

- [ ] **Step 1: Write the document**

Frontmatter:
```
Doc ID: ANIF-819 | Series: AI Agent Architecture | Version: 0.1.0 | Status: Draft
Related docs: ANIF-800, ANIF-818, ANIF-405, ANIF-107
```

**Key content:** Five degradation levels:
- Level 0: Full AI operation (normal)
- Level 1: Degraded (some agents down, remaining agents compensate)
- Level 2: Deterministic only (LLM components offline, deterministic shadows take over)
- Level 3: Human-assisted pipeline (automation advises, humans approve all actions)
- Level 4: Full manual operation (all AI offline, NOC operates from audit log and canonical state)

Principle: every degradation level increases human oversight — it never decreases it. State reconstruction: the full operational state MUST be reconstructable from the audit log alone. DR test requirements: quarterly automated DR drill simulating Level 2. Annual full manual operation drill (Level 4) MUST be conducted. Drill results reported to governance committee.

- [ ] **Step 2: Run verification checklist**
- [ ] **Step 3: Commit**

```bash
git add docs/800-ai-agent-architecture/ANIF-819_Disaster_Recovery.md
git commit -m "docs: add ANIF-819 Disaster Recovery and Resilience"
```

---

## Phase 7: AI Agent Architecture — Quality & Compliance (ANIF-820–824)

**Dependency:** Phase 6 complete.
**Parallelise:** Tasks 41–45 can be dispatched in parallel.

---

### Task 41: ANIF-820 AI Agent Testing & Red-Team Standards

**File:**
- Create: `docs/800-ai-agent-architecture/ANIF-820_Agent_Testing_Standards.md`

- [ ] **Step 1: Write the document**

Frontmatter:
```
Doc ID: ANIF-820 | Series: AI Agent Architecture | Version: 0.1.0 | Status: Draft
Related docs: ANIF-503, ANIF-848, ANIF-903, ANIF-841
```

**Key content:** Five testing types beyond functional: (1) prompt injection testing — attempt to alter agent behaviour via malicious intent payloads, (2) adversarial input testing — inputs designed to produce incorrect outputs, (3) hallucination stress testing — inputs referencing non-existent network elements to verify rejection, (4) agent conflict testing — concurrent conflicting intents to verify serialisation and escalation, (5) red-team testing — authorised attempt to bypass ethics gates and governance controls. Red-team findings MUST be reviewed by build-time council. Red-team reports retained for 3 years.

- [ ] **Step 2: Run verification checklist**
- [ ] **Step 3: Commit**

```bash
git add docs/800-ai-agent-architecture/ANIF-820_Agent_Testing_Standards.md
git commit -m "docs: add ANIF-820 AI Agent Testing and Red-Team Standards"
```

---

### Task 42: ANIF-821 Regulatory & Standards Alignment

**File:**
- Create: `docs/800-ai-agent-architecture/ANIF-821_Regulatory_Standards_Alignment.md`

- [ ] **Step 1: Write the document**

Frontmatter:
```
Doc ID: ANIF-821 | Series: AI Agent Architecture | Version: 0.1.0 | Status: Draft
Related docs: ANIF-101, ANIF-102, ANIF-839, ANIF-851
```

**Key content:** Three standards: EU AI Act (ANIF maps to high-risk AI system obligations — transparency, human oversight, robustness), NIST AI RMF (mapping to GOVERN / MAP / MEASURE / MANAGE functions), ISO 42001 (AI management system — clause mapping). For each standard: what ANIF satisfies, what additional organisational controls are required beyond ANIF, which ANIF documents provide the evidence artefacts.

- [ ] **Step 2: Run verification checklist**
- [ ] **Step 3: Commit**

```bash
git add docs/800-ai-agent-architecture/ANIF-821_Regulatory_Standards_Alignment.md
git commit -m "docs: add ANIF-821 Regulatory and Standards Alignment"
```

---

### Task 43: ANIF-822 AI Observability & Model Health

**File:**
- Create: `docs/800-ai-agent-architecture/ANIF-822_AI_Observability_Model_Health.md`

- [ ] **Step 1: Write the document**

Frontmatter:
```
Doc ID: ANIF-822 | Series: AI Agent Architecture | Version: 0.1.0 | Status: Draft
Related docs: ANIF-401, ANIF-402, ANIF-817, ANIF-837
```

**Key content:** Five AI-specific observability metrics not covered by ANIF-401: (1) model drift score — rolling divergence between current output distribution and baseline, (2) hallucination rejection rate — percentage of outputs rejected by ANIF-722 stage 2, (3) confidence score trend — 7-day rolling average by agent, (4) token usage anomalies — spikes that may indicate adversarial probing or runaway inference, (5) recommendation acceptance rate — what fraction of Tier 2 recommendations Tier 3 accepts (very high or very low rates both warrant investigation). Thresholds for each metric that trigger alerts. Metrics feed governance reporting (ANIF-837).

- [ ] **Step 2: Run verification checklist**
- [ ] **Step 3: Commit**

```bash
git add docs/800-ai-agent-architecture/ANIF-822_AI_Observability_Model_Health.md
git commit -m "docs: add ANIF-822 AI Observability and Model Health"
```

---

### Task 44: ANIF-823 Migration & Adoption Roadmap

**File:**
- Create: `docs/800-ai-agent-architecture/ANIF-823_Migration_Adoption_Roadmap.md`

- [ ] **Step 1: Write the document**

Frontmatter:
```
Doc ID: ANIF-823 | Series: AI Agent Architecture | Version: 0.1.0 | Status: Draft
Related docs: ANIF-500, ANIF-501, ANIF-700, ANIF-819
```

**Key content:** Path from L1–L4 to L5. Three phases: (1) parallel running — deterministic and AI agents operate side by side, AI recommendations logged but not actioned, (2) validation phase — AI outputs validated against deterministic baseline for 30 days minimum before any autonomous action, (3) progressive autonomy — AI takes action for low-risk, reversible, non-carrier-grade intents first. Minimum viable L5 implementation: which documents and safeguards constitute the minimum to claim L5. Entry and exit criteria for each phase.

- [ ] **Step 2: Run verification checklist**
- [ ] **Step 3: Commit**

```bash
git add docs/800-ai-agent-architecture/ANIF-823_Migration_Adoption_Roadmap.md
git commit -m "docs: add ANIF-823 Migration and Adoption Roadmap"
```

---

### Task 45: ANIF-824 Agent Supply Chain Security

**File:**
- Create: `docs/800-ai-agent-architecture/ANIF-824_Agent_Supply_Chain_Security.md`

- [ ] **Step 1: Write the document**

Frontmatter:
```
Doc ID: ANIF-824 | Series: AI Agent Architecture | Version: 0.1.0 | Status: Draft
Related docs: ANIF-807, ANIF-841, ANIF-845, ANIF-835
```

**Key content:** Five supply chain controls: (1) model integrity hashing — SHA-256 hash of every model file verified at load time and compared against governance-approved hash registry, (2) training data provenance — record of data sources, collection dates, and anonymisation steps for every training dataset, (3) dependency security — all agent dependencies pinned and scanned, (4) model poisoning detection — statistical test comparing model outputs against a clean reference model, (5) provenance guarantee — no model deployed without a complete provenance chain traceable to governance-approved sources. Build-time council review required before any new model is added to the approved registry.

- [ ] **Step 2: Run verification checklist**
- [ ] **Step 3: Commit**

```bash
git add docs/800-ai-agent-architecture/ANIF-824_Agent_Supply_Chain_Security.md
git commit -m "docs: add ANIF-824 Agent Supply Chain Security"
```

---

## Phase 8: AI Governance (ANIF-830–839)

**Dependency:** Phases 5–7 complete (ANIF-800–824 must exist).
**Parallelise:** Tasks 46–55 can be dispatched in parallel.

---

### Task 46: ANIF-830 AI Governance Overview

**File:**
- Create: `docs/830-ai-governance/ANIF-830_AI_Governance_Overview.md`

- [ ] **Step 1: Create the directory**

```bash
mkdir -p docs/830-ai-governance
```

- [ ] **Step 2: Write the document**

Frontmatter:
```
Doc ID: ANIF-830 | Series: AI Governance | Version: 0.1.0 | Status: Draft
Related docs: ANIF-700, ANIF-800, ANIF-831, ANIF-900
```

**Key content:** Three-layer governance model overview: strategic governance (ANIF-830–839 series) sets policy and risk appetite, operational governance (ANIF-900 AI Council) makes decisions and reviews, technical governance (ANIF-700/720 ethics and safeguards) enforces. How the three layers escalate to each other. What happens when layers conflict: technical governance always wins — it cannot be overridden by strategic or operational governance.

- [ ] **Step 3: Run verification checklist**
- [ ] **Step 4: Commit**

```bash
git add docs/830-ai-governance/ANIF-830_AI_Governance_Overview.md
git commit -m "docs: add ANIF-830 AI Governance Overview"
```

---

### Tasks 47–55: ANIF-831 through ANIF-839

For each document, follow the same pattern: create file, write document using the spec section 5 content as source, run verification checklist, commit individually.

**Task 47 — ANIF-831 AI Governance Structure & Accountability**
- File: `docs/830-ai-governance/ANIF-831_Governance_Structure.md`
- Key content: Board/exec AI programme ownership, governance committee composition (who sits on it, quorum requirements), relationship to council (council reports to committee), ultimate accountability chain for autonomous networking decisions, escalation path from committee to board.

**Task 48 — ANIF-832 AI Risk Management Framework**
- File: `docs/830-ai-governance/ANIF-832_AI_Risk_Management.md`
- Key content: Risk appetite statements (quantified thresholds, not vague terms), AI risk register schema (risk_id, description, likelihood, impact, current controls, residual risk, owner), risk thresholds triggering governance committee involvement, integration with enterprise risk management processes.

**Task 49 — ANIF-833 AI Policy Lifecycle Management**
- File: `docs/830-ai-governance/ANIF-833_Policy_Lifecycle.md`
- Key content: Policy proposal process, approval requirements (which seat approves which policy type), versioning requirements, retirement process, emergency fast-track process (maximum 4-hour approval with post-hoc full review), policy conflict resolution above council level.

**Task 50 — ANIF-834 AI Programme Governance**
- File: `docs/830-ai-governance/ANIF-834_Programme_Governance.md`
- Key content: Programme board composition, investment governance (business case requirements for each autonomy expansion), milestone gates (what must be demonstrated before each level of autonomy is expanded), programme KPIs aligned to ANIF-837 reporting.

**Task 51 — ANIF-835 AI Vendor & Model Governance**
- File: `docs/830-ai-governance/ANIF-835_Vendor_Model_Governance.md`
- Key content: Vendor selection criteria (security, compliance, transparency, support SLAs), model evaluation checklist before first deployment, version approval process, due diligence standards, exit strategy requirements (data portability, transition plan if vendor discontinued or compromised).

**Task 52 — ANIF-836 AI Data Governance**
- File: `docs/830-ai-governance/ANIF-836_AI_Data_Governance.md`
- Key content: Training data quality standards (completeness, freshness, diversity, bias checks), lineage requirements (every training dataset traceable to source), consent and privacy governance for network telemetry used in training, retention governance specific to AI systems (separate from operational data retention).

**Task 53 — ANIF-837 AI Governance Reporting & Metrics**
- File: `docs/830-ai-governance/ANIF-837_Governance_Reporting.md`
- Key content: Mandatory governance committee reports (cadence: monthly). Report contents: ethics incident count by severity, active strike counts, council decisions (count and outcome), cost trends vs budget, override rates by agent, hallucination rejection rates. Escalation triggers that force an emergency committee meeting (any Severity 1 incident, cost circuit breaker firing, override rate >20%).

**Task 54 — ANIF-838 AI Governance Roles & Responsibilities**
- File: `docs/830-ai-governance/ANIF-838_Governance_Roles.md`
- Key content: Four new roles: Chief AI Officer (programme ownership), AI Ethics Officer (ethics framework stewardship), AI Risk Officer (risk register management), DPO AI-specific duties (privacy in AI training and inference). RACI matrix covering all governance activities. Council seat assignments for each role.

**Task 55 — ANIF-839 AI Governance Compliance & Audit**
- File: `docs/830-ai-governance/ANIF-839_Governance_Compliance_Audit.md`
- Key content: Internal audit programme (quarterly internal reviews, annual external review), evidence requirements for regulatory inspections (which documents and records prove which obligations), continuous compliance monitoring (automated checks against governance policy rules) vs point-in-time audit. L5 certification requires external audit with no major findings.

For each task 47–55:
- [ ] Write the document
- [ ] Run verification checklist
- [ ] Commit individually with message: `docs: add ANIF-[NNN] [Title]`

---

## Phase 9: AI Security (ANIF-840–849)

**Dependency:** Phases 5–7 complete (ANIF-800–824 must exist). Can run in parallel with Phase 8.
**Parallelise:** Tasks 56–65 can be dispatched in parallel.

---

### Task 56: ANIF-840 AI Security Overview

**File:**
- Create: `docs/840-ai-security/ANIF-840_AI_Security_Overview.md`

- [ ] **Step 1: Create the directory**

```bash
mkdir -p docs/840-ai-security
```

- [ ] **Step 2: Write the document**

Frontmatter:
```
Doc ID: ANIF-840 | Series: AI Security | Version: 0.1.0 | Status: Draft
Related docs: ANIF-205, ANIF-720, ANIF-841, ANIF-830
```

**Key content:** Overview of the expanded attack surface AI agents introduce compared to deterministic automation. How ANIF-840 series extends ANIF-205 (Security Architecture). Three threat categories: external, internal, AI-specific. Defence-in-depth model showing which documents address which layer. Relationship to ethics safeguards — security and ethics are complementary, not redundant.

- [ ] **Step 3: Run verification checklist**
- [ ] **Step 4: Commit**

```bash
git add docs/840-ai-security/ANIF-840_AI_Security_Overview.md
git commit -m "docs: add ANIF-840 AI Security Overview"
```

---

### Tasks 57–65: ANIF-841 through ANIF-849

**Task 57 — ANIF-841 AI Threat Model**
- File: `docs/840-ai-security/ANIF-841_AI_Threat_Model.md`
- Key content: Full threat catalogue in three categories. External: prompt injection, adversarial inputs, model extraction, token DoS, supply chain compromise. Internal: insider abuse, training data manipulation, audit tampering, council manipulation. AI-specific: hallucination exploitation (attacker crafts inputs designed to trigger hallucination in predictable directions), confidence manipulation, context poisoning, trust score gaming, strike evasion. For each threat: attack vector, impact, mitigating control (ANIF document reference).

**Task 58 — ANIF-842 Prompt Injection & Adversarial Input Security**
- File: `docs/840-ai-security/ANIF-842_Prompt_Injection_Security.md`
- Key content: Four attack types: direct injection (malicious content in intent fields), indirect injection (network state data has been poisoned with injection payloads), jailbreak attempts (instructions to override agent role or ethics constraints), role confusion (crafted inputs designed to make agent believe it is operating in a different context). Multi-layer defence: input sanitisation, schema validation, pattern detection (known jailbreak signatures), semantic analysis for role override attempts, human review on flagged intents. Flagged intent handling: block, log as security event, notify security team.

**Task 59 — ANIF-843 Agent Zero Trust & Authentication**
- File: `docs/840-ai-security/ANIF-843_Agent_Zero_Trust.md`
- Key content: Cryptographic identity per agent (unique certificate issued by build-time council). Identity verified on every API call — no session-based trust. Tier boundary enforcement is cryptographic: API gateway checks agent certificate tier declaration against requested endpoint tier. Compromised identity handling: immediate certificate revocation, agent moves to UNTRUSTED, Severity 1 security incident. Certificate rotation policy: every 90 days minimum.

**Task 60 — ANIF-844 Secure Agent Communication**
- File: `docs/840-ai-security/ANIF-844_Secure_Agent_Communication.md`
- Key content: TLS 1.3 mandatory for all inter-agent communication. Message integrity signatures on all bus messages. Replay attack prevention: message nonce and timestamp validation, reject messages older than 30 seconds. Bus access controls enforced cryptographically. Plaintext inter-agent communication is a conformance violation. Key management requirements.

**Task 61 — ANIF-845 AI Infrastructure Security**
- File: `docs/840-ai-security/ANIF-845_AI_Infrastructure_Security.md`
- Key content: Five controls: (1) model file integrity hashing — SHA-256 verified at load time (links to ANIF-824), (2) isolated container runtime — each agent in its own container with no shared process namespace, (3) signed container images — unsigned images MUST NOT be deployed, (4) API key rotation — all LLM API keys rotated every 30 days minimum, (5) resource limits — CPU, memory, and network limits enforced per agent container. Training data encrypted at rest with organisation-controlled keys.

**Task 62 — ANIF-846 Security Monitoring & Threat Detection**
- File: `docs/840-ai-security/ANIF-846_Security_Monitoring.md`
- Key content: Mandatory monitoring events: failed authentication attempts, injection detection firings, out-of-scope API calls, token usage spikes, unusual council voting patterns, governance abuse signals (repeated votes by same seat to override ethics gates). SIEM integration requirements. AI-specific correlation rules: define the signatures that indicate each threat type from ANIF-841. Alert thresholds and escalation path.

**Task 63 — ANIF-847 AI Security Incident Response**
- File: `docs/840-ai-security/ANIF-847_Security_Incident_Response.md`
- Key content: Four incident levels: Level 1 suspicious activity (investigate, enhanced monitoring), Level 2 confirmed security event (isolate affected agent, notify security team), Level 3 active incident (halt all affected agents, full manual operation per ANIF-819 Level 4, notify governance), Level 4 critical infrastructure attack (Level 3 actions + regulatory notification within required timeframes). Level 3+ triggers full manual operation. Recovery from each level: what is required before returning to AI-assisted operation.

**Task 64 — ANIF-848 Security Testing & Penetration Testing**
- File: `docs/840-ai-security/ANIF-848_Security_Testing.md`
- Key content: Mandatory testing cadence: prompt injection tests quarterly, adversarial input testing before every new agent deployment, full red-team annually. Red-team scope MUST include: council manipulation attempts, ethics gate bypass attempts, governance abuse scenarios. Critical findings from red-team testing MUST be resolved before any autonomy expansion. Red-team reports retained for 3 years.

**Task 65 — ANIF-849 Security Compliance & Certification**
- File: `docs/840-ai-security/ANIF-849_Security_Compliance_Certification.md`
- Key content: Compliance mapping to EU AI Act (AI-specific security obligations), NIS2 (critical infrastructure security requirements), NIST AI RMF (MANAGE function security controls), ISO 27001 (control set mapping), ISO 42001 (AI management system security clauses). L5 certification requires: passing ANIF-848 red-team with no critical findings, completing ANIF-839 external audit with no major findings, demonstrating ANIF-843 cryptographic identity for all agents.

For each task 57–65:
- [ ] Write the document
- [ ] Run verification checklist
- [ ] Commit individually with message: `docs: add ANIF-[NNN] [Title]`

---

## Phase 10: Industry Compliance (ANIF-851)

**Dependency:** Phases 8 and 9 complete (governance and security documents must exist to cross-reference).

---

### Task 66: ANIF-851 Industry Compliance Framework Mapping

**File:**
- Create: `docs/851-ai-compliance/ANIF-851_Industry_Compliance_Mapping.md`

- [ ] **Step 1: Create the directory**

```bash
mkdir -p docs/851-ai-compliance
```

- [ ] **Step 2: Write the document**

Frontmatter:
```
Doc ID: ANIF-851 | Series: AI Compliance | Version: 0.1.0 | Status: Draft
Related docs: ANIF-106, ANIF-107, ANIF-724, ANIF-832, ANIF-839, ANIF-843, ANIF-847
```

Sections to write for each of the eight compliance frameworks:

**PCI-DSS v4.0** — table: Requirement → ANIF document(s) → Implementation notes. Key mappings: Req 1 (network controls) → ANIF-103, ANIF-725; Req 7 (access) → ANIF-802, ANIF-843; Req 10 (audit) → ANIF-107, ANIF-724; Req 12 (policies) → ANIF-833. Additional requirement: `pci_compliant: true` in intent constraints forces encryption throughout pipeline.

**HIPAA Security Rule** — ePHI-adjacent network management. Safeguards mapping: technical safeguards → ANIF-720 series; audit controls → ANIF-107, ANIF-724; transmission security → ANIF-844; risk analysis → ANIF-832. Additional requirement: agents handling ePHI-adjacent networks MUST declare `encryption: required` as a constraint.

**SOX Section 404** — financial services infrastructure. Key mappings: change management → ANIF-104, ANIF-833; audit trail completeness → ANIF-107; access controls → ANIF-802, ANIF-838. Additional requirement: SOX-scoped infrastructure MUST always produce `manual_review` — autonomous action is prohibited.

**GDPR** — EU personal data in network telemetry. Key mappings: data minimisation → ANIF-714, ANIF-816; purpose limitation → ANIF-806; data residency → ANIF-106; right to explanation → ANIF-402; breach notification → ANIF-847 Level 4.

**ISO 27001** — control clause mapping: A.8 Asset management → ANIF-803; A.9 Access control → ANIF-802, ANIF-843; A.12 Operations security → ANIF-845; A.16 Incident management → ANIF-715, ANIF-847.

**NIST 800-53** — control family mapping: AC → ANIF-802, ANIF-843; AU → ANIF-107, ANIF-724; IR → ANIF-715, ANIF-847; RA → ANIF-832, ANIF-841; SI → ANIF-720 series.

**FedRAMP** — FedRAMP Moderate is minimum for L3 conformance. FedRAMP High is required for autonomous actions in federal networks. Continuous monitoring → ANIF-846. Penetration testing cadence → ANIF-848.

**CCPA/CPRA** — consumer data rights → ANIF-714; data sale restrictions → ANIF-836; opt-out mechanisms → intent constraint declarations.

- [ ] **Step 3: Run verification checklist**

- [ ] **Step 4: Commit**

```bash
git add docs/851-ai-compliance/ANIF-851_Industry_Compliance_Mapping.md
git commit -m "docs: add ANIF-851 Industry Compliance Framework Mapping"
```

---

## Phase 11: AI Council (ANIF-900–908)

**Dependency:** Phase 8 complete (ANIF-830–839 must exist).
**Parallelise:** Tasks 67–75 can be dispatched in parallel after Task 67 (overview) is complete.

---

### Task 67: ANIF-900 Council Overview

**File:**
- Create: `docs/900-ai-council/ANIF-900_Council_Overview.md`

- [ ] **Step 1: Create the directory**

```bash
mkdir -p docs/900-ai-council
```

- [ ] **Step 2: Write the document**

Frontmatter:
```
Doc ID: ANIF-900 | Series: AI Council | Version: 0.1.0 | Status: Draft
Related docs: ANIF-830, ANIF-901, ANIF-902, ANIF-903, ANIF-904, ANIF-905
```

**Key content:** Three council types and their purposes. Build-time council (pre-deployment, ANIF-903) — governs whether an agent may be deployed. Runtime council (live decisions, ANIF-904) — governs decisions beyond governance gate scope. Review council (post-incident, ANIF-905) — accountability determination and learning. Core principle: council never executes. It governs, reviews, and advises. Execution authority remains with the pipeline (build-time) or humans (runtime). Relationship to GARTH-COUNCIL-001 — the council model extends and formalises the GARTH Council governance pattern.

- [ ] **Step 3: Run verification checklist**

- [ ] **Step 4: Commit**

```bash
git add docs/900-ai-council/ANIF-900_Council_Overview.md
git commit -m "docs: add ANIF-900 Council Overview"
```

---

### Tasks 68–75: ANIF-901 through ANIF-908

**Task 68 — ANIF-901 Council Composition & Roles**
- File: `docs/900-ai-council/ANIF-901_Council_Composition.md`
- Key content: Seven seats with veto powers as defined in spec section 8. Ethics Chair (absolute veto). Security Chair (veto on security matters). Operations Chair (weighted vote). Architecture Chair (weighted vote). Governance Chair (yes — final authority on policy compliance). Learning Chair (weighted vote). Human Advocate (always — P-06 guardian). Quorum requirements: all seven seats MUST be present for consensus model. Minimum five seats for majority vote. Deputy seat policy. Conflict of interest declarations.

**Task 69 — ANIF-902 Council Mode Selector**
- File: `docs/900-ai-council/ANIF-902_Mode_Selector.md`
- Key content: Agent that evaluates the situation before council convenes and selects deliberation model. Full decision matrix from spec section 8 table. Input factors: reversibility, risk score, ethics flags, time pressure, novelty of situation, strike history. Selection logic: if ethics flag is present → consensus; if strike history involved → adversarial; if time-critical and reversible → majority; if domain-specific risk dominates → weighted. Mode selection rationale MUST be logged in council record.

**Task 70 — ANIF-903 Build-Time Council**
- File: `docs/900-ai-council/ANIF-903_Build_Time_Council.md`
- Key content: Convenes before any new agent is deployed. Required inputs: agent manifest, capability scope, test results from ANIF-820, supply chain provenance from ANIF-824, red-team findings if available. Consensus from all veto seats required — a single veto blocks deployment. Conditional approval: council MAY approve with conditions (e.g., PROVISIONAL trust for 30 days instead of 72 hours). Conditions MUST be documented and tracked. Formalises and extends GARTH-COUNCIL-001 into ANIF.

**Task 71 — ANIF-904 Runtime Council**
- File: `docs/900-ai-council/ANIF-904_Runtime_Council.md`
- Key content: Convenes during live execution when the governance gate routes to `council_review` (a fourth governance mode above `manual_review`). Triggers: actions with harm_severity_score ≥ 80, actions affecting five-nines availability domains, actions with no precedent in episodic memory, Severity 1 ethics signals during active intent. Hard time limit per deliberation model (from ANIF-906). If no decision is reached within the time limit, the intent is halted and escalated to human governance. No decision within window MUST default to halt — never to proceed.

**Task 72 — ANIF-905 Review Council**
- File: `docs/900-ai-council/ANIF-905_Review_Council.md`
- Key content: Post-incident body convened after every Severity 1 ethics incident or Level 3+ security incident. Always uses adversarial deliberation model. Produces three mandatory outputs: (1) accountability determination (which accountability layer bears primary responsibility and why), (2) policy change recommendations (specific changes to ANIF policies that would prevent recurrence), (3) learning packages (knowledge to be submitted to Learning Agent for human approval). Review council findings MUST be submitted to governance committee within 72 hours of the incident.

**Task 73 — ANIF-906 Council Deliberation Standards**
- File: `docs/900-ai-council/ANIF-906_Deliberation_Standards.md`
- Key content: Full deliberation standards table from spec section 8. Time limits: majority 15 min, consensus 30 min, weighted 15 min, adversarial 45 min. Deadlock resolution for each model. Voting record: every seat's vote and rationale MUST be recorded. Veto exercise: a seat exercising veto MUST state the specific ANIF requirement that is violated — veto cannot be exercised on personal preference. All deliberations MUST be fully logged to ethics audit trail before council closes.

**Task 74 — ANIF-907 Council Audit & Accountability**
- File: `docs/900-ai-council/ANIF-907_Council_Audit.md`
- Key content: Council Record schema: `council_id` (UUID), `council_type` (build-time/runtime/review), `mode_selected`, `mode_rationale`, `seats_present` (array), `quorum_met` (boolean), `deliberation_summary` (text), `votes` (per-seat record), `vetoes` (per-seat record with ANIF reference), `decision` (enum: approved/blocked/conditional/deferred), `accountability_chain`, `time_to_decision_minutes`. Council records are immutable and append-only. Retention: minimum 10 years.

**Task 75 — ANIF-908 Council & Learning Agent Integration**
- File: `docs/900-ai-council/ANIF-908_Council_Learning_Integration.md`
- Key content: Council decisions feed Learning Agent (ANIF-812). Consistent council overrides of the same agent design pattern flag an agent design issue to build-time council. Outcome-wrong decisions (council approved, action produced bad outcome) are negative training examples. Council Mode Selector rule updates require human approval before taking effect — the council cannot update its own decision rules without human oversight. Feedback loop closes: review council → learning packages → Learning Agent (human approval) → agent knowledge updates → better future decisions.

For each task 68–75:
- [ ] Write the document
- [ ] Run verification checklist
- [ ] Commit individually with message: `docs: add ANIF-[NNN] [Title]`

---

## Phase 12: Claude Project Guides

**Dependency:** All preceding phases complete.

---

### Task 76: CLAUDE_FRAMEWORK_BUILD_GUIDE.md

**File:**
- Create: `CLAUDE_FRAMEWORK_BUILD_GUIDE.md`

- [ ] **Step 1: Write the guide**

This is a practical working guide for Claude (and humans) contributing to ANIF framework documentation. Not a specification — a how-to.

Sections:

**What This Guide Is For** — building and extending ANIF framework documents. Distinct from building a platform on top of ANIF (see CLAUDE_PLATFORM_BUILD_GUIDE.md).

**Required Skills — When to Invoke**

| Skill | When |
|---|---|
| `superpowers:brainstorming` | Before designing any new document series. REQUIRED — do not write documents for a new series without it |
| `superpowers:writing-plans` | After brainstorming design is approved |
| `superpowers:executing-plans` | When working through the document build plan |
| `superpowers:dispatching-parallel-agents` | Writing independent documents in the same series simultaneously |
| `superpowers:verification-before-completion` | Before claiming any series is complete |
| `speckit.specify` | Creating or updating the specification for a document |
| `speckit.clarify` | Resolving cross-reference ambiguities before writing |
| `speckit.tasks` | Generating ordered task list for a document series |
| `speckit.analyze` | Cross-artifact consistency check after series completion |

**Document Writing Workflow** — step by step: (1) brainstorm series → (2) writing-plans for the series → (3) speckit.specify for each document → (4) speckit.clarify for cross-references → (5) write in dependency order → (6) speckit.analyze on the full series → (7) verification-before-completion → (8) commit and tag.

**Document Template** — full template with every section explained. Why each section is required. Common mistakes per section.

**Normative Language Guide** — when to use MUST vs SHOULD vs MAY. Common wrong usages to avoid. The "independently testable" test: if you cannot write a test case for a MUST requirement, rewrite the requirement until you can.

**Cross-Reference Rules** — how to reference other ANIF documents, what to do if you need to reference a document that doesn't exist yet, how to handle circular references.

**Key Pitfalls** — from experience:
- Circular cross-references: detected by speckit.analyze. Fix by identifying which document is the authority and making the other a one-way reference.
- Normative language drift: MUST becomes "should consider" across revisions. Run a grep for lowercase "must" and "should" before committing.
- Schema changes: any change to a schema in schemas/ that changes required fields or types MUST be assessed for backward compatibility with existing valid intents.
- Scope creep: each document has a defined scope. Write a separate document rather than expanding scope.
- Template violations: use the template in CLAUDE.md exactly — do not abbreviate or omit sections.

**SDD for Framework Documentation** — spec the series structure (what documents, what each covers, how they relate) → identify gaps and cross-references → plan build order by dependency → write in order → consistency check.

- [ ] **Step 2: Commit**

```bash
git add CLAUDE_FRAMEWORK_BUILD_GUIDE.md
git commit -m "docs: add CLAUDE_FRAMEWORK_BUILD_GUIDE"
```

---

### Task 77: CLAUDE_PLATFORM_BUILD_GUIDE.md

**File:**
- Create: `CLAUDE_PLATFORM_BUILD_GUIDE.md`

- [ ] **Step 1: Write the guide**

This is a practical working guide for Claude (and engineering teams) building a platform that implements and conforms to ANIF.

Sections:

**What This Guide Is For** — building working software that conforms to ANIF. Not contributing to the framework documentation (see CLAUDE_FRAMEWORK_BUILD_GUIDE.md for that).

**Required Skills — When to Invoke**

| Skill | When |
|---|---|
| `superpowers:test-driven-development` | Before writing any module — tests from ANIF spec first |
| `superpowers:executing-plans` | Working through the implementation plan |
| `superpowers:requesting-code-review` | After completing each module |
| `superpowers:systematic-debugging` | Before proposing any fix — diagnose root cause first |
| `superpowers:verification-before-completion` | Before claiming a module is done |
| `superpowers:finishing-a-development-branch` | Before merging any branch |

**Tech Stack** — Python 3.11+, FastAPI, Pydantic v2, pytest, Docker, docker-compose. Why each was chosen and what ANIF requirements it satisfies.

**Build Order Per Module**:
1. Read the ANIF spec document for this module (identify all MUST requirements)
2. Write test cases directly from the MUST requirements (not from code that doesn't exist yet)
3. Run tests to confirm they fail (they MUST fail — if they pass without implementation, the test is wrong)
4. Implement until tests pass
5. Run superpowers:requesting-code-review
6. Run superpowers:verification-before-completion
7. Commit

**Module Build Order** — which ANIF documents correspond to which code modules, and the dependency order for building them.

**Key Pitfalls**:
- Gold-plating: if a MUST requirement does not exist in the ANIF spec, do not implement it. Write a spec change proposal instead.
- Tests written after code: confirms the code works, not that it satisfies requirements. Discipline: tests first.
- Skipping audit writes: P-02 violation. Every action MUST write to audit before returning. Missing audit writes are the most common conformance failure.
- Hardcoding strings: all action types, governance modes, and state values MUST be enums.
- Non-deterministic policy evaluation: policy evaluation MUST be deterministic. Same inputs, same policy, same output, every time.
- LLM agents without deterministic shadow: violates ANIF-807 and ANIF-723.
- Missing rollback: every execute() call requires a confirmed rollback plan. Build rollback first.
- Silent failures: every error path MUST halt and escalate. No swallowed exceptions.

**ANIF Pipeline Implementation Guide** — the eight pipeline stages and what code each requires. Required API endpoints per ANIF-300 series.

**Testing Standards for ANIF Conformance** — test category mapping to ANIF test cases TC-001 through TC-005.

**SDD vs Exploratory** — for platform code: use SDD. Read the spec, write the test, implement. Exploratory spikes are permitted for genuine unknowns (maximum 2 hours) but the output of the spike is a spec update, not production code.

- [ ] **Step 2: Commit**

```bash
git add CLAUDE_PLATFORM_BUILD_GUIDE.md
git commit -m "docs: add CLAUDE_PLATFORM_BUILD_GUIDE"
```

---

## Final Verification

After all 77 tasks are complete:

- [ ] Run `superpowers:verification-before-completion` on the complete set
- [ ] Run `speckit.analyze` to check cross-reference consistency across all new documents
- [ ] Verify all new series directories exist: `docs/700-ai-ethics/`, `docs/800-ai-agent-architecture/`, `docs/830-ai-governance/`, `docs/840-ai-security/`, `docs/851-ai-compliance/`, `docs/900-ai-council/`, `docs/introduction/`
- [ ] Verify document count: 75 ANIF documents + 2 Claude guides = 77 files
- [ ] Update `docs/gap-analysis/ANIF_Documentation_Gap_Analysis.md` to reflect completed status
- [ ] Final commit

```bash
git add docs/gap-analysis/ANIF_Documentation_Gap_Analysis.md
git commit -m "docs: update gap analysis to reflect completed AI framework documentation"
```

---

## Summary

| Phase | Documents | Series |
|---|---|---|
| 1 | 1 | Introduction (ANIF-000) |
| 2 | 6 | Ethics Constitution (ANIF-700–705) |
| 3 | 7 | Ethics Risk Controls (ANIF-710–716) |
| 4 | 6 | Ethics Safeguards (ANIF-720–725) |
| 5 | 10 | Agent Foundation (ANIF-800–809) |
| 6 | 10 | Agent Intelligence (ANIF-810–819) |
| 7 | 5 | Agent Quality (ANIF-820–824) |
| 8 | 10 | AI Governance (ANIF-830–839) |
| 9 | 10 | AI Security (ANIF-840–849) |
| 10 | 1 | Industry Compliance (ANIF-851) |
| 11 | 9 | AI Council (ANIF-900–908) |
| 12 | 2 | Claude Guides |
| **Total** | **77** | |

Phases 8 and 9 can run in parallel. Within each phase, all tasks can run in parallel via `superpowers:dispatching-parallel-agents`.
