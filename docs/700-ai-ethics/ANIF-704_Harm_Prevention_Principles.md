# ANIF-704: Harm Prevention Principles

| Field        | Value                                              |
|--------------|----------------------------------------------------|
| Doc ID       | ANIF-704                                           |
| Series       | AI Ethics                                          |
| Version      | 0.1.0                                              |
| Status       | Draft                                              |
| Authors      | ANIF Working Group                                 |
| Reviewers    | —                                                  |
| Approved by  | —                                                  |
| Created      | 2026-04-07                                         |
| Last updated | 2026-04-07                                         |
| Replaces     | N/A                                                |
| Related docs | ANIF-701, ANIF-712, ANIF-720, ANIF-725             |

---

## Abstract

This document defines three harm classes applicable to autonomous network actions, assigns a default governance posture to each, and establishes that harm prevention operates as a blocking gate — not an advisory signal. An action that crosses a harm threshold is stopped, not warned about. The operational harm classification policy is defined in ANIF-712; the technical gate enforcing it is in ANIF-720.

---

## 1. Introduction

### 1.1 Purpose

The Non-maleficence value in ANIF-701 states that agents MUST NOT cause predictable harm. This document gives that obligation precision. "Harm" in an autonomous networking context is not a single concept — it spans immediate service degradation, lasting infrastructure damage, and propagating failures that spread beyond the intended scope of the action.

Each category of harm carries a different default governance posture because the recovery path, the blast radius, and the time-to-restore differ significantly between them.

### 1.2 Scope

This document covers:

- The three harm classes and their precise definitions
- The default governance posture for each harm class
- The harm severity score and its composition
- The position of harm classification in the ANIF pipeline
- The principle that harm gates are blocking — not advisory

### 1.3 Out of Scope

This document does not cover:

- The algorithmic classification procedure (see ANIF-712)
- The technical implementation of harm gates (see ANIF-720, ANIF-721)
- Digital twin simulation mechanics (see ANIF-308)
- Incident response after harm has occurred (see ANIF-715, ANIF-847)

### 1.4 Intended Audience

- AI platform engineers implementing harm classification in the pipeline
- Network architects defining harm thresholds for their environment
- Governance and compliance reviewers assessing action risk posture
- Build-time council members evaluating agent deployment proposals

---

## 2. Normative References

- ANIF-701 — Ethics Constitution and Core Values (Non-maleficence)
- ANIF-304 — Risk and Trust Quantification
- ANIF-308 — Digital Twin and Change Validation
- ANIF-712 — Harm Classification and Prevention Policy
- ANIF-720 — Safeguard Architecture Overview
- ANIF-721 — Agent Action Constraints
- RFC 2119 — Key words for use in RFCs to indicate requirement levels

---

## 3. Terms and Definitions

**Harm class:** One of three categories into which a proposed action is classified based on the nature of its potential adverse effects: service harm, infrastructure harm, or cascading harm.

**Harm severity score:** A parallel score to the risk score, computed independently of likelihood. Measures the magnitude of harm if the action produces adverse effects. Formula: `harm_severity = impact_score × blast_radius_multiplier`. Range: 0–100.

**Blast radius:** The set of network segments, services, or tenants that would be adversely affected if the action produces its worst-case outcome.

**Rollback confirmation:** Verification, before execution begins, that a valid rollback plan exists and can be executed within the SLA defined in ANIF-306. Rollback confirmation is a prerequisite for any action classified as service harm.

**Digital twin simulation:** A pre-execution simulation of the proposed action against a representation of the current network state, conducted via the capability defined in ANIF-308. Required for all cascading harm actions.

**Default governance posture:** The governance mode that applies to an action based solely on its harm class, before considering the risk score. The default posture is a floor — the risk score may increase it but MUST NOT decrease it below the default.

---

## 4. Three Harm Classes

### 4.1 Service Harm

**Definition:** An action that, if it produces adverse effects, would result in degradation or loss of a service covered by a declared SLA. Service harm is the most common harm class and represents the typical risk of network automation.

**Characteristics:**
- Affects one or more services with declared SLA obligations
- Recovery is feasible within normal operational timescales if rollback is available
- Blast radius is limited to the targeted service and its direct dependencies

**Default governance posture:** `auto` is permitted only if rollback is confirmed available before execution begins. If rollback cannot be confirmed, the action MUST be escalated to `manual_review`. No service harm action MAY proceed without a confirmed rollback plan.

**Examples:**
- Rerouting traffic for a service covered by a 99.9% availability SLA
- Applying QoS changes that reduce bandwidth for a declared service
- Scaling bandwidth for a service in a manner that affects its SLA headroom

### 4.2 Infrastructure Harm

**Definition:** An action that, if it produces adverse effects, would cause physical or logical damage to network equipment, links, or configurations that cannot be restored to their prior state within the rollback SLA defined in ANIF-306.

**Characteristics:**
- May affect the ability to execute rollback (the harm removes the recovery path)
- Recovery requires human engineering effort beyond automated rollback
- May affect services beyond those targeted by the intent

**Default governance posture:** `manual_review` is MANDATORY for all infrastructure harm actions, regardless of risk score or policy configuration. No policy setting, intent constraint, or risk score may override this default. A risk score of zero does not remove the manual review requirement for infrastructure harm.

**Examples:**
- Actions that modify firmware or device configurations that require manual recovery
- Actions that could cause routing protocol instability affecting the entire autonomous system
- Actions targeting carrier-grade segments with five-nines availability commitments
- Actions that modify security group rules or ACLs in ways that cannot be automatically reversed

### 4.3 Cascading Harm

**Definition:** An action that creates conditions for further harm beyond the immediate target segment — failures that propagate, routing instabilities that spread, or security breaches that enable lateral movement.

**Characteristics:**
- Harm extends beyond the blast radius of the immediate action
- Secondary failures may be triggered in segments not addressed by the intent
- The propagation path may be non-obvious at the time of action selection

**Default governance posture:** Digital twin simulation (ANIF-308) MUST be completed and the simulation results reviewed before execution. Simulation results MUST be included in the audit record. If simulation is unavailable or returns inconclusive results, the action MUST be escalated to `manual_review`.

**Examples:**
- Traffic rerouting actions that could create routing loops in upstream or downstream segments
- QoS changes that could cause congestion collapse propagating across interconnected domains
- Segment isolation actions that could partition a network in unexpected ways
- Actions targeting shared infrastructure used by multiple tenants or services

---

## 5. Harm Severity Score

The harm severity score is a parallel metric to the risk score. It measures the magnitude of harm if the action produces adverse effects — independent of the probability that it will.

### 5.1 Formula

```
harm_severity = impact_score × blast_radius_multiplier
```

**impact_score (0–50):** Derived from the SLA tier of the affected services. A service with 99.999% availability commitment contributes a higher impact score than one with 99.9%.

**blast_radius_multiplier (1.0–2.0):** Derived from the number of dependent segments and services estimated to be affected. A single-service action has a multiplier near 1.0; an action affecting a shared transit segment has a multiplier approaching 2.0.

### 5.2 Threshold Escalation

An action with a harm severity score ≥ 60 MUST be treated as infrastructure harm regardless of which harm class it was initially assigned to. The severity score overrides the class assignment when the score exceeds this threshold.

### 5.3 Independence from Risk Score

The harm severity score is computed independently of the risk score defined in ANIF-304. A low-risk, high-severity action — such as an action that is highly likely to succeed but whose failure mode is catastrophic — MUST receive infrastructure harm treatment.

### 5.4 Inclusion in Audit Record

The harm class, harm severity score, and blast radius estimate MUST be included in the audit record for every action. An audit record that omits these fields for an action involving AI decision-making is incomplete per ANIF-724.

---

## 6. Harm Gates Are Blocking

Every harm gate in the ANIF pipeline is a blocking gate. A harm classification result does not produce a warning that allows the pipeline to continue — it either passes or stops the action.

This is a principle, not a configuration option. An implementation that converts a harm gate into an advisory signal is non-conformant regardless of the configuration that produced this behaviour.

The rationale: a warning that is ignored provides no protection. In an automated pipeline, there is no human watching each decision to respond to a warning. If a gate fires, the action stops. Humans are then notified and can choose to proceed with explicit approval.

---

## 7. Position in Pipeline

Harm classification runs after risk scoring and before the decision engine. This position is defined in the safeguard architecture overview (ANIF-720). A harm gate failure MUST override the risk score decision — a low risk score does not permit bypassing a harm gate.

The pipeline sequence for harm classification:

```
... → Risk Scoring → Harm Classification Gate → Decision Engine → ...
```

If harm classification returns infrastructure harm, the decision engine receives a mandatory `manual_review` instruction regardless of the risk score output.

---

## 8. Conformance Requirements

An implementation MUST classify every proposed action into at least one harm class before execution.

Infrastructure harm actions MUST always produce a `manual_review` governance decision. This requirement MUST NOT be configurable. No intent constraint, policy rule, or risk score may override it.

Cascading harm actions MUST be simulated in the digital twin before execution. Simulation MUST be completed — partial or incomplete simulations do not satisfy this requirement.

An action with a harm severity score ≥ 60 MUST be treated as infrastructure harm regardless of its initial harm class assignment.

Harm severity score, harm class, and blast radius MUST be written to the audit record for every action.

---

## 9. Security Considerations

Harm classification can be attacked by crafting inputs that cause an agent to misclassify a harmful action as lower-harm. Input sanitisation (ANIF-842) and canonical state integrity (ANIF-711) are the primary defences. An agent whose harm classification is systematically incorrect is a candidate for the adversarial testing defined in ANIF-820 and ANIF-848.

---

## 10. Operational Considerations

Harm thresholds and harm class definitions SHOULD be reviewed whenever the network topology changes materially — for example, when new carrier-grade segments are added or when the blast radius of existing actions changes due to topology changes.

The default governance postures defined in this document are floors. Organisations MAY configure stricter postures (for example, requiring `manual_review` for all actions, not just infrastructure harm) but MUST NOT configure postures less strict than the defaults defined here.

---

## Appendix A: Change History

| Version | Date | Author | Changes |
|---|---|---|---|
| 0.1.0 | 2026-04-07 | ANIF Working Group | Initial draft |
