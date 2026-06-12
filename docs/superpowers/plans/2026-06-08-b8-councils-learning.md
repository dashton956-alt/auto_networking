# B8: Councils & Learning — Implementation Plan

Date: 2026-06-08
Specs: ANIF-902, ANIF-903, ANIF-904, ANIF-905, ANIF-907, ANIF-812, ANIF-908

## MUSTs Extracted

### ANIF-902 Mode Selector
- CR-902-01: Evaluate all 6 input factors for every council decision
- CR-902-02: Deterministic; no LLM; same output for same input
- CR-902-03: Mode selection rationale logged in council record before deliberation
- CR-902-04: Selected model MUST NOT be overridden after selection complete

### ANIF-903 Build-Time Council
- CR-903-01: Convene before new agent deployment / model version change / capability expansion / trust reinstatement
- CR-903-02: Deliberation MUST NOT begin with incomplete required inputs
- CR-903-03: Consensus from all 3 veto seats (Ethics, Security, Governance) required
- CR-903-04: Blocked decision MUST state specific ANIF requirement(s)
- CR-903-05: Conditional approval MUST list each condition precisely
- CR-903-06: Agents with unmet conditions MUST NOT be VERIFIED
- CR-903-07: Build artefacts retained for agent lifetime + 3 years

### ANIF-904 Runtime Council
- CR-904-01: Intent processing MUST be paused within 5 min of council_review trigger
- CR-904-02: Mode Selector MUST complete before session opens
- CR-904-03: Deliberation within time limits (Majority/Weighted: 15 min, Consensus: 30 min, Adversarial: 45 min)
- CR-904-04: No decision within time limit → intent MUST be halted (HALTED_COUNCIL_TIMEOUT)
- CR-904-05: Timeout MUST NOT result in intent proceeding
- CR-904-06: 3+ timeouts in 30 days → reported to governance committee

### ANIF-905 Review Council
- CR-905-01: Convened within 5 business days of Severity 1 ethics incident or Level 3+ security incident
- CR-905-02: MUST always use adversarial deliberation model
- CR-905-03: MUST produce 3 outputs: accountability_determination, policy_change_recommendations, learning_packages
- CR-905-04: Policy change recs MUST cite specific ANIF docs + sections
- CR-905-05: Report submitted to governance committee within 72 hours of incident closure
- CR-905-06: Learning packages submitted to Learning Agent within 10 business days

### ANIF-907 Council Audit
- CR-907-01: Every session MUST produce council record per schema
- CR-907-02: Council records immutable after session close; corrections append-only
- CR-907-03: Write-once or cryptographic append-only guarantees
- CR-907-04: Agent components MUST NOT have read access to council records
- CR-907-05: 10-year retention (Build-Time and Runtime)
- CR-907-06: Level 4 security incident Review Council records permanently retained

### ANIF-812 Learning Agent
- CR-812-01: No knowledge package distributed without human approval
- CR-812-02: Knowledge items MUST reference verifiable evidence
- CR-812-03: Packages delivered only to agents whose roles match target_roles
- CR-812-04: Packages pending > 5 business days → escalated to AI Council
- CR-812-05: Source quality < 0.60 → flagged; items withheld until > 0.70
- CR-812-06: Negative examples captured from: failed intents, human overrides, ethics violations, rollbacks
- CR-812-07: Negative examples same approval process as positive items

## Module Structure

```
src/anif_platform/council/
    __init__.py
    models.py        — CouncilRecordRow (SQLAlchemy, append-only)
    schemas.py       — Pydantic request/response schemas
    mode_selector.py — ANIF-902 deterministic 9-rule matrix
    service.py       — BuildTimeCouncil, RuntimeCouncil, ReviewCouncil
    router.py        — FastAPI endpoints

src/anif_platform/learning/
    __init__.py
    models.py        — KnowledgePackageRow, KnowledgeItemRow
    broker.py        — KnowledgeBroker (approval gate, distribution, quality)
    router.py        — FastAPI endpoints

migrations/versions/007_add_council_records.py
migrations/versions/008_add_knowledge_packages.py
```

## Tasks

1. Write failing tests (all MUSTs above)
2. council/models.py + migration 007
3. learning/models.py + migration 008
4. council/mode_selector.py (ANIF-902)
5. council/service.py (ANIF-903/904/905)
6. council/schemas.py + council/router.py
7. learning/broker.py (ANIF-812)
8. learning/router.py
9. Wire main.py (routers, dependency overrides)
10. Final: ruff + pytest, commit
