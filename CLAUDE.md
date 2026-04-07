# CLAUDE.md — Autonomous Networking & Infrastructure Framework (ANIF)

## What This Project Is

The Autonomous Networking & Infrastructure Framework (ANIF) is a vendor-neutral, open governance framework for specifying, implementing, and operating autonomous network and infrastructure management systems. This repository contains the normative framework documentation, schemas, and reference prototype.

ANIF does not build products. ANIF specifies what conformant products must do.

---

## Document Writing Standards

All ANIF documents are formal technical specifications. Every document written in this repository MUST conform to these standards without exception.

### Language

- **British English spelling throughout.** Use: organisation, authorisation, virtualisation, behaviour, catalogue, recognise, licence (noun), standardise. Never use American spellings.
- **Third person only.** Never use "we", "you", "our", or "I" in specification text.
- **No contractions.** Write "do not", not "don't". Write "it is", not "it's".
- **No marketing language.** Words such as "powerful", "seamless", "cutting-edge", "robust", "best-in-class", and "innovative" are banned.
- **No hedging language.** Do not write "it is worth noting", "it is important to", "please note", "as mentioned above". State the fact directly.
- **No padding.** Every sentence must carry information. Remove sentences that restate what the previous sentence said.

### Normative Language — RFC 2119

All requirements MUST use RFC 2119 key words exactly as defined. The key words are:

| Term | Meaning |
|---|---|
| MUST | Absolute requirement. Non-negotiable. |
| MUST NOT | Absolute prohibition. |
| SHOULD | Recommended. Deviation requires documented justification. |
| SHOULD NOT | Not recommended. Deviation requires documented justification. |
| MAY | Optional. Permitted but not required. |

Rules:
- Key words MUST be written in ALL CAPS in specification text.
- Do not use "must" (lowercase) when you mean MUST. Lowercase "must" implies a natural necessity, not a normative requirement.
- Do not use "should" (lowercase) when you mean SHOULD.
- Every MUST and MUST NOT requirement MUST be independently testable.
- Do not use "required to" as a synonym for MUST. Use MUST.
- Do not use "it is recommended that" as a synonym for SHOULD. Use SHOULD.

### Structure

Every ANIF document MUST use this template structure:

```
# ANIF-NNN: Title

| Field        | Value   |
|---|---|
| Doc ID       | ANIF-NNN |
| Series       | [Foundation / Governance / Architecture / Core / Operations / Conformance / Annexes / AI Ethics / AI Agent Architecture / AI Governance / AI Security / AI Compliance / AI Council] |
| Version      | 0.1.0   |
| Status       | Draft   |
| Authors      | ANIF Working Group |
| Reviewers    | —       |
| Approved by  | —       |
| Created      | YYYY-MM-DD |
| Last updated | YYYY-MM-DD |
| Replaces     | N/A     |
| Related docs | [comma-separated ANIF-NNN list] |

---

## Abstract
[One paragraph. What this document specifies. Why it exists. Who must read it.]

---

## 1. Introduction
### 1.1 Purpose
### 1.2 Scope
### 1.3 Out of Scope
### 1.4 Intended Audience

---

## 2. Normative References

---

## 3. Terms and Definitions

---

## [4–N]. Core specification sections

---

## [N+1]. Conformance Requirements

---

## [N+2]. Security Considerations

---

## [N+3]. Operational Considerations

---

## Appendix A: [Examples / Change History / etc.]
```

Rules:
- The frontmatter table is mandatory on every document.
- The Abstract is a single paragraph — not a bullet list.
- Scope and Out of Scope are mandatory. "Out of scope" sets boundaries explicitly; never omit it.
- Conformance Requirements is mandatory on all normative documents. List each MUST and SHOULD as a discrete, testable statement.
- Section numbering is decimal (1, 1.1, 1.2, 2, 2.1, etc.). No letters.
- Use tables over prose lists where two or more attributes are being described.
- Code blocks use triple backticks with a language identifier (```yaml, ```json, ```python).

### Cross-References

- Reference other ANIF documents as: `ANIF-NNN — Document Title`
- In running text: "as defined in ANIF-301" or "see ANIF-302 for policy engine internals"
- Do not forward-reference a document that does not exist yet unless the reference is to a document that is explicitly planned and listed in the document index
- Do not invent ANIF document IDs that are not in the authorised document index

### Numbers and Values

- Threshold values MUST be stated precisely. Never write "a high risk score" — write "a risk score greater than 70".
- Percentages include the % symbol: 99.999%, not "five nines" in normative text.
- Time durations state the unit: 15 minutes, not "fifteen minutes" in normative contexts.
- UUIDs are always referred to as UUID v4 unless a different version is required.

---

## ANIF Document ID Registry

Do not invent IDs outside this registry.

| Series | Range | Topic |
|---|---|---|
| ANIF-000 | Introduction | Problem statement and vision |
| ANIF-001–004 | Foundation | Charter, principles, glossary, RACI |
| ANIF-100–107 | Governance | Operational governance and compliance |
| ANIF-200–205 | Architecture | Reference, business, data, application, technology, security |
| ANIF-300–308 | Core | Intent framework, policy, risk, decision, execution |
| ANIF-400–407 | Operations | Observability, closed-loop, incident, human-in-loop |
| ANIF-500–506 | Conformance | Levels, certification, test cases, vendor/cloud/telco profiles |
| ANIF-600–604 | Annexes | Schemas, worked examples, implementation guide, glossary extensions |
| ANIF-700–725 | AI Ethics | Principles, policies, code-enforced constraints, agent containment |
| ANIF-800–824 | AI Agent Architecture | Agent model, roles, learning, context, scaling, disaster recovery |
| ANIF-830–839 | AI Governance | Policy engine, audit, human override, council governance |
| ANIF-840–849 | AI Security | Threat model, access control, adversarial, supply chain |
| ANIF-851 | AI Compliance | Industry compliance (HIPAA, PCI-DSS, SOX, GDPR, NIST, FedRAMP) |
| ANIF-900–908 | AI Council | Council charter, deliberation models, escalation, mode selector |

---

## Skills — When to Use Each

### Before designing a new document series
Use `superpowers:brainstorming`. Do not write documents for a new series without first brainstorming the series structure and getting approval.

### After a design is approved
Use `superpowers:writing-plans` to produce the ordered implementation plan before writing any documents.

### When writing multiple independent documents
Use `superpowers:dispatching-parallel-agents`. Documents in the same series with no cross-dependencies can be written in parallel.

### Before claiming a series is complete
Use `superpowers:verification-before-completion`. Check every document in the series has: frontmatter, Abstract, conformance section, normative language, and correct cross-references.

### When building prototype or platform code
Use `superpowers:test-driven-development`. Write tests from the ANIF spec before writing implementation code.

### When debugging prototype code
Use `superpowers:systematic-debugging` before proposing any fix.

### After completing a platform module
Use `superpowers:requesting-code-review`.

### Before merging any branch
Use `superpowers:finishing-a-development-branch`.

### Speckit workflow for each document
`speckit.specify` → `speckit.clarify` → `speckit.tasks` → write → `speckit.analyze`

---

## What Not To Do

- **Do not invent ANIF document IDs** outside the authorised registry above.
- **Do not add scope** to a document that is not in its defined purpose — write a separate document if new scope is needed.
- **Do not skip the Conformance Requirements section** on any normative document.
- **Do not use lowercase normative terms** (must, should, may) when RFC 2119 key words (MUST, SHOULD, MAY) are required.
- **Do not forward-reference unplanned documents** — if an ID is not in the registry, do not reference it.
- **Do not write abstract or vague requirements** — every MUST must be independently testable.
- **Do not pad documents with caveats, disclaimers, or transitional prose** — state the requirement and move on.
- **Do not use American English spelling** in any document in this repository.
- **Do not start a new document series without brainstorming first.**

---

## Build Order Rules

Documents have dependencies. Write in this order within and across series:

1. Foundation (ANIF-001–004) — required before everything
2. Governance overview (ANIF-100) — required before other governance docs
3. Architecture overview (ANIF-200) — required before other architecture docs
4. Core framework overview (ANIF-300) — required before other core docs
5. Operations overview (ANIF-400) — required before other operations docs
6. Within any series: overview/introduction document before detail documents
7. AI Ethics (ANIF-700–725) — before AI Agent Architecture
8. AI Agent Architecture (ANIF-800–824) — before AI Governance and AI Security
9. AI Governance (ANIF-830–839) and AI Security (ANIF-840–849) — can proceed in parallel
10. AI Council (ANIF-900–908) — after AI Governance

---

## Schema Standards

All schemas live in `schemas/`. YAML format. Validated against the schema reference (ANIF-600).

Schema files follow naming convention: `[entity]_schema.yml` (lowercase, underscores).

Every schema field must have:
- `type`
- `description`
- `example` (where not self-evident)
- Constraints (minimum, maximum, pattern, enum values) where applicable

---

## Repository Structure

```
/
├── CLAUDE.md                        ← this file
├── docs/
│   ├── 000-foundation/              ← ANIF-001 to ANIF-004
│   ├── 100-governance/              ← ANIF-100 to ANIF-107
│   ├── 200-architecture/            ← ANIF-200 to ANIF-205
│   ├── 300-core/                    ← ANIF-300 to ANIF-308
│   ├── 400-operations/              ← ANIF-400 to ANIF-407
│   ├── 500-conformance/             ← ANIF-500 to ANIF-506
│   ├── 600-annexes/                 ← ANIF-600 to ANIF-604
│   ├── 700-ai-ethics/               ← ANIF-700 to ANIF-725
│   ├── 800-ai-agent-architecture/   ← ANIF-800 to ANIF-824
│   ├── 830-ai-governance/           ← ANIF-830 to ANIF-839
│   ├── 840-ai-security/             ← ANIF-840 to ANIF-849
│   ├── 851-ai-compliance/           ← ANIF-851
│   ├── 900-ai-council/              ← ANIF-900 to ANIF-908
│   ├── gap-analysis/
│   └── superpowers/specs/           ← design documents
├── schemas/                         ← YAML schemas
├── prompts/                         ← implementation prompt drafts
└── profiles/                        ← vendor/cloud/telco conformance profiles
```
