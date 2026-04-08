# CLAUDE_FRAMEWORK_BUILD_GUIDE.md

## What This Guide Is For

This guide is for contributors — human or AI — who are **writing and extending ANIF framework documentation**. It covers how to add new document series, write individual documents, verify quality, and maintain consistency across the corpus.

This guide is distinct from `CLAUDE_PLATFORM_BUILD_GUIDE.md`, which covers building conformant software on top of ANIF.

---

## Required Skills — When to Invoke

| Skill | When |
|---|---|
| `superpowers:brainstorming` | Before designing any new document series. **REQUIRED** — do not write documents for a new series without it |
| `superpowers:writing-plans` | After brainstorming design is approved; produces the ordered implementation plan |
| `superpowers:executing-plans` | When working through the document build plan task by task |
| `superpowers:dispatching-parallel-agents` | Writing independent documents in the same series simultaneously |
| `superpowers:verification-before-completion` | Before claiming any series is complete |
| `speckit.specify` | Creating or updating the specification for a document |
| `speckit.clarify` | Resolving cross-reference ambiguities before writing |
| `speckit.tasks` | Generating an ordered task list for a document series |
| `speckit.analyze` | Cross-artefact consistency check after series completion |

---

## Document Writing Workflow

Follow this order. Do not skip steps.

1. **Brainstorm the series** — invoke `superpowers:brainstorming`. Define: what documents are needed, their IDs (from the authorised registry in CLAUDE.md), their dependencies, and their build order. Get approval before writing.
2. **Write the implementation plan** — invoke `superpowers:writing-plans`. Produce an ordered plan with one task per document, content specifications for each section, and the dependency sequence.
3. **Specify each document** — invoke `speckit.specify` for each document to confirm its scope, key content, and cross-references before writing.
4. **Clarify ambiguities** — invoke `speckit.clarify` to resolve any cross-reference questions before writing begins.
5. **Write in dependency order** — always write the series overview/introduction document before detail documents. Never write a document that references an unwritten document unless the reference is to a document that exists in the authorised registry.
6. **Consistency check** — invoke `speckit.analyze` on the full series after all documents are written. Fix any cross-reference inconsistencies.
7. **Verify completeness** — invoke `superpowers:verification-before-completion`. Every document must pass the verification checklist before the series is declared complete.
8. **Commit** — commit each document or batch with a clear commit message following the pattern `docs: add ANIF-NNN Title`.

---

## Document Template

Every ANIF document MUST use this structure exactly. No sections may be omitted from normative documents.

```markdown
# ANIF-NNN: Title

| Field        | Value          |
|---|---|
| Doc ID       | ANIF-NNN       |
| Series       | [Series name]  |
| Version      | 0.1.0          |
| Status       | Draft          |
| Authors      | ANIF Working Group |
| Reviewers    | —              |
| Approved by  | —              |
| Created      | YYYY-MM-DD     |
| Last updated | YYYY-MM-DD     |
| Replaces     | N/A            |
| Related docs | ANIF-NNN, ... |

---

## Abstract
[Single paragraph. What this document specifies. Why it exists. Who must read it.]

---

## 1. Introduction
### 1.1 Purpose
### 1.2 Scope
### 1.3 Out of Scope
### 1.4 Intended Audience

## 2. Normative References

## 3. Terms and Definitions   ← omit if no new terms

## [4–N]. Core specification sections

## [N+1]. Conformance Requirements

## [N+2]. Security Considerations

## [N+3]. Operational Considerations
```

**Why each section is mandatory:**

- **Frontmatter table** — provides machine-readable metadata; auditors use it to confirm document currency.
- **Abstract** — single paragraph only. Reviewers read this to decide whether to read the full document. Bullet lists here are a template violation.
- **Scope / Out of Scope** — explicitly sets boundaries. "Out of scope" prevents scope creep by naming what other documents cover. Never omit it.
- **Normative References** — establishes which documents a reader must have read before this one. Cross-references in the body MUST correspond to entries here.
- **Conformance Requirements** — the testable checklist an auditor uses to assess conformance. Every MUST and SHOULD in the document body should have a corresponding entry here.
- **Security Considerations** — even non-security documents MUST address security. If there are no security implications, state that explicitly.
- **Operational Considerations** — real-world implementation notes that are not normative but are necessary for competent deployment.

**Common mistakes per section:**

| Section | Common mistake |
|---|---|
| Abstract | Multiple paragraphs; bullet lists; hedging language ("this document aims to...") |
| Scope | Vague scope statement ("covers AI governance"); no Out of Scope |
| Requirements | Lowercase "must" and "should" instead of MUST and SHOULD |
| Conformance Requirements | Untestable requirements ("agents should behave ethically") |
| Security Considerations | Omitted; or copied from another document without adaptation |

---

## Normative Language Guide

RFC 2119 key words MUST be written in ALL CAPS. No exceptions.

| Term | Use when | Example |
|---|---|---|
| MUST | The requirement is absolute and non-negotiable | "Agents MUST declare `deterministic: false`" |
| MUST NOT | The prohibition is absolute | "Agents MUST NOT invoke Tier 3 actions without a deterministic validator" |
| SHOULD | The requirement is recommended; deviation requires documented justification | "Organisations SHOULD maintain an audit-ready posture year-round" |
| SHOULD NOT | Not recommended; deviation requires documented justification | "Organisations SHOULD NOT defer annual penetration testing" |
| MAY | Optional; permitted but not required | "The council MAY approve deployment with conditions" |

**Wrong usages to avoid:**

| Wrong | Correct |
|---|---|
| "must" (lowercase) | MUST |
| "required to" | MUST |
| "it is recommended that" | SHOULD |
| "should consider" | SHOULD (or delete if too vague) |
| "is encouraged to" | SHOULD |
| "is allowed to" | MAY |
| "can" (in normative context) | MAY |

**The independently testable test:** Before finalising any MUST requirement, ask: "Can I write a test case for this?" If the answer is no, the requirement is too vague. Rewrite it until it is testable.

Example of an untestable requirement: "Agents MUST behave safely." This cannot be tested because "safely" is undefined.

Example of a testable requirement: "Agents MUST NOT submit an intent with `action_type: interface_shutdown` without a corresponding `rollback_plan` field." This can be tested with a schema validator.

---

## Cross-Reference Rules

- Reference other ANIF documents as: `ANIF-NNN — Document Title` in tables or `ANIF-NNN` in running text.
- In running text: "as defined in ANIF-301" or "see ANIF-302 for policy engine internals".
- Do not forward-reference a document that does not exist. If an ID is not in the authorised registry in CLAUDE.md, do not use it.
- Do not invent ANIF document IDs. The registry in CLAUDE.md is authoritative.
- All documents referenced in the body MUST appear in the Normative References table.
- Circular references — document A references B, B references A — are permitted where unavoidable (e.g., overview documents reference detail documents and detail documents reference the overview). Resolve by making the reference one-directional where possible.

---

## Key Pitfalls

**Circular cross-references:** Detected by `speckit.analyze`. Fix by identifying which document is the authority and making the other document a one-way reference. If both documents genuinely need to reference each other, ensure neither creates a dependency that prevents the reader from understanding one without the other.

**Normative language drift:** Documents written over many sessions develop inconsistent normative language. Run a search for the words "must", "should", and "shall" (lowercase) before committing any document. Every occurrence should be either RFC 2119 key words in ALL CAPS or natural-language use of these words that does not carry normative meaning.

**Schema changes:** Any change to a schema in `schemas/` that modifies required fields, field types, or enumeration values MUST be assessed for backward compatibility. An existing valid intent that would fail the new schema is a breaking change. Breaking changes require a major version bump and a migration note.

**Scope creep:** Each document has a defined scope. When new content is needed that falls outside that scope, write a separate document rather than expanding the existing document's scope. One document, one responsibility.

**Template violations:** The most common template violations are: omitting the Out of Scope section, writing a multi-paragraph Abstract, omitting the Conformance Requirements section, and omitting Security Considerations. `superpowers:verification-before-completion` will catch these.

**Padding:** Sentences that restate the previous sentence, transitional paragraphs that summarise what was just said, and caveats that acknowledge limitations without adding information are all padding. Delete them. Every sentence must carry information.

**American English:** British English is mandatory. Use a spell checker configured for British English before committing. Common failures: "organization" (should be "organisation"), "authorization" (should be "authorisation"), "behavior" (should be "behaviour"), "license" (noun; should be "licence").

---

## Series Design Decision Record

When designing a new series using `superpowers:brainstorming`, capture and record the following decisions before writing begins:

- What is the series responsible for that no existing series covers?
- What are the dependencies — which series must be complete before this one can be written?
- What is the build order within the series (overview first, then detail documents)?
- Which documents in the series have cross-dependencies on each other?
- Which documents can be written in parallel?

These decisions go into the implementation plan (`superpowers:writing-plans`) and form the basis for the task sequence.

---

## Verification Checklist

Before declaring any series complete, every document in the series MUST satisfy:

- [ ] Frontmatter table complete with all fields populated
- [ ] Abstract is a single paragraph
- [ ] Scope and Out of Scope sections present
- [ ] All normative key words in ALL CAPS
- [ ] No lowercase "must", "should", or "shall" used with normative intent
- [ ] Conformance Requirements section present with independently testable statements
- [ ] Security Considerations section present
- [ ] Operational Considerations section present
- [ ] All cross-referenced ANIF IDs exist in the repository
- [ ] British English spelling throughout
- [ ] No marketing language ("powerful", "seamless", "innovative")
- [ ] No hedging language ("it is worth noting", "please note")
- [ ] No contractions
- [ ] Third person only — no "we", "you", "our", "I"
- [ ] Every number used in a normative requirement is precise (no "high", "low", "significant")
