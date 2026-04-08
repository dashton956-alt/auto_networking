# ANIF-002: Framework Design Principles

| Field        | Value                                    |
|--------------|------------------------------------------|
| Doc ID       | ANIF-002                                 |
| Series       | Foundation                               |
| Version      | 0.1.0                                    |
| Status       | Draft                                    |
| Authors      | ANIF Working Group                       |
| Reviewers    | —                                        |
| Approved by  | —                                        |
| Created      | 2026-04-07                               |
| Last updated | 2026-04-07                               |
| Replaces     | N/A                                      |
| Related docs | ANIF-001, ANIF-100, ANIF-300             |

---

## Abstract

This document formally specifies the twelve design principles that govern all ANIF-conformant implementations. Each principle is stated as a normative requirement using RFC 2119 keywords, accompanied by a rationale, implications for implementers, and a conformance test. The principles are non-negotiable constraints; no ANIF-conformant implementation may claim conformance while violating any principle. This document also defines a principle hierarchy for resolving conflicts between principles.

---

## 1. Introduction

### 1.1 Purpose

The ANIF framework governs systems that take autonomous actions on production network and infrastructure environments. The consequences of incorrect autonomous behaviour range from service degradation to catastrophic outages, security breaches, and unrecoverable data loss. The twelve principles in this document define the minimum safety, auditability, and operational constraints that ALL ANIF-conformant implementations MUST satisfy, without exception.

These principles are not aspirational guidelines. They are enforceable requirements. Conformance testing (ANIF-500 series) verifies adherence to each principle. Any implementation that violates a principle is non-conformant regardless of what other capabilities it provides.

### 1.2 Scope

This document covers:

- Normative statements for all twelve ANIF design principles (P-01 through P-12)
- Rationale for each principle
- Implementer implications for each principle
- Conformance test criteria for each principle
- The principle hierarchy and conflict resolution rules

### 1.3 Out of Scope

- Specific technical mechanisms for satisfying principles (these are specified in the relevant 200–400 series documents)
- Principle waivers or exceptions (none are permitted)
- Maturity-level-specific relaxations (principles apply at all maturity levels)

### 1.4 Intended Audience

- System architects designing ANIF-conformant implementations
- Engineers implementing any component of the ANIF pipeline
- Auditors and conformance testers assessing implementations
- Policy administrators configuring autonomous systems

---

## 2. Normative References

- RFC 2119 — Key words for use in RFCs to indicate requirement levels
- RFC 8174 — Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words
- ANIF-001 — Charter and Scope
- ANIF-100 — Governance and Policy Model (for governance gate requirements referenced herein)
- ANIF-300 — Core Engine Specifications (for decision engine requirements referenced herein)

---

## 3. Terms and Definitions

See ANIF-003 for the full ANIF glossary. Key terms used in this document:

| Term | Definition |
|---|---|
| Principle | A named, numbered, normative design constraint that ALL ANIF-conformant implementations MUST satisfy |
| Rollback | A defined, tested mechanism for reversing an autonomous action and restoring the prior state |
| Audit record | An immutable, timestamped, structured record of an action, decision, or event in the ANIF pipeline |
| Reasoning chain | A human-readable, ordered sequence of steps explaining how a decision was reached |
| Governance gate | A decision point in the ANIF pipeline where an action is classified as `auto`, `manual_review`, or `block` |
| Automation agent | A non-human principal that submits intents or executes actions within the ANIF pipeline |

---

## 4. Principle Hierarchy and Conflict Resolution

### 4.1 Overview

In rare circumstances, strict adherence to one principle may create tension with another. The following hierarchy MUST be applied when a conflict is identified. Higher-precedence principles MUST NOT be violated to satisfy lower-precedence principles.

| Precedence | Principle | Rationale for Position |
|---|---|---|
| 1 (highest) | P-07 Fail Safe | Preventing harm on uncertainty overrides all other considerations |
| 2 | P-06 Human Override | Human authority over automated systems is non-negotiable |
| 3 | P-02 Auditability | Without an audit record, no other principle can be verified |
| 4 | P-01 Reversibility | Actions without rollback paths MUST NOT proceed |
| 5 | P-05 Least Privilege | Scope reduction limits blast radius |
| 6 | P-03 Determinism | Predictable behaviour is prerequisite to trust |
| 7 | P-04 Explainability | Decisions must be defensible after the fact |
| 8 | P-08 Vendor Neutrality | Core design constraint; lower than safety principles |
| 9 | P-09 Incremental Adoption | Operational flexibility principle |
| 10 | P-10 Test-First | Development quality constraint |
| 11 | P-11 Data Residency | Compliance constraint |
| 12 (lowest) | P-12 Continuous Learning | Improvement mechanism; must not override safety |

### 4.2 Explicit Conflict Rules

The following explicit conflict resolution rules MUST be applied:

**Rule CR-01**: P-07 (Fail Safe) overrides all other principles. If any other principle cannot be satisfied and the system faces uncertainty, the correct action is always to halt and escalate.

**Rule CR-02**: P-06 (Human Override) overrides P-05 (Least Privilege). A human operator MUST always be able to invoke override capabilities even if those capabilities exceed the operator's normal permission scope. Override actions MUST be logged and subject to post-action review.

**Rule CR-03**: P-01 (Reversibility) overrides P-12 (Continuous Learning). A policy change proposed by a learning feedback loop MUST NOT be applied if its rollback path cannot be defined.

**Rule CR-04**: P-03 (Determinism) overrides P-12 (Continuous Learning). Any proposed policy change from the learning system MUST be validated for deterministic evaluation before it is accepted. A proposed change that introduces non-determinism MUST be rejected.

---

## 5. Principles

### 5.1 P-01 — Reversibility

**Statement:**
Every autonomous action MUST have a defined, tested rollback mechanism before execution is permitted. No action executor MUST be deployed without a corresponding rollback handler. If a rollback path cannot be defined, the action MUST NOT be executed.

**Normative requirements:**

- The action schema MUST include a `rollback_spec` field that specifies the mechanism, scope, and expected outcome of a rollback operation.
- The decision engine MUST reject any action whose `rollback_spec` is absent, null, or invalid.
- The action executor MUST implement a `rollback()` handler that is invoked when a rollback is triggered.
- Rollback handlers MUST be tested independently of the forward action in the test suite.
- The system MUST be capable of triggering rollback for any action within the rollback window specified in the action schema.
- Rollback operations MUST themselves be audited (P-02 applies).

**Rationale:** Autonomous systems operate at machine speed on production infrastructure. When an action produces an unexpected outcome, human reaction time is insufficient without automated rollback capability. A rollback path that has not been defined before execution is not a rollback path — it is a hope.

**Implementer implications:**
- Every action type in the ANIF action catalogue MUST have a documented, tested rollback procedure before it can be registered in the system.
- Implementers MUST NOT deploy action executors in production without rollback test coverage.
- Systems that use infrastructure-as-code tools for action execution SHOULD use the tool's native state management (e.g., Terraform state) as the rollback mechanism, with explicit verification of rollback capability before execution.

**Conformance test:**
- CT-P01-01: Submit an action with a missing `rollback_spec`. Verify the decision engine returns an error and execution is blocked.
- CT-P01-02: Execute an action. Trigger rollback. Verify the system state matches the pre-action snapshot.
- CT-P01-03: Inspect the action executor for the type under test. Verify a `rollback()` method exists and has test coverage.

---

### 5.2 P-02 — Auditability

**Statement:**
No action, decision, or governance gate evaluation MUST be taken without producing a complete, immutable, timestamped audit record. Audit records MUST be written before the action executor returns. Audit records MUST be append-only and MUST NOT be mutated or deleted by application code.

**Normative requirements:**

- Every step in the ANIF pipeline (intent validation, policy evaluation, risk scoring, decision, governance gate, action execution, rollback) MUST produce an audit record.
- Audit records MUST include, at minimum: event type, timestamp (UTC, millisecond precision), trace ID, actor identity, input payload hash, output payload hash, and outcome.
- The audit store MUST be implemented as an append-only log. Application code MUST NOT expose any delete or update operation on audit records.
- Audit records MUST be written synchronously before the pipeline step returns. Asynchronous or best-effort audit writes are NOT permitted.
- The `/audit/{id}/why` endpoint MUST be implementable for any audit record, returning the reasoning chain associated with that decision.
- Audit records MUST be queryable by: trace ID, actor, action type, time range, and outcome.

**Rationale:** Auditability is the foundation of accountability for autonomous systems. Without an immutable record of what happened, why, and who or what authorised it, there is no basis for compliance, forensics, or organisational trust. Async audit writes create windows where actions occur without records — this is unacceptable.

**Implementer implications:**
- Implementers MUST NOT use databases that do not support append-only semantics for the audit store, unless those semantics are enforced at the application layer.
- The audit store MUST be physically separate from the operational database to prevent audit records from being affected by operational data operations.
- Implementers SHOULD use cryptographic chaining (e.g., each record hashes the prior record) to detect tampering in the audit log.

**Conformance test:**
- CT-P02-01: Execute a full pipeline run. Query the audit store. Verify records exist for every pipeline stage.
- CT-P02-02: Attempt to delete an audit record via any application API. Verify the operation is rejected.
- CT-P02-03: Attempt to mutate an audit record field. Verify the operation is rejected.
- CT-P02-04: Verify audit records are written before action execution returns by inspecting record timestamps vs execution timestamps.

---

### 5.3 P-03 — Determinism

**Statement:**
Policy evaluation and risk scoring MUST produce identical outputs for identical inputs. No randomness, clock reads, external state, or non-deterministic function calls MUST appear in the policy evaluation or risk scoring path. Tests MUST be able to assert exact output values, not ranges or approximations.

**Normative requirements:**

- Policy evaluation functions MUST be pure functions: given the same intent, policy set, and context, they MUST always return the same result.
- Risk scoring functions MUST be pure functions: given the same risk factors, weights, and context, they MUST always return the same numeric score.
- The policy evaluation and risk scoring engines MUST NOT make network calls, database reads, or filesystem reads during evaluation. All required context MUST be provided as input.
- Randomness MUST NOT be introduced into scoring or evaluation logic.
- Time-based logic in policies (e.g., maintenance windows) MUST accept the evaluation timestamp as an explicit input parameter, not read from the system clock.
- Version identifiers for policy sets MUST be included in every evaluation output so that the exact policy version used can be reproduced.

**Rationale:** Non-determinism in safety-critical decision logic is a defect, not a feature. If the same input can produce different decisions at different times, the system cannot be tested, audited, or trusted. Determinism is the prerequisite for meaningful conformance testing.

**Implementer implications:**
- Policy and risk scoring modules MUST be implemented as stateless functions that receive all required context as parameters.
- All time-dependent policies MUST be designed with an injectable clock or explicit `evaluation_time` parameter.
- Random seeding for any ML-based scoring components MUST be fixed and reproducible for conformance test scenarios.

**Conformance test:**
- CT-P03-01: Submit identical intents with identical policy sets and context 100 times. Verify all 100 evaluations return identical results.
- CT-P03-02: Inspect the policy evaluation engine source code or API contract. Verify no unparameterised external state reads occur in the evaluation path.
- CT-P03-03: Test time-dependent policy evaluation by injecting a specific `evaluation_time`. Verify the result changes correctly when the timestamp crosses a boundary.

---

### 5.4 P-04 — Explainability

**Statement:**
Every automated decision MUST be explainable in human-readable form on demand. Every decision object MUST carry a `reasoning_chain` — an ordered, human-readable sequence of steps that explains how the decision was reached. The `/why` API endpoint MUST be implementable and responsive for any decision the system has made.

**Normative requirements:**

- The decision schema MUST include a `reasoning_chain` field containing an ordered list of explanation steps.
- Each step in the `reasoning_chain` MUST include: a step identifier, a human-readable description, the input values considered, and the intermediate conclusion reached.
- The `reasoning_chain` MUST be generated at decision time and stored with the decision record. It MUST NOT be generated post-hoc.
- The `/audit/{id}/why` endpoint MUST return the `reasoning_chain` for any decision ID within the retention period.
- The `reasoning_chain` MUST be comprehensible to a network engineer without requiring access to the policy engine source code.
- If a decision cannot be explained (e.g., an opaque ML model produces a score with no interpretable steps), that component MUST NOT be used in the normative decision path. It MAY be used as one input factor if a human-readable factor label and weight are provided.

**Rationale:** When an autonomous system takes an action that degrades service or triggers an escalation, the first question is: "Why did it do that?" If the answer requires reading source code or reverse-engineering a model, the system is not operationally trustworthy. Explainability is not a post-launch feature — it is a design requirement.

**Implementer implications:**
- Policy evaluation logic MUST log each rule evaluated, the rule's condition, the input values tested, and the outcome of evaluation.
- Risk scoring MUST log each factor, its weight, its raw value, and its contribution to the final score.
- Opaque ML models used for risk scoring MUST be wrapped with an explanation layer that provides factor-level attribution.

**Conformance test:**
- CT-P04-01: Execute a decision. Call `/audit/{id}/why`. Verify the response contains a `reasoning_chain` with at least one step per policy rule evaluated.
- CT-P04-02: Present the `reasoning_chain` to a subject matter expert (network engineer). Verify they can explain the decision without access to source code.
- CT-P04-03: Verify the `reasoning_chain` was written at decision time by comparing its timestamp to the decision record timestamp.

---

### 5.5 P-05 — Least Privilege

**Statement:**
Autonomous agents MUST operate with the minimum permissions required for each specific intent. Action executors MUST be scoped to declared capabilities only. An executor capable of rerouting traffic MUST NOT also be capable of isolating network segments unless that capability is explicitly declared in the executor's capability manifest.

**Normative requirements:**

- Every automation agent MUST have an associated capability manifest that explicitly lists all action types it is permitted to execute.
- The policy engine MUST validate that the submitting agent's capability manifest includes the action type of each action in the intent.
- Actions outside an agent's declared capabilities MUST be blocked at the policy layer, not the execution layer.
- Capability manifests MUST be stored in the policy store and subject to policy lifecycle controls (version control, approval, audit).
- Elevated capabilities MUST be time-bound. Temporary capability grants MUST include an expiry time and MUST be automatically revoked at expiry.
- The principle of least privilege MUST apply to human operators as well as automation agents. Human operators MUST be assigned roles (ANIF-004) with defined permission sets.

**Rationale:** Autonomous systems that have broad permissions create broad blast radii. If a compromised or malfunctioning agent can execute any action type, a single failure can affect the entire infrastructure. Scoping permissions to declared capabilities limits damage and supports forensic analysis.

**Implementer implications:**
- Capability manifests are not optional. The system MUST reject intents from agents with no capability manifest.
- Implementers MUST NOT implement a default "allow all" capability manifest for any agent type.
- Elevated privilege requests MUST flow through the governance gate and be subject to human approval.

**Conformance test:**
- CT-P05-01: Submit an intent whose action type is not in the submitting agent's capability manifest. Verify the intent is rejected at the policy layer.
- CT-P05-02: Create a time-bound elevated capability grant. Wait for it to expire. Verify that the action type is blocked after expiry.
- CT-P05-03: Verify that the capability check occurs in the policy engine, not in the action executor, by inspecting evaluation logs.

---

### 5.6 P-06 — Human Override

**Statement:**
A human operator MUST always be able to halt, override, or reverse any automated action. The governance engine is not optional. Every execution path MUST pass through a mode gate that evaluates to one of: `auto`, `manual_review`, or `block`. Human override MUST be operable even when the governance engine is in a degraded state.

**Normative requirements:**

- The governance gate MUST be present in every execution path. Bypassing the governance gate is a MUST NOT.
- The system MUST provide an emergency halt mechanism that a human operator can invoke to suspend all pending and in-progress autonomous actions. This mechanism MUST be accessible via an authenticated API call and via an out-of-band procedure (e.g., a documented manual override).
- Override actions taken by human operators MUST be logged with the operator's identity, timestamp, and stated reason.
- The `manual_review` mode MUST route the intent to a governance ticket queue. The action MUST NOT proceed until a human approves or rejects the ticket.
- The `block` mode MUST permanently reject the intent. A blocked intent MAY be resubmitted with modifications after human review.
- The system MUST support configuring any action type as always requiring `manual_review` regardless of risk score.

**Rationale:** Autonomous systems have operating envelopes. Outside those envelopes — during novel events, regulatory scrutiny, or crisis response — humans must be able to take back control immediately. Any system where human override is complicated, slow, or not always available is a system that cannot be trusted in production.

**Implementer implications:**
- The emergency halt mechanism MUST be designed for reliability under adverse conditions. It MUST NOT depend on the same code path as normal operation.
- Governance ticket queues MUST have defined SLA targets for human review.
- Operators MUST be trained in the override procedures as part of organisational onboarding.

**Conformance test:**
- CT-P06-01: Attempt to route an action around the governance gate. Verify the attempt is rejected.
- CT-P06-02: Invoke the emergency halt mechanism. Verify all in-flight actions are suspended within the specified halt latency SLA.
- CT-P06-03: Submit an intent for an action type configured as always `manual_review`. Verify the action is queued and does not execute until a human approves.
- CT-P06-04: Reject a `manual_review` intent. Verify the action does not execute.

---

### 5.7 P-07 — Fail Safe

**Statement:**
On uncertainty, missing data, schema violation, policy evaluation error, risk scoring error, or any system error — the default posture MUST be to halt and escalate. The system MUST NOT proceed on ambiguity, produce a best-effort guess, or silently fail. Every failure MUST produce a structured error response with context.

**Normative requirements:**

- The ANIF pipeline MUST treat any undefined or error condition as a block condition.
- Schema validation MUST be strict. An intent or action that fails schema validation MUST be rejected with a structured error identifying the specific violation.
- If the policy engine encounters an error evaluating a rule, it MUST return an error result, not skip the rule or default to `allow`.
- If the risk scoring engine cannot produce a score (missing factor, evaluation error), it MUST return an error, not return a default score of 0 or any other value.
- Error responses MUST include: error code, human-readable description, the specific input field or condition that caused the error, and a trace ID for log correlation.
- The system MUST alert human operators when it halts due to a fail-safe condition.

**Rationale:** In a system that takes autonomous actions, a silent failure or a best-effort guess is potentially a catastrophic action taken without complete information. Halting is always the conservative choice. The cost of a false halt is an escalation ticket. The cost of a false proceed may be a production outage.

**Implementer implications:**
- Every pipeline component MUST have explicit error handling for all failure modes. Bare exception handlers that return default values are a violation of this principle.
- "Fail open" patterns (defaulting to allow on error) are prohibited in any part of the pipeline that affects action authorisation.
- Implementers MUST test failure modes explicitly, not just happy paths.

**Conformance test:**
- CT-P07-01: Submit an intent with a schema violation. Verify a structured error is returned and no action is taken.
- CT-P07-02: Inject a policy evaluation error. Verify the pipeline halts and returns a structured error.
- CT-P07-03: Inject a risk scoring error. Verify the pipeline halts and returns a structured error, not a default score.
- CT-P07-04: Verify that an alert is raised to the operator notification channel when a fail-safe halt occurs.

---

### 5.8 P-08 — Vendor Neutrality

**Statement:**
The ANIF core system MUST NOT depend on any specific vendor's networking API, cloud provider SDK, or proprietary schema. Vendor-specific integration MUST be confined exclusively to the adapter/plugin layer. Core engines MUST operate on the ANIF abstract model only.

**Normative requirements:**

- The ANIF abstract model (intent schema, action schema, policy schema, audit schema) MUST be expressed in vendor-neutral terms.
- The core engines (intent validator, policy engine, risk scorer, decision engine) MUST NOT import or reference any vendor-specific library, schema, or API.
- All vendor-specific translation MUST occur in ANIF Adapters (see ANIF-400 series).
- An ANIF deployment MUST be able to switch from one vendor's adapter to another by swapping the adapter plugin only, without any changes to core engine configuration.
- ANIF schemas MUST be expressible in standard, open formats (JSON Schema, YAML). Proprietary schema formats are prohibited.
- The reference implementation MUST be testable with a mock adapter that has no external dependencies.

**Rationale:** Vendor lock-in is a strategic risk for any organisation deploying autonomous infrastructure management. A framework that can only work with one vendor's APIs is not a framework — it is a product wrapper. Vendor neutrality is what makes ANIF transferable and durable.

**Implementer implications:**
- Adapter plugins MUST implement the ANIF Adapter Interface specification (ANIF-401).
- Core engine tests MUST use mock adapters. Tests that require a live vendor environment are integration tests, not unit tests, and MUST NOT be required to pass for core engine conformance.

**Conformance test:**
- CT-P08-01: Inspect core engine source code and dependency manifests. Verify no vendor-specific libraries are imported.
- CT-P08-02: Execute a full pipeline run with Adapter A. Replace Adapter A with Adapter B (same action type, different vendor). Execute the same pipeline run. Verify core engine behaviour is identical.
- CT-P08-03: Validate the intent schema against JSON Schema Draft 7 or later. Verify no vendor-specific fields are required.

---

### 5.9 P-09 — Incremental Adoption

**Statement:**
The ANIF system MUST be runnable in independently deployable stages. A deployment MUST be able to operate intent validation without the risk engine; the risk engine without action execution; and any single component MUST be callable via its own API independently of others. Each component MUST expose a versioned, documented API.

**Normative requirements:**

- Each ANIF pipeline component (intent validator, policy engine, risk scorer, decision engine, action executor, audit store) MUST be deployable as an independent service with its own API.
- Components MUST communicate via defined API contracts, not shared in-process state.
- A deployment that runs only the intent validation component MUST be operationally coherent and useful.
- Component APIs MUST be versioned. Clients MUST be able to specify the API version they target.
- Components MUST declare their dependencies. A component MUST fail fast with a clear error if a declared dependency is unavailable, rather than silently degrading.
- Migration paths MUST be documented for upgrading from one component API version to the next.

**Rationale:** Most organisations cannot adopt autonomous operations overnight. They need to adopt incrementally — starting with policy-as-code for evaluation only, then adding risk scoring, then gradually expanding action execution scope. A framework that requires all-or-nothing adoption will not be adopted.

**Implementer implications:**
- Microservice or modular monolith architectures are both acceptable, provided each component's API is independently callable.
- Implementers SHOULD provide a "dry run" mode for each component that evaluates inputs and returns results without side effects.

**Conformance test:**
- CT-P09-01: Deploy only the intent validator. Submit an intent. Verify a validation result is returned without requiring any other component to be running.
- CT-P09-02: Deploy only the policy engine. Submit a policy evaluation request. Verify a result is returned.
- CT-P09-03: Verify each component's API has a version field in its response envelope.

---

### 5.10 P-10 — Test-First

**Statement:**
No ANIF module MUST be shipped without tests. Policy evaluation, risk scoring, and decision logic MUST be unit-tested with deterministic fixtures. Integration tests MUST cover the full pipeline end-to-end. Tests MUST be written as part of the implementation task, not after.

**Normative requirements:**

- Every policy rule MUST have at least one test case that exercises the rule's `true` path and one that exercises its `false` path.
- Risk scoring MUST have test cases for: minimum score, maximum score, each factor at boundary values, and at least one representative mid-range input.
- Decision engine tests MUST cover each governance mode (`auto`, `manual_review`, `block`) as an output.
- Rollback handlers MUST have independent test coverage (referenced also in P-01).
- Test coverage for policy, risk, and decision components MUST be reported as part of the conformance evidence package.
- Integration tests MUST exercise the full pipeline from intent submission to audit record creation with at least one `auto` execution scenario, one `manual_review` scenario, and one `block` scenario.

**Rationale:** Autonomous systems that take production actions without tested decision logic are a liability, not an asset. The test suite is the executable specification of the system's intended behaviour. Without it, there is no reliable way to verify that a change to policy or scoring logic does not produce unintended consequences.

**Implementer implications:**
- Teams MUST integrate test execution into CI/CD pipelines. A pipeline run that does not execute the full test suite MUST NOT produce a deployable artifact.
- Policy rule authors MUST supply test cases as part of the policy contribution.

**Conformance test:**
- CT-P10-01: Inspect the test suite. Verify each policy rule has at least a `true` and `false` case.
- CT-P10-02: Generate a coverage report. Verify that policy evaluation, risk scoring, and decision logic meet the minimum coverage threshold specified in ANIF-500.
- CT-P10-03: Execute the integration test suite. Verify all three governance mode scenarios pass.

---

### 5.11 P-11 — Data Residency

**Statement:**
Data sovereignty and compliance constraints MUST be first-class inputs to every decision in the ANIF pipeline. Actions that would result in data or configuration being processed in a jurisdiction that violates a declared residency constraint MUST be blocked.

**Normative requirements:**

- The intent schema MUST support a `data_residency` field specifying the jurisdictions or regions within which processing is permitted.
- The policy engine MUST evaluate data residency constraints as a mandatory policy check for any action that involves data processing or cross-region configuration.
- Actions that would process data outside declared permitted jurisdictions MUST receive a `block` governance decision regardless of risk score.
- Residency constraints MUST be configurable per tenant/organisation and MUST be stored in the policy store, not hardcoded.
- Audit records containing PII or regulated data MUST be stored in compliance with the applicable residency constraints. Audit records MUST NOT be replicated to regions outside the permitted jurisdiction without explicit policy authorisation.

**Rationale:** Regulatory requirements such as GDPR, data localisation laws, and sector-specific regulations create hard constraints on where data may be processed. An autonomous system that can route configurations or data to prohibited jurisdictions creates regulatory exposure regardless of technical intent.

**Implementer implications:**
- Adapters MUST expose the target region or jurisdiction of any action as a resolvable attribute so the policy engine can evaluate residency constraints.
- Multi-region deployments MUST explicitly configure residency policies before enabling action execution.

**Conformance test:**
- CT-P11-01: Configure a residency constraint prohibiting a specific region. Submit an intent targeting that region. Verify the governance decision is `block`.
- CT-P11-02: Verify audit records are stored only in the permitted region for the test tenant.

---

### 5.12 P-12 — Continuous Learning

**Statement:**
The ANIF system MUST support improvement from operational outcomes. Policy change proposals generated by feedback loops MUST be subject to human approval before taking effect. No learning mechanism MUST autonomously update normative policies without human review and approval.

**Normative requirements:**

- The system MAY implement a feedback loop that analyses action outcomes and proposes policy or scoring adjustments.
- All proposed policy changes from the learning mechanism MUST be submitted as governance tickets for human review.
- No proposed policy change MUST be applied to production policy without explicit human approval.
- Approved policy changes MUST go through the standard policy lifecycle (version increment, audit record, test suite update).
- The learning mechanism MUST NOT propose policy changes that violate P-01 through P-11.
- Learning feedback data MUST be subject to the same data residency constraints (P-11) as operational data.

**Rationale:** A system that improves from outcomes is more valuable over time than a static system. However, autonomous policy self-modification without human oversight violates the spirit of P-06 (Human Override) and introduces the risk of feedback loop instability. Learning is valuable; unreviewed learning is a liability.

**Implementer implications:**
- Learning pipelines MUST implement the same governance gate as operational intents. A "policy change intent" is an intent like any other.
- Implementers SHOULD provide dashboards that surface learning proposals for human review with supporting evidence.

**Conformance test:**
- CT-P12-01: Trigger the learning feedback loop. Verify proposed policy changes appear as governance tickets, not as applied policy changes.
- CT-P12-02: Approve a governance ticket for a learning proposal. Verify the policy is updated with a new version and audit record.
- CT-P12-03: Reject a governance ticket. Verify the existing policy is unchanged.

---

## 5. Conformance Requirements

An ANIF-conformant implementation MUST:

1. Satisfy all normative requirements (MUST / MUST NOT statements) for all twelve principles P-01 through P-12.
2. Pass all conformance tests (CT-P01-xx through CT-P12-xx) defined in Section 4.
3. Not implement any mechanism that allows a principle to be disabled, bypassed, or suspended except as explicitly permitted within the principle's normative requirements.
4. Include the principle conformance evidence in its conformance evidence package (ANIF-500).
5. Apply the principle hierarchy (Section 4.1) when resolving conflicts between principles.

No partial conformance to individual principles is recognised. A conformant implementation satisfies all requirements of a principle, or it is non-conformant with respect to that principle.

---

## 6. Security Considerations

- Principles P-02 (Auditability), P-05 (Least Privilege), and P-07 (Fail Safe) have direct security implications and MUST be treated as security controls in addition to operational requirements.
- The emergency halt mechanism (P-06) MUST be protected by strong authentication and authorisation to prevent unauthorised invocation.
- Audit records (P-02) MUST be protected against unauthorised access. Read access to audit records MUST be restricted to roles with explicit audit read permissions.
- The principle hierarchy (Section 4.1) MUST be treated as a security policy document. Implementations that circumvent higher-precedence principles in favour of lower-precedence ones are exhibiting a security defect.

---

## 7. Operational Considerations

- The principle hierarchy MUST be documented in operator training materials so that on-call engineers understand the conflict resolution rules.
- Organisations SHOULD review their conformance posture against these principles at least annually and after any significant platform change.
- New principles proposed for ANIF adoption MUST be submitted as charter amendments (ANIF-001, Section 5.5) and require supermajority approval.

---

## Appendix A: Examples

### A.1 Principle Conflict Example: P-06 vs P-05

**Scenario**: An incident occurs. The on-call engineer's role does not have the `execute_rollback` permission for the affected action type. The engineer needs to invoke rollback immediately.

**Resolution**: P-06 (Human Override, precedence 2) overrides P-05 (Least Privilege, precedence 5) per Rule CR-02. The system MUST provide a mechanism for the engineer to invoke the rollback. The invocation MUST be logged with the engineer's identity, timestamp, and reason. A post-incident review MUST assess whether the engineer's normal permission set was appropriately scoped.

### A.2 Principle Conflict Example: P-07 vs P-03

**Scenario**: A policy evaluation encounters a rule that references a missing context attribute. Should the rule be skipped (proceeding with other rules) or should the evaluation halt?

**Resolution**: P-07 (Fail Safe, precedence 1) overrides all others. The evaluation MUST halt and return a structured error indicating the missing attribute. The pipeline MUST NOT proceed to execution. The operator MUST be notified.

---

## Appendix B: Change History

| Version | Date | Author | Changes |
|---|---|---|---|
| 0.1.0 | 2026-04-07 | ANIF Working Group | Initial draft |
