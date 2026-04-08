# AI Autonomous Networking Framework — Design Document

**Date:** 2026-04-07
**Status:** Approved
**Author:** ANIF Working Group

---

## 1. Problem Statement & Why This Exists

### The Problem

Networks are growing faster than human teams can manage them. Traffic patterns shift in milliseconds. Security threats emerge continuously. Service SLAs demand five-nines availability. The gap between network complexity and human operational capacity is widening every year.

Existing automation is scripted and brittle — it handles anticipated scenarios, not real ones. When something unexpected happens, the script fails and a human has to intervene. That's not automation; it's delayed manual operation.

AI introduces genuine autonomous capability — the ability to reason about novel situations, interpret ambiguous intent, and select actions dynamically. But AI without governance is dangerous in critical infrastructure:

- AI agents can hallucinate — producing confident but wrong recommendations
- AI agents can drift — behaving differently over time for the same inputs
- AI agents create accountability gaps — "the AI did it" is not an acceptable answer when a network goes down
- AI agents can be manipulated — prompt injection, adversarial inputs, and supply chain attacks are real threats
- AI agents can accumulate power — without hard containment, they expand scope beyond what was intended

**No existing framework addresses all of this together.** ETSI ZSM covers intent interfaces but not AI governance. TMForum covers autonomous network maturity but not agent ethics. NIST AI RMF covers AI risk but not network-specific operational controls. The ANIF AI framework fills this gap.

### What This Framework Solves

A single, coherent framework governing how AI agents are built, deployed, governed, secured, and held accountable in autonomous networking environments. It covers:

- **Ethics** — what values AI agents must uphold and what they are prohibited from doing
- **Agent architecture** — the roles, tiers, lifecycle, communication, and containment of AI agents
- **Governance** — strategic, operational, and technical governance at every layer
- **Security** — the expanded attack surface AI introduces and how to defend it
- **Council** — a formal deliberative body that governs decisions no single agent should make alone

### Who This Is For

- Network architects designing autonomous network systems
- Automation engineers building agent-based network management
- Security teams governing AI in critical infrastructure
- Compliance officers satisfying regulators about autonomous systems
- AI teams building and deploying agents in networking contexts
- Executives accountable for autonomous network decisions

### Design Philosophy

**Intent-based first.** Every action must trace to a declared intent. AI that cannot explain its action in terms of an original human intent has no business taking that action.

**Determinism-first.** AI is used where deterministic reasoning is genuinely insufficient — not as a default. Every LLM agent runs a deterministic shadow. If the deterministic shadow is sufficient, the LLM is not invoked.

**Human override is non-negotiable.** P-06 is absolute. No AI agent, no council decision, no governance configuration can remove a human's ability to halt and reverse any action.

**Fail safe always.** On uncertainty, missing data, or system error — halt and escalate. Never proceed on ambiguity.

**Ethics before architecture.** The ethics framework is designed first and the agent architecture is constrained by it — not the other way around.

---

## 2. Framework Structure

Three new ANIF series extending the existing framework (ANIF-000 through ANIF-604):

```
ANIF-000       Introduction & Problem Statement
ANIF-700–725   Ethics Framework        (WHY — principles, risk controls, safeguards)
ANIF-800–824   Agent Architecture      (WHO/WHAT — roles, lifecycle, intelligence)
ANIF-830–839   AI Governance           (STRATEGIC — programme, risk, vendor, data)
ANIF-840–849   AI Security             (DEFENCE — threats, monitoring, response)
ANIF-851       Industry Compliance     (REGULATORY — HIPAA, PCI-DSS, SOX, GDPR etc.)
ANIF-900–908   AI Council              (DECISION — deliberation, review, oversight)
```

A new **L5 conformance level** covers organisations that implement 700+800+900 series on top of existing L1–L4.

---

## 3. ANIF-700 Series — Ethics Framework

### Three-layer enforcement model

```
Layer 1 — Ethics Constitution (ANIF-700–705)    WHY   — principles & values
Layer 2 — Ethical Risk Controls (ANIF-710–716)  WHAT  — binding policies
Layer 3 — Technical Safeguards (ANIF-720–725)   HOW   — code-enforced constraints
```

### ANIF-700: Ethics Framework Overview
Entry point. Maps the three-layer model, shows how ethics extends ANIF principles P-01 through P-12, introduces L5 conformance level.

### ANIF-701: Ethics Constitution & Core Values
Nine normative values every AI agent must uphold:

| Value | Core Statement |
|---|---|
| Non-maleficence | Agents MUST NOT take actions that predictably cause harm |
| Beneficence | Agents MUST optimise for genuine outcomes, not proxy metrics |
| Autonomy preservation | Human override MUST be technically impossible to remove |
| Justice | Resource allocation decisions MUST be auditable for systematic bias |
| Transparency | Every AI decision MUST have a human-readable explanation |
| Proportionality | Agent authority MUST be proportional to confidence and risk level |
| Reversibility | Irreversible actions require a higher ethical burden |
| Accountability | Every action has a named accountability chain — no decision is ownerless |
| Reproducibility | Given the same inputs, the system MUST always produce the same outcome; non-determinism MUST be declared |

### ANIF-702: Accountability Chain Model
Shared accountability across four layers: designer → deployer → operator → approver. Incident trace always resolves to a named human at each layer. No layer shifts blame to another.

### ANIF-703: Bias & Fairness Principles
Four bias types: resource allocation bias, training data bias, LLM reasoning bias, ground process bias. "Fair" in networking means proportional to declared SLA — not equal allocation.

### ANIF-704: Harm Prevention Principles
Three harm classes with default postures:
- Service harm → block unless rollback confirmed
- Infrastructure harm → always manual_review
- Cascading harm → digital twin simulation required

### ANIF-705: LLM-Specific Ethics Principles
Hallucination accountability, prompt integrity, confidence calibration, non-determinism disclosure. LLM uncertainty MUST propagate to risk scoring.

---

### ANIF-710: Risk Control Overview
Traceability document mapping every 700-series principle to its enforcing policy and technical constraint.

### ANIF-711: Bias Detection & Fairness Controls
Detection method and policy response for all four bias types. Canonical state freshness gate blocks decisions based on stale data.

### ANIF-712: Harm Classification & Prevention Policy
Prevention gate per harm class. Parallel harm severity score independent of likelihood.

### ANIF-713: LLM Guardrails Policy
Output validation, confidence thresholds, prompt audit requirements, hallucination circuit breaker, jailbreak detection.

### ANIF-714: Privacy & Data Ethics Policy
Telemetry anonymisation before AI training, data residency enforcement, no PII retention beyond intent scope.

### ANIF-715: Ethics Incident Response Policy
Three-severity model: Severity 1 (breach — immediate halt, 15-min notification SLA), Severity 2 (warning — manual approval required), Severity 3 (drift — trend analysis and human review).

### ANIF-716: Agent Failure & Progressive Intervention
Four-strike escalation: logging → mandatory human review → suspension → decommission. Failure memory persists across restarts. No automated reinstatement — human clears each strike.

---

### ANIF-720: Safeguard Architecture Overview
Hard gate placement across the full pipeline. Every safeguard blocks — never warns and continues.

### ANIF-721: Agent Action Constraints
Four code-level constraints: bounded action enum (compile-time error for invalid types), rollback required as function parameter, human override hardcoded and unconfigurable, strike counter append-only.

### ANIF-722: LLM Output Validation
Schema check → hallucination check against canonical state → confidence check → prompt integrity hash. Failed validation increments strike counter.

### ANIF-723: Fairness Enforcement Controls
Allocation check against SLA floor, ground truth freshness gate, reproducibility check with parallel deterministic computation.

### ANIF-724: Ethics Audit Trail Requirements
Extends ANIF-107 with mandatory AI fields: agent_id, deterministic flag, LLM prompt hash, fairness result, hallucination result, harm score, full accountability chain.

### ANIF-725: Agent Containment & Governance Enforcement
`execute()` requires all prior stage results as mandatory parameters. Governance gate owned by orchestrator not agent. Capability scope signed and read-only at runtime. No agent can reason its way out of the pipeline.

---

## 4. ANIF-800 Series — Agent Architecture

### Four-tier agent model

```
Tier 0 — Management & Orchestration  (coordinate agents + humans, no network access)
Tier 1 — Monitor Agents              (observe only — read, no write to decision path)
Tier 2 — Advisor Agents              (reason + recommend — no execute access)
Tier 3 — Decision Agents             (bounded action selection via pipeline only)
```

### ANIF-800: Agent Architecture Overview
Four-tier model with hard boundaries. A tier cannot reach above itself — enforced architecturally, not by configuration.

### ANIF-801: Agent Types, Roles & Human Counterparts
Full role catalogue. Every AI agent maps to a human counterpart. Human retains authority; agent extends capacity.

**Tier 0 — Management:**
NOC Manager, Change Manager, Problem Manager, Project Manager, Service Manager, Vendor Manager, Configuration Manager, Knowledge Manager, Escalation Coordinator, Learning Agent, Intent Manager, Agent Pool Controller

**Tier 1 — Monitor:**
Network Observer, Security Sentinel, Compliance Watcher, Capacity Monitor, Service Health Monitor, Ethics Sentinel

**Tier 2 — Advisor:**
Intent Interpreter, Network Design Advisor, Security Advisor, Routing Advisor, Automation Advisor, Risk Analyst, Policy Advisor, Incident Analyst, Change Advisor, Intent Engineer Agent

**Tier 3 — Decision:**
Action Selector, Rollback Coordinator, Incident Responder, Provisioning Agent

### ANIF-802: Agent Capabilities & Permissions
Permission model: READ / WRITE / CALL per tier. Hard limits enforced architecturally — Tier 1 cannot call execute endpoints regardless of configuration.

### ANIF-803: Agent Lifecycle Management
Five states: registered → validated → active → degraded (auto on Strike 2) → suspended → decommissioned. Every transition requires a defined approver.

### ANIF-804: Agent Communication Protocol
Three separate buses: observation (T1→T2), recommendation (T2→T3), management (T0 only). No peer-to-peer outside declared buses. All messages include agent_id, timestamp, confidence_score, trace_id.

### ANIF-805: Agent Trust Model
Four levels: SYSTEM, VERIFIED, PROVISIONAL (first 72 hours), UNTRUSTED (Strike 2+). Trust level affects bus publish rights and whether recommendations are flagged to humans.

### ANIF-806: Agent Memory & State
Working memory cleared per intent, episodic memory read-only, no shared state writes, no cross-agent memory reads. LLM agents get a clean context window per intent — no carryover of sensitive data.

### ANIF-807: LLM Agent Specification
Must declare non-deterministic, run deterministic shadow in parallel, log prompt hash, define fallback if LLM unavailable, pin model version. Cannot be used in Tier 3 without deterministic validator in same pipeline stage.

### ANIF-808: Human-Agent Collaboration Model
Per role pairing: what human MUST decide, what agent MAY decide autonomously, what requires joint action. Answers "what do I still own as a Network Architect?"

### ANIF-809: Agent Coordination Model
Tier 0 can prioritise, delay, escalate, assign, report. Tier 0 cannot approve, execute, or override ethics constraints. All coordination logged.

### ANIF-810: Process Agent Integration
Management agents integrate with ITSM, project management, CMDB via adapter pattern. All integrations follow ANIF-725 containment.

### ANIF-811: Intent Lifecycle Management
Full state machine: DRAFT → SUBMITTED → QUEUED → IN_PIPELINE → PENDING_APPROVAL → EXECUTING → COMPLETED/FAILED/CANCELLED. Conflict detection between concurrent intents targeting same segments.

### ANIF-812: Learning Agent & Network Intelligence
Network knowledge broker — learns from incidents, problems, changes, expert feedback, and agent failures. Routes role-scoped knowledge packages to relevant agents after mandatory human approval. Three knowledge types: network pattern, operational, resolution.

```
Input sources: NOC Manager, Problem Manager, Change Manager,
               Project Manager, Network Observers, human expert feedback
Output targets: Role-scoped packages to relevant agent types only
Rule:          No update ever auto-applied — human approval always required
```

### ANIF-813: Intent Integration Architecture
External intent sources (OSS/BSS, monitoring, project tools) and quality feedback loop. High-failure intent sources flagged to Intent Engineer agent for correction templates.

### ANIF-814: Agent Tool Integration & MCP
Standard protocol for agent-to-tool connections. Every tool declared in capability manifest, tool calls logged to audit trail, tool versions pinned, graceful failure handling with declared fallback.

### ANIF-815: Human-Agent Interaction Model
Four interaction modes: directive (human instructs), approval (human reviews), override (human halts/reverses), query (human asks). Query responses generated from audit log and canonical state — never from LLM inference.

### ANIF-816: Context Window Management
Six strategies: intent isolation, context budgets per agent role, prompt compression and caching, selective retrieval (RAG), summarisation checkpoints between stages, role-scoped context delivery. Context overflow feeds Learning Agent as design signal.

### ANIF-817: AI Cost Optimisation & Governance
Model tier selection (small/mid/full), seven cost controls including response caching, deterministic-first check, token budget per intent, cost circuit breaker. LLM invoked only where deterministic is genuinely insufficient. Cost data flows to observability layer.

### ANIF-818: Agent Framework Scaling
Three-dimensional scaling: agent instances, pipeline, buses. Agent Pool Controller manages instance counts. Scaling never deploys unchecked agents. Scale events logged as anomalies if sudden.

### ANIF-819: Disaster Recovery & Resilience
Five degradation levels (full AI → full manual). Failures increase human oversight — never decrease it. State reconstructable from audit log. Quarterly DR tests mandatory. Annual full manual drill required.

```
DR Levels:
  0 — Full AI operation
  1 — Degraded (some agents down)
  2 — Deterministic only (LLM offline)
  3 — Human-assisted pipeline
  4 — Full manual operation
```

### ANIF-820: AI Agent Testing & Red-Team Standards
Testing types beyond functional: prompt injection, adversarial inputs, hallucination stress, agent conflict, red-team (attempt to bypass ethics and governance). Findings feed build-time council.

### ANIF-821: Regulatory & Standards Alignment
EU AI Act, NIST AI RMF, ISO 42001. Defines what the framework satisfies and where additional organisational controls are required.

### ANIF-822: AI Observability & Model Health
Model drift detection, hallucination rejection rate, confidence score trends, token usage anomalies, recommendation acceptance rate. Fills the gap ANIF-401 doesn't cover.

### ANIF-823: Migration & Adoption Roadmap
Path from L1-L4 to AI-native L5. Parallel running of deterministic and AI agents, validation against deterministic baseline, minimum viable L5 implementation.

### ANIF-824: Agent Supply Chain Security
Model poisoning detection, training data provenance, dependency security, model integrity hashing, provenance guarantees before any agent is deployed.

---

## 5. ANIF-830 Series — AI Governance Framework

### Three-layer governance model

```
ANIF-830 Strategic Governance   → sets policy and risk appetite
ANIF-900 AI Council             → operational decisions and review
ANIF-700/720 Ethics/Safeguards  → technical enforcement
```

### ANIF-830: AI Governance Overview
Three-layer model entry point. How strategic, operational, and technical governance interact and escalate.

### ANIF-831: AI Governance Structure & Accountability
Board/exec AI programme ownership, governance committee composition, relationship to council, ultimate accountability chain for autonomous networking decisions.

### ANIF-832: AI Risk Management Framework
Risk appetite statements, AI risk register, thresholds triggering governance committee involvement. Integration with enterprise risk management.

### ANIF-833: AI Policy Lifecycle Management
Policy proposal, approval, versioning, retirement. Emergency fast-track process. Policy conflict resolution above council level.

### ANIF-834: AI Programme Governance
Programme board, investment governance, business case requirements, milestone gates before autonomy expansion, programme KPIs.

### ANIF-835: AI Vendor & Model Governance
Vendor selection criteria, model evaluation before deployment, version approval, due diligence standards, exit strategy if vendor discontinued or compromised.

### ANIF-836: AI Data Governance
Training data quality standards, lineage requirements, consent and privacy governance for network telemetry, retention governance specific to AI systems.

### ANIF-837: AI Governance Reporting & Metrics
Mandatory governance committee reports: ethics incidents, strike counts, council decisions, cost trends, override rates. Escalation triggers forcing an emergency meeting.

### ANIF-838: AI Governance Roles & Responsibilities
Chief AI Officer, AI Ethics Officer, AI Risk Officer, DPO (AI-specific duties). RACI for all governance activities mapped to council seats.

### ANIF-839: AI Governance Compliance & Audit
Internal and external audit programme. Evidence requirements for regulatory inspections. Continuous compliance monitoring vs point-in-time audit.

---

## 6. ANIF-840 Series — AI Security Framework

### ANIF-840: AI Security Overview
Expanded attack surface from AI agents. How 840 series extends ANIF-205 and the technical safeguards.

### ANIF-841: AI Threat Model
Full threat catalogue:
- External: prompt injection, adversarial inputs, model extraction, token DoS, supply chain
- Internal: insider abuse, training data manipulation, audit tampering, council manipulation
- AI-specific: hallucination exploitation, confidence manipulation, context poisoning, trust score gaming, strike evasion

### ANIF-842: Prompt Injection & Adversarial Input Security
Direct injection, indirect injection via network state data, jailbreak attempts, role confusion. Multi-layer defence: input sanitisation, schema validation, pattern detection, human review on flagged intents.

### ANIF-843: Agent Zero Trust & Authentication
Cryptographic identity per agent, verified on every API call. Tier boundaries enforced cryptographically. Compromised identity triggers immediate suspension.

### ANIF-844: Secure Agent Communication
TLS 1.3 for all inter-agent communication. Message integrity signatures. Replay attack prevention. Bus access controls cryptographically enforced.

### ANIF-845: AI Infrastructure Security
Model file integrity hashing, isolated container runtime, signed images, API key rotation, resource limits, training data encrypted at rest.

### ANIF-846: Security Monitoring & Threat Detection
What must be monitored: failed auth, injection detections, out-of-scope API calls, token spikes, unusual council patterns, governance abuse signals. SIEM integration with AI-specific correlation rules.

### ANIF-847: AI Security Incident Response
Four levels: suspicious activity → confirmed event → active incident → critical infrastructure attack. Level 3+ triggers full manual operation. Level 4 requires regulatory notification.

### ANIF-848: Security Testing & Penetration Testing
Mandatory cadence: prompt injection quarterly, adversarial testing before every new agent deployment, red-team annually. Red-team scope includes council manipulation attempts.

### ANIF-849: Security Compliance & Certification
Mapping to EU AI Act, NIS2, NIST AI RMF, ISO 27001, ISO 42001. L5 certification requires passing ANIF-848 with no critical findings.

---

## 7. ANIF-851 — Industry Compliance Framework Mapping

### PCI-DSS v4.0
Autonomous agents handling payment network infrastructure. Key mappings:
- Requirement 1 (network controls) → ANIF-103, ANIF-725
- Requirement 7 (access control) → ANIF-802, ANIF-843
- Requirement 10 (audit logging) → ANIF-107, ANIF-724
- Requirement 12 (policies) → ANIF-833
- Encryption requirement enforced via pci_compliant policy in pipeline

### HIPAA Security Rule
Healthcare networks carrying ePHI:
- Technical safeguards → ANIF-720 series
- Audit controls → ANIF-107, ANIF-724
- Transmission security → ANIF-844
- Risk analysis → ANIF-832
- Agents handling ePHI-adjacent networks must declare encryption: true

### SOX Section 404
Financial services infrastructure:
- Change management → ANIF-104, ANIF-833
- Audit trail completeness → ANIF-107
- Access controls → ANIF-802, ANIF-838
- SOX-scoped infrastructure always requires manual_review — never auto

### GDPR
EU personal data in network telemetry:
- Data minimisation → ANIF-714, ANIF-816
- Purpose limitation → ANIF-806
- Data residency → ANIF-106 (EU region constraint)
- Right to explanation → ANIF-402
- Breach notification → ANIF-847 Level 4 response

### ISO 27001
- A.8 Asset management → ANIF-803
- A.9 Access control → ANIF-802, ANIF-843
- A.12 Operations security → ANIF-845
- A.16 Incident management → ANIF-715, ANIF-847

### NIST 800-53
US federal and critical infrastructure:
- AC (Access Control) → ANIF-802, ANIF-843
- AU (Audit) → ANIF-107, ANIF-724
- IR (Incident Response) → ANIF-715, ANIF-847
- RA (Risk Assessment) → ANIF-832, ANIF-841
- SI (System Integrity) → ANIF-720 series

### FedRAMP
- FedRAMP Moderate: minimum for L3 conformance
- FedRAMP High: required for autonomous actions in federal networks
- Continuous monitoring → ANIF-846
- Penetration testing cadence → ANIF-848

### CCPA / CPRA
- Consumer data rights → ANIF-714
- Data sale restrictions → ANIF-836
- Opt-out mechanisms → intent constraint declarations

---

## 8. ANIF-900 Series — AI Council Governance

### ANIF-900: Council Overview
Three council types: build-time (pre-deployment), runtime (live decisions), review (post-incident). Council never executes — governs, reviews, advises only.

### ANIF-901: Council Composition & Roles

| Seat | Domain | Veto? |
|---|---|---|
| Ethics Chair | Ethical violations, bias, fairness | Yes — absolute |
| Security Chair | Security posture, zero-trust | Yes — on security matters |
| Operations Chair | Operational risk, MTTR | Weighted vote |
| Architecture Chair | Design integrity, topology risk | Weighted vote |
| Governance Chair | Policy compliance, risk acceptance | Yes — final authority |
| Learning Chair | Knowledge quality, update approvals | Weighted vote |
| Human Advocate | Human override right P-06 | Yes — always |

### ANIF-902: Council Mode Selector
Agent that evaluates situation and selects deliberation model before council convenes:

| Model | Used When |
|---|---|
| Majority vote | Routine, reversible, time pressure |
| Consensus | High risk, irreversible, ethics flags, novel situation |
| Weighted vote | Domain-specific risk |
| Adversarial | Strike history involved, previous similar decisions failed |

### ANIF-903: Build-Time Council
Reviews every agent before deployment. Consensus from all veto seats required. Formalises and extends GARTH-COUNCIL-001 into the ANIF framework.

### ANIF-904: Runtime Council
Convenes during live execution for decisions beyond governance gate scope. Hard time limit — no decision within window defaults to halt and escalate.

### ANIF-905: Review Council
Post-incident body. Always uses adversarial model. Produces accountability determination, policy change recommendations, learning packages.

### ANIF-906: Council Deliberation Standards

| Model | Time Limit | Deadlock Resolution |
|---|---|---|
| Majority | 15 min | Human Advocate casts deciding vote |
| Consensus | 30 min | Escalates to Review Council |
| Weighted | 15 min | Human Advocate breaks ties |
| Adversarial | 45 min | Human Advocate decides |

All deliberations fully logged to ethics audit trail before council closes.

### ANIF-907: Council Audit & Accountability
Council Record schema: council_id, type, mode selected, mode rationale, seats present, quorum met, deliberation summary, votes, vetoes, decision, accountability chain, time to decision. Immutable and append-only.

### ANIF-908: Council & Learning Agent Integration
Council decisions feed Learning Agent. Consistent council overrides flag agent design issues to Build-time Council. Outcome-wrong decisions are negative examples. All Learning Agent updates to Council Mode Selector rules require human approval.

---

## 9. Claude Project Guides

### Guide 1: CLAUDE_FRAMEWORK_BUILD_GUIDE.md
For ANIF working group members building/extending framework documentation.

**Focus:** Document consistency, normative language, cross-references, schema correctness, conformance test coverage

**Required skills:**
- superpowers:brainstorming — before every new document series
- superpowers:writing-plans — after design is approved
- superpowers:executing-plans — during documentation build
- speckit.specify — create/update feature specifications
- speckit.clarify — resolve ambiguities before writing
- speckit.plan — generate design artefacts
- speckit.tasks — ordered task list from spec
- speckit.analyze — cross-artifact consistency check

**Approach:** SDD — spec the document series before writing docs

**Key pitfalls:**
- Circular cross-references between docs
- Normative language drift (MUST drifting to "should consider")
- Schema changes that break existing valid intents
- Document template violations
- Adding scope that doesn't align with ANIF-000 problem statement

**SDD for framework docs:**
Spec the series (what documents, what each covers, how they relate) → clarify gaps → plan document order → write in dependency order → cross-reference consistency check.

---

### Guide 2: CLAUDE_PLATFORM_BUILD_GUIDE.md
For engineering teams building a platform that conforms to ANIF.

**Focus:** Working code, API contracts, test coverage, conformance to ANIF specs

**Required skills:**
- superpowers:test-driven-development — before every module
- superpowers:executing-plans — during implementation
- superpowers:requesting-code-review — after each module
- superpowers:systematic-debugging — before proposing any fix
- superpowers:verification-before-completion — before claiming done

**Stack:** Python 3.11+, FastAPI, Pydantic v2, pytest, Docker

**Build order per module:**
1. Read the ANIF spec document for this module
2. Write tests from acceptance criteria (not from code)
3. Implement until tests pass
4. Run code-reviewer
5. Run verification-before-completion

**Key pitfalls:**
- Implementing logic not in the spec (gold-plating)
- Tests written after code (confirms code, not requirements)
- Skipping audit writes (P-02 violation)
- Hardcoding strings instead of enums
- Non-deterministic policy evaluation
- LLM agents without deterministic shadow
- Missing rollback() implementations
- Silent failures instead of halt-and-escalate

---

### SDD vs Exploratory — Comparison

**Spec-Driven Development (SDD)**

Pros:
- Full traceability — every decision links to a spec requirement
- Tests written from spec are honest — challenge the design, not confirm the code
- Easier onboarding — engineers read spec, not code
- Scope discipline — if not in spec, not built
- Audit-friendly — compliance can read specs, not code
- Claude performs better — clear spec reduces drift and hallucinations
- Aligns with ANIF principles — determinism and auditability carry through

Cons:
- Upfront time investment
- Specs become stale if not maintained alongside code
- Can feel rigid when requirements genuinely change
- Risk of over-specifying decisions better made during implementation

**Best for:** This project — both framework docs and platform code.

**Exploratory / Iterative**

Pros:
- Faster to get something running
- Adapts naturally to discoveries
- Good for genuine unknowns
- Lower upfront cognitive load

Cons:
- Drift without a spec
- Technical debt compounds
- Hard to audit — no traceable rationale
- Tests confirm code not requirements
- Claude spirals without clear spec
- Incompatible with ANIF conformance requirements

**Best for:** Time-boxed spikes (max 2 hours) to understand an unknown problem. Then write the spec from what you learnt and build properly.

---

## 10. Complete Document Index

| Series | Range | Count | Topic |
|---|---|---|---|
| Introduction | ANIF-000 | 1 | Problem statement & vision |
| Foundation | ANIF-001–004 | 4 | Charter, principles, glossary, RACI |
| Governance | ANIF-100–107 | 8 | Operational governance |
| Architecture | ANIF-200–205 | 6 | System architecture |
| Core Framework | ANIF-300–308 | 9 | Intent, policy, risk, decision, action |
| Operations | ANIF-400–407 | 8 | Observability, feedback, incidents |
| Conformance | ANIF-500–506 | 7 | Test cases, certification, profiles |
| Annexes | ANIF-600–604 | 5 | Schemas, examples, guides |
| Ethics | ANIF-700–725 | 17 | Values, controls, safeguards |
| Agents | ANIF-800–824 | 25 | Architecture, roles, intelligence |
| AI Governance | ANIF-830–839 | 10 | Strategic, programme, vendor, data |
| AI Security | ANIF-840–849 | 10 | Threats, monitoring, response |
| Compliance | ANIF-851 | 1 | HIPAA, PCI-DSS, SOX, GDPR, NIST |
| Council | ANIF-900–908 | 9 | Deliberation, review, oversight |
| **Total** | | **120** | |

Plus:
- `CLAUDE_FRAMEWORK_BUILD_GUIDE.md`
- `CLAUDE_PLATFORM_BUILD_GUIDE.md`

---

## 11. Conformance Levels

| Level | Name | Requirements |
|---|---|---|
| L1 | Aware | Self-assessment completed |
| L2 | Aligned | ANIF-001–107 satisfied, audit trail in place |
| L3 | Conformant | ANIF-300–407 satisfied, TC-001–005 passed |
| L4 | Certified | Third-party verified, ANIF-500–503 completed |
| L5 | AI-Native | ANIF-700–725, ANIF-800–824, ANIF-900–908 implemented and verified |

---

*Design approved 2026-04-07. Proceed to implementation planning.*
