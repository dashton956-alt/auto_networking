# ANIF Framework Gap Analysis — 2026-04-08

| Field | Value |
|---|---|
| Document | ANIF Framework Gap Analysis |
| Version | 1.0.0 |
| Status | Current |
| Date | 2026-04-08 |
| Scope | Full ANIF framework: ANIF-000 through ANIF-908, schemas, and supporting artefacts |
| Supersedes | ANIF_Documentation_Gap_Analysis.md (2026-04-07) — that document is obsolete |

---

## Executive Summary

The ANIF framework is **substantially complete**. All 122 ANIF-numbered documents exist on disk across 14 series. All 6 YAML schemas exist. Two Claude project guides have been written. The framework covers the full lifecycle from foundation (ANIF-001) through AI Council governance (ANIF-908).

The remaining gaps are editorial and integration issues, not missing documents:

| Category | Gap Count | Severity |
|---|---|---|
| Missing L5 conformance level definition | 1 | **Critical** — blocks L5 certification claims |
| Phantom cross-references (reference to non-existent doc) | 2 | High |
| L5 definition omits two series | 2 locations | High |
| Glossary missing AI-specific terms | ~15 terms | Medium |
| Structural template violations (missing sections) | 14 documents | Medium |
| Governance mode inconsistency (3 modes vs 4) | 2 locations | Medium |
| Outdated gap analysis file | 1 | Low |

---

## 1. Document Inventory

### 1.1 Documents on Disk

| Series | Range | Count | Directory |
|---|---|---|---|
| Introduction | ANIF-000 | 1 | `docs/introduction/` |
| Foundation | ANIF-001–004 | 4 | `docs/000-foundation/` |
| Governance | ANIF-100–107 | 8 | `docs/100-governance/` |
| Architecture | ANIF-200–205 | 6 | `docs/200-architecture/` |
| Core | ANIF-300–308 | 9 | `docs/300-core/` |
| Operations | ANIF-400–407 | 8 | `docs/400-operations/` |
| Conformance | ANIF-500–506 | 7 | `docs/500-conformance/` |
| Annexes | ANIF-600–604 | 5 | `docs/600-annexes/` |
| AI Ethics | ANIF-700–725 | 19 | `docs/700-ai-ethics/` |
| AI Agent Architecture | ANIF-800–824 | 25 | `docs/800-ai-agent-architecture/` |
| AI Governance | ANIF-830–839 | 10 | `docs/830-ai-governance/` |
| AI Security | ANIF-840–849 | 10 | `docs/840-ai-security/` |
| AI Compliance | ANIF-851 | 1 | `docs/851-ai-compliance/` |
| AI Council | ANIF-900–908 | 9 | `docs/900-ai-council/` |
| **Total** | | **122** | |

Note: The AI Ethics series (ANIF-700–725) uses 19 non-contiguous IDs (700–705, 710–716, 720–725); IDs 706–709 and 717–719 are unassigned. ID gaps also exist at 309–399, 408–499, 507–599, 605–699, 825–829, and 850 — these are intentional registry gaps, not missing documents. Some documents (ANIF-805, ANIF-806) exist with titles differing from the original plan but are valid and complete.

### 1.2 Schemas

| Schema File | Status |
|---|---|
| `schemas/intent_schema.yml` | Exists |
| `schemas/policy_schema.yml` | Exists |
| `schemas/action_schema.yml` | Exists |
| `schemas/risk_score_schema.yml` | Exists |
| `schemas/audit_record_schema.yml` | Exists |
| `schemas/example_intent.yml` | Exists (example, not normative) |

### 1.3 Supporting Artefacts

| Artefact | Status |
|---|---|
| `CLAUDE.md` | Exists — authoritative document registry and writing standards |
| `CLAUDE_FRAMEWORK_BUILD_GUIDE.md` | Exists |
| `CLAUDE_PLATFORM_BUILD_GUIDE.md` | Exists |
| `docs/gap-analysis/ANIF_Documentation_Gap_Analysis.md` | Exists — **OBSOLETE**, claims zero documents exist |
| `docs/superpowers/plans/2026-04-07-anif-ai-framework-documentation.md` | Exists — implementation plan for Phases 1–12 |

---

## 2. Critical Gaps

### 2.1 ANIF-501: No L5 (AI-Native) Conformance Level Section

**Severity: Critical**

ANIF-501 (Conformance Level Definitions) defines L1 through L4 in sections 4.1–4.4. There is no section 4.5 for L5 (AI-Native). The summary table in section 5 has only four columns (L1–L4) and no L5 column.

ANIF-000 (Introduction) references L5 at line 213 and states: "L5 AI-Native = ANIF-700–725, ANIF-800–824, ANIF-900–908 implemented and third-party verified." Multiple documents in the 800–900 series reference L5 conformance requirements. Without a normative L5 definition in ANIF-501, these references have no formal basis.

**Impact:** No organisation can claim L5 conformance because the conformance level is not formally defined with mandatory requirements, evidence requirements, or verification methods.

**Required action:** Add section 4.5 (L5 — AI-Native) to ANIF-501 with:
- 4.5.1 Description
- 4.5.2 Mandatory Requirements (referencing ANIF-700–725, 800–824, 830–839, 840–849, 900–908)
- 4.5.3 Recommended Requirements
- 4.5.4 Evidence Required
- 4.5.5 ANIF Document Series That MUST Be Satisfied
- 4.5.6 Verification Method
- Update section 5 summary table to include an L5 column

### 2.2 L5 Definition Omits Two Series

**Severity: High**

Everywhere L5 is defined (ANIF-000 line 213, ANIF-823 section 7), it lists: "ANIF-700–725, ANIF-800–824, ANIF-900–908". This omits:

- **ANIF-830–839** (AI Governance) — 10 documents
- **ANIF-840–849** (AI Security) — 10 documents
- **ANIF-851** (AI Compliance) — 1 document

Without these three series, an L5 claim would not require AI governance or AI security. This is clearly an error — multiple 830/840-series documents themselves reference L5 certification requirements (e.g., ANIF-849 section 8 defines L5 security certification conditions).

**Required action:** Update all locations where L5 is defined to include: ANIF-700–725, ANIF-800–824, ANIF-830–839, ANIF-840–849, ANIF-851, ANIF-900–908.

### 2.3 Phantom Cross-References

**Severity: High**

Two ANIF IDs are referenced in the corpus but have no corresponding document on disk:

| Phantom ID | Referenced In | Context |
|---|---|---|
| ANIF-108 | `docs/gap-analysis/ANIF_Documentation_Gap_Analysis.md` line 346 | Suggested as potential "AI Validation Governance" document |
| ANIF-311 | `CLAUDE_PLATFORM_BUILD_GUIDE.md` lines 35, 110 | Referenced as "Intent queue" for Redis and pipeline close stage |

**Required action:**
- ANIF-108: Reference is in the obsolete gap analysis file. No action needed if that file is superseded.
- ANIF-311: Fix in CLAUDE_PLATFORM_BUILD_GUIDE.md — replace with the correct ANIF document reference (likely ANIF-300 or ANIF-306) or remove the reference.

---

## 3. Structural Template Gaps

14 documents are missing one or more mandatory template sections per CLAUDE.md standards.

### 3.1 Missing Conformance Requirements Section

| Document | Notes |
|---|---|
| ANIF-000 Introduction | Acceptable — introduction documents are informative, not normative |
| ANIF-401 Observability Standard | Also missing Security Considerations |
| ANIF-500 Conformance Overview | Also missing Security and Operational Considerations |
| ANIF-502 Certification Process | Also missing Security and Operational Considerations |
| ANIF-504 Vendor Profile Template | Template document — may be acceptable |
| ANIF-505 Cloud Profile Template | Template document — may be acceptable |

### 3.2 Missing Security Considerations Section

| Document |
|---|
| ANIF-401 Observability Standard |
| ANIF-500 Conformance Overview |
| ANIF-501 Conformance Level Definitions |
| ANIF-502 Certification Process |
| ANIF-503 Test Case Catalogue |

### 3.3 Missing Operational Considerations Section

| Document |
|---|
| ANIF-500 Conformance Overview |
| ANIF-501 Conformance Level Definitions |
| ANIF-502 Certification Process |
| ANIF-503 Test Case Catalogue |

### 3.4 Missing or Non-Standard Scope Sections

Verification of individual files found the following actual state:

| Document | Actual State |
|---|---|
| ANIF-506 Telco Profile Template | Missing Out of Scope section |
| ANIF-600 Schema Reference | Has `### 1.4 Scope` — non-standard position (should be 1.2); no Out of Scope |
| ANIF-601 Worked Examples | Has `### 1.2 Conventions Used` — no Scope or Out of Scope sections |
| ANIF-602 Implementation Guide | Has `### 1.3 Document Scope` — non-standard heading; no Out of Scope |
| ANIF-603 Glossary Extensions | Has `### 1.2 Scope` and `### 1.3 Out of scope` — present but lowercase heading |
| ANIF-604 Reference Prototype Guide | Has `### 1.2 Scope` and `### 1.3 What the prototype is NOT` — non-standard Out of Scope heading |

**Required action:** ANIF-601 and ANIF-602 have genuine gaps and are addressed in Task 9. ANIF-600, ANIF-603, ANIF-604 have sections in non-standard positions or with non-standard headings — these are low-priority cosmetic issues. ANIF-506 is a profile template; the structural gap is acceptable.

**Pattern:** The structural gaps are concentrated in the 400–600 series (written first) and are absent from the 700–900 series (written later with stricter template adherence).

---

## 4. Content Consistency Gaps

### 4.1 Governance Mode Inconsistency

The base framework (ANIF-003 Glossary, ANIF-300 series) defines **three** governance modes: `auto`, `manual_review`, `block`.

The AI Council series (ANIF-900, ANIF-904) introduces a **fourth** mode: `council_review`. This fourth mode is also referenced in the 700-series ethics documents (ANIF-702, ANIF-712, ANIF-720, ANIF-724, ANIF-725).

However, the foundational documents have not been updated to reflect this fourth mode:
- ANIF-003 Glossary (line 85): defines only three modes
- ANIF-301 (Policy Engine): routes to three modes only
- ANIF-305 (Decision Engine): produces three modes only

**Required action:** Update ANIF-003, ANIF-301, and ANIF-305 to acknowledge the fourth `council_review` governance mode. This can be done by adding it as an L5-specific mode that is only available when the AI Council series is implemented.

### 4.2 Glossary Missing AI-Specific Terms

ANIF-003 (Glossary) contains ~65 terms covering the base framework (ANIF-001–604). It has no AI-specific terms from the 700–900 series. The following terms are used extensively across the AI series but are not defined in either ANIF-003 or ANIF-603 (Glossary Extensions):

| Term | Primary Usage | Suggested Definition Location |
|---|---|---|
| Deterministic shadow | ANIF-807 | ANIF-003 or ANIF-603 |
| Ethics strike | ANIF-716, ANIF-805, ANIF-907 | ANIF-003 or ANIF-603 |
| Trust level (SYSTEM/VERIFIED/PROVISIONAL/UNTRUSTED) | ANIF-805 | ANIF-003 or ANIF-603 |
| Council review (governance mode) | ANIF-900, ANIF-904 | ANIF-003 |
| Mode Selector | ANIF-902 | ANIF-003 or ANIF-603 |
| Harm severity score | ANIF-712, ANIF-904 | ANIF-003 or ANIF-603 |
| Episodic memory | ANIF-806, ANIF-904 | ANIF-003 or ANIF-603 |
| Knowledge package | ANIF-812, ANIF-905, ANIF-908 | ANIF-003 or ANIF-603 |
| Build-Time Council | ANIF-903 | ANIF-003 or ANIF-603 |
| Runtime Council | ANIF-904 | ANIF-003 or ANIF-603 |
| Review Council | ANIF-905 | ANIF-003 or ANIF-603 |
| Agent manifest | ANIF-802, ANIF-903 | ANIF-003 or ANIF-603 |
| Tier (agent tier 0–3) | ANIF-800, ANIF-801 | ANIF-003 or ANIF-603 |
| Prompt injection | ANIF-842 | ANIF-003 or ANIF-603 |
| Zero trust (agent context) | ANIF-843 | ANIF-003 or ANIF-603 |

**Required action:** Add these terms to ANIF-003 (if the glossary is to remain the single terminology source) or to ANIF-603 (Glossary Extensions), with cross-references to the defining documents.

### 4.3 Policy Condition Syntax Undefined

`schemas/policy_schema.yml` defines a `condition` field as an opaque string. No document specifies the grammar for policy condition expressions. ANIF-302 (Policy Engine Specification) describes policy evaluation but does not define the condition language.

**Required action:** Define the condition expression grammar in ANIF-302 or create a dedicated appendix. Without this, implementers cannot write interoperable policy conditions.

---

## 5. Obsolete Artefacts

| Artefact | Issue | Required Action |
|---|---|---|
| `docs/gap-analysis/ANIF_Documentation_Gap_Analysis.md` | Claims "zero formally structured ANIF-numbered documents exist"; lists all series as MISSING | Mark as superseded by this document or delete |

---

## 6. Prioritised Action Plan

| Priority | Action | Affected Documents | Effort |
|---|---|---|---|
| P0 | Add L5 conformance level to ANIF-501 | ANIF-501 | Medium — new section 4.5 with ~15 mandatory requirements |
| P0 | Fix L5 series list (add ANIF-830–849, ANIF-851) | ANIF-000, ANIF-501, ANIF-823 | Small — text edits in 3 documents |
| P1 | Fix phantom reference ANIF-311 | CLAUDE_PLATFORM_BUILD_GUIDE.md | Small — replace with correct reference |
| P1 | Add `council_review` as fourth governance mode | ANIF-003, ANIF-301, ANIF-305 | Medium — update glossary entries and routing logic |
| P1 | Add missing structural sections to 500-series | ANIF-500, ANIF-501, ANIF-502, ANIF-503 | Medium — add Security/Operational Considerations |
| P2 | Add AI-specific glossary terms | ANIF-003 or ANIF-603 | Medium — ~15 term definitions |
| P2 | Add missing structural sections to 400/600-series | ANIF-401, ANIF-504–506, ANIF-600–604 | Medium |
| P2 | Define policy condition expression grammar | ANIF-302 | Medium — language specification |
| P3 | Supersede or delete obsolete gap analysis | Gap analysis file | Small |

---

## 7. Summary

The ANIF framework documentation is complete in coverage — all 14 series, 122 documents, 6 schemas, and 2 project guides exist. The remaining work is integration and consistency: defining L5 formally, synchronising terminology across the base and AI series, and bringing early-written documents up to the template standard established by the later series.

No new documents need to be written. The work is editorial.
