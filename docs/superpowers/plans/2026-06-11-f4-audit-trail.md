# F4: Audit Trail Viewer — Implementation Plan

Date: 2026-06-11
Specs: ANIF-107 §4.5 (audit query API), §4.7 (hash chaining)
Backend dependency: B2 Audit API — complete
WCAG 2.1 AA required on every page (enforced by Playwright/axe)

## Scope (design spec §16)

Queryable audit log table, reasoning chain expander, intent history timeline.

Backend endpoints (all exist):
- `GET /audit` — filters: stage, outcome, date_from, date_to, operator_id,
  action_type, environment; limit (≤1000, default 50) + offset; returns a
  bare list (no total — UI infers "more" when a full page returns)
- `GET /audit/{intent_id}` — chronological records for one intent
- `GET /audit/{intent_id}/why` — synthesised explanation
- `GET /audit/{intent_id}/verify` — `{valid, broken_at, record_count}`

## Backend fix in scope: audit endpoints are unauthenticated

Same gap class as the /override finding: the audit router has no
`get_api_key` dependency — the audit trail (operational reasoning,
operator ids) is world-readable. Fix (TDD):

1. Failing test: unauthenticated `GET /audit*` → 401 with key configured
2. Add `Depends(get_api_key)` to all four audit endpoints
3. conftest `client` fixture additionally overrides `get_api_key` so
   existing fixture-based tests stay unauthenticated-in-test

## Frontend architecture

```
src/anif_ui/src/
  api/audit.ts            ← listAuditRecords(filters), verifyChain
  components/AuditRecordDetail.tsx ← reasoning steps + in/out summaries +
                                      policies (shared by table + timeline)
  pages/AuditTrailPage.tsx     ← /audit (replaces placeholder)
  pages/IntentTimelinePage.tsx ← /audit/:intentId
```

### AuditTrailPage (/audit)
- Filter bar: stage Select, outcome Select, environment Select, operator
  Input, date-from / date-to (datetime-local Inputs), intent-id Input with
  "View timeline" jump; Apply + Reset buttons (explicit apply, no
  fetch-per-keystroke)
- Records table (custom expandable table, F1 styling): timestamp, intent
  id (link → timeline), stage Badge, outcome Badge, duration, operator
- **Reasoning chain expander**: per-row toggle button (aria-expanded +
  aria-controls) revealing AuditRecordDetail in a full-width detail row
- Pagination: Previous/Next via offset; "Next" enabled when a full page
  came back; loading skeleton, error Alert, empty state

### IntentTimelinePage (/audit/:intentId)
- **Hash-chain verification banner** from `/verify`: valid → success Alert
  (n records verified); broken → danger Alert naming `broken_at`
- "Why" explanation panel
- **Vertical timeline** (ol) of records: stage Badge + outcome Badge,
  timestamp, duration, expandable AuditRecordDetail per entry
- Links: back to /audit, across to /intents/:id

## WCAG / tests
- axe audits: /audit (filters + expanded row) and /audit/:intentId
  (timeline + expanded entry), mocked API — 0 violations
- Live UAT: real backend, seed records via /orchestrate + /governance/check,
  filter, expand reasoning, open timeline, verify chain banner

## Task order
1. Backend TDD: audit auth test → fix router + conftest → green
2. api/audit.ts + AuditRecordDetail component
3. AuditTrailPage (filters, expandable table, pagination) + route
4. IntentTimelinePage (verify banner, why, timeline) + route
5. axe audits (2 new) — 0 violations
6. Gates: eslint, build, pytest, mypy/ruff/black on touched backend
7. Live UAT + architecture doc update + commit
