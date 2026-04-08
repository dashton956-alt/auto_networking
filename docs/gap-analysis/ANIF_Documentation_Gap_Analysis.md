# ANIF Documentation Gap Analysis

| Field | Value |
|---|---|
| Document | ANIF Documentation Gap Analysis |
| Version | 0.1.0 |
| Status | Draft |
| Date | 2026-04-07 |
| Scope | ANIF framework documentation layer (ANIF-000 through ANIF-600) |

---

## Executive Summary

The ANIF repository contains strong planning artefacts — a detailed feature specification, a project constitution, 10 strategic concept documents, 14 prompt files, 3 YAML schemas, and a comprehensive framework structure index — but **zero formally structured ANIF-numbered documents exist**. Every document in the `docs/strategic/` folder and the `prompts/` folder represents unformatted draft content that maps to a target ANIF document ID but has not been authored to the required template. Of the ~60 documents defined in the ANIF framework index, **16 have some draft source material** and **44 are entirely absent**. Additionally, 2 schemas required by the prototype specification (`risk_score_schema.yml`, `audit_record_schema.yml`) are missing. The repo is well-designed but pre-documentation.

**Headline numbers:**

| Metric | Count |
|---|---|
| ANIF documents defined in framework index | ~60 |
| Formally authored ANIF documents (ANIF-NNN_*.md) | 0 |
| Documents with usable draft/source content | 16 |
| Documents entirely absent | 44 |
| Schemas defined | 3 of 5 |
| P0 (blocker) documents missing | 16 |

---

## 1. Inventory of Existing Assets

Every file in the repo that contains relevant documentation content, its mapping to a target ANIF document, and a quality assessment.

| Source File | Target ANIF ID(s) | Quality | Key Gaps |
|---|---|---|---|
| `docs/strategic/03_Closed_Loop_Feedback_Learning.md` | ANIF-403 | ~70% | No success metrics, no ML algorithm detail, no approval workflow |
| `docs/strategic/04_Policy_Conflict_Resolution_Precedence.md` | ANIF-303 | ~65% | No conflict syntax, no examples, no performance guidance |
| `docs/strategic/05_Distributed_Source_of_Truth.md` | ANIF-307 | ~60% | No merged data schema, no consistency guarantees, no retry logic |
| `docs/strategic/06_Governance_Human_in_Loop.md` | ANIF-404, ANIF-406 | ~70% | No SLA targets, no RBAC group definitions, no reversal process |
| `docs/strategic/07_Incident_Outage_Modeling.md` | ANIF-405 | ~65% | No runbook examples, no confidence scoring, no classification schema |
| `docs/strategic/08_Dark_NOC_Evolution_Plan.md` | ANIF-407 | ~70% | No KPI values, no entry/exit criteria, no timeline |
| `docs/strategic/09_Observability_Explainability_Artifacts.md` | ANIF-401, ANIF-402 | ~75% | No log schema, no API response examples, no retention policy |
| `docs/strategic/10_Extensibility_Plugin_Model.md` | ANIF-203 (plugin section) | ~70% | No plugin manifest schema, no security isolation model |
| `docs/strategic/Ai_ethics.md` | ANIF-103, ANIF-205 (adjacent) | ~80% | Truncated — ends mid-section 7; sections 8–11 incomplete |
| `docs/strategic/comprehensive, production-grade_Markdown_document.md` | Cross-cutting reference | ~85% | Sections 21–23 sparse; no diagrams; no cost estimates |
| `docs/strategic/GARTH-COUNCIL-001.md` | No ANIF mapping assigned | ~95% | No ANIF equivalent doc; not integrated into framework index |
| `docs/strategic/Ai Autonomous Networking Roadmap.md` | Cross-cutting (ANIF-407 adjacent) | ~75% | No timeline, no resource requirements, no integration mapping |
| `prompts/01_Risk_Trust_Quantification_Framework_prompt.md` | ANIF-304 | Prompt-level | Good algorithmic detail; not a spec format |
| `prompts/02_Change_Validation_Digital_Twin_prompt.md` | ANIF-308 | Prompt-level | Good topology modelling; not a spec format |
| `prompts/03_Closed_Loop_Feedback_Learning_prompt.md` | ANIF-403 (supplement) | Prompt-level | Supplements strategic doc |
| `prompts/04_Policy_Conflict_Resolution_Precedence_prompt.md` | ANIF-303 (supplement) | Prompt-level | Supplements strategic doc |
| `prompts/05_Distributed_Source_of_Truth_prompt.md` | ANIF-307 (supplement) | Prompt-level | Supplements strategic doc |
| `prompts/06_Governance_Human_in_Loop_prompt.md` | ANIF-404 (supplement) | Prompt-level | Supplements strategic doc |
| `prompts/07_Incident_Outage_Modeling_prompt.md` | ANIF-405 (supplement) | Prompt-level | Supplements strategic doc |
| `prompts/08_Dark_NOC_Evolution_Plan_prompt.md` | ANIF-407 (supplement) | Prompt-level | Supplements strategic doc |
| `prompts/09_Observability_Explainability_Artifacts_prompt.md` | ANIF-401 (supplement) | Prompt-level | Supplements strategic doc |
| `prompts/10_Extensibility_Plugin_Model_prompt.md` | ANIF-203 (supplement) | Prompt-level | Supplements strategic doc |
| `prompts/policy_engine.md` | ANIF-302 | Prompt-level | Implementation prompt; no normative spec content |
| `prompts/Intent_Vailidation_service_prompt.md` | ANIF-301 | Prompt-level | Implementation prompt; no normative spec content |
| `prompts/architecture_doc_prompt.md` | ANIF-200 (adjacent) | Prompt-level | Architecture mapping prompt; not a spec |
| `prompts/Decision Engine Prompt (Bounded AI).md` | ANIF-305 | Prompt-level | Bounded decision logic described; not a spec |
| `prompts/Schema_gen_Prompt.md` | ANIF-600 (adjacent) | Prompt-level | Schema generation guidance only |
| `prompts/Refactor Prompt.md` | Tooling aid | N/A | Not a framework document |
| `prompts/Test Generator Prompt.md` | Tooling aid | N/A | Not a framework document |
| `schemas/intent_schema.yml` | ANIF-600, ANIF-301 | Schema only | No narrative spec; `priority` not in `required` array |
| `schemas/action_schema.yml` | ANIF-600, ANIF-306 | Schema only | No narrative spec |
| `schemas/policy_schema.yml` | ANIF-600, ANIF-302 | Schema only | `condition` field is opaque string — no syntax defined |
| `schemas/example_intent.yml` | ANIF-601 (annex) | Example only | Good sample; no narrative documentation |
| `constitution.md` | ANIF-002 (adjacent) | ~80% | Not formatted to ANIF template; no normative language |
| `spec.md` | ANIF-604 (adjacent) | ~90% | Prototype spec, not a framework document; well-detailed |
| `Anif framework structure.md` | Master index | ~90% | The authoritative index; no content gaps — this is the index itself |

---

## 2. Gap Map by Series

Status key: `MISSING` = no content exists anywhere | `DRAFT` = source content exists but not in ANIF format | `SCHEMA ONLY` = schema exists, no narrative

### ANIF-000 Foundation

| Doc ID | Title | Status | Priority |
|---|---|---|---|
| ANIF-001 | Charter and Scope | MISSING | P0 |
| ANIF-002 | Principles | DRAFT (`constitution.md`) | P0 |
| ANIF-003 | Glossary | MISSING | P0 |
| ANIF-004 | Roles and RACI | MISSING | P1 |

All 4 foundation documents are absent in ANIF format. `constitution.md` contains principle content that overlaps ANIF-002 but is not formatted to template and uses no normative language.

---

### ANIF-100 Governance

| Doc ID | Title | Status | Priority |
|---|---|---|---|
| ANIF-100 | Governance Overview | MISSING | P0 |
| ANIF-101 | Compliance Mapping (TMForum, ETSI ZSM) | MISSING | P1 |
| ANIF-102 | NIST CSF Alignment | MISSING | P1 |
| ANIF-103 | Autonomous Action Policy | MISSING | P0 |
| ANIF-104 | Change Management Policy | MISSING | P0 |
| ANIF-105 | Escalation and Exception Policy | MISSING | P1 |
| ANIF-106 | Data Residency and Compliance Policy | MISSING | P1 |
| ANIF-107 | Audit Trail Requirements | MISSING | P0 |

All 8 governance documents are absent. `Ai_ethics.md` covers ethical dimensions adjacent to ANIF-103 but is not a policy document and is incomplete. The framework structure document contains partial alignment tables for ANIF-101 and ANIF-102 but these are index entries, not document content.

---

### ANIF-200 Architecture

| Doc ID | Title | Status | Priority |
|---|---|---|---|
| ANIF-200 | Reference Architecture | MISSING | P0 |
| ANIF-201 | Business Architecture | MISSING | P1 |
| ANIF-202 | Data Architecture | MISSING | P1 |
| ANIF-203 | Application Architecture (incl. Plugin Model) | MISSING | P1 |
| ANIF-204 | Technology Architecture | MISSING | P1 |
| ANIF-205 | Security Architecture | MISSING | P1 |

All 6 architecture documents are absent. `overview.png` exists at the repo root but there is no corresponding written architecture document. Sections of the `comprehensive, production-grade_Markdown_document.md` cover business, data, and application domain content at a conceptual level but are not structured to ANIF format and sections 21–23 are sparse. The plugin model material in `docs/strategic/10` maps to the plugin section of ANIF-203.

---

### ANIF-300 Core Framework

| Doc ID | Title | Status | Priority |
|---|---|---|---|
| ANIF-300 | Intent Framework Overview | MISSING | P0 |
| ANIF-301 | Intent Authoring Standard | MISSING | P0 |
| ANIF-302 | Policy Engine Specification | MISSING | P0 |
| ANIF-303 | Policy Conflict Resolution and Precedence | DRAFT (`docs/strategic/04` + `prompts/04`) | P0 |
| ANIF-304 | Risk and Trust Quantification | DRAFT (`prompts/01`) | P0 |
| ANIF-305 | Decision Engine Specification | MISSING | P0 |
| ANIF-306 | Action Execution Standard | SCHEMA ONLY (`action_schema.yml`) | P1 |
| ANIF-307 | Distributed Source of Truth | DRAFT (`docs/strategic/05` + `prompts/05`) | P1 |
| ANIF-308 | Digital Twin and Change Validation | DRAFT (`prompts/02`) | P1 |

This is the most critical series for the prototype. Five documents are entirely missing. Four have draft-level content in prompt or strategic doc form but none are in ANIF format. The `intent_schema.yml` provides schema coverage for ANIF-301/300 but there is no authoring standard narrative or intent framework overview.

---

### ANIF-400 Operations

| Doc ID | Title | Status | Priority |
|---|---|---|---|
| ANIF-400 | Operations Overview | MISSING | P1 |
| ANIF-401 | Observability Standard | DRAFT (`docs/strategic/09` + `prompts/09`) | P1 |
| ANIF-402 | Explainability Requirements | DRAFT (`docs/strategic/09` + `prompts/09`) | P1 |
| ANIF-403 | Closed Loop Feedback and Learning | DRAFT (`docs/strategic/03` + `prompts/03`) | P1 |
| ANIF-404 | Human-in-Loop Controls | DRAFT (`docs/strategic/06` + `prompts/06`) | P0 |
| ANIF-405 | Incident and Outage Modeling | DRAFT (`docs/strategic/07` + `prompts/07`) | P1 |
| ANIF-406 | Governance Controls | DRAFT (`docs/strategic/06` — shared with ANIF-404) | P0 |
| ANIF-407 | Dark NOC Maturity Model | DRAFT (`docs/strategic/08` + `prompts/08`) | P1 |

This is the best-covered series — 7 of 8 documents have draft source content. None are in ANIF format. ANIF-401 and ANIF-402 share the same source file (`09_Observability...`), meaning both documents need to be split and authored from that single source. ANIF-404 and ANIF-406 are similarly co-located in `06_Governance...`.

---

### ANIF-500 Conformance

| Doc ID | Title | Status | Priority |
|---|---|---|---|
| ANIF-500 | Conformance Overview | MISSING | P1 |
| ANIF-501 | Conformance Level Definitions | MISSING | P1 |
| ANIF-502 | Certification Process | MISSING | P2 |
| ANIF-503 | Test Case Catalogue | MISSING | P1 |
| ANIF-504 | Vendor Profile Template | MISSING | P2 |
| ANIF-505 | Cloud Profile Template | MISSING | P2 |
| ANIF-506 | Telco Profile Template | MISSING | P2 |

All 7 conformance documents are absent. The framework structure document defines the 4 conformance levels (L1–L4) and lists 5 test case IDs (TC-001 through TC-005), but no actual test case content or conformance documents have been written. This entire series is blocked until the ANIF-300 core specs are established.

---

### ANIF-600 Annexes

| Doc ID | Title | Status | Priority |
|---|---|---|---|
| ANIF-600 | Schema Reference | SCHEMA ONLY (3 of 5 schemas) | P0 |
| ANIF-601 | Worked Examples | MISSING | P1 |
| ANIF-602 | Implementation Guide | MISSING | P1 |
| ANIF-603 | Glossary Extensions | MISSING | P2 |
| ANIF-604 | Reference Prototype Guide | MISSING | P1 |

ANIF-600 has 3 schemas (`intent`, `action`, `policy`) but is missing `risk_score_schema.yml` and `audit_record_schema.yml` — both are explicitly required by `spec.md` and are blocking the prototype implementation. `example_intent.yml` exists and covers part of ANIF-601 but no narrative examples are written.

---

## 3. Issues in Existing Draft Content

These are specific, actionable deficiencies in files that already exist.

### Structural issues (all `docs/strategic/` files)

| Issue | Impact |
|---|---|
| Not formatted to ANIF document template | Cannot be published as ANIF documents without reformatting |
| No ANIF doc ID, version, or status frontmatter | Untraceable and unversioned |
| No normative language (MUST / SHOULD / MAY) | Requirements are ambiguous — cannot drive conformance testing |
| No conformance requirements section | Documents cannot be used for L3/L4 certification |
| No related docs cross-references | Readers cannot navigate between documents |
| No security or operational considerations sections | Required by template |

### Content issues (file-specific)

| File | Issue |
|---|---|
| `docs/strategic/Ai_ethics.md` | File truncated — ends mid-example in section 7; sections 8–11 are incomplete or absent |
| `docs/strategic/comprehensive, production-grade_Markdown_document.md` | Sections 21 (compliance), 22 (maturity model), 23 (checklist) are sparse or empty; no diagram content despite references |
| `docs/strategic/08_Dark_NOC_Evolution_Plan.md` | KPI targets are vague (e.g., "high automation" without threshold values); no entry/exit criteria per maturity level |
| `docs/strategic/07_Incident_Outage_Modeling.md` | No concrete runbook examples; no confidence scoring algorithm; no incident classification schema |
| `docs/strategic/04_Policy_Conflict_Resolution_Precedence.md` | Policy condition syntax never defined — `condition` in `policy_schema.yml` is an opaque string |
| `docs/strategic/05_Distributed_Source_of_Truth.md` | No data consistency model (eventual vs strong); no schema for merged canonical state; no source failure handling |
| `docs/strategic/06_Governance_Human_in_Loop.md` | RBAC role definitions missing; no SLA for approval timeouts; no appeal/reversal process |
| `docs/strategic/GARTH-COUNCIL-001.md` | Excellent document with no ANIF mapping — not referenced in framework index; not integrated into governance series |

### Schema issues

| Schema | Issue |
|---|---|
| `schemas/intent_schema.yml` | `priority` field is not in the `required` array — but `spec.md` custom rules depend on it being present |
| `schemas/policy_schema.yml` | `condition` is an opaque `string` — no syntax grammar defined; makes deterministic evaluation impossible to specify |
| `schemas/risk_score_schema.yml` | Does not exist — required by `spec.md` US-03 and the prototype pipeline |
| `schemas/audit_record_schema.yml` | Does not exist — required by `spec.md` US-07 and every pipeline stage |

### Naming issues

| File | Issue |
|---|---|
| `Anif framework structure.md` | Filename has spaces — violates the naming convention defined in section 4 of that same file |
| `docs/strategic/comprehensive, production-grade_Markdown_document.md` | Filename has spaces and commas — not a valid ANIF document name |
| `docs/strategic/Ai Autonomous Networking Roadmap.md` | Filename has spaces; no ANIF mapping assigned |
| `prompts/Intent_Vailidation_service_prompt.md` | Typo: "Vailidation" |

---

## 4. Priority Matrix

### P0 — Blockers (16 documents)

These must exist before the framework can be described as coherent or before the prototype can be called conformant. They are also the prerequisite input for all P1 work.

| Doc ID | Title | Why P0 |
|---|---|---|
| ANIF-001 | Charter and Scope | Defines the framework's purpose and boundaries — all other docs depend on it |
| ANIF-002 | Principles | Formalises P-01 through P-12 — referenced by all governance and core docs |
| ANIF-003 | Glossary | Shared terminology — required for normative precision in all other documents |
| ANIF-100 | Governance Overview | Entry point for the governance series |
| ANIF-103 | Autonomous Action Policy | Defines what autonomous actions are permitted — core safety constraint |
| ANIF-104 | Change Management Policy | Every action execution triggers a change — no policy means unconstrained changes |
| ANIF-107 | Audit Trail Requirements | Every pipeline stage writes audit records — framework requirements must precede implementation |
| ANIF-200 | Reference Architecture | Foundational system design — all component specs depend on shared architecture |
| ANIF-300 | Intent Framework Overview | Entry point for the core framework |
| ANIF-301 | Intent Authoring Standard | Defines how intents are written — prerequisite for validation and policy evaluation |
| ANIF-302 | Policy Engine Specification | Policy evaluation is the central safety gate — must be fully specified |
| ANIF-303 | Policy Conflict Resolution | Draft exists; needs to be formalised — conflict resolution is safety-critical |
| ANIF-304 | Risk and Trust Quantification | Draft exists; needs to be formalised — scoring algorithm must be normative |
| ANIF-305 | Decision Engine Specification | The bounded decision tree is the core AI safety control — must be formally specified |
| ANIF-404 | Human-in-Loop Controls | Human override is principle P-06 — governance gate must be documented |
| ANIF-406 | Governance Controls | Required alongside ANIF-404; shared source; must be split and authored |
| ANIF-600 | Schema Reference + missing schemas | `risk_score_schema.yml` and `audit_record_schema.yml` block prototype implementation |

### P1 — Important (24 documents)

Required for a complete, publishable v0.1 framework. Not immediate blockers for prototype implementation but needed for documentation completeness and L2/L3 conformance claims.

ANIF-004, ANIF-101, ANIF-102, ANIF-105, ANIF-106, ANIF-201, ANIF-202, ANIF-203, ANIF-204, ANIF-205, ANIF-306, ANIF-307, ANIF-308, ANIF-400, ANIF-401, ANIF-402, ANIF-403, ANIF-405, ANIF-407, ANIF-500, ANIF-501, ANIF-503, ANIF-601, ANIF-602, ANIF-604

### P2 — Nice to Have (7 documents)

Post-v0.1 concerns. Needed for certification and vendor adoption but not for the prototype or initial framework release.

ANIF-502, ANIF-504, ANIF-505, ANIF-506, ANIF-603

---

## 5. Recommended Build Order

Aligned to the phased approach in `Anif framework structure.md` Appendix A, adjusted for current repo state.

### Phase 1 — Foundation (resolve before any other authoring)

```
ANIF-001   Charter and Scope            [nothing exists — write from scratch]
ANIF-002   Principles                   [migrate from constitution.md]
ANIF-003   Glossary                     [write from scratch — extract terms from all docs]
ANIF-103   Autonomous Action Policy     [write from scratch — draw from Ai_ethics.md]
ANIF-107   Audit Trail Requirements     [write from scratch — draw from spec.md US-07]
```

Also complete missing schemas:
```
schemas/risk_score_schema.yml           [write from scratch — spec.md US-03 defines all fields]
schemas/audit_record_schema.yml         [write from scratch — spec.md US-07 defines all fields]
```

Fix `intent_schema.yml`: add `priority` to the `required` array.  
Define `condition` syntax in `policy_schema.yml`.

### Phase 2 — Architecture and Core Framework

```
ANIF-200   Reference Architecture       [write from scratch — draw from overview.png + comprehensive doc]
ANIF-300   Intent Framework Overview    [write from scratch — draw from intent_schema.yml]
ANIF-301   Intent Authoring Standard    [formalise from prompts/Intent_Vailidation_service_prompt.md]
ANIF-302   Policy Engine Specification  [formalise from prompts/policy_engine.md]
ANIF-303   Policy Conflict Resolution   [formalise from docs/strategic/04 + prompts/04]
ANIF-304   Risk and Trust Quantification [formalise from prompts/01]
ANIF-305   Decision Engine Specification [formalise from prompts/Decision Engine Prompt (Bounded AI).md]
ANIF-407   Dark NOC Maturity Model      [formalise from docs/strategic/08 + prompts/08]
```

### Phase 3 — Governance and Operations

```
ANIF-100   Governance Overview
ANIF-102   NIST CSF Alignment           [expand table from framework structure doc]
ANIF-104   Change Management Policy
ANIF-404   Human-in-Loop Controls       [formalise from docs/strategic/06 + prompts/06]
ANIF-406   Governance Controls          [split from same source as ANIF-404]
ANIF-401   Observability Standard       [formalise from docs/strategic/09 + prompts/09]
ANIF-402   Explainability Requirements  [split from same source as ANIF-401]
ANIF-403   Closed Loop Feedback         [formalise from docs/strategic/03 + prompts/03]
ANIF-405   Incident and Outage Modeling [formalise from docs/strategic/07 + prompts/07]
```

### Phase 4 — Conformance and Annexes

```
ANIF-500   Conformance Overview
ANIF-501   Conformance Level Definitions [expand from framework structure section 9]
ANIF-503   Test Case Catalogue
ANIF-600   Schema Reference             [narrative wrapper around all schemas]
ANIF-602   Implementation Guide
ANIF-604   Reference Prototype Guide    [expand README.md]
```

---

## 6. Unassigned Documents

These files in the repo have no current ANIF mapping and should be assigned or explicitly noted as out-of-scope:

| File | Recommendation |
|---|---|
| `docs/strategic/GARTH-COUNCIL-001.md` | Assign as ANIF-106 appendix or create ANIF-108 (AI Validation Governance) |
| `docs/strategic/Ai Autonomous Networking Roadmap.md` | Assign as ANIF-407 appendix or ANIF-400 supplement |
| `docs/strategic/Ai_ethics.md` | Complete truncated sections; assign as ANIF-002 appendix or ANIF-103 normative reference |

---

## 7. Summary Counts

| Series | Total Defined | Missing | Draft Only | Schema/Prompt Only |
|---|---|---|---|---|
| ANIF-000 Foundation | 4 | 3 | 1 | 0 |
| ANIF-100 Governance | 8 | 8 | 0 | 0 |
| ANIF-200 Architecture | 6 | 6 | 0 | 0 |
| ANIF-300 Core Framework | 9 | 5 | 2 | 2 |
| ANIF-400 Operations | 8 | 1 | 7 | 0 |
| ANIF-500 Conformance | 7 | 7 | 0 | 0 |
| ANIF-600 Annexes | 5 | 4 | 0 | 1 |
| **Total** | **47** | **34** | **10** | **3** |

_Note: ~60 total documents are listed in the framework index including profiles and annexes not captured in the series tables above._

---

*This document was produced by analysing all files in the ANIF repository against the framework index defined in `Anif framework structure.md`. It is the authoritative gap record as of 2026-04-07 and should be updated as documents are created.*
